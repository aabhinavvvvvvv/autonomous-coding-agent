# Architecture

> Status: **design**. Only the package skeleton exists (Milestone 0). Sections
> below describe the planned system; the roadmap tracks what is implemented.

## Goals

**Functional:** accept a coding task for a controlled workspace; gather context;
plan; edit files; run tests in an isolated sandbox; evaluate from real evidence;
make bounded correction attempts; report and record everything.

**Non-functional:** untrusted code is isolated from the platform; every run is
bounded (attempts, tokens, wall-clock time, output size); every step is
observable and replayable; the model provider is replaceable; agent logic is
testable without network access or model cost.

## Shape: a modular monolith, two processes

One Python codebase (`src/agent_platform`), deployed as:

- **API process** — serves HTTP. Low privilege: talks only to Postgres.
- **Worker process** — claims queued runs and executes the agent workflow.
  Holds Docker access, so it is the most privileged component.

Generated code runs only in **ephemeral sandbox containers** created per
execution. See [ADR-001](decisions/ADR-001-modular-monolith-python.md).

```
Browser ──► API (FastAPI) ──INSERT run──► PostgreSQL ◄──claim/heartbeat/events── Worker
                                         (state + queue)                          │
                                                                                  ├─ Orchestrator (state machine)
                                                                                  ├─ LLM adapter (Claude | Fake)
                                                                                  ├─ Workspace (path-safe file ops)
                                                                                  ├─ Evaluator (deterministic)
                                                                                  └─ Runner ──Docker API──► sandbox container
                                                                                                           (untrusted code)
```

## Components and boundaries

Dependencies point toward pure logic. The orchestrator depends on interfaces,
not on HTTP, the DB driver, or the Docker SDK.

| Package | Responsibility | Must not |
|---|---|---|
| `api` | HTTP, validation, history/metrics queries | Execute code, call the LLM, touch Docker |
| `worker` | Claim jobs, run orchestrator, heartbeat | Run generated code in-process |
| `orchestrator` | State machine, budgets, stop conditions | Depend on HTTP/DB driver/Docker directly |
| `llm` | Provider-neutral model interface + implementations | Leak provider SDK types |
| `workspace` | Per-run copies, path-safe read/list/write, diffs | Follow symlinks, escape the root, edit protected files |
| `runner` | Execute a command in a hardened container | Bind-mount host dirs, pass host env, expose Docker socket |
| `evaluator` | Verdict from execution evidence | Call the LLM |
| `db` | Schema, migrations, repositories | — |

## Run lifecycle (planned state machine)

```
QUEUED → PREPARING → BASELINE → CONTEXT → PLANNING → EDITING → EXECUTING → EVALUATING
  EVALUATING ─pass─► REPORTING → SUCCEEDED
  EVALUATING ─fail, budget left, progress─► DIAGNOSING → EDITING (next attempt)
  EVALUATING ─fail, otherwise─► REPORTING → FAILED
  any ─infrastructure error─► ERRORED       any ─cancel / deadline─► CANCELLED / TIMED_OUT
```

- **BASELINE** runs the tests before any edit, so the evaluator can detect
  regressions and removed tests.
- **FAILED** (the code is still wrong) is distinct from **ERRORED** (our
  infrastructure failed: model outage, Docker down, worker lost).

### Evaluator success criteria (all required)

1. Sandbox exit code 0; no timeout; no OOM kill.
2. JUnit report parses; ≥ 1 test; 0 failures; 0 errors.
3. Protected test files unchanged (hash check); collected test count ≥ baseline.
4. No regressions: tests passing at baseline still pass.

### Budgets and stop conditions

Max correction attempts (default 3), max model calls and tokens, run wall-clock
deadline, per-execution timeout, max files changed and bytes per file, and
**no-progress detection** (same failure signature twice in a row → stop).

## Persistence (planned, Milestone 4)

| Table | Purpose |
|---|---|
| `workspaces` | Fixture metadata |
| `runs` | Task, status, failure reason, budgets, lease (`locked_by`, `heartbeat_at`) |
| `run_events` | Append-only timeline; unique `(run_id, seq)`; drives UI and replay |
| `attempts` / `file_changes` | Per-attempt plan and diffs |
| `executions` | Exit code, duration, timeout/OOM flags, truncated output, test counts, error category |
| `llm_calls` | Purpose, model, tokens, latency, status |

Postgres is also the job queue (`SELECT … FOR UPDATE SKIP LOCKED` + heartbeat
lease). See [ADR-003](decisions/ADR-003-postgres-job-queue.md).

## Observability (planned)

- Structured JSON logs (structlog) correlated by `run_id`.
- Metrics derived from SQL: run success rate, p50/p95 execution and model
  latency, error-category counts, tokens per run.
- `/health` (process alive) and `/ready` (DB, Docker daemon, sandbox image,
  model configuration).

## Technology choices

| Concern | Choice |
|---|---|
| Language | Python 3.12, strict mypy |
| Packaging | uv |
| API | FastAPI + Pydantic v2 |
| DB | PostgreSQL, SQLAlchemy 2.0, Alembic |
| Sandbox | Docker SDK for Python, hardened containers |
| Quality | ruff, mypy, pytest, GitHub Actions |
| UI | React + TypeScript + Vite (Milestone 5) |
