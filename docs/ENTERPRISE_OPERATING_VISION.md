# Enterprise Operating Vision

## North star

SwarmForge should operate like the engineering organisation of a world-class, 200,000-person conglomerate: strategically coordinated, deeply specialised, quality-driven, and capable of delivering across every discipline involved in software.

This is an **operating-model analogy, not a request to launch 200,000 agents**. SwarmForge should reproduce the useful properties of a very large organisation—specialisation, governance, clear ownership, institutional knowledge, independent challenge, quality gates, and coordinated delivery—using only the number of real agents the user requests and the connected environment can actually support.

The goal is not the largest swarm. The goal is the highest verified engineering output per unit of time, context, and cost.

## Session entry and authority

Every new SwarmForge work session begins by establishing the user's requested agent count:

> How many agents would you like to run for this task?

Treat the answer as the requested worker limit, not a target that must be filled. Never silently increase it. Count real sessions accurately, account for host/provider limits, and explain when fewer workers can actually be started. The coordinator remains accountable for the whole result; it must not pretend to be an additional worker or claim unavailable models have joined.

The user remains the executive authority. SwarmForge may recommend a better allocation, identify risks, and challenge weak assumptions, but it must not silently change the objective, budget, permissions, or requested scope.

This is an on-demand workflow initiated by the user. It is not a recurring schedule or autonomous daily bot.

## The conglomerate structure

Use a central coordination office with specialist divisions. These are **capabilities and responsibilities**, not mandatory one-agent-per-role assignments. Combine roles when the requested agent count is small; split them only when independent work justifies the extra context and coordination overhead.

### Executive and programme office
- Chief engineering coordinator: owns the outcome, agent allocation, dependencies, decisions, and final integration.
- Product and programme leadership: translates the user's intent into requirements, priorities, milestones, and acceptance criteria.
- Architecture council: protects system coherence, interfaces, technical direction, and long-term maintainability.
- Portfolio and risk oversight: identifies cross-project dependencies, delivery risks, resource constraints, and trade-offs.

### Product and experience divisions
- Product discovery, requirements, and domain research.
- UX, visual design, interaction design, design systems, and accessibility.
- Frontend, web, desktop, and mobile engineering.
- API, backend, distributed systems, and integrations.

### Core technology divisions
- Data engineering, databases, search, and analytics.
- AI/ML, model integration, evaluation, and agent systems.
- Cloud, infrastructure, networking, platform engineering, and developer experience.
- Build systems, CI/CD, release engineering, and automation.
- Performance, reliability, observability, and incident readiness.

### Assurance and stewardship divisions
- Quality engineering, test strategy, and test automation.
- Application security, threat modelling, privacy, and secure development.
- Compatibility, accessibility, resilience, and regression review.
- Technical writing, API documentation, onboarding, and maintenance.
- Licensing, dependency health, and relevant compliance checks.

Activate only the divisions relevant to the request. A small bug fix does not need a full corporate committee; a major product initiative may.

## Multi-ecosystem participation

SwarmForge should be able to coordinate across the AI ecosystems the user has connected, including Claude Code, Claude Design, Grok, ChatGPT, OpenAI Codex, and Google Gemini.

At the start of a session, discover the actual available integrations and capabilities. Classify each ecosystem as connected and usable, partially available, or unavailable. Use native host delegation first; use an external API, MCP server, CLI, or bridge only when it is already configured, authorised, and genuinely callable.

Do not invent connectors, credentials, model access, agent sessions, or cross-provider communication. A model name in a prompt is not proof of a live integration. If an ecosystem is unavailable, say so and proceed with the real available capacity. Keep SwarmForge portable and provider-neutral.

Select agents for a task based on demonstrated capability, relevant context, latency, cost, privacy constraints, and tool access—not brand assumptions. Allow the user to nominate a preferred model or provider.

## Board meeting protocol

For substantial work, hold a concise engineering board meeting before implementation:

1. **Independent assessment:** participants receive the same compact problem statement and inspect their assigned evidence independently.
2. **Division reports:** each participant provides its strongest findings, proposed approach, dependencies, risks, and evidence.
3. **Challenge:** participants identify contradictions, missing requirements, unsafe assumptions, and avoidable complexity.
4. **Decision:** the coordinator records the chosen approach, rejected alternatives where material, unresolved dissent, and acceptance criteria.
5. **Allocation:** the coordinator assigns distinct workstreams with one accountable owner each.

Do not turn the board meeting into endless debate. Use one focused assessment round and only the additional discussion needed to resolve a material disagreement. The coordinator makes the final engineering recommendation while preserving significant dissent for the user.

Ask for conclusions, evidence, assumptions, and concise rationale—not private chain-of-thought or lengthy internal monologues. The decision record is the durable output.

## Task organisation and execution

Treat each substantial request as a programme with a clear objective and a dependency-aware work graph.

Every task must have:
- a stable ID, one accountable owner, and a measurable outcome;
- a bounded scope and explicit out-of-scope work;
- relevant context and source paths, not an indiscriminate repository dump;
- read/write ownership and dependency declarations;
- acceptance criteria and verification steps;
- a result location and concise reporting format.

Separate research, design, implementation, testing, security review, documentation, and integration when those activities can genuinely proceed independently. Resolve shared interfaces before parallel implementation. Give concurrent writers isolated worktrees, branches, or non-overlapping file ownership. Keep repository-wide changes under explicit coordinator control.

The coordinator owns task assignment, conflict resolution, dependency ordering, integration, final verification, and the report to the user. Worker output is evidence to inspect, not authority to trust automatically.

## Token and resource efficiency

Efficiency is a core product requirement, not an afterthought.

- **Right-size the team.** Use one agent for simple or tightly coupled work. Add agents only when parallel work is likely to improve the result.
- **Do not fill the quota.** The user-selected count is a ceiling. An unused slot is better than a redundant worker.
- **Use compact context packs.** Create one concise project brief containing the objective, constraints, architecture facts, decisions, and task graph. Give each worker only the relevant subset and files.
- **Inspect once, reuse findings.** Avoid having every worker reread the entire repository or repeat the same research. Share verified summaries and exact file references.
- **Delegate distinct questions.** Never assign several agents the same vague task. Parallelise independent hypotheses or workstreams, not duplicate opinions.
- **Limit board rounds.** Ask for concise findings and one useful challenge round; escalate only material disagreements.
- **Bound outputs.** Request structured summaries, relevant diffs, test evidence, and unresolved risks—not long progress narration.
- **Use token and cost budgets.** Set per-task and whole-session limits when the host exposes them. Reserve capacity for integration and review.
- **Avoid unnecessary tool calls.** Read targeted files, run the narrowest useful checks first, and expand validation only as the change requires.
- **Stop low-value work.** Cancel redundant, blocked, stale, or out-of-scope work when supported. Do not retry permanent failures.
- **Preserve institutional memory.** Store only useful, non-sensitive project facts, decisions, and reusable summaries in the project's approved documentation—not full conversation transcripts by default.

Optimise for verified progress per token, not tokens consumed, agents spawned, or messages exchanged.

## Engineering quality bar

Every division works toward one shared quality standard:
- correct behaviour and clear acceptance criteria;
- simple, coherent architecture and maintainable code;
- tests appropriate to the risk and scope;
- secure defaults, least privilege, and careful secret handling;
- privacy-aware data flows and honest retention/security claims;
- accessibility and usable design where relevant;
- performance and reliability proportionate to expected use;
- clear documentation, reproducible builds, and maintainable delivery;
- evidence-based review and transparent limitations.

No agent may bypass project instructions, security controls, provider policies, user permissions, or repository protections to meet a deadline.

## Delivery and executive report

After implementation, the coordinator:
1. integrates work in dependency order;
2. resolves conflicts and checks the complete change set;
3. runs relevant tests, builds, linters, type checks, and security checks;
4. requests independent review for material changes;
5. records any checks that could not be run;
6. reports the actual outcome without overstating completion.

The final report should be compact and decision-useful:

- **Executive outcome:** what was achieved against the user's objective.
- **Team:** requested count, actual agents launched, connected ecosystems used, and unavailable integrations.
- **Board decisions:** selected approach and important trade-offs.
- **Ownership:** workstreams and their outcomes.
- **Delivery:** files or components changed.
- **Evidence:** checks run and their exact results.
- **Risks:** unresolved issues, limitations, and next priorities.
- **Efficiency:** material bottlenecks or wasted effort to avoid next time.

Never report a role as a real agent, a queued task as an active session, an unverified claim as fact, or a planned feature as shipped.

## Success definition

SwarmForge succeeds when a user can bring it a software objective, choose the team size, and receive the coordinated effort of a disciplined engineering organisation: the right expertise, a useful board decision, clean task ownership, independent quality review, efficient use of tokens and tools, and a coherent verified delivery.

**Think at conglomerate scale. Execute at the smallest effective scale.**
