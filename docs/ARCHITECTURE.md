# Architecture

## Product boundary

SwarmForge is a portable Agent Skill installed from this repository. The root `SKILL.md` contains the coordinator workflow; supporting Markdown files provide installation guidance, patterns, security practices, and optional integration contracts.

**There is no SwarmForge runtime service in this repository.** The Skill does not create model sessions, host workers, schedule provider requests, store task state, or expose a web UI. Those capabilities belong to the AI host or to an external integration that a user has separately configured.

## Runtime relationship

~~~mermaid
flowchart TD
    U[User request] --> S[SwarmForge Skill]
    S --> D[Discover host capabilities]
    D --> N{Real delegation available?}
    N -->|Yes| H[Host-native subagents or teams]
    N -->|Configured integration| X[Existing authorized bridge]
    N -->|No| F[Single-agent plan and task briefs]
    H --> I[Collect and inspect results]
    X --> I
    F --> I
    I --> V[Integrate and verify]
    V --> R[Evidence-based report]
~~~

The host is the runtime. Native subagents and agent teams are the preferred execution path. An already configured external integration may be used when needed. Otherwise, SwarmForge falls back to a single-agent plan.

## What exists in this repository

| Component | Purpose | Runtime status |
|---|---|---|
| `SKILL.md` | Portable workflow, delegation policy, task contracts, verification | Used by the host |
| `docs/` | Installation, patterns, security, scaling, and optional adapter guidance | Reference material |
| `agents/openai.yaml` | Optional presentation metadata for supported OpenAI Skill surfaces | Metadata only |
| `scripts/validate.py` | Checks package frontmatter, required docs, JSON config, action pins, and local links | Maintainer tool |
| `tests/` | Package smoke tests | Maintainer checks |
| `.github/workflows/` | Package validation and repository security automation | CI only |

No compiled application, server, database, queue, orchestrator, provider integration, or dashboard is bundled.

## Responsibility boundaries

| Responsibility | Owner |
|---|---|
| Read and apply the Skill instructions | Compatible AI host |
| Create native subagents or teammates | Host's exposed agent tools |
| Enforce account, model, and provider quotas | Host and provider |
| Provide model access, tool permissions, and runtime isolation | Host/provider configuration |
| Coordinate tasks, assign ownership, reconcile results | SwarmForge instructions executed by the coordinator |
| Execute an optional external bridge | User-configured external integration |
| Validate this repository's package | Maintainer scripts and CI |

The Skill may request a behavior; it cannot grant itself permissions or manufacture capabilities the host does not expose.

## Optional external integrations

MCP servers, provider SDK services, local CLI process managers, remote queues, and CI worker pools are possible integration paths, not core SwarmForge components. They should be considered only when native host delegation is inadequate and an external integration is explicitly configured or separately requested.

The adapter contract in [ADAPTER_CONTRACT.md](ADAPTER_CONTRACT.md) describes logical capabilities for such integrations. It is not a universal API schema or a shipped implementation.

## Language policy

The Skill package is Markdown and YAML and has no application-language requirement.

If a separate companion runtime is deliberately approved later, use the following preference:
- **Rust:** default choice for a coordinator, scheduler, worker lifecycle, and provider/host adapters.
- **C++:** narrow native integrations or performance-critical components where native interop provides a concrete benefit. Avoid duplicating the coordinator in two languages.
- **Next.js:** only for a separately requested web interface. A web UI is not needed to install, invoke, or use the Skill.

These choices do not authorize adding a runtime or UI to the Skill package. Keep any future companion implementation separate and optional.

## Coordination model

When the host supports delegation, the coordinator:
1. discovers the actual tools and limits;
2. decomposes work into independent tasks and dependencies;
3. assigns one owner and clear read/write boundaries per task;
4. collects results and verifies claims;
5. integrates changes in dependency order;
6. runs final checks and reports evidence.

For high-concurrency planning, distinguish active sessions from queued tasks, logical roles, completed work, and retries. See [Scaling to 500](SCALING_TO_500.md).

## Related decisions

- [ADR 0001: The Skill is the product](DECISIONS/0001-skill-is-the-product.md)
