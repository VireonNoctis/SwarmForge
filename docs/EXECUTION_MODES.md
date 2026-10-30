# Execution Modes

SwarmForge is installed as a Skill and uses the AI host as its runtime. Choose the simplest real delegation path exposed by the current session.

## Primary: native host delegation

### A. Native subagents

Use the host's subagent tools when it can create workers, pass scoped task briefs, and return results. This is the default for independent research, implementation, tests, and review.

### B. Native agent teams

Use native teams when the host supports teammate communication, shared task state, or peer coordination. Use them only when that communication provides value beyond isolated subagents.

Host feature availability, permissions, concurrency limits, and workspace behavior remain authoritative. Do not infer capabilities from product names or documentation for a different surface.

## Fallback: single-agent operation

When the current host exposes no real delegation mechanism, SwarmForge still:
- creates a dependency-aware task graph;
- identifies workstreams that could run independently;
- writes bounded task briefs with acceptance criteria;
- plans ownership and safe integration order;
- executes what it can as the current agent.

This is a valid operating mode. Do not pretend that agents were spawned, and do not require the user to deploy a service just to use the Skill.

## Optional: already configured external integrations

These paths are not bundled with SwarmForge. Use one only when it is already configured, authorized, and available to the host—or when the user separately asks to design or implement it.

| Integration | What it can provide | Important boundary |
|---|---|---|
| MCP orchestration bridge | Common worker tools for connected hosts | MCP is a protocol; the server must implement a real worker lifecycle |
| Provider API/SDK service | Provider sessions, routing, quotas, and scheduling | Requires a separate implementation, credentials, quota handling, and operations |
| Local CLI/process manager | Agent CLI processes and isolated workspaces | Requires installed/authenticated CLIs and local resources |
| Remote queue and worker pool | Durable dispatch to container/VM workers | Requires separately operated infrastructure and security controls |
| CI matrix/build farm | Parallel deterministic build, test, or scan jobs | CI jobs are not AI agents unless a real agent runner is involved |

Do not present any of these integrations as a SwarmForge dependency or as already implemented in this repository.

## Workspace strategies

For parallel code changes, prefer:
1. separate worktrees or branches per writer;
2. patch-only contributions with one integrator;
3. isolated clones or containers;
4. explicit file ownership and serialized writes when sharing a workspace.

Read-only research can use a shared snapshot. Concurrent access does not make overlapping writes safe.

## Selection rule

Use native subagents first, native teams when communication is useful, and an already configured external bridge only when it solves a real gap. Otherwise, stay single-agent and provide a clear plan. Do not add infrastructure for its own sake.
