# Installation

The repository root is the Skill package. Install the whole directory so the host can read `SKILL.md` and its referenced documentation. Use the exact installation path supported by your AI host.

## Claude Code

Personal Skill:

~~~text
~/.claude/skills/swarmforge/
~~~

Project Skill:

~~~text
.claude/skills/swarmforge/
~~~

Place `SKILL.md` directly inside the `swarmforge` directory, with the supporting files alongside it.

## Claude.ai

1. Download this repository as a ZIP.
2. Ensure `SKILL.md` is at the root of the Skill folder inside the ZIP.
3. Upload it through Claude's Skills settings.
4. Enable code execution where required.
5. Test with a small task and inspect the tools actually available.

Plan requirements and interface details can change; follow the current official instructions in [Sources](SOURCES.md).

## Claude API

Use the documented Skills API and attach the Skill with the required code-execution tool. API Skills run in a constrained sandbox; do not assume they can make arbitrary network requests or install runtime packages. A separately configured external orchestrator is only needed when the user explicitly requires capabilities outside that sandbox.

## Codex CLI and IDE extension

Repository Skill:

~~~text
.agents/skills/swarmforge/
~~~

Personal Skill:

~~~text
~/.agents/skills/swarmforge/
~~~

Place the full Skill directory at the host's documented location. Refresh/restart the host if a newly added Skill is not detected.

## ChatGPT and OpenAI surfaces

Use the standalone Skill installation flow provided by the supported ChatGPT/Codex surface. Where the product distributes Skills through a plugin or another packaging mechanism, follow the current official instructions for that surface.

The repository includes optional `agents/openai.yaml` presentation metadata. It does not bundle an MCP server or declare a server dependency.

## VS Code and Copilot

VS Code documents project Skill locations including `.github/skills/`, `.claude/skills/`, and `.agents/skills/` for supported harnesses. A Skill being discoverable does not guarantee agent spawning. Use the selected harness's actual tools.

## Cursor and other clients

Check the client's current documentation for Agent Skills compatibility and its install path. Do not assume compatibility or feature parity.

## No native delegation?

The Skill still works as a single-agent coordinator: it creates a task graph, identifies independent workstreams, and prepares task briefs. Do not deploy a separate backend just to install or use SwarmForge.

If the user explicitly requires live delegation in a host without it, an existing authorized adapter may be used or an external integration can be separately designed. See [Execution modes](EXECUTION_MODES.md) and [Adapter contract](ADAPTER_CONTRACT.md).

## Verify installation

Invoke SwarmForge on a task with two independent read-only workstreams. Confirm that the host reports actual worker sessions and that the coordinator collects their results. Do not begin with simultaneous writes to the same file.

## Official documentation

Host-specific instructions and references are collected in [Sources](SOURCES.md). Re-check those documents before relying on plan, region, or feature availability.
