"""Semantic validation for SwarmForge task registries and result envelopes.

This is maintainer-side contract validation, not a host runtime or artifact verifier.
"""

from __future__ import annotations

import copy
import heapq
import json
import re
from pathlib import Path
from typing import Any

UNRESOLVED_WORKER_STATES = {"dispatch_pending", "queued", "active", "unknown"}
ALLOWED_TRANSITIONS = {
    None: {"planned", "ready"},
    "planned": {"ready", "blocked", "cancelled"},
    "ready": {"active", "blocked", "cancelled"},
    "active": {"blocked", "completed", "failed", "cancelled"},
    "blocked": {"planned", "cancelled"},
    "failed": {"planned", "completed"},
    "cancelled": {"planned"},
    "completed": set(),
}
RETRY_DECISIONS = {"retry", "reassign", "resume"}
CANCEL_RESUME_DECISIONS = {"reassign", "resume"}
URI_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def _error(code: str, message: str) -> str:
    return f"{code}: {message}"


def _normalise_repo_path(value: Any) -> str | None:
    if not isinstance(value, str) or not value or value.startswith("/") or "\\" in value:
        return None
    if re.match(r"^[A-Za-z]:", value):
        return None
    parts = value.rstrip("/").split("/")
    if not parts or any(part in {"", ".", ".."} for part in parts):
        return None
    return "/".join(parts)


def _paths_overlap(left: str, right: str) -> bool:
    return (
        left == right
        or left.startswith(right + "/")
        or right.startswith(left + "/")
    )


def _depends_on(task_id: str, ancestor_id: str, dependencies: dict[str, list[str]]) -> bool:
    pending = list(dependencies.get(task_id, []))
    visited: set[str] = set()
    while pending:
        current = pending.pop()
        if current == ancestor_id:
            return True
        if current in visited:
            continue
        visited.add(current)
        pending.extend(dependencies.get(current, []))
    return False


def _coordinator_record_is_complete(task: dict[str, Any]) -> bool:
    verification = task.get("coordinator_verification")
    if not isinstance(verification, dict):
        return False
    criteria = {
        item.get("id")
        for item in task.get("acceptance_criteria", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    outcomes = verification.get("criterion_outcomes")
    criterion_evidence = verification.get("criterion_evidence_refs")
    evidence_refs = verification.get("evidence_refs")
    attempts = task.get("attempts", [])
    latest = attempts[-1] if isinstance(attempts, list) and attempts else None
    expected_attempt_id = latest.get("attempt_id") if isinstance(latest, dict) else None
    return (
        verification.get("verified_by") == "coordinator"
        and verification.get("task_spec_revision") == task.get("task_spec_revision")
        and verification.get("attempt_id") == expected_attempt_id
        and verification.get("result_correlation") == "matched"
        and verification.get("artifact_integrity") == "verified"
        and verification.get("accepted") is True
        and bool(verification.get("accepted_at"))
        and bool(verification.get("verified_at"))
        and isinstance(evidence_refs, list)
        and bool(evidence_refs)
        and isinstance(outcomes, dict)
        and set(outcomes) == criteria
        and all(outcomes.get(criterion_id) == "pass" for criterion_id in criteria)
        and isinstance(criterion_evidence, dict)
        and set(criterion_evidence) == criteria
        and all(
            isinstance(criterion_evidence.get(criterion_id), list)
            and bool(criterion_evidence[criterion_id])
            and set(criterion_evidence[criterion_id]) <= set(evidence_refs)
            for criterion_id in criteria
        )
    )


def _has_completion_evidence(task: dict[str, Any]) -> bool:
    history = task.get("state_history", [])
    if not history or history[-1].get("to") != "completed":
        return False
    if not history[-1].get("evidence_refs"):
        return False
    attempts = task.get("attempts", [])
    if attempts:
        latest = attempts[-1]
        if latest.get("result_completeness") != "complete":
            return False
        if not latest.get("acceptance_evidence_refs"):
            return False
    return _coordinator_record_is_complete(task)


def _validate_coordinator_verification(
    task_id: str,
    task: dict[str, Any],
    criterion_ids: list[str],
    registry_revision: int,
) -> list[str]:
    errors: list[str] = []
    verification = task.get("coordinator_verification")
    if not isinstance(verification, dict):
        return [_error("REGISTRY_COORDINATOR_VERIFICATION_MISSING", f"{task_id} has no coordinator verification record")]

    attempts = task.get("attempts", [])
    latest = attempts[-1] if isinstance(attempts, list) and attempts and isinstance(attempts[-1], dict) else None
    expected_attempt_id = latest.get("attempt_id") if latest else None
    verified_revision = verification.get("verified_registry_revision")
    if (
        verification.get("verified_by") != "coordinator"
        or verification.get("task_spec_revision") != task.get("task_spec_revision")
        or verification.get("attempt_id") != expected_attempt_id
        or not isinstance(verified_revision, int)
        or verified_revision > registry_revision
        or (latest is not None and verified_revision < latest.get("dispatch_registry_revision", 0))
    ):
        errors.append(_error("REGISTRY_COORDINATOR_VERIFICATION_STALE", f"{task_id} coordinator verification is not bound to the current task specification and latest attempt"))

    outcomes = verification.get("criterion_outcomes")
    criterion_evidence = verification.get("criterion_evidence_refs")
    global_evidence = verification.get("evidence_refs")
    if (
        not isinstance(outcomes, dict)
        or set(outcomes) != set(criterion_ids)
        or not isinstance(criterion_evidence, dict)
        or set(criterion_evidence) != set(criterion_ids)
    ):
        errors.append(_error("REGISTRY_COORDINATOR_CRITERIA_MISMATCH", f"{task_id} coordinator verification must cover exactly its acceptance criteria"))
    elif isinstance(global_evidence, list):
        for criterion_id in criterion_ids:
            refs = criterion_evidence.get(criterion_id)
            if outcomes.get(criterion_id) != "pending" and (not isinstance(refs, list) or not refs):
                errors.append(_error("REGISTRY_COORDINATOR_CRITERION_EVIDENCE_MISSING", f"{task_id} criterion {criterion_id} has a non-pending outcome without evidence"))
            elif isinstance(refs, list) and not set(refs) <= set(global_evidence):
                errors.append(_error("REGISTRY_COORDINATOR_EVIDENCE_REFERENCE_MISSING", f"{task_id} criterion {criterion_id} evidence is absent from the coordinator record"))

    accepted = verification.get("accepted") is True
    if accepted:
        complete = (
            task.get("status") == "completed"
            and verification.get("result_correlation") == "matched"
            and verification.get("artifact_integrity") == "verified"
            and isinstance(outcomes, dict)
            and set(outcomes) == set(criterion_ids)
            and all(outcomes.get(criterion_id) == "pass" for criterion_id in criterion_ids)
            and isinstance(criterion_evidence, dict)
            and set(criterion_evidence) == set(criterion_ids)
            and all(isinstance(criterion_evidence.get(criterion_id), list) and criterion_evidence[criterion_id] for criterion_id in criterion_ids)
            and isinstance(global_evidence, list)
            and bool(global_evidence)
            and verification.get("accepted_at") is not None
            and verification.get("verified_at") is not None
        )
        if not complete:
            errors.append(_error("REGISTRY_COORDINATOR_ACCEPTANCE_INCOMPLETE", f"{task_id} is accepted without complete coordinator verification"))
    else:
        if task.get("status") == "completed":
            errors.append(_error("REGISTRY_COMPLETED_WITHOUT_COORDINATOR_ACCEPTANCE", f"{task_id} completed without an accepted coordinator verification record"))
        if verification.get("accepted_at") is not None:
            errors.append(_error("REGISTRY_COORDINATOR_ACCEPTANCE_TIMESTAMP_MISMATCH", f"{task_id} has accepted_at while accepted is false"))
    return errors


def _validate_workspace_verification(
    task_id: str,
    task: dict[str, Any],
    registry_revision: int,
) -> list[str]:
    """Validate that workspace evidence still covers the current task scope."""
    errors: list[str] = []
    verification = task.get("workspace_verification")
    if not isinstance(verification, dict):
        return [_error("REGISTRY_WORKSPACE_VERIFICATION_MISSING", f"{task_id} has no workspace verification record")]
    if verification.get("verified_by") != "coordinator":
        errors.append(_error("REGISTRY_WORKSPACE_VERIFIER_INVALID", f"{task_id} workspace evidence is not coordinator-owned"))

    if verification.get("task_spec_revision") != task.get("task_spec_revision"):
        errors.append(_error("REGISTRY_WORKSPACE_VERIFICATION_STALE", f"{task_id} workspace evidence is bound to a different task-spec revision"))

    verified_revision = verification.get("verified_registry_revision")
    if not isinstance(verified_revision, int) or isinstance(verified_revision, bool) or verified_revision < 1:
        errors.append(_error("REGISTRY_WORKSPACE_VERIFICATION_REVISION_INVALID", f"{task_id} workspace evidence has an invalid registry revision"))
    elif verified_revision > registry_revision:
        errors.append(_error("REGISTRY_WORKSPACE_VERIFICATION_FUTURE_REVISION", f"{task_id} workspace evidence references a future registry revision"))

    scope = verification.get("scope")
    if not isinstance(scope, dict):
        errors.append(_error("REGISTRY_WORKSPACE_SCOPE_MISSING", f"{task_id} workspace evidence has no read/write scope snapshot"))
    else:
        def normalised_paths(paths: Any) -> list[str] | None:
            if not isinstance(paths, list):
                return None
            normalised = [_normalise_repo_path(path) for path in paths]
            if any(path is None for path in normalised):
                return None
            return sorted(normalised)

        for field in ("read_paths", "write_paths"):
            recorded_paths = normalised_paths(scope.get(field))
            current_paths = normalised_paths(task.get(field, []))
            if recorded_paths is None or current_paths is None or recorded_paths != current_paths:
                errors.append(_error("REGISTRY_WORKSPACE_SCOPE_MISMATCH", f"{task_id} workspace evidence does not match current {field}"))
                break

    write_paths = task.get("write_paths", [])
    mode = verification.get("mode")
    status = verification.get("status")
    workspace_ref = verification.get("workspace_ref")
    evidence_ref = verification.get("evidence_ref")
    verified_at = verification.get("verified_at")
    if not write_paths:
        if mode != "read_only" or status != "not_required" or any(value is not None for value in (workspace_ref, evidence_ref, verified_at)):
            errors.append(_error("REGISTRY_READ_ONLY_WORKSPACE_MISMATCH", f"{task_id} has no write paths but does not declare a read-only workspace"))
    else:
        if mode == "read_only" or status == "not_required":
            errors.append(_error("REGISTRY_WRITE_WORKSPACE_MISMATCH", f"{task_id} has write paths but declares no writable workspace"))
        if status == "verified":
            if not workspace_ref or not evidence_ref or not verified_at:
                errors.append(_error("REGISTRY_WORKSPACE_EVIDENCE_MISSING", f"{task_id} verified workspace record lacks a workspace, evidence reference, or timestamp"))
        elif task.get("status") in {"ready", "active", "completed"}:
            errors.append(_error("REGISTRY_WORKSPACE_NOT_VERIFIED", f"{task_id} cannot be ready, active, or completed without verified workspace evidence"))
    return errors

def _root_blockers(
    task_id: str,
    by_id: dict[str, dict[str, Any]],
    dependencies: dict[str, list[str]],
    visiting: set[str] | None = None,
) -> set[str]:
    visiting = set() if visiting is None else set(visiting)
    if task_id in visiting:
        return set()
    visiting.add(task_id)
    blockers: set[str] = set()
    for dependency_id in dependencies.get(task_id, []):
        dependency = by_id.get(dependency_id)
        if dependency is None or _has_completion_evidence(dependency):
            continue
        if dependency.get("status") not in {"failed", "cancelled"}:
            nested = _root_blockers(dependency_id, by_id, dependencies, visiting)
            if nested:
                blockers.update(nested)
                continue
        blockers.add(dependency_id)
    return blockers


def validate_registry_semantics(registry: dict[str, Any]) -> list[str]:
    """Return semantic invariant violations for a structurally valid registry."""
    errors: list[str] = []
    if not isinstance(registry, dict):
        return [_error("REGISTRY_NOT_OBJECT", "registry must be an object")]
    tasks = registry.get("tasks")
    if not isinstance(tasks, list):
        return [_error("REGISTRY_TASKS_NOT_ARRAY", "tasks must be an array")]

    task_ids = [task.get("id") for task in tasks if isinstance(task, dict)]
    if len(task_ids) != len(set(task_ids)):
        duplicates = sorted(
            {task_id for task_id in task_ids if task_ids.count(task_id) > 1}
        )
        return [_error("REGISTRY_DUPLICATE_TASK_ID", f"duplicate task IDs: {duplicates}")]

    by_id = {
        task["id"]: task
        for task in tasks
        if isinstance(task, dict) and isinstance(task.get("id"), str)
    }
    if len(by_id) != len(tasks):
        errors.append(_error("REGISTRY_INVALID_TASK", "every task must be an object with an ID"))
        return errors

    registry_revision = registry.get("registry_revision", 0)
    dependencies: dict[str, list[str]] = {}
    malformed_edges = False
    for task_id, task in by_id.items():
        task_dependencies = task.get("depends_on", [])
        dependencies[task_id] = list(task_dependencies) if isinstance(task_dependencies, list) else []
        seen_dependencies: set[str] = set()
        for dependency_id in dependencies[task_id]:
            if dependency_id == task_id:
                errors.append(_error("REGISTRY_SELF_DEPENDENCY", f"{task_id} depends on itself"))
                malformed_edges = True
            elif dependency_id not in by_id:
                errors.append(
                    _error(
                        "REGISTRY_DEPENDENCY_MISSING",
                        f"{task_id} references missing dependency {dependency_id}",
                    )
                )
                malformed_edges = True
            if dependency_id in seen_dependencies:
                errors.append(
                    _error(
                        "REGISTRY_DEPENDENCY_DUPLICATE",
                        f"{task_id} repeats dependency {dependency_id}",
                    )
                )
                malformed_edges = True
            seen_dependencies.add(dependency_id)

    has_cycle = False
    if not malformed_edges:
        indegree = {task_id: len(dependencies[task_id]) for task_id in by_id}
        children: dict[str, list[str]] = {task_id: [] for task_id in by_id}
        for task_id, task_dependencies in dependencies.items():
            for dependency_id in task_dependencies:
                children[dependency_id].append(task_id)
        ready = [task_id for task_id, degree in indegree.items() if degree == 0]
        heapq.heapify(ready)
        emitted = 0
        while ready:
            current = heapq.heappop(ready)
            emitted += 1
            for child in sorted(children[current]):
                indegree[child] -= 1
                if indegree[child] == 0:
                    heapq.heappush(ready, child)
        if emitted != len(by_id):
            residual = sorted(task_id for task_id, degree in indegree.items() if degree > 0)
            errors.append(
                _error("REGISTRY_DEPENDENCY_CYCLE", f"cycle participants: {residual}")
            )
            has_cycle = True

    attempt_locations: dict[str, tuple[str, int]] = {}
    attempt_duplicates: set[str] = set()
    for task_id, task in by_id.items():
        attempts = task.get("attempts", [])
        if not isinstance(attempts, list):
            continue
        for index, attempt in enumerate(attempts):
            if not isinstance(attempt, dict):
                continue
            attempt_id = attempt.get("attempt_id")
            if not isinstance(attempt_id, str):
                continue
            if attempt_id in attempt_locations:
                attempt_duplicates.add(attempt_id)
            else:
                attempt_locations[attempt_id] = (task_id, index)
    for attempt_id in sorted(attempt_duplicates):
        errors.append(_error("REGISTRY_DUPLICATE_ATTEMPT_ID", f"duplicate attempt ID {attempt_id}"))

    for task_id, task in by_id.items():
        owner = task.get("owner")
        worker_session_id = task.get("worker_session_id")
        if owner == "coordinator":
            if worker_session_id is not None:
                errors.append(
                    _error(
                        "REGISTRY_COORDINATOR_OWNER_HAS_WORKER",
                        f"{task_id} is coordinator-owned but has a worker session ID",
                    )
                )
        elif not worker_session_id or owner != worker_session_id:
            errors.append(
                _error(
                    "REGISTRY_OWNER_MISMATCH",
                    f"{task_id} owner must be coordinator or its recorded worker session ID",
                )
            )

        attempts = task.get("attempts", [])
        if not isinstance(attempts, list):
            attempts = []
        unresolved = [
            attempt
            for attempt in attempts
            if isinstance(attempt, dict)
            and attempt.get("worker_status") in UNRESOLVED_WORKER_STATES
        ]
        if len(unresolved) > 1:
            errors.append(
                _error(
                    "REGISTRY_MULTIPLE_UNRESOLVED_ATTEMPTS",
                    f"{task_id} has {len(unresolved)} unresolved attempts",
                )
            )

        for index, attempt in enumerate(attempts):
            if not isinstance(attempt, dict):
                continue
            attempt_id = attempt.get("attempt_id")
            previous_id = attempt.get("previous_attempt_id")
            if previous_id is None:
                if index > 0:
                    errors.append(
                        _error(
                            "REGISTRY_ATTEMPT_LINEAGE_MISSING",
                            f"{task_id} attempt {attempt_id} omits its previous attempt",
                        )
                    )
            else:
                previous_location = attempt_locations.get(previous_id)
                if previous_location is None:
                    errors.append(
                        _error(
                            "REGISTRY_ATTEMPT_PREVIOUS_MISSING",
                            f"{task_id} attempt {attempt_id} references missing attempt {previous_id}",
                        )
                    )
                elif previous_location[0] != task_id:
                    errors.append(
                        _error(
                            "REGISTRY_ATTEMPT_PREVIOUS_CROSS_TASK",
                            f"{task_id} attempt {attempt_id} references another task's attempt",
                        )
                    )
                elif previous_location[1] >= index:
                    errors.append(
                        _error(
                            "REGISTRY_ATTEMPT_LINEAGE_ORDER",
                            f"{task_id} attempt {attempt_id} does not reference an earlier attempt",
                        )
                    )
            if attempt.get("dispatch_registry_revision", 0) > registry_revision:
                errors.append(
                    _error(
                        "REGISTRY_ATTEMPT_FUTURE_REVISION",
                        f"{task_id} attempt {attempt_id} has a future dispatch revision",
                    )
                )

        if attempts:
            latest = attempts[-1]
            if isinstance(latest, dict):
                latest_worker_status = latest.get("worker_status")
                if latest_worker_status in {"dispatch_pending", "queued", "unknown"}:
                    if owner != "coordinator" or worker_session_id is not None or task.get("worker_status") is not None:
                        errors.append(
                            _error(
                                "REGISTRY_UNCONFIRMED_WORKER_OWNERSHIP",
                                f"{task_id} must remain coordinator-owned until worker activity is confirmed",
                            )
                        )
                    if latest_worker_status in {"dispatch_pending", "queued"} and task.get("status") != "ready":
                        errors.append(
                            _error(
                                "REGISTRY_QUEUED_TASK_STATE",
                                f"{task_id} must remain ready while its dispatch is pending or queued",
                            )
                        )
                    if latest_worker_status == "unknown" and task.get("status") != "blocked":
                        errors.append(
                            _error(
                                "REGISTRY_UNKNOWN_ATTEMPT_NOT_BLOCKED",
                                f"{task_id} must be blocked while its worker outcome is unknown",
                            )
                        )
                else:
                    if latest.get("worker_session_id") != worker_session_id:
                        errors.append(
                            _error(
                                "REGISTRY_LATEST_WORKER_MISMATCH",
                                f"{task_id} worker session does not match its latest active/terminal attempt",
                            )
                        )
                    if (
                        "worker_status" in latest
                        and latest.get("worker_status") != task.get("worker_status")
                    ):
                        errors.append(
                            _error(
                                "REGISTRY_LATEST_WORKER_STATUS_MISMATCH",
                                f"{task_id} worker status does not match its latest attempt",
                            )
                        )
                if task.get("result_ref") is not None and latest.get("result_ref") != task.get("result_ref"):
                    errors.append(
                        _error(
                            "REGISTRY_LATEST_RESULT_MISMATCH",
                            f"{task_id} result reference does not match its latest attempt",
                        )
                    )

        criteria_ids = [item.get("id") for item in task.get("acceptance_criteria", []) if isinstance(item, dict)]
        errors.extend(_validate_coordinator_verification(task_id, task, criteria_ids, registry_revision))
        errors.extend(_validate_workspace_verification(task_id, task, registry_revision))
        if len(criteria_ids) != len(set(criteria_ids)):
            errors.append(_error("REGISTRY_DUPLICATE_CRITERION_ID", f"{task_id} repeats a criterion ID"))
        slot_ids = [item.get("slot_id") for item in task.get("expected_artifacts", []) if isinstance(item, dict)]
        if len(slot_ids) != len(set(slot_ids)):
            errors.append(_error("REGISTRY_DUPLICATE_ARTIFACT_SLOT", f"{task_id} repeats an artifact slot"))
        known_criteria = set(criteria_ids)
        for slot in task.get("expected_artifacts", []):
            if isinstance(slot, dict):
                unknown = set(slot.get("satisfies", [])) - known_criteria
                if unknown:
                    errors.append(
                        _error(
                            "REGISTRY_SLOT_UNKNOWN_CRITERION",
                            f"{task_id} artifact slot references unknown criteria {sorted(unknown)}",
                        )
                    )

        history = task.get("state_history", [])
        if not isinstance(history, list) or not history:
            errors.append(_error("REGISTRY_STATE_HISTORY_EMPTY", f"{task_id} has no state history"))
            continue
        previous_state: str | None = None
        previous_revision = 0
        for index, transition in enumerate(history):
            if not isinstance(transition, dict):
                continue
            source = transition.get("from")
            target = transition.get("to")
            revision = transition.get("registry_revision", 0)
            if index == 0 and source is not None:
                errors.append(_error("REGISTRY_STATE_HISTORY_INITIAL", f"{task_id} first transition must start at null"))
            elif index > 0 and source != previous_state:
                errors.append(
                    _error(
                        "REGISTRY_STATE_HISTORY_CHAIN",
                        f"{task_id} transition {index + 1} starts at {source!r}, expected {previous_state!r}",
                    )
                )
            if target not in ALLOWED_TRANSITIONS.get(source, set()):
                errors.append(
                    _error(
                        "REGISTRY_INVALID_TRANSITION",
                        f"{task_id} transition {source!r} -> {target!r} is not allowed",
                    )
                )
            if revision <= previous_revision or revision > registry_revision:
                errors.append(
                    _error(
                        "REGISTRY_STATE_REVISION_ORDER",
                        f"{task_id} transition revisions must increase and not exceed registry_revision",
                    )
                )
            if target == "completed" and not transition.get("evidence_refs"):
                errors.append(
                    _error(
                        "REGISTRY_COMPLETION_EVIDENCE_MISSING",
                        f"{task_id} completed transition has no coordinator evidence reference",
                    )
                )
            if source == "planned" and target == "ready":
                if any(
                    not _has_completion_evidence(by_id[dependency_id])
                    for dependency_id in dependencies.get(task_id, [])
                    if dependency_id in by_id
                ):
                    errors.append(
                        _error(
                            "REGISTRY_READY_WITH_INCOMPLETE_DEPENDENCY",
                            f"{task_id} became ready before all dependencies had verified completion evidence",
                        )
                    )
            if source == "failed" and target == "planned":
                if task.get("recovery_decision") not in RETRY_DECISIONS or len(attempts) < 2:
                    errors.append(
                        _error(
                            "REGISTRY_FAILED_RETRY_UNRECORDED",
                            f"{task_id} failed-to-planned transition needs a retry/reassign/resume decision and a new attempt",
                        )
                    )
            if source == "cancelled" and target == "planned":
                if task.get("recovery_decision") not in CANCEL_RESUME_DECISIONS or len(attempts) < 2:
                    errors.append(
                        _error(
                            "REGISTRY_CANCELLED_RESUME_UNRECORDED",
                            f"{task_id} cancelled-to-planned transition needs a resume/reassign decision and a new attempt",
                        )
                    )
            if source == "failed" and target == "completed":
                if task.get("recovery_decision") != "accept_verified_deliverable":
                    errors.append(
                        _error(
                            "REGISTRY_FAILED_ACCEPTANCE_UNRECORDED",
                            f"{task_id} failed-to-completed transition needs accept_verified_deliverable",
                        )
                    )
            if source == "active" and target == "cancelled" and owner != "coordinator":
                latest = attempts[-1] if attempts else {}
                if not isinstance(latest, dict) or latest.get("terminal_state") != "cancelled":
                    errors.append(
                        _error(
                            "REGISTRY_CANCELLATION_UNOBSERVED",
                            f"{task_id} worker cancellation lacks an observed cancelled terminal state",
                        )
                    )
            if source == "active" and target == "completed" and attempts:
                latest = attempts[-1]
                if (
                    not isinstance(latest, dict)
                    or latest.get("result_completeness") != "complete"
                    or not latest.get("acceptance_evidence_refs")
                ):
                    errors.append(
                        _error(
                            "REGISTRY_ACTIVE_COMPLETION_UNVERIFIED",
                            f"{task_id} completed without a complete result and acceptance evidence",
                        )
                    )
            previous_state = target
            previous_revision = revision

        if history[-1].get("to") != task.get("status"):
            errors.append(
                _error(
                    "REGISTRY_STATUS_HISTORY_MISMATCH",
                    f"{task_id} status does not match its last state transition",
                )
            )
        if task.get("status") in {"ready", "active"}:
            if any(
                not _has_completion_evidence(by_id[dependency_id])
                for dependency_id in dependencies.get(task_id, [])
                if dependency_id in by_id
            ):
                errors.append(
                    _error(
                        "REGISTRY_NOT_READY",
                        f"{task_id} is {task.get('status')} while a dependency is incomplete or unverified",
                    )
                )
        if task.get("status") == "completed" and not _has_completion_evidence(task):
            errors.append(
                _error(
                    "REGISTRY_COMPLETED_WITHOUT_EVIDENCE",
                    f"{task_id} lacks complete result and coordinator acceptance evidence",
                )
            )

    if not malformed_edges and not has_cycle:
        for task_id, task in by_id.items():
            expected_blockers = _root_blockers(task_id, by_id, dependencies)
            actual_blockers = set(task.get("blocked_by", []))
            if actual_blockers != expected_blockers:
                errors.append(
                    _error(
                        "REGISTRY_BLOCKED_BY_MISMATCH",
                        f"{task_id} blocked_by is {sorted(actual_blockers)}, expected {sorted(expected_blockers)}",
                    )
                )

        concurrent = [
            (task_id, task)
            for task_id, task in by_id.items()
            if task.get("status") in {"ready", "active"}
        ]
        for index, (left_id, left_task) in enumerate(concurrent):
            left_paths = [
                _normalise_repo_path(path)
                for path in left_task.get("write_paths", [])
            ]
            left_workspace = left_task.get("workspace_verification", {})
            for right_id, right_task in concurrent[index + 1 :]:
                if _depends_on(left_id, right_id, dependencies) or _depends_on(right_id, left_id, dependencies):
                    continue
                right_paths = [
                    _normalise_repo_path(path)
                    for path in right_task.get("write_paths", [])
                ]
                right_workspace = right_task.get("workspace_verification", {})
                left_isolated = (
                    isinstance(left_workspace, dict)
                    and left_workspace.get("mode") == "isolated"
                    and left_workspace.get("status") == "verified"
                    and bool(left_workspace.get("workspace_ref"))
                )
                right_isolated = (
                    isinstance(right_workspace, dict)
                    and right_workspace.get("mode") == "isolated"
                    and right_workspace.get("status") == "verified"
                    and bool(right_workspace.get("workspace_ref"))
                )
                same_workspace = (
                    bool(left_workspace.get("workspace_ref"))
                    and left_workspace.get("workspace_ref") == right_workspace.get("workspace_ref")
                )
                if same_workspace and (left_isolated or right_isolated):
                    errors.append(_error("REGISTRY_WORKSPACE_REUSED", f"ready/active tasks {left_id} and {right_id} reuse an isolated workspace reference"))
                overlaps = any(
                    left_path and right_path and _paths_overlap(left_path, right_path)
                    for left_path in left_paths
                    for right_path in right_paths
                )
                isolated_pair = left_isolated and right_isolated and left_workspace.get("workspace_ref") != right_workspace.get("workspace_ref")
                if overlaps and not isolated_pair:
                    errors.append(_error("REGISTRY_WRITE_PATH_OVERLAP", f"ready/active tasks {left_id} and {right_id} have overlapping write paths without distinct verified isolated workspaces"))

    return errors


def _locator_within_slot(locator: str, slot: dict[str, Any], immutable_ref: Any) -> bool:
    if locator.startswith("/") or "\\" in locator or any(part in {".", ".."} for part in locator.split("/")):
        return False
    if URI_SCHEME.match(locator):
        return bool(slot.get("approved_store") and immutable_ref)
    path = _normalise_repo_path(locator)
    if path is None:
        return False
    allowed_paths = [
        _normalise_repo_path(value)
        for value in slot.get("allowed_paths", [])
    ]
    if any(
        root and (path == root or path.startswith(root + "/"))
        for root in allowed_paths
    ):
        return True
    return bool(slot.get("approved_store") and immutable_ref)


def validate_result_semantics(
    registry: dict[str, Any],
    result: dict[str, Any],
) -> list[str]:
    """Correlate one result with the latest recorded task attempt and its contract."""
    errors: list[str] = []
    if not isinstance(registry, dict) or not isinstance(result, dict):
        return [_error("RESULT_INPUT_NOT_OBJECT", "registry and result must be objects")]
    tasks = registry.get("tasks", [])
    by_id = {
        task.get("id"): task
        for task in tasks
        if isinstance(task, dict) and isinstance(task.get("id"), str)
    }
    task_id = result.get("task_id")
    task = by_id.get(task_id)
    if task is None:
        return [_error("RESULT_TASK_UNKNOWN", f"result references unknown task {task_id!r}")]

    if result.get("session_id") != registry.get("session_id"):
        errors.append(_error("RESULT_SESSION_MISMATCH", "result session_id does not match the registry"))
    if result.get("task_spec_revision") != task.get("task_spec_revision"):
        errors.append(_error("RESULT_TASK_REVISION_MISMATCH", "result task_spec_revision is stale or mismatched"))

    attempts = task.get("attempts", [])
    attempt_id = result.get("attempt_id")
    attempt_index = next(
        (
            index
            for index, attempt in enumerate(attempts)
            if isinstance(attempt, dict) and attempt.get("attempt_id") == attempt_id
        ),
        None,
    )
    if attempt_index is None:
        return errors + [_error("RESULT_ATTEMPT_UNKNOWN", f"result references unknown attempt {attempt_id!r}")]
    attempt = attempts[attempt_index]
    if attempt_index != len(attempts) - 1:
        errors.append(_error("RESULT_STALE_ATTEMPT", "result belongs to a superseded attempt"))
    if result.get("dispatch_registry_revision") != attempt.get("dispatch_registry_revision"):
        errors.append(_error("RESULT_DISPATCH_REVISION_MISMATCH", "result dispatch revision does not match its admission record"))
    if result.get("worker_session_id") != attempt.get("worker_session_id"):
        errors.append(_error("RESULT_WORKER_SESSION_MISMATCH", "result worker session does not match its attempt"))
    if attempt_index == len(attempts) - 1 and result.get("worker_session_id") != task.get("worker_session_id"):
        errors.append(_error("RESULT_TASK_OWNER_SESSION_MISMATCH", "result worker session does not match the current task owner"))
    if result.get("terminal_state") != attempt.get("terminal_state"):
        errors.append(_error("RESULT_TERMINAL_STATE_MISMATCH", "result terminal state does not match the observed attempt"))
    if result.get("result_completeness") != attempt.get("result_completeness"):
        errors.append(_error("RESULT_COMPLETENESS_MISMATCH", "result completeness does not match the attempt record"))
    if result.get("worker_session_id") is None:
        if task.get("owner") != "coordinator" or result.get("terminal_state") is not None:
            errors.append(_error("RESULT_COORDINATOR_IDENTITY_MISMATCH", "null worker identity is valid only for coordinator-owned work"))
    elif task.get("owner") != result.get("worker_session_id") or result.get("terminal_state") is None:
        errors.append(_error("RESULT_WORKER_IDENTITY_MISMATCH", "worker result lacks the task's host-issued owner or terminal state"))

    slots = {
        slot.get("slot_id"): slot
        for slot in task.get("expected_artifacts", [])
        if isinstance(slot, dict) and isinstance(slot.get("slot_id"), str)
    }
    criteria = {
        criterion.get("id")
        for criterion in task.get("acceptance_criteria", [])
        if isinstance(criterion, dict)
    }
    artifacts = result.get("artifacts", [])
    artifact_by_id: dict[str, dict[str, Any]] = {}
    claimed_slots: set[str] = set()
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            continue
        artifact_id = artifact.get("artifact_id")
        slot_id = artifact.get("slot_id")
        if artifact_id in artifact_by_id:
            errors.append(_error("RESULT_DUPLICATE_ARTIFACT_ID", f"duplicate artifact ID {artifact_id}"))
        elif isinstance(artifact_id, str):
            artifact_by_id[artifact_id] = artifact
        slot = slots.get(slot_id)
        if slot is None:
            errors.append(_error("RESULT_ARTIFACT_SLOT_UNKNOWN", f"artifact {artifact_id} claims undeclared slot {slot_id!r}"))
            continue
        if slot_id in claimed_slots:
            errors.append(_error("RESULT_DUPLICATE_SLOT_CLAIM", f"multiple artifacts claim slot {slot_id}"))
        claimed_slots.add(slot_id)
        if artifact.get("producer_task_id") != task_id or artifact.get("producer_attempt_id") != attempt_id:
            errors.append(_error("RESULT_ARTIFACT_PRODUCER_MISMATCH", f"artifact {artifact_id} has incorrect producer identity"))
        artifact_criteria = set(artifact.get("acceptance_criteria_ids", []))
        if not artifact_criteria <= criteria or not artifact_criteria <= set(slot.get("satisfies", [])):
            errors.append(_error("RESULT_ARTIFACT_CRITERIA_MISMATCH", f"artifact {artifact_id} claims criteria outside its task or slot"))
        if not _locator_within_slot(artifact.get("locator", ""), slot, artifact.get("immutable_ref")):
            errors.append(_error("RESULT_ARTIFACT_PATH_OUT_OF_SCOPE", f"artifact {artifact_id} locator is outside its allowed path or approved store"))
        digest = artifact.get("content_digest", {})
        if digest.get("value") is not None and artifact.get("byte_length") is None:
            errors.append(_error("RESULT_ARTIFACT_LENGTH_MISSING", f"artifact {artifact_id} has a digest but no byte length"))
        if result.get("result_completeness") == "complete":
            if not artifact.get("immutable_ref") and not (
                digest.get("value") and artifact.get("byte_length") is not None
            ):
                errors.append(_error("RESULT_ARTIFACT_INTEGRITY_MISSING", f"complete result artifact {artifact_id} has no immutable reference or digest/length pair"))

    evidence_by_criterion: dict[str, dict[str, Any]] = {}
    for evidence in result.get("acceptance_evidence", []):
        if not isinstance(evidence, dict):
            continue
        criterion_id = evidence.get("criterion_id")
        if criterion_id not in criteria:
            errors.append(_error("RESULT_CRITERION_UNKNOWN", f"evidence references unknown criterion {criterion_id!r}"))
            continue
        if criterion_id in evidence_by_criterion:
            errors.append(_error("RESULT_CRITERION_DUPLICATE", f"criterion {criterion_id} has duplicate evidence records"))
        evidence_by_criterion[criterion_id] = evidence
        for artifact_id in evidence.get("artifact_ids", []):
            artifact = artifact_by_id.get(artifact_id)
            if artifact is None:
                errors.append(_error("RESULT_EVIDENCE_ARTIFACT_UNKNOWN", f"criterion {criterion_id} references unknown artifact {artifact_id}"))
            elif criterion_id not in artifact.get("acceptance_criteria_ids", []):
                errors.append(_error("RESULT_EVIDENCE_ARTIFACT_CRITERION_MISMATCH", f"artifact {artifact_id} does not claim criterion {criterion_id}"))

    if result.get("result_completeness") == "complete":
        missing_slots = sorted(
            slot_id
            for slot_id, slot in slots.items()
            if slot.get("required") and slot_id not in claimed_slots
        )
        if missing_slots:
            errors.append(_error("RESULT_REQUIRED_ARTIFACT_MISSING", f"complete result omits required slots {missing_slots}"))
        missing_criteria = sorted(criteria - set(evidence_by_criterion))
        if missing_criteria:
            errors.append(_error("RESULT_CRITERION_EVIDENCE_MISSING", f"complete result omits evidence for criteria {missing_criteria}"))

    return errors


def _materialise_case(case: dict[str, Any], bases: dict[str, Any]) -> tuple[dict[str, Any], Any]:
    base = bases.get(case.get("base"))
    if not isinstance(base, dict) or not isinstance(base.get("registry"), dict):
        raise ValueError(f"unknown or malformed base {case.get('base')!r}")
    registry = copy.deepcopy(base["registry"])
    result = None if case.get("kind") == "registry" else copy.deepcopy(base.get("result"))
    for change in case.get("overrides", []):
        if not isinstance(change, dict) or change.get("target") not in {"registry", "result"}:
            raise ValueError("each override must target registry or result")
        document = registry if change["target"] == "registry" else result
        path = change.get("path")
        if not isinstance(document, dict) or not isinstance(path, list) or not path:
            raise ValueError("override needs an existing document and non-empty path")
        parent = document
        for part in path[:-1]:
            parent = parent[part]
        parent[path[-1]] = copy.deepcopy(change.get("value"))
    return registry, result


def validate_semantic_fixtures(root: Path) -> tuple[list[str], int, int]:
    """Validate compact positive and negative semantic fixtures against both schemas."""
    fixture_path = root / "tests" / "fixtures" / "contracts" / "semantic.json"
    errors: list[str] = []
    try:
        import jsonschema
        bundle = json.loads(fixture_path.read_text(encoding="utf-8"))
        task_schema = json.loads((root / "docs" / "schemas" / "task-registry.schema.json").read_text(encoding="utf-8"))
        result_schema = json.loads((root / "docs" / "schemas" / "result-envelope.schema.json").read_text(encoding="utf-8"))
    except (ImportError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"semantic contract fixtures: cannot load inputs ({exc})"], 0, 0

    if not isinstance(bundle, dict) or set(bundle) != {"bases", "valid", "invalid"}:
        return ["semantic contract fixtures: expected bases, valid, and invalid"], 0, 0
    bases = bundle["bases"]
    valid_cases = bundle["valid"]
    invalid_cases = bundle["invalid"]
    if not isinstance(bases, dict) or not isinstance(valid_cases, list) or not isinstance(invalid_cases, list):
        return ["semantic contract fixtures: bases must be an object and cases must be arrays"], 0, 0
    if not valid_cases or not invalid_cases:
        return ["semantic contract fixtures: valid and invalid must both be non-empty arrays"], 0, 0

    task_validator = jsonschema.Draft202012Validator(task_schema, format_checker=jsonschema.FormatChecker())
    result_validator = jsonschema.Draft202012Validator(result_schema, format_checker=jsonschema.FormatChecker())
    names: set[str] = set()

    for expectation, cases in (("valid", valid_cases), ("invalid", invalid_cases)):
        for index, case in enumerate(cases, start=1):
            label = f"semantic.json#{expectation}[{index}]"
            if not isinstance(case, dict) or not isinstance(case.get("name"), str) or not case["name"].strip():
                errors.append(f"{label}: case must have a non-empty name")
                continue
            name = case["name"]
            if name in names:
                errors.append(f"{label}: duplicate case name {name!r}")
                continue
            names.add(name)
            kind = case.get("kind")
            if kind not in {"registry", "result"}:
                errors.append(f"{label}/{name}: kind must be registry or result")
                continue
            try:
                registry, result = _materialise_case(case, bases)
            except (KeyError, TypeError, ValueError) as exc:
                errors.append(f"{label}/{name}: cannot materialise fixture ({exc})")
                continue
            structural_errors = list(task_validator.iter_errors(registry))
            if structural_errors:
                errors.append(f"{label}/{name}: registry is not structurally valid: {structural_errors[0].message}")
                continue
            semantic_errors = validate_registry_semantics(registry)
            if kind == "result":
                if not isinstance(result, dict):
                    errors.append(f"{label}/{name}: result case requires a result object")
                    continue
                structural_result_errors = list(result_validator.iter_errors(result))
                if structural_result_errors:
                    errors.append(f"{label}/{name}: result is not structurally valid: {structural_result_errors[0].message}")
                    continue
                if not semantic_errors:
                    semantic_errors.extend(validate_result_semantics(registry, result))
            elif result is not None:
                errors.append(f"{label}/{name}: registry-only base must not contain a result")

            codes = {item.split(":", 1)[0] for item in semantic_errors}
            if expectation == "valid" and semantic_errors:
                errors.append(f"{label}/{name}: expected valid; {'; '.join(semantic_errors)}")
            elif expectation == "invalid":
                expected_codes = case.get("expected_errors")
                if not isinstance(expected_codes, list) or not expected_codes:
                    errors.append(f"{label}/{name}: invalid case requires expected_errors")
                elif not set(expected_codes) <= codes:
                    errors.append(
                        f"{label}/{name}: expected error codes {sorted(set(expected_codes))}, got {sorted(codes)}"
                    )
            elif expectation == "valid" and "expected_errors" in case:
                errors.append(f"{label}/{name}: valid case must not declare expected_errors")

    return errors, len(valid_cases), len(invalid_cases)
