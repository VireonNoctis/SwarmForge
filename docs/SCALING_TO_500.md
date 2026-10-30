# Scaling to 500 Active Agent Sessions

## Ambition and definition

The design ambition is a configurable global ceiling of up to **500 active AI worker sessions** across a capable execution environment. This is not the Skill's default launch count and not a promise that a particular host, account, model, or provider can reach it.

Decide whether the root coordinator is included. For a strict 500-total-session limit, reserve one slot for the root and allow no more than 499 worker sessions.

Do not count task definitions, queued jobs, logical roles, completed sessions, or retry attempts that are not currently running. Report active, queued, completed, failed, and cancelled separately.

## A Skill cannot manufacture capacity

A `SKILL.md` can request an orchestration strategy. It cannot raise host-managed limits, create API credentials, bypass provider quotas, supply compute or workspaces, or guarantee 500 simultaneous sessions.

Use native delegation first. If a real deployment eventually uses an external orchestrator, its capacity must be measured against the actual accounts, provider limits, workspace resources, and budgets.

## Capacity model

Maintain one global budget plus per-provider and per-model budgets:

~~~text
Global active-session cap:   500 (or lower if runtime requires)
Provider A active cap:       confirmed quota
Provider B active cap:       confirmed quota
Provider C active cap:       confirmed quota
Workspace cap:               CPU, memory, disk, containers
Request budget:              per minute / per day
Token budget:                per task and whole run
Cost budget:                 user-approved maximum
~~~

Effective capacity is the lowest applicable limit:

~~~text
effective_limit = min(global, provider, model, workspace, user_budget)
~~~

Unknown limits must not be treated as unlimited.

## Staged scaling strategy

1. **Probe:** inspect current host concurrency, provider rate limits, model quotas, workspace capacity, cancellation, and budget controls.
2. **Baseline:** start with a few workers for a large task, or less when limits are lower.
3. **Measure:** track useful completed work per unit time, integration time, failures, context use, and cost.
4. **Expand:** add workers in small batches only while throughput and quality improve.
5. **Backpressure:** queue work when a provider, workspace, or budget is full.
6. **Drain:** stop new admissions on cancellation, hard limits, or integration overload.
7. **Reconcile:** collect results, close sessions, release workspaces, and report final counts.

## Requirements for a separate high-volume scheduler

If a separately commissioned external runtime ever targets hundreds of sessions, it should support:
- one global concurrency gate across nested supervisors;
- per-provider, per-model, and per-user quotas;
- priority queues and dependency-aware dispatch;
- leases and heartbeats for worker liveness;
- idempotency keys to prevent duplicate execution;
- bounded retries with exponential backoff and jitter;
- cancellation propagation through the full hierarchy;
- stale-session detection and orphan cleanup;
- deadlines, token and cost budgets;
- rate-limit-aware admission and fair scheduling;
- durable state and recovery after coordinator restart.

These are requirements for that hypothetical companion runtime, not capabilities shipped in the Skill.

## When to stop expanding

Stop when workers duplicate one another, provider calls are throttled, integration becomes the bottleneck, edit conflicts rise, cost exceeds expected value, or useful throughput no longer improves. The goal is verified progress, not the highest possible session count.

## Acceptance test for a real 500-agent claim

A production claim requires repeatable evidence of:
- 500 distinct sessions admitted concurrently, not queued;
- worker heartbeats and observable status;
- measured provider/workspace utilization;
- correct completion, timeout, crash, retry, and cancellation behavior;
- isolation between worker workspaces and task data;
- no cross-task secret or file leakage;
- deterministic result collection and cleanup;
- measured cost, latency, error rate, and useful throughput;
- compliance with provider and workspace limits.

Until these tests pass, call 500 a design ambition, not an achieved capability.
