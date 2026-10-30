# ADR 0001: The Skill is the product

- Status: Accepted
- Date: 2026-10-30

## Context

The objective is to coordinate specialist agents across compatible coding assistants. The user explicitly wants a portable `/skill` that can be installed from this Git repository, not a standalone IDE or mandatory orchestration service.

## Decision

Ship SwarmForge as a portable Agent Skill with the root `SKILL.md` as its entrypoint. The current AI host is the execution runtime. Prefer native subagents or agent teams exposed by that host.

External MCP, provider API/SDK, CLI, or remote-queue integrations remain optional and must already be configured or be separately requested. The package must work as a Skill without a SwarmForge backend.

The Skill is language-independent. If a separate companion implementation is explicitly approved later, prefer Rust for its core, C++ for focused native/performance-critical components, and Next.js only for an optional separately requested UI.

## Alternatives

- Standalone IDE: rejected because the requested product is a Skill.
- Prompt-only mega-prompt: rejected because it lacks progressive disclosure and reusable references.
- Mandatory proprietary backend: rejected because it prevents hosts from using their own agent runtime.
- Mandatory dashboard or database: rejected because neither is needed for a portable Skill.
- Claiming 500 agents from the Skill itself: rejected because instructions cannot override host/provider capacity.

## Consequences

The package can be installed on compatible hosts without a SwarmForge service, provider keys, compiled binary, or web UI. Live execution depends on real tools available in the host or a separately configured integration. A 500-session limit remains a design target until a real runtime is deployed and load-tested.
