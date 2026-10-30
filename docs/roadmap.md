# Roadmap

## Session handoff (read this first in a new chat)

- **Last updated:** 2026-10-30
- **Current milestone:** M0 — Foundation. Complete: committed, pushed, CI green.
- **Repo state:** branch `main` tracks `origin` =
  https://github.com/aabhinavvvvvvv/autonomous-coding-agent (public).
- **Next step:** plan M1 (sandbox runner) — explain concepts and design, agree
  acceptance criteria, then implement. Do not start M1 without user approval.
- **Environment notes:** run all tooling inside WSL (see docs/development.md).
  Docker Desktop is reachable from WSL; see docs/security.md for verified
  seccomp/cgroup observations.
- **Open decisions:** model provider and API key (needed by M3; tests use a
  fake provider).
- **Follow-ups:** CI warns that `actions/checkout@v4` and `astral-sh/setup-uv@v6`
  target the deprecated Node.js 20 runtime; bump to current major versions.

## Milestones

Each milestone ends with: checks passing, diff review, secret scan, docs
updated, and a commit after user approval.

### M0 — Foundation ✅

- Git, `.gitignore`, `.gitattributes`, `.env.example`.
- uv project, ruff (with security rules), strict mypy, pytest.
- Package skeleton with one documented sub-package per component.
- GitHub Actions CI; docs skeleton; ADR-001..003.

**Acceptance:** `ruff check`, `ruff format --check`, `mypy`, and `pytest` pass
inside WSL. CI passes on GitHub once a remote exists.

**Verified 2026-10-29:** all four local checks pass (9 tests). The structure
test was shown to fail when a component's docstring is removed.
**Verified 2026-10-30:** CI run 41044049927 on GitHub passed the same four
checks (9 tests) on commit `2f81608`.

### M1 — Sandbox runner (next)

Standalone: no LLM, no database.

- Sandbox image (Python + pytest, pinned) and `Runner.execute(files, command, limits)`.
- Hardened container configuration (see docs/security.md).
- JUnit XML result parsing; error taxonomy (TIMEOUT, OOM, ...).
- Output capping, deadline enforcement, guaranteed cleanup.

**Acceptance:** the malicious-fixture suite passes against the real sandbox;
no container survives any test, including timeouts.
**Learn:** namespaces, cgroups, capabilities, seccomp, threat modelling.

### M2 — Workspace, file tools, evaluator

- 2–3 buggy Python fixture projects; per-run copies.
- Path-safe list/read/write; protected-file policy; diff generation.
- Deterministic evaluator with baseline and tamper detection.

**Acceptance:** traversal/symlink tests pass; evaluator rejects a deleted test,
a modified protected file, and a regression.
**Learn:** filesystem security, defining success rigorously.

### M3 — Model adapter and orchestrator (CLI-driven)

- Provider-neutral `ModelProvider`; `FakeProvider`; one real adapter.
- State machine, budgets, no-progress detection, schema-validated outputs.

**Acceptance (fake provider):** pass first try; pass on retry; budget
exhausted; no-progress stop; malformed output; provider outage → ERRORED.
**Real provider:** record the actual fix rate on fixtures (no claimed numbers).
**Learn:** state machines, structured outputs, prompt design, prompt injection.

### M4 — Persistence, API, worker

- Schema + Alembic migrations; REST API (`POST/GET /runs`, `GET /runs/{id}`,
  `GET /runs/{id}/events`, `POST /runs/{id}/cancel`, `GET /workspaces`,
  `/health`, `/ready`).
- Worker claiming via `SKIP LOCKED`, heartbeat lease, lost-worker reaper.

**Acceptance:** API tests for valid/invalid input; submit → worker → done
integration test; killed worker → `WORKER_LOST`; two workers never claim the
same run.
**Learn:** REST design, transactions, locking, idempotency, queue semantics.

### M5 — Minimal web UI → MVP complete

React + TypeScript + Vite: task form, run list, run detail (timeline, diffs,
logs, final report). Polling for updates.

### M6 — Observability and agent benchmark

Metrics (success rate, p50/p95 latency, error categories, tokens), log
correlation, and a benchmark that runs the agent across all fixtures.

### Later (not scheduled)

Live updates (SSE), Monaco diff view, gVisor or VM isolation, BullMQ/Redis if a
trigger in ADR-003 appears, real repository import, more languages, tool-using
(ReAct) agent loop, authentication.
