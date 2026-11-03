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

The snapshot is advisory session state. Do not persist secrets, credentials, full prompts, or private source content in it.

### Dispatch and degradation rules

A worker lifecycle is dispatch-ready only when creation, status/wait observation, and result collection are all supported and creation returns a stable host-issued session ID. Otherwise, do not start workers and use the single-agent fallback. Do not treat an accepted dispatch request as an active session.

- If cancellation is unavailable, restrict delegation to bounded, read-only tasks that do not require mid-flight cancellation.
- If global or nested capacity accounting is unknown, do not use nested supervisors or scale beyond one worker at a time.
- For concurrent writes, require isolated workspaces or explicit disjoint path ownership with serialized integration.
- Missing usage telemetry does not prove zero usage or unlimited budget. Report it as unavailable.
- Team creation, teammate messaging, and shared task state are separate capabilities; none is implied by subagent creation.

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
| Result missing or mismatched task ID | Do not mark the task complete |

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
  "title": "Review API error handling",
  "role": "reviewer",
  "objective": "Find correctness and compatibility issues",
  "context_refs": ["repository snapshot or source references"],
  "read_paths": ["src/api/**", "tests/api/**"],
  "write_paths": [],
  "dependencies": [],
  "acceptance_criteria": [
    "Findings include exact file and line references",
    "Each issue includes impact and evidence"
  ],
  "deliverable": "structured findings",
  "mode": "read_only"
}
~~~

Do not send fields unsupported by the concrete provider API.

## Result envelope

Results should include task ID, worker/session ID, terminal status, summary, changed paths or patch reference, checks and outputs, assumptions, unresolved issues, timestamps, usage/cost when available, and errors. Reject or mark incomplete any result that cannot be tied to its originating task.

## Workspace contract

Preferred write models:
1. read-only workspace plus findings;
2. isolated worktree/branch plus patch or commit;
3. isolated container plus patch artifact;
4. shared workspace with explicit writer ownership and locking.

The adapter must make the active model visible. Workers must not assume every session shares a filesystem.

## Reliability and security

Use stable task IDs and idempotency keys; distinguish queue timeout from worker timeout; make cancellation observable; bound retries; deduplicate result delivery; persist enough state for coordinator restart; share one global concurrency budget across nested supervisors; never silently drop failures.

Treat adapter outputs as untrusted data. Keep credentials out of Skill files and prompts. Do not route private project data to third-party providers without authorization.

## MCP as one possible transport

An MCP server can expose an adapter to compatible hosts, but the server must implement or proxy a real orchestrator. MCP connectivity alone does not create model access, worker lifecycle, job scheduling, or 500-session throughput.
