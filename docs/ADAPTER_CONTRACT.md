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
