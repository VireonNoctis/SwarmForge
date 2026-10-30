# SwarmForge

> A portable Agent Skill that helps coding assistants coordinate real subagents and agent teams exposed by their host.

SwarmForge is installed as a **Skill from this Git repository**. It gives a compatible coding assistant a reusable engineering-coordinator workflow: inspect a project, split substantial work into independent tasks, delegate to available agents, integrate their results, verify the combined changes, and report what actually happened.

**The Skill is the product.** SwarmForge is not an IDE, hosted service, agent runtime, scheduler, database, or dashboard. It does not need a mandatory backend or a particular programming language.

## How it works

1. Install this repository as a Skill in a compatible AI host.
2. Invoke SwarmForge for work that genuinely benefits from parallel execution.
3. SwarmForge checks which delegation tools the current host actually exposes.
4. It prefers the host's native subagents or agent teams and uses external integrations only when they are already configured and authorized.
5. It assigns bounded tasks, tracks ownership and dependencies, integrates the results, and verifies the final work.

When a host does not expose live delegation, SwarmForge remains useful as a single agent: it creates the task graph and ready-to-use task briefs. It never pretends that workers were started.

## What it provides

- Task decomposition and dependency-aware planning.
- Native subagent and agent-team coordination where supported.
- Clear worker briefs, ownership boundaries, and expected deliverables.
- Concurrency, budget, retry, cancellation, and backpressure guidance.
- Workspace and file-conflict prevention for parallel code changes.
- Result collection, integration, independent review, and evidence-based verification.
- A single-agent fallback for hosts without live delegation.

## The 500-session ambition

SwarmForge is designed with a configurable target ceiling of up to **500 active worker sessions**. That is an ambition for a capable host/runtime, not a feature the Skill can manufacture.

A Skill cannot create model sessions, override account or provider quotas, or supply compute. The real limit is whatever the host, provider, account, workspace, and approved budget permit. Increase concurrency in measured batches and report active sessions separately from queued tasks, completed work, and retries. See [Scaling to 500](docs/SCALING_TO_500.md).

## Install

Use the install path documented by your AI host. The repository root is the Skill directory and contains `SKILL.md`.

- [Installation instructions](docs/INSTALLATION.md)
- [Platform compatibility](docs/PLATFORM_COMPATIBILITY.md)

The portable package can be read and installed without API keys, a database, a compiled binary, or a web service. An optional bridge is not a prerequisite.

## Optional integrations

Native host delegation is the default. A preconfigured MCP bridge, provider API/SDK, local CLI worker, or remote worker pool may be used only when it is actually available and authorized. Those systems are external integrations; this repository does not ship them.

Do not build or deploy an external orchestrator just to install SwarmForge. See [Execution modes](docs/EXECUTION_MODES.md) and the [adapter contract](docs/ADAPTER_CONTRACT.md) only when an external integration is genuinely needed.

## Language and implementation policy

The Skill itself is Markdown with small YAML metadata. It has no application runtime, so **Rust, C++, and Next.js are not required to install or use it**. The Python script in this repository is maintainer-only package validation; Python is not a Skill runtime dependency.

If a separate companion implementation is deliberately commissioned later, the preferred choices are:

- **Rust** for the core coordinator, scheduling, lifecycle management, and adapters.
- **C++** for narrowly scoped native integrations or genuinely performance-sensitive components—not a second implementation of the whole coordinator.
- **Next.js** only for an independently requested web interface. A dashboard is not part of the Skill and is not needed for agent delegation.

These are future implementation preferences, not shipped features or dependencies.

## Repository layout

~~~text
.
├── SKILL.md                 # Portable Skill entrypoint
├── agents/                  # Optional host metadata
├── docs/                    # Installation, patterns, security, references
├── scripts/                 # Maintainer-only validation
└── tests/                   # Package smoke tests
~~~

The repository also retains its editor, Codespaces, security, and GitHub automation configuration.

## Validate changes

Maintainers can run the package checks with Python 3 and its standard library:

~~~bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
~~~

These checks validate package structure and smoke tests. They do not test provider integrations or prove 500-session capacity.

## Principles

**Portable by default.** Keep the core workflow host- and vendor-neutral.

**Native first.** Prefer the delegation tools the current host already provides.

**Optional means optional.** Never require an external service, account key, database, or UI for the Skill to work.

**Honest capacity.** Never claim a worker exists or a concurrency target was reached without evidence.

**Controlled parallelism.** Give workers clear scope, isolate writes, and verify the integrated result.

## Scope today

This repository contains the portable Skill, optional host metadata, documentation, and package validation. It does not contain a production orchestration runtime, MCP server, provider integration, remote worker fleet, web dashboard, or 500-agent load test.

## Documentation

| Topic | Document |
|---|---|
| Portable coordinator workflow | [SKILL.md](SKILL.md) |
| Install the Skill | [Installation](docs/INSTALLATION.md) |
| Supported host surfaces | [Platform compatibility](docs/PLATFORM_COMPATIBILITY.md) |
| Product boundaries | [Architecture](docs/ARCHITECTURE.md) |
| Native and optional execution paths | [Execution modes](docs/EXECUTION_MODES.md) |
| Coordination patterns | [Orchestration patterns](docs/ORCHESTRATION_PATTERNS.md) |
| 500-session capacity model | [Scaling to 500](docs/SCALING_TO_500.md) |
| Optional integrations | [Adapter contract](docs/ADAPTER_CONTRACT.md) |
| Permissions and isolation | [Security model](docs/SECURITY_MODEL.md) |
| Example workflows | [Workflows](docs/WORKFLOWS.md) |
| Maintainer setup and checks | [Project setup](docs/PROJECT_SETUP.md) |

## Contributing

Read [AGENTS.md](AGENTS.md) and [CONTRIBUTING.md](CONTRIBUTING.md) before making changes. Keep the Skill portable, make the smallest complete change, and distinguish shipped functionality from designs for optional external integrations.

## Security

Do not commit credentials, private keys, tokens, or production data. See [SECURITY.md](SECURITY.md) and the [SwarmForge security model](docs/SECURITY_MODEL.md).

## License

No license is included yet. Until a license is selected and added, do not assume permission to reuse, modify, or redistribute this repository.
