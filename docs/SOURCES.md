# Official Sources

Provider behavior, product surfaces, packaging requirements, and limits can change. Re-check official documentation before updating compatibility claims.

## Agent Skills format

- [Agent Skills specification](https://agentskills.io/specification) — package layout and SKILL.md metadata.
- [Anthropic: Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) — loading, references, Claude surfaces, API sandbox limitations.
- [OpenAI: Build skills](https://learn.chatgpt.com/docs/build-skills) — ChatGPT/Codex Skill layout, install locations, optional agent metadata, distribution guidance.
- [OpenAI: Skills and plugins](https://learn.chatgpt.com/docs/skills-and-plugins) — distinction between Skills and plugins/MCP tools.

## Claude orchestration

- [Claude Code: Agent teams](https://code.claude.com/docs/en/agent-teams) — teammate coordination and native team limitations.
- [Claude Help: What are Skills?](https://support.claude.com/en/articles/12512176-what-are-skills) — Skill upload and product requirements.

## OpenAI orchestration

- [OpenAI Agents API: Multi-agent](https://developers.openai.com/api/docs/guides/agents-api/multi-agent) — an API-specific multi-agent approach and its concurrency controls.
- [OpenAI Responses API: Multi-agent](https://developers.openai.com/api/docs/guides/responses-multi-agent) — a distinct multi-agent API approach.
- [OpenAI: Skills in plugins](https://developers.openai.com/plugins/concepts/skills) — Skills distributed with MCP-backed plugins.

## VS Code and Copilot

- [VS Code: Agent Skills](https://code.visualstudio.com/docs/agent-customization/agent-skills) — supported project and personal Skill locations and host-specific discovery.

## Interpretation

1. Agent Skills standardize workflow packaging, not every host's execution API.
2. Provider concurrency settings are not portable across products.
3. A documented default is not an account quota or capacity guarantee.
4. A configured ceiling does not prove all sessions can be admitted concurrently.
5. Confirm current plan, region, workspace, and feature availability for the target deployment.

## Native host delegation and Skill discovery

- [Claude Code: Create custom subagents](https://code.claude.com/docs/en/sub-agents) — subagent contexts, tool access, foreground/background work, and result handling.
- [Claude Code: Agent teams](https://code.claude.com/docs/en/agent-teams) — peer messaging and shared tasks; experimental and disabled by default.
- [OpenAI: Subagents in ChatGPT and Codex](https://learn.chatgpt.com/docs/agent-configuration/subagents) — ChatGPT Work eligibility, Codex app/CLI/IDE workflows, inspection, and configuration.
- [Gemini CLI: Agent Skills](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/skills.md) — user/workspace discovery, `.agents/skills` alias, installation, and activation.
- [Gemini CLI: Subagents](https://github.com/google-gemini/gemini-cli/blob/main/docs/core/subagents.md) — native subagent behavior and custom agents.
- [Gemini CLI: Remote subagents](https://github.com/google-gemini/gemini-cli/blob/main/docs/core/remote-agents.md) — optional A2A connections to remote agents.
- [VS Code: Custom agents](https://code.visualstudio.com/docs/agent-customization/custom-agents) — harness-specific custom-agent and subagent behavior.

## Provider API orchestration (separate from product integrations)

- [OpenAI Agents API: Multi-agent](https://developers.openai.com/api/docs/guides/agents-api/multi-agent) — API sessions, subagent creation, coordination events, and limits.
- [OpenAI Responses API: Multi-agent](https://developers.openai.com/api/docs/guides/responses-multi-agent) — beta hosted collaboration actions, agent-tree accounting, and tool-call handling.
- [Google Gemini API: Agents overview](https://ai.google.dev/gemini-api/docs/agents) — managed API agents and their preview status; not a Gemini CLI capability claim.
- [xAI: Realtime Multi-agent Research](https://docs.x.ai/developers/model-capabilities/text/multi-agent) — beta provider-managed research orchestration and its request-level agent configurations.
