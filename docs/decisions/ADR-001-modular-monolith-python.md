# ADR-001: Modular monolith in Python, deployed as API + worker

- **Status:** Accepted
- **Date:** 2026-10-29

## Context

The platform needs an HTTP API, a long-running agent workflow (minutes per
run), a sandbox runner, persistence, and later a web UI. It is built by one
developer as a learning-focused portfolio project. Agent runs cannot execute
inside an HTTP request, and the component that controls Docker is
root-equivalent on its host.

## Alternatives considered

1. **Microservices** (separate API, orchestrator, runner services). Independent
   scaling and deployment, but network contracts, distributed failure modes,
   and operational overhead without any current scaling need.
2. **Single process** (API runs agent work in background tasks). Simplest, but
   a crash loses in-flight runs, and Docker privileges would sit in the
   internet-facing process.
3. **Modular monolith, two processes** (chosen).

Language: **TypeScript/Node** (the developer's most familiar stack) vs
**Python**. Python offers the official Docker SDK, Pydantic for validating both
API input and model output, a first-class Anthropic SDK, and strong relevance to
AI-engineering roles. The cost is a less familiar production ecosystem and
opt-in typing.

## Decision

One Python 3.12 package, `agent_platform`, with sub-packages per component
(`api`, `worker`, `orchestrator`, `llm`, `workspace`, `runner`, `evaluator`,
`db`), deployed as an **API process** and a **worker process**. Strict mypy is
enabled from the start to compensate for opt-in typing. The web UI (Milestone 5)
uses React + TypeScript.

## Consequences

- One repository, one test suite, simple refactoring across components.
- The API stays low-privilege; only the worker holds Docker access.
- Boundaries are enforced by convention, docstrings, and tests rather than by
  network separation; the `runner` interface allows moving execution to a
  separate host later.
- The trust boundary for generated code is the **container**, not the language.
  The platform must never import or evaluate workspace code in-process.
