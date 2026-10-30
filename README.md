# Autonomous Coding Agent

An autonomous coding agent and code-evaluation platform. Give it a coding task
for a project workspace; it inspects the code and tests, plans, edits files,
runs the tests in an isolated sandbox, judges the result from **real execution
evidence**, makes a bounded number of correction attempts, and records every
step for review and replay.

> The agent's own claim of success is never treated as proof. Only
> deterministic checks on actual test results count.

## Current status

**Milestone 0 — Foundation.** The repository skeleton, tooling, CI workflow,
and design documents exist. **No agent, sandbox, API, or database functionality
is implemented yet.** See [docs/roadmap.md](docs/roadmap.md) for progress and
the session handoff.

## Planned MVP

- Controlled Python/pytest fixture workspaces (each run works on its own copy).
- Bounded workflow: plan → edit → execute in sandbox → evaluate → up to N corrections.
- Hardened, network-less, non-root, resource-limited Docker sandbox per execution.
- Deterministic evaluator with test-tampering detection.
- Run history, event timeline, per-attempt diffs and logs, operational metrics.
- Minimal React UI.

## Architecture (summary)

A modular monolith in Python, deployed as two processes — an **API** (FastAPI)
and a **worker** — with PostgreSQL as the source of truth and job queue.
Generated code runs only in ephemeral sandbox containers. Details:
[docs/architecture.md](docs/architecture.md), security model:
[docs/security.md](docs/security.md), decisions: [docs/decisions/](docs/decisions/).

## Quick start (development)

Requires WSL/Linux, Python 3.12, and [uv](https://docs.astral.sh/uv/).
Run all commands **inside WSL**, not from Windows — see
[docs/development.md](docs/development.md).

```bash
uv sync                      # create .venv and install dev tools
uv run ruff check .          # lint
uv run ruff format --check . # formatting
uv run mypy                  # strict type check
uv run pytest                # tests
```

## Documentation

| File | Purpose |
|---|---|
| [docs/architecture.md](docs/architecture.md) | Components, boundaries, data flow |
| [docs/roadmap.md](docs/roadmap.md) | Milestones, acceptance criteria, session handoff |
| [docs/security.md](docs/security.md) | Threat model, sandbox controls, known limits |
| [docs/development.md](docs/development.md) | Setup, commands, workflow |
| [docs/learning-log.md](docs/learning-log.md) | Concepts and lessons learned |
| [docs/decisions/](docs/decisions/) | Architecture decision records |
