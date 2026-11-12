# Optional Adapter Contract

This is a vendor-neutral reference for an external execution adapter. It is not an implementation or a declaration that any adapter is installed. Most SwarmForge users should use native host delegation and never need this document.

Consider an adapter only when native delegation is unavailable or insufficient and the user explicitly wants an external integration.

## Capability discovery

Before dispatch, an adapter should report:
- adapter identity and version;
- supported providers/models;
- worker creation and result collection;
- messaging and shared task-state support;
- workspace model and permissions;
- active-session caps, including root/nested accounting;
- visible provider quotas and current availability;
- timeout, cancellation, retry, and budget controls;
- retention, telemetry, and secret handling.

Unknown values remain unknown. An absent limit is not unlimited.

## Normalized capability snapshot

An adapter or host integration should expose a session-local snapshot in a form the coordinator can inspect. This is a conceptual record, not a required JSON schema or a command the Skill can invoke.

Use three evidence states:

- `supported`: the operation is visible, callable in this session, and permitted for the intended task.
- `unsupported`: the operation is known not to exist or is unavailable under the current permissions.
- `unknown`: it has not been verified, or the evidence is ambiguous.

Every `supported` entry should cite the exact tool/surface, relevant input/output behavior, and any permission or scope constraint. An error caused by missing permission is not proof that the operation is globally unsupported; record the current-session limitation. Treat `unknown` as unavailable when deciding whether to dispatch.

Suggested capability groups:

~~~yaml
capabilities:
  worker:
    create: unknown
    observe: unknown
    collect_result: unknown
    cancel: unknown
    message: unknown
  team:
    create: unknown
    message: unknown
    shared_state: unknown
  workspace:
    isolate: unknown
    release: unknown
  capacity:
    global_limit: unknown
    nested_accounting: unknown
    provider_limits: unknown
    current_usage: unknown
  usage:
    token_cost_rate_limit: unknown
evidence:
  - capability: "worker.create"
    status: "supported"
    surface: "exact host tool name"
    constraints: "confirmed scope, permission, or limit"
~~~

The normalized capability IDs are not tool names. Map them to the concrete operations exposed by the integration; for example:

| Normalized capability | Example logical operation |
|---|---|
| `worker.create` | `create_worker` |
| `worker.observe` | `get_worker` and/or `wait_worker` |
| `worker.collect_result` | `collect_result` |
| `worker.cancel` | `cancel_worker` |
| `worker.message` | `send_message` |
| `workspace.isolate` | `create_workspace` |
| `workspace.release` | `release_workspace` |

These names are illustrative mappings only. Confirm that the actual operation's schema and returned data satisfy the capability before marking it supported.

The snapshot and its evidence are advisory, session-local state. Do not persist secrets, credentials, full prompts, or private source content in them.

### Evidence record and freshness

Use this compact record for each capability assessment. It is a documentation template, not a required API schema:

~~~yaml
session_context:
  host: "..."
  client_surface: "..."
  client_version: null
  observed_at: "<ISO-8601 timestamp>"
  inventory_complete: false
evidence:
  - capability: "worker.create"
    status: "unknown"
    evidence_kind: "tool_inventory"
    operation: "exact exposed tool/control name, or null"
    schema_ref: "tool-schema identifier or source path"
    permission_scope: "current task and workspace permissions"
    task_id: null
    worker_session_id: null
    observed_outcome: "visible in inventory; not invoked solely for testing"
    terminal_state: null
    result_ref: null
    evidence_ref: "redacted source or observation reference"
    constraints: "..."
~~~

Evidence kinds have deliberately different weight:

| Evidence kind | What it establishes | What it does not establish |
|---|---|---|
| `live_observation` | An operation's observed behavior during authorized, ordinary task execution | Behavior outside the observed scope or session |
| `tool_inventory` | An exact operation and schema are exposed in the current session | Successful execution unless the schema and permission contract are sufficient and the outcome is observed |
| `configuration` | A feature, setting, or permission appears configured | That the current host exposes or can successfully use it |
| `official_documentation` | A provider documents a product or API capability | That this session has the product, account entitlement, credentials, permissions, or integration |

For a dispatch-critical capability, a complete current-session tool inventory may establish the declared contract only when the exact callable schema and permission scope satisfy the normalized requirement. In particular, `worker.create` must expose a stable host-issued session identifier; `worker.observe` must expose status or wait information; and `worker.collect_result` must expose a result that can be correlated to the originating task/session. A tool name, product feature, activity panel, or documentation example is not enough. Prefer a live observation from legitimate task work when available, but never create a worker, cancel work, send messages, allocate a workspace, or spend provider budget solely to test a capability.

Record `worker_session_id`, terminal state, and result reference only when the host actually supplies them. For workspace isolation, record the observed workspace boundary or the coordinator-enforced non-overlapping path ownership. For capacity, record the reporting surface, scope, timestamp, whether the root and descendants are included, and whether the value is configured or currently available.

Use `unsupported` only when the relevant current-session inventory is complete and the operation is absent from that surface, or when the current task is explicitly denied permission. A permission denial is a session/task limitation, not proof that the provider lacks the feature globally. Use `unknown` when inventory is incomplete, a schema omits a required contract detail, or evidence consists only of configuration or official documentation.

Keep evidence minimal and redacted: IDs, status, timestamps, schema/source references, permission scope, and concise outcomes are sufficient. Do not copy prompts, private source text, credentials, or full logs into the record. Reassess at each new task session and after host/client version, configuration, permission, or workspace changes. There is no universal evidence TTL; if freshness cannot be established, downgrade the capability to `unknown`.

### Dispatch and degradation rules

A worker lifecycle is dispatch-ready only when creation, status/wait observation, and result collection are all supported and creation returns a stable host-issued session ID. Otherwise, do not start workers and use the single-agent fallback. Do not treat an accepted dispatch request as an active session.

- If cancellation is unavailable, restrict delegation to bounded, read-only tasks that do not require mid-flight cancellation.
- If global or nested capacity accounting is unknown, do not use nested supervisors or scale beyond one worker at a time.
- For concurrent writes, require isolated workspaces or explicit disjoint path ownership with serialized integration.
- Missing usage telemetry does not prove zero usage or unlimited budget. Report it as unavailable.
- Team creation, teammate messaging, and shared task state are separate capabilities; none is implied by subagent creation.

### Compact capability report

At the end of each task session, emit one concise capability summary from the session-local evidence. This is a decision record, not a copy of every tool schema.

Use the following template and omit optional rows that were not relevant to the task. Keep every dispatch-critical row.

~~~yaml
capability_report:
  session_ref: "session-scoped reference"
  host_surface: "exact current host/client surface"
  client_version: null
  observed_at: "<ISO-8601 timestamp>"
  inventory_complete: false
  capabilities:
    worker.create:
      status: unknown
      evidence_ref: null
      constraint: "stable host-issued session ID not established"
    worker.observe:
      status: unknown
      evidence_ref: null
      constraint: "status or wait contract not established"
    worker.collect_result:
      status: unknown
      evidence_ref: null
      constraint: "task-correlated result contract not established"
    worker.cancel:
      status: unknown
      evidence_ref: null
    worker.message:
      status: unknown
      evidence_ref: null
    team.create:
      status: unknown
      evidence_ref: null
    team.message:
      status: unknown
      evidence_ref: null
    team.shared_state:
      status: unknown
      evidence_ref: null
    workspace.isolate:
      status: unknown
      evidence_ref: null
    workspace.release:
      status: unknown
      evidence_ref: null
    capacity.global_limit:
      status: unknown
      evidence_ref: null
    capacity.nested_accounting:
      status: unknown
      evidence_ref: null
    capacity.provider_limits:
      status: unknown
      evidence_ref: null
    capacity.current_usage:
      status: unknown
      evidence_ref: null
    usage.token_cost_rate_limit:
      status: unknown
      evidence_ref: null
  ecosystems:
    claude_code: {status: "<connected_usable|partially_available|unavailable>", surface: "<exact inspected surface or inventory>", evidence_ref: "<redacted evidence reference>"}
    claude_design: {status: "<connected_usable|partially_available|unavailable>", surface: "<exact inspected surface or inventory>", evidence_ref: "<redacted evidence reference>"}
    grok: {status: "<connected_usable|partially_available|unavailable>", surface: "<exact inspected surface or inventory>", evidence_ref: "<redacted evidence reference>"}
    chatgpt: {status: "<connected_usable|partially_available|unavailable>", surface: "<exact inspected surface or inventory>", evidence_ref: "<redacted evidence reference>"}
    openai_codex: {status: "<connected_usable|partially_available|unavailable>", surface: "<exact inspected surface or inventory>", evidence_ref: "<redacted evidence reference>"}
    google_gemini: {status: "<connected_usable|partially_available|unavailable>", surface: "<exact inspected surface or inventory>", evidence_ref: "<redacted evidence reference>"}
  dispatch:
    decision: single_agent_fallback
    blocking_reasons:
      - "worker.create: unknown — exact create contract and stable session ID not established"
      - "worker.observe: unknown — status or wait contract not established"
      - "worker.collect_result: unknown — task-correlated result contract not established"
  limits:
    global_active_sessions: {value: unknown, evidence_ref: null}
    nested_accounting: {value: unknown, evidence_ref: null}
    provider_limits: {value: unknown, evidence_ref: null}
    workspace_capacity: {value: unknown, evidence_ref: null}
    usage_telemetry: {value: unknown, evidence_ref: null}
~~~

Use only these capability statuses: `supported`, `unsupported`, and `unknown`. Ecosystem availability is a separate classification: `connected_usable`, `partially_available`, or `unavailable`. Include the exact exposed surface and a redacted evidence reference for every non-unknown claim; a status without provenance is not an auditable finding.

Set `dispatch.decision` to `dispatch_ready` only when `worker.create`, `worker.observe`, and `worker.collect_result` are all supported by current-session evidence and creation returns a stable host-issued session ID. Otherwise set it to `single_agent_fallback` and list every blocking capability, its status, and the missing evidence or permission. An incomplete inventory makes unverified operations unknown, not unsupported.

Keep ecosystem labels separate from operation status: a partially available provider can still lack the required worker lifecycle, and documented provider features do not make an ecosystem connected. Report only limits actually exposed by the host; leave the rest unknown. Do not include credentials, prompts, private source content, or full logs.

### Lifecycle and error semantics

Keep task state and worker-session state separate. A task may be planned, ready, active, blocked, completed, failed, or cancelled; a worker session has its own host-reported lifecycle. Mark a worker active only after its session ID and active state are confirmed. A queued request is not a running session.

Normalize outcomes without hiding the provider's original evidence:

| Outcome | Coordinator response |
|---|---|
| Unsupported operation or permission denied | Do not retry; use an allowed fallback or stop |
| Capacity exhausted | Apply backpressure; do not bypass the limit |
| Rate limited | Respect a host-supplied retry delay; retry only idempotent work |
| Transport interruption | Reconcile session state before retrying to avoid duplicate workers |
| Queue timeout | Report that the worker was not confirmed started |
| Worker timeout or failure | Collect available evidence, mark the task accurately, and assess dependants |
| Cancellation requested | Keep the session active until cancellation is confirmed |
| Result missing or mismatched task ID | Do not mark the task complete; quarantine the uncorrelated result |
| Partial or truncated result | Preserve available artifacts and checks; do not complete the task or unlock dependants |
| Failed or cancelled dependency | Block every not-yet-started transitive dependant and record the root cause |
| Active dependant after dependency invalidation | Keep its worker state separate, mark its task blocked/provisional, and do not automatically cancel it |
| Coordinator interruption or restart | Reconcile checkpointed worker IDs with host state before any redispatch |

### Partial-result and dependency rules

Use this attempt-level record when an adapter returns a result:

~~~yaml
session_id: "sf-20261108-r9m4"
task_id: "sf-20261108-r9m4-02"
task_spec_revision: 1
dispatch_registry_revision: 4
attempt_id: "sf-20261108-r9m4-02-a01"
previous_attempt_id: null
worker_session_id: "<host-issued ID, or null for coordinator-owned work>"
worker_terminal_state: null
result_completeness: "complete|partial|unavailable"
artifact_refs: []
acceptance_evidence_refs: []
coordinator_acceptance: "pending|accepted|rejected"
unmet_criteria: []
~~~

result_completeness describes the returned evidence, not task status. A partial or unavailable result never satisfies a dependency. A complete worker result is still only a proposal until the coordinator verifies the deliverable and all acceptance criteria. A worker may fail after producing a usable artifact; preserve the worker failure and assess the artifact independently rather than automatically accepting or discarding it.

When a dependency fails, is cancelled, or remains incomplete, block all not-yet-started transitive dependants. Keep blocked_by references to the root task IDs. Do not automatically cancel active dependants: assess whether their work remains useful, request cancellation only when supported and safe, and wait for confirmation. Any result produced while its dependency is invalid remains provisional until revalidated. Preserve completed task history and create a corrective task if an already-completed dependant no longer meets acceptance criteria.

Every retry or reassignment keeps the stable task ID and adds a new unique attempt_id linked through previous_attempt_id. Reconcile the previous worker's state before redispatch; if it is unobservable, keep the task blocked rather than risking duplicate work. Record the coordinator's explicit recovery decision and rationale.

Retry only transient, idempotent operations with bounded attempts. Never invent an idempotency field or retry delay when the concrete integration does not expose one.

## Native-host lifecycle mapping (reference only)

The following mappings translate documented host behavior into questions for the normalized capability snapshot. They are not universal tool schemas, and documentation alone does not make a capability supported. Names, controls, return shapes, permissions, and behavior vary by client and version.

| Host surface | Create candidate | Observe / wait candidate | Result collection candidate | Stop / cancel evidence | Coordination and workspace caveats |
|---|---|---|---|---|---|
| Claude Code | The Agent tool creates subagents when that tool is exposed. Current documentation says Task was renamed to Agent in version 2.1.63; legacy Task references may remain valid aliases. | A foreground call blocks until completion. Background work can report through completion notifications and the /tasks interface; wait behavior differs by session mode and fork configuration. Confirm the current session exposes an observable status or wait path. | The parent receives the subagent result; preserve partial output and explicit failure information rather than treating any returned text as success. | Use only a stop operation or control exposed to the parent in this session. TaskStop appears in context-specific tool availability; do not assume it is a universal parent cancellation API. Verify terminal state after requesting a stop. | SendMessage, cross-session visibility, and task tools depend on configuration and context. Agent Teams are distinct from subagents and require their own feature availability. A separate context does not prove a separate filesystem or isolated write workspace. |
| Codex CLI / IDE / app and ChatGPT Work | The host can orchestrate subagent workflows, but the documented workflow does not define one portable tool name shared by every client. ChatGPT Work availability is account-dependent. | Codex documents the /subagents command and client activity panels. Treat a UI-only indicator as human visibility, not as a machine-readable status API unless the current session exposes it to the coordinator. | The host can consolidate results into the parent response; supported clients also allow inspection of individual agent threads. Correlate each result to its originating task using evidence available in the current session. | Use the client’s exposed stop/close control or instruction path only when available, then verify that the worker actually reached a terminal state. Do not infer cancellation from a request being accepted. | Parent sandbox and approval settings are inherited. A custom agent definition does not itself create a read-only sandbox. Parent-driven steering does not imply peer messaging, shared task state, or isolated worktrees. |
| Gemini CLI | The main agent can invoke configured or built-in subagent tools by their agent names. The @name prompt syntax nudges routing; it is not a portable lifecycle API. | A subagent reports when its delegated task completes, but the cited documentation does not define a universal machine-readable status/wait interface for every CLI session. Inspect the tools actually exposed. | Collect the report returned to the main agent and verify task identity and completeness. Do not assume a stable session ID unless the live host returns one. | Do not assume a generic cancellation operation from subagent support alone. Mark cancellation supported only when the current surface exposes an operation and its outcome can be observed. | Local subagents do not automatically provide peer-team semantics, shared task state, or filesystem isolation. Remote A2A agents are a separately configured integration and must be assessed independently. |

### Evidence required before normalizing a host

For each candidate operation, record the client and version when available, exact exposed tool or control, relevant schema or observable input/output, permission scope, and evidence of the outcome. Then apply these checks:

1. Mark worker.create supported only when the current surface actually starts a distinct model session and returns a stable host-issued session identifier.
2. Mark worker.observe supported only when the coordinator can inspect status or wait for an outcome in the current session. A documentation page, activity panel, or human-visible command is not automatically a callable adapter operation.
3. Mark worker.collect_result supported only when the result can be retrieved and correlated to the originating task/session; preserve failure and partial-result signals.
4. Mark worker.cancel supported only when the current surface exposes cancellation and the resulting state can be verified. A request to stop is not proof that work stopped.
5. Mark workspace.isolate supported only when the current environment proves the worker's write workspace is isolated, or the coordinator has established non-overlapping paths and serialized integration.
6. Assess team creation, peer messaging, shared state, global/nested accounting, and usage telemetry separately. Never infer them from subagent creation.

If the required creation, observation, or result-collection evidence is missing, keep that capability unknown and follow the single-agent fallback in SKILL.md. Do not manufacture a cross-provider adapter from similar-looking product features.

## Logical operations

Names below are descriptive placeholders. Call the actual tool names and schemas discovered in the host.

| Operation | Purpose |
|---|---|
| `discover` | Return capabilities, quotas, and limits |
| `create_worker` | Start a worker with a task brief |
| `get_worker` | Read session status and metadata |
| `wait_worker` | Await completion or an event |
| `send_message` | Send a follow-up or coordination message |
| `cancel_worker` | Stop a worker and propagate cancellation |
| `list_workers` | Enumerate active and terminal sessions |
| `create_workspace` | Allocate an isolated worktree/container |
| `collect_result` | Retrieve output, logs, or patch |
| `release_workspace` | Clean up the workspace |
| `get_usage` | Return usage, cost, and rate-limit telemetry |

A minimal bridge may implement discovery, creation, waiting, cancellation, and result collection. Add workspace isolation and telemetry before concurrent code editing or high-scale runs.

## Task envelope

Illustrative logical payload (not a universal API schema):

~~~json
{
  "task_id": "stable-id",
  "task_spec_revision": 1,
  "title": "Review API error handling",
  "role": "reviewer",
  "objective": "Find correctness and compatibility issues",
  "context_refs": ["repository snapshot or source references"],
  "read_paths": ["src/api/**", "tests/api/**"],
  "write_paths": [],
  "dependencies": [],
  "acceptance_criteria": [
    {"id": "AC-01", "description": "Findings include exact file and line references"},
    {"id": "AC-02", "description": "Each issue includes impact and evidence"}
  ],
  "expected_artifacts": [
    {"slot_id": "OUT-01", "kind": "report", "required": true, "allowed_paths": [], "approved_store": "host-issued session artifact reference", "satisfies": ["AC-01", "AC-02"]}
  ],
  "deliverable": "structured findings",
  "mode": "read_only"
}
~~~

Do not send fields unsupported by the concrete provider API.

## Result envelope

A result must echo the identifiers and revisions from its recorded dispatch attempt. Use this portable envelope as a mapping aid, not as a universal provider schema:

~~~yaml
schema_version: 1
session_id: "<session ID>"
task_id: "<stable task ID>"
task_spec_revision: 1
attempt_id: "<unique attempt ID>"
dispatch_registry_revision: 4
worker_session_id: "<host-issued ID, or null for coordinator-owned work>"
terminal_state: "<host-confirmed terminal state, or null for coordinator-owned work>"
result_completeness: "complete|partial|unavailable"
artifacts:
  - artifact_id: "<unique artifact instance ID>"
    slot_id: "<declared expected-artifact slot>"
    producer_task_id: "<task ID>"
    producer_attempt_id: "<attempt ID>"
    locator: "<repository-relative path or approved artifact reference>"
    immutable_ref: null
    byte_length: null
    content_digest:
      algorithm: "sha-256"
      value: null
    acceptance_criteria_ids: ["<criterion ID>"]
acceptance_evidence:
  - criterion_id: "<criterion ID>"
    artifact_ids: ["<artifact ID>"]
    evidence_ref: "<redacted reference>"
    verification_command: "<exact command or inspection method>"
~~~

The task brief must declare `task_spec_revision`, stable acceptance-criterion IDs, and `expected_artifacts` slots before dispatch. Each slot defines its kind, whether it is required, allowed paths or approved store, and the criterion IDs it can satisfy. A task with no file/patch outputs declares an empty list, but still supplies evidence for every criterion.

The coordinator—not the worker—records acceptance. Correlate the exact tuple `(session_id, task_id, task_spec_revision, attempt_id, dispatch_registry_revision, worker_session_id)` against the admission and attempt records. The dispatch revision must match the attempt's historical admission revision; it need not equal the current global revision. A late/superseded attempt, stale task revision, mismatched session, duplicate slot, missing required artifact, unexpected artifact, wrong producer ID, or out-of-scope locator is quarantined and cannot satisfy current acceptance.

Retrieve every required artifact and verify its kind, provenance, and allowed path boundary. Prefer an immutable host-issued artifact reference; otherwise the coordinator computes SHA-256 over the exact retrieved bytes and rechecks it before integration. A worker-supplied digest is only a hint. A digest proves byte identity against a value, not authorship, correctness, or safety.

Map every acceptance criterion to concrete evidence and independently execute its verification command or inspection. Record pass/fail/unknown per criterion. Missing evidence or an unrun required check is unknown. Do not integrate or complete the task unless correlation matches, the result is complete, all required artifacts are verified, every criterion passes, and dependencies are valid. Preserve quarantined or partial artifacts as untrusted history; do not silently discard or execute them.

## Workspace contract

Preferred write models:
1. read-only workspace plus findings;
2. isolated worktree/branch plus patch or commit;
3. isolated container plus patch artifact;
4. shared workspace with explicit writer ownership and serialized integration.

Registry v3 binds the coordinator's workspace assessment to the current task specification and path scope:

~~~yaml
workspace_verification:
  verified_by: "coordinator"
  mode: "read_only|isolated|shared_serialized"
  status: "not_required|verified|unverified|failed"
  task_spec_revision: 1
  verified_registry_revision: 3
  scope:
    read_paths: ["docs/ORCHESTRATION_PATTERNS.md"]
    write_paths: []
  workspace_ref: "<opaque host/workspace reference, or null>"
  evidence_ref: "<redacted observation or ownership record, or null>"
  verified_at: "<timestamp, or null>"
~~~

The record's `task_spec_revision` must match the task and its `scope` must exactly match the normalized current `read_paths` and `write_paths`; `verified_registry_revision` must not exceed the registry revision being validated. Any task-spec revision or path-scope change invalidates the prior workspace evidence until it is refreshed. A writable task cannot become ready, active, or completed until the record is verified. Overlapping write paths are safe only when both tasks have distinct verified isolated workspace references. A shared workspace requires non-overlapping ownership and serialized integration. Read-only tasks declare no write paths. The record describes observed host isolation or coordinator-enforced ownership; it does not make an adapter's assertion self-proving.

The adapter must make the active model visible. Workers must not assume every session shares a filesystem.

## Reliability and security

Use stable task IDs and idempotency keys; distinguish queue timeout from worker timeout; make cancellation observable; bound retries; deduplicate result delivery; persist enough state for coordinator restart; share one global concurrency budget across nested supervisors; never silently drop failures.

Treat adapter outputs as untrusted data. Keep credentials out of Skill files and prompts. Do not route private project data to third-party providers without authorization.

## MCP as one possible transport

An MCP server can expose an adapter to compatible hosts, but the server must implement or proxy a real orchestrator. MCP connectivity alone does not create model access, worker lifecycle, job scheduling, or 500-session throughput.
