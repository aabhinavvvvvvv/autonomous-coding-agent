# ADR-003: PostgreSQL as the job queue instead of BullMQ/Redis

- **Status:** Accepted for the MVP
- **Date:** 2026-10-29

## Context

Agent runs are submitted through the API and executed by a separate worker.
We need durable hand-off, exactly-one worker per run, detection of crashed
workers, and status visibility. The developer previously used BullMQ + Redis
for an uptime monitor with many small, scheduled, repeatable jobs.

This workload differs: low volume (runs per minute), long jobs (minutes), and
run state (status, events, attempts) must live in Postgres anyway for history
and replay.

## Alternatives considered

1. **BullMQ + Redis.** Mature retries, delayed/repeatable jobs, rate limiting,
   and fast pub/sub. But job state then lives in Redis while run state lives in
   Postgres: every transition is a dual write, and a crash between the two
   leaves them inconsistent ("queue says completed, DB says running").
2. **In-process background tasks.** No durability; runs lost on restart.
3. **Postgres-backed queue** (chosen): workers claim runs with
   `SELECT … FOR UPDATE SKIP LOCKED`, hold a lease (`locked_by`,
   `heartbeat_at`), and a reaper marks runs with expired leases `WORKER_LOST`.

## Decision

Use Postgres as both the source of truth and the queue, behind a small
`JobQueue` interface so the implementation can change later.

## Consequences

- One store, transactional state changes, no dual-write inconsistency.
- No extra infrastructure to run, monitor, or secure.
- We implement leasing and reaping ourselves (a deliberate learning goal).
- Polling adds small pick-up latency; fine at this volume.

## Revisit when

- Several worker hosts must share a model-provider rate limit.
- Delayed or scheduled jobs are needed (e.g. nightly benchmark runs).
- Live progress must fan out to many browser connections (Redis pub/sub).
