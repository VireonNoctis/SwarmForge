# Platform Compatibility

Agent Skills standardize packaging and instructions, not identical runtime behavior. Treat host support and live delegation as separate questions. Re-check official sources before making product or account-specific claims.

## Compatibility matrix

| Host / surface | Skill packaging | Live multi-agent execution |
|---|---|---|
| Claude Code | Project `.claude/skills/` or personal `~/.claude/skills/` directory | Native subagents; Agent Teams are a separate, experimental opt-in feature |
| Claude.ai | Upload a custom Skill ZIP through Skills settings; code execution is required | Uploading a Skill does not itself provide a worker lifecycle |
| Claude API | Skills API with the documented code-execution sandbox | API Skills do not imply Claude Code subagents or an Agent Team; use a separately configured API/SDK integration only when authorized |
| ChatGPT Work | Skills bundled in an installed plugin for ChatGPT Work | Hosted subagent workflows are documented for eligible accounts; inspect the current session and workspace controls |
| ChatGPT desktop | Standalone Skills are supported in the desktop app | Codex app chat exposes subagent threads; distinguish that surface from ordinary ChatGPT chats and ChatGPT Work |
| Codex CLI / IDE extension | Repository or user `.agents/skills/` directory | Current Codex releases document native subagent workflows and custom agents; inspect per-session configuration and tools |
| ChatGPT web / mobile | Skills bundled in plugins distributed through the supported plugin flow | Plugin tools are not workers; do not infer ChatGPT Work's subagent availability for every ChatGPT surface |
| Gemini CLI | User `~/.gemini/skills/` or `~/.agents/skills/`; workspace `.gemini/skills/` or `.agents/skills/` | Native subagents; remote subagents can be configured through A2A |
| VS Code / Copilot | Supported skill folders include `.github/skills/`, `.claude/skills/`, and `.agents/skills/` | Custom agents can act as subagents in supported harnesses; the selected harness controls lifecycle and tools |
| OpenAI Agents API / Responses API | API-side Skill support depends on the API and sandbox used | API-level multi-agent orchestration is available as a separate integration; it is not proof of Codex or ChatGPT host connectivity |
| xAI / Grok API | API integration, not a local Skill install location | Realtime Multi-agent Research is a beta, provider-managed research request—not a general-purpose host worker pool |
| Generic Agent Skills host | Load this directory and root `SKILL.md` | No delegation unless the host provides it |

This matrix describes documented packaging and broad capability boundaries, not a guarantee for every account, plan, region, model, or installation.

## Do not conflate packaging, tools, and agents

- **Skill packaging** means a host can discover and load `SKILL.md`; it says nothing by itself about delegation.
- **A native subagent** is a distinct model task created by the host and returned to a parent/coordinator. Verify creation, observable status or waiting, and result collection in the current tool surface.
- **An agent team** adds peer coordination such as direct teammate messaging and shared task state. Several subagent calls do not automatically make a team.
- **An ordinary tool call** runs an operation in the current agent's tool surface. Shell, MCP, browser, function, plugin, and CI calls are not additional model workers unless they explicitly create and expose a separate model session.
- **Provider API orchestration** is an API-level execution path. It is optional and separate from a first-party desktop, CLI, or chat surface unless that surface actually exposes the same operations.

SwarmForge's dispatch gate still applies even when a host documents subagents: the current session must expose worker creation, status/wait observation, result collection, and a stable host-issued session ID. Verify cancellation, messaging, team state, isolation, and limits independently; do not infer them from the word "subagent".

## Claude

Claude Code discovers custom Skills as directories containing `SKILL.md`; personal and project locations are documented by Anthropic. Native subagents run in their own contexts and return results to the parent session. Agent Teams are a separate feature with peer messaging and shared task coordination; the official documentation describes them as experimental and disabled by default until explicitly enabled. Do not assume team support from subagent support.

Claude.ai accepts uploaded Skills on supported plans with code execution enabled. Claude API supports Skills in a constrained sandbox. Do not assume an API Skill can directly call arbitrary provider APIs.

## ChatGPT and Codex

OpenAI documents standalone Skills for the ChatGPT desktop app, Codex CLI, and IDE extension; Skills bundled in plugins are also available in Chat and Work across ChatGPT web, desktop, and mobile. Codex discovers repository and user Skill directories under `.agents/skills` and current Codex releases document native subagent workflows, custom agents, and per-session concurrency settings. ChatGPT Work exposes hosted subagent workflows to eligible accounts. These are distinct surfaces: do not assume that plugin availability, a ChatGPT chat, or an API feature gives every surface the same delegation tools.

The optional `agents/openai.yaml` supplies presentation metadata for supported OpenAI Skill surfaces. It does not create an orchestration backend or declare a worker integration.

## Gemini CLI

Gemini CLI documents Agent Skills discovery in user and workspace locations, including the `.agents/skills/` alias. Its native subagents have separate contexts and can use specialized tool sets; the CLI also documents optional remote subagents through the Agent-to-Agent (A2A) protocol. A remote A2A connection is an external agent integration that must be configured and authorized. The documented subagent tool is not, by itself, proof that every lifecycle operation SwarmForge needs is exposed in the current session.

## Provider API orchestration

Provider APIs can expose real orchestration without making those capabilities native to every product surface:

- **OpenAI Agents API and Responses API:** official API documentation describes subagent creation, coordination, waiting, interruption, and result synthesis. Treat these as separate API integrations with their own session, environment, credentials, and limits. Do not transfer API defaults or lifecycle behavior to Codex CLI or ChatGPT Work without observing those host tools.
- **xAI Grok:** the documented Realtime Multi-agent Research feature uses a beta API model for provider-managed research. Its documented 4-agent and 16-agent configurations describe internal research agents for a request, not 4 or 16 independently addressable general-purpose coding workers. Do not count them as SwarmForge worker sessions unless the concrete integration exposes separate session identities and lifecycle operations.
- **Gemini API managed agents:** this is a separate managed API agent surface documented as public preview. It does not establish that Gemini CLI, ChatGPT, or another host can create or manage those agents without an explicit integration.

Provider API capabilities are optional integration candidates, not dependencies of the portable Skill. Review the linked official documentation and the actual adapter schema before using one.

## VS Code and other hosts

VS Code documents project Skill directories including `.github/skills/`, `.claude/skills/`, and `.agents/skills/` for supported harnesses. Discovery does not guarantee that the model will invoke the Skill on every relevant request, nor does it imply agent spawning is supported.

For any other client:
1. Confirm it supports the Agent Skills format.
2. Install the whole Skill directory in its documented location.
3. Inspect the tools and delegation operations actually exposed.
4. Prefer native delegation; use an external adapter only when already configured or separately requested.
5. Test with independent read-only tasks before allowing concurrent writes.

## Not guaranteed

SwarmForge does not promise that a Skill can force a product to spawn agents, that all clients share tool names or workspace access, that a subscription includes API usage, or that a 500-session pool is available on any specific account. No third-party product endorsement is implied.
