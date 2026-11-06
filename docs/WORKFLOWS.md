# Workflows

Use these recipes with the capability-aware rules in the root [Skill](../SKILL.md). Each recipe assumes the host exposes the relevant native delegation features; otherwise, apply it as a single-agent plan.

## Repository reconnaissance

1. Coordinator reads repository instructions and identifies the stack.
2. Read-only workers inspect distinct domains: architecture, tests/CI, security, product areas, and dependencies.
3. Each returns paths, evidence, risks, and next steps.
4. Coordinator consolidates findings and resolves contradictions.
5. No worker edits during reconnaissance unless the user requested changes.

## Parallel feature implementation

1. Architect identifies interfaces and dependencies.
2. Repository analyst assigns non-overlapping ownership.
3. Implementers use isolated worktrees or disjoint paths when supported.
4. Test worker prepares relevant checks when independent.
5. Integrator applies patches in dependency order.
6. Reviewer inspects the combined diff.
7. Coordinator runs final verification and reports evidence.

## Multi-hypothesis bug investigation

1. Provide each investigator the same reproduction and immutable evidence.
2. Ask for distinct hypotheses and disconfirming tests.
3. Keep investigators read-only until a likely cause is supported.
4. Run the smallest experiment that distinguishes the hypotheses.
5. Assign one implementer after diagnosis.
6. Add a regression test and independent review.

## Test and quality swarm

Split by unit, integration, end-to-end, performance, accessibility, or security only when suites can run independently. Avoid simultaneous edits to shared test configuration.

## Documentation and research swarm

Assign each researcher one specific question and source requirements. Require exact URLs and publication dates for changing claims. Synthesis must deduplicate and mark uncertain findings.

## Large repository migration

1. Inventory the affected paths and classify migration cases.
2. Define a reversible transformation and test it on a sample.
3. Use map/reduce across independent files only after sample validation.
4. Have workers return patches or isolated commits.
5. Run formatters and tests after integration.
6. Inspect the whole diff for missed cases and accidental churn.

## Failure recovery

1. Stop new dispatch to tasks whose prerequisites are no longer verified; preserve the original task and worker-session states separately.
2. Collect the worker's terminal state, partial artifacts, completed checks, unmet acceptance criteria, and redacted evidence references. A partial result is useful evidence, not task completion.
3. Classify the failure as provider, permission, capacity, timeout, transport, tool, context, workspace, or task-quality failure. Do not retry permanent permission, validation, or hard-quota failures.
4. Block every not-yet-started transitive dependant and record the root task IDs in blocked_by. Do not mark descendants failed/cancelled solely because a dependency failed.
5. Review active dependants individually. Do not automatically cancel them; if cancellation is necessary and supported, request it and verify the terminal state. Keep any work produced against invalid dependencies provisional.
6. Choose and record an explicit coordinator decision: retry, reassign, split, resume, accept a fully verified deliverable, or fail. Retry only transient, idempotent work after reconciling the previous worker.
7. Keep the task ID stable and append a unique attempt ID linked to the prior attempt. Preserve partial artifacts and failure evidence instead of overwriting them.
8. Recompute readiness after a dependency is repaired and its acceptance criteria are verified. Unblock dependants only through a recorded graph revision.
9. Checkpoint task transitions and recovery decisions in host-native task state or session notes. After coordinator restart, reconcile every nonterminal worker with the host before redispatch. If state cannot be recovered, keep uncertain tasks blocked and report the limitation.

Do not claim durable crash recovery unless the host actually preserves the checkpoint and worker state.

## Final report

~~~text
Execution mode:
Workers: launched / completed / failed / cancelled / queued
Tasks and outcomes:
Files changed:
Verification and results:
Checks not run:
Risks and remaining work:
Capacity ambition: requested / confirmed / not reached (reason)
~~~
