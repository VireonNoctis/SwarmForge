# Orchestration Patterns

Choose a topology based on task dependencies and communication needs. No single pattern is optimal for every job. These patterns are instructions for the host's real agents, not a requirement to deploy an external scheduler.

## Fan-out / fan-in

One coordinator dispatches independent tasks and combines their results.

~~~text
Coordinator
  ├── Research A
  ├── Research B
  ├── Implement A
  ├── Test B
  └── Review
        ↓
  Integration and synthesis
~~~

Best for repository reconnaissance, independent modules, parallel code review, test generation, documentation research, and separate bug hypotheses. Simple and easy to cap, but the coordinator can become a bottleneck and scopes must prevent duplicate work.

## Hierarchical swarm

A root coordinator assigns domains to supervisors, who coordinate specialists.

~~~text
Coordinator
  ├── Frontend lead -> UI workers + test worker
  ├── Backend lead  -> API workers + test worker
  └── Quality lead  -> security + integration review
~~~

Best for large projects with clear domains. All descendants must debit one global concurrency budget; supervisor trees must not multiply a 500-session limit. Use only if the host supports nested delegation.

## DAG / pipeline

Tasks run only when dependencies are complete: repository analysis → interface design → implementation → integration → tests → independent review. Best for tightly dependent changes where speculative parallel work would create rework.

## Task graph and task registry

For every substantial task, keep one compact project brief and a session-local task registry. Use the host's native task list or session notes when available; otherwise keep the registry in the coordinator's working context. **Do not add a database, service, or persistent scheduler just to track tasks.**

Generate a unique session ID for each invocation, then number tasks within it (for example, `sf-20261031-x7k2-01`). A date alone is not a unique session ID. Each task must have exactly one accountable owner: the coordinator or a real, host-issued worker-session ID. A role name, planned worker, or queued job is not an owner.

Use this compact record:

~~~yaml
session_id: "sf-20261031-x7k2"
registry_revision: 1
objective: "Deliver the user's requested outcome"
requested_worker_cap: "<user-provided maximum>"
tasks:
  - id: "sf-20261031-x7k2-01"
    owner: "coordinator"
    objective: "Inspect the existing task lifecycle and identify the smallest safe change"
    context_refs:
      - "SKILL.md"
      - "docs/ORCHESTRATION_PATTERNS.md"
    read_paths:
      - "docs/ORCHESTRATION_PATTERNS.md"
      - "tests/test_skill_package.py"
    write_paths: []
    depends_on: []
    status: "ready"
    state_history:
      - from: null
        to: "ready"
        actor: "coordinator"
        recorded_at: "<timestamp>"
        registry_revision: 1
        reason: "No dependencies; the task is ready to start"
        evidence_refs: []
    acceptance_criteria:
      - "Findings cite exact paths and identify a bounded implementation"
    verification_commands:
      - "python3 -m unittest discover -s tests -v"
    deliverable: "Evidence-backed implementation brief"
    worker_session_id: null
    worker_status: null
    result_ref: null
    attempts: []
    blocked_by: []
    recovery_decision: null
~~~

The cap is optional when the user has not supplied one; never infer host capacity from a requested cap. Keep references narrow and use repository-relative paths. Add fields only when they improve coordination.

### Graph and ownership rules

- Task IDs are unique within the session. Every dependency must reference an existing task; reject cycles before dispatch.
- A task is `planned` while prerequisites remain, `ready` when all dependencies are complete, `active` only after its owner actually begins, `blocked` when it cannot safely proceed, and `completed`, `failed`, or `cancelled` only with an explicit outcome.
- A failed or cancelled dependency blocks its dependants until the coordinator deliberately revises the graph and records the reason. Do not silently treat failure as completion.
- Keep task status separate from worker-session status. A queued dispatch is not an active task or a confirmed active agent; populate `worker_session_id` and `worker_status` only from host-confirmed session data.
- Default to read-only tasks. Concurrent write paths must not overlap. Serialize shared-file work or reserve those paths for the coordinator; never rely on a role label as a file lock.
- Mark a task complete only after its deliverable exists, its acceptance criteria are checked, and the coordinator has inspected the evidence. Record failed checks and unresolved risks in the result.

### Pre-dispatch graph validation and admission

Treat validation as a fail-closed gate, not a best-effort review. Validate the complete session registry after planning, immediately before every dispatch, and after any change to tasks, dependencies, owners, attempts, states, or acceptance evidence. Maintain a monotonic `registry_revision` in host task state or coordinator notes; increment it for every such mutation. Bind each validation and admission decision to the exact revision checked. A later mutation invalidates the earlier decision. If a consistent snapshot or revision cannot be established, admission is unknown and no worker is dispatched.

**Validation sequence**

1. **Session, task, and owner identity**
   - Require one non-empty session ID. Every task ID must be non-empty and unique within that session; reject duplicate task IDs before resolving any edges.
   - Every task has exactly one owner: `coordinator` or a host-issued worker-session ID actually returned and recorded in this session. The coordinator retains ownership until a worker's active state is confirmed. Role names, planned workers, queued requests, and guessed IDs are not owners.
   - Every `attempt_id` is non-empty and unique across the session; reject duplicate attempt IDs before validating lineage. Each attempt belongs to exactly one existing task. A `previous_attempt_id` must identify an earlier attempt of the same task; reject missing, cross-task, duplicate, self-referential, or cyclic attempt lineage.
2. **Dependency references**
   - Reject missing or cross-session dependency IDs, self-dependencies, and duplicate dependency edges. A task may depend on a given task only once.
   - Recompute `blocked_by` from the current graph and verified dependency outcomes; do not trust a stale saved list as proof that a task is unblocked.
   - Normalize read/write paths as repository-relative paths. Reject absolute paths and paths that escape the repository. Treat exact paths and ancestor/descendant directory paths as overlapping writes. Concurrent overlapping writes require isolated workspaces; otherwise serialize ownership.
3. **Cycle detection and ordering**
   - Run a topological sort over the full graph (for example, Kahn's algorithm), using task ID as a stable tie-breaker when several tasks are ready.
   - If the sort emits fewer tasks than the registry contains, reject the graph and report the residual task IDs as cycle participants. Do not dispatch any task from an invalid graph.
   - Missing references and duplicate edges must be rejected before cycle detection so the cycle report is not used to hide malformed input.
4. **State and transition history**
   - Accept only `planned`, `ready`, `active`, `blocked`, `completed`, `failed`, and `cancelled` as task states.
   - Keep an append-only `state_history` (or equivalent host-native audit events). Each transition records `from`, `to`, actor, timestamp, registry revision, reason, and evidence references. Derive the current status from the last valid event; never silently overwrite a status field.
   - Validate every transition against this table. Any transition not listed is invalid.

| From | Allowed next state | Required condition |
|---|---|---|
| `planned` | `ready`, `blocked`, `cancelled` | `ready` only when every dependency is completed with verified acceptance evidence; `blocked` records its reason and root blockers |
| `ready` | `active`, `blocked`, `cancelled` | `active` only after the coordinator starts the work or the host confirms the assigned worker is active |
| `active` | `blocked`, `completed`, `failed`, `cancelled` | `completed` only after all acceptance criteria are verified; `cancelled` for worker-owned work only after cancellation is observed |
| `blocked` | `planned`, `cancelled` | Return to `planned` only after blockers are repaired, the registry revision changes, and the full graph is revalidated |
| `failed` | `planned`, `completed` | `planned` requires an explicit retry/reassign/resume decision and a new attempt; `completed` requires `accept_verified_deliverable` and coordinator verification |
| `cancelled` | `planned` | Requires an explicit resume/reassign decision and reconciliation of the prior worker/attempt |
| `completed` | none | Terminal; create a new corrective task rather than rewriting completed history |

   - In particular, reject `planned → active`, `ready → completed`, `blocked → active`, and direct `failed/cancelled → active` transitions. A retry must pass through `planned` and create a new attempt.
   - A task is `ready` only when all dependencies are completed and their acceptance evidence is verified, with no unresolved dependency blocker. A dependency that is merely queued, active, partial, unavailable, failed, cancelled, or unverified does not satisfy the prerequisite.
5. **Attempts and write admission**
   - Permit at most one unresolved attempt per task. `dispatch_pending`, `queued`, `active`, and `unknown` are unresolved; `unknown` is never treated as terminal.
   - Before another attempt, reconcile the prior worker with the host and preserve its terminal state and artifacts. Never start a retry while the previous attempt may still be running.
   - Verify read/write ownership and workspace isolation again at admission time; a valid graph does not make overlapping concurrent writes safe.

**Dispatch-admission gate**

Before each `worker.create`, the coordinator records an admission decision containing `task_id`, `registry_revision`, `decision` (`admitted` or `denied`), reasons, timestamp, and redacted evidence references. Admit a worker dispatch only when every condition below is true:

1. The complete graph passed validation at the current `registry_revision`.
2. The target task is `ready`; every dependency is `completed` with coordinator-verified acceptance evidence; recomputed `blocked_by` is empty.
3. The task has exactly one valid owner, non-overlapping write ownership or confirmed workspace isolation, and no unresolved prior attempt.
4. A new unique `attempt_id` is reserved and recorded as `dispatch_pending`; admission is then checked against the revision that includes this attempt.
5. The current-session capability snapshot proves the required create/observe/result-collection lifecycle, stable session-ID contract, permission scope, and sufficient confirmed capacity. Apply nested-session and workspace safety gates from the Skill. Unknown required facts deny admission.

If any condition fails or is unknown, do not call `worker.create`. Record the denial and keep the task non-active; a capacity/permission denial does not turn a valid dependency graph into task failure. Coordinator-owned single-agent work may start directly when `ready`, but it follows the same dependency, state-transition, and acceptance rules.

After a create request, record only the host-returned session ID. If the host reports the request as queued, keep the attempt `queued`, the task `ready`, and ownership with the coordinator; do not count a worker or create a duplicate attempt. Transfer ownership to the host-issued session ID and set the task `active` only after `worker.observe` confirms active state. If the request is accepted without a stable ID, or its outcome cannot be observed, mark the attempt `unknown`, block further dispatch for that task, and reconcile with the host before retrying. Never infer success from a submitted request.

These are host-neutral coordinator procedures; SwarmForge does not ship an executable graph parser, scheduler, or dispatch service. If the host cannot expose or preserve the required state, perform the checks manually where possible; if correctness or worker state remains unknown, stay in the single-agent fallback rather than claiming validation or dispatch succeeded.

### Dependency failure, partial results, and recovery

Treat graph readiness as an evidence-derived condition, not a dispatch preference.

**Dependency propagation**

- A task is ready only when every direct dependency is completed and its acceptance evidence has been verified by the coordinator.
- If a dependency is blocked, failed, cancelled, or has only a partial/unavailable result, block every not-yet-started transitive dependant. Record the root blocking task IDs in blocked_by; do not label descendants failed or cancelled merely because an upstream task failed.
- If an upstream dependency becomes invalid while a dependant is active, set the dependant task to blocked with a clear reason while keeping its worker-session state separate. Do not automatically cancel active dependants. If stopping is necessary and cancellation is available, request it and wait for observed confirmation; otherwise let bounded work finish but keep its output provisional and out of integration until dependencies are revalidated.
- Preserve completed task history. If an upstream result is later invalidated, re-check completed dependants against the corrected evidence and create an explicit corrective task for any regression; do not silently erase or rewrite prior outcomes.
- Unblock work only after the dependency is repaired, its acceptance criteria are re-verified, and the coordinator records the graph revision and reason. Recompute readiness from the full dependency graph rather than clearing one blocked flag manually.

**Partial results and attempts**

- Keep task state, worker-session state, and result completeness as separate fields. result_completeness is complete, partial, or unavailable; it describes the returned artifact, not the task's lifecycle state.
- Preserve partial artifacts, checks already run, missing acceptance criteria, and redacted evidence references. Partial or unavailable results never satisfy a dependency. A complete result also does not complete the task until the coordinator verifies every acceptance criterion.
- A worker's failed terminal state does not by itself determine the task outcome. The coordinator may accept a deliverable only when the artifact exists and all acceptance criteria are independently verified; otherwise keep the task blocked pending recovery or mark it failed with evidence.
- Keep a stable task ID across retries and append a unique attempt_id for every attempt, with its worker session, terminal state, result completeness, artifact/evidence references, and any previous_attempt_id. Never overwrite a failed attempt with a later success.
- Choose an explicit recovery decision: retry, reassign, split, resume, accept_verified_deliverable, or fail. Record the rationale and coordinator decision. Retry only transient, idempotent work, and reconcile the previous worker before starting another attempt to avoid duplicate side effects.

**Coordinator checkpoint and restart recovery**

Use the host's native task state or session notes for a compact checkpoint; do not add a database or persistent scheduler. A checkpoint should include:

~~~yaml
checkpoint_schema_version: 1
session_id: "sf-20261031-x7k2"
checkpointed_at: "<timestamp>"
tasks:
  - id: "sf-20261031-x7k2-02"
    status: "blocked"
    depends_on: ["sf-20261031-x7k2-01"]
    blocked_by: ["sf-20261031-x7k2-01"]
    attempt_ids: ["sf-20261031-x7k2-02-a01"]
    recovery_decision: "pending"
~~~

Record an attempt separately, including attempt_id, previous_attempt_id, host-issued worker_session_id when present, worker status/terminal state, result_completeness, artifact references, and evidence references. Checkpoint after material transitions: dispatch acceptance, confirmed worker identity/status, result receipt, task-state changes, and recovery decisions. An accepted dispatch remains queued until the host confirms an active session.

On coordinator restart:

1. Load the latest checkpoint and authoritative host task/session state; validate the session ID, task IDs, owners, dependency references, and acyclic graph.
2. Reconcile every nonterminal worker with the host. Mark it active only if the host confirms it. If status cannot be observed, record unknown, block affected work, and do not redispatch an unobservable worker.
3. Re-open referenced artifacts and verify completed-task acceptance evidence; re-derive readiness and all transitive blocked dependants.
4. Require an explicit coordinator recovery decision before retrying, reassigning, splitting, or resuming. Preserve prior attempt IDs and failure evidence.
5. If no durable checkpoint exists, reconstruct only from trusted host state, session notes, and verifiable repository artifacts. Keep uncertain work blocked and disclose the recovery limit; never claim full restart recovery.

Checkpoints contain identifiers, statuses, paths, and redacted references only—never credentials, secrets, prompts, or full private logs. If the host cannot preserve task state across restarts, recovery is limited to the context that remains available.

## Map / reduce

Map a common operation across independent files, records, or modules; reduce normalized results into a deduplicated, evidence-preserving summary. Best for migrations, audits, large test collections, and bulk analysis. Validate the transformation on a small sample first.

## Specialist ensemble

Independent reviewers inspect the same immutable snapshot for correctness, security, performance, accessibility, maintainability, or test coverage. Use for high-risk work. Reviewers should return findings, not overlapping patches.

## Competing hypotheses

Agents independently investigate possible causes or designs. The coordinator compares evidence and runs discriminating tests. Majority vote is not a correctness test; require source evidence and falsifiable claims.

## Peer team / mesh

Agents message one another and work from shared task state. Use only when the host actually supports teammate communication and coordination. This can improve discussion but increases context cost and makes ownership harder to supervise.

## Hybrid execution

Native host agents may be combined with an already configured MCP bridge, provider SDK, CLI worker pool, or remote queue. These are optional external integrations, not core SwarmForge requirements. Keep one authoritative task registry and one global capacity budget.

## Pattern selection

| Work shape | Suggested pattern |
|---|---|
| Independent reviews/research | Fan-out / fan-in |
| Large multi-domain project | Hierarchical, if nested agents are supported |
| Strict dependencies | DAG / pipeline |
| Many similar independent items | Map / reduce |
| High-risk implementation | Specialist ensemble |
| Uncertain diagnosis/design | Competing hypotheses |
| Ongoing peer coordination | Team / mesh |
| Multiple hosts/providers | Hybrid, only when configured |

## Anti-patterns

- One worker per file without considering value.
- Multiple uncoordinated writers on the same file.
- Repeating full repository discovery in every worker.
- Voting instead of testing.
- Deep supervisor trees without global concurrency accounting.
- Counting queued jobs as active AI agents.
- Keeping workers alive after their deliverable is complete.
- Deploying infrastructure merely to make the Skill usable.
