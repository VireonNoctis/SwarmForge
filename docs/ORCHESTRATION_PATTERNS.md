# Orchestration Patterns

Choose a topology based on task dependencies and communication needs. No single pattern is optimal for every job. These patterns are instructions for the host's real agents, not a requirement to deploy an external scheduler.

## Fan-out / fan-in

One coordinator dispatches independent tasks and combines their results.

~~~text
Coordinator
  ├── Research A
  ├── Research B
  ├── Implement A
  ├── Test B
  └── Review
        ↓
  Integration and synthesis
~~~

Best for repository reconnaissance, independent modules, parallel code review, test generation, documentation research, and separate bug hypotheses. Simple and easy to cap, but the coordinator can become a bottleneck and scopes must prevent duplicate work.

## Hierarchical swarm

A root coordinator assigns domains to supervisors, who coordinate specialists.

~~~text
Coordinator
  ├── Frontend lead -> UI workers + test worker
  ├── Backend lead  -> API workers + test worker
  └── Quality lead  -> security + integration review
~~~

Best for large projects with clear domains. All descendants must debit one global concurrency budget; supervisor trees must not multiply a 500-session limit. Use only if the host supports nested delegation.

## DAG / pipeline

Tasks run only when dependencies are complete: repository analysis → interface design → implementation → integration → tests → independent review. Best for tightly dependent changes where speculative parallel work would create rework.

## Map / reduce

Map a common operation across independent files, records, or modules; reduce normalized results into a deduplicated, evidence-preserving summary. Best for migrations, audits, large test collections, and bulk analysis. Validate the transformation on a small sample first.

## Specialist ensemble

Independent reviewers inspect the same immutable snapshot for correctness, security, performance, accessibility, maintainability, or test coverage. Use for high-risk work. Reviewers should return findings, not overlapping patches.

## Competing hypotheses

Agents independently investigate possible causes or designs. The coordinator compares evidence and runs discriminating tests. Majority vote is not a correctness test; require source evidence and falsifiable claims.

## Peer team / mesh

Agents message one another and work from shared task state. Use only when the host actually supports teammate communication and coordination. This can improve discussion but increases context cost and makes ownership harder to supervise.

## Hybrid execution

Native host agents may be combined with an already configured MCP bridge, provider SDK, CLI worker pool, or remote queue. These are optional external integrations, not core SwarmForge requirements. Keep one authoritative task registry and one global capacity budget.

## Pattern selection

| Work shape | Suggested pattern |
|---|---|
| Independent reviews/research | Fan-out / fan-in |
| Large multi-domain project | Hierarchical, if nested agents are supported |
| Strict dependencies | DAG / pipeline |
| Many similar independent items | Map / reduce |
| High-risk implementation | Specialist ensemble |
| Uncertain diagnosis/design | Competing hypotheses |
| Ongoing peer coordination | Team / mesh |
| Multiple hosts/providers | Hybrid, only when configured |

## Anti-patterns

- One worker per file without considering value.
- Multiple uncoordinated writers on the same file.
- Repeating full repository discovery in every worker.
- Voting instead of testing.
- Deep supervisor trees without global concurrency accounting.
- Counting queued jobs as active AI agents.
- Keeping workers alive after their deliverable is complete.
- Deploying infrastructure merely to make the Skill usable.
