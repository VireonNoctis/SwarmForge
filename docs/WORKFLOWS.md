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

Classify worker failure as provider, permission, timeout, tool, context, workspace, or task-quality failure. Retry only transient, idempotent work. Preserve task lineage and report failures that cannot be safely recovered.

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
