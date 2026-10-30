# ADR-002: Hardened ephemeral Docker containers as the execution sandbox

- **Status:** Accepted (implementation in Milestone 1)
- **Date:** 2026-10-29

## Context

The platform runs code produced by a language model and influenced by
repository content we do not control. It must not affect the host, read
secrets, reach the network, exhaust resources, or persist between executions.
The development environment is Windows + WSL2 with Docker Desktop.

## Alternatives considered

| Option | Isolation | Cost / fit |
|---|---|---|
| Subprocess in the worker | None meaningful | Unacceptable: shares the worker's privileges and secrets |
| Judge0 / hosted executor | Good | Hides the threat model we want to understand and own |
| nsjail / bubblewrap | Good, low overhead | Linux-specific tooling; less common; harder to explain in a portfolio |
| Firecracker microVMs | Strong (separate kernel) | Heavy setup; impractical under WSL2 for this stage |
| gVisor (`runsc`) | Strong (user-space kernel) | Not practical on Docker Desktop |
| **Hardened Docker containers** | Moderate (shared kernel) | Available now, well understood, enforceable limits |

## Decision

Each execution runs in a fresh container: no network, non-root user, all
capabilities dropped, `no-new-privileges`, an explicit seccomp profile,
read-only root filesystem, size-limited tmpfs for `/workspace` and `/tmp`,
memory/CPU/PID limits, a deadline enforced by the orchestrator, capped output,
an empty environment, no host bind mounts, and no Docker socket. Files are
copied in and out by archive. Full table in docs/security.md.

## Consequences

- Strong protection against resource abuse, network exfiltration, and casual
  filesystem damage; every control is testable from inside the container.
- **Shared-kernel risk remains:** a kernel exploit could escape into the WSL VM.
  Documented as a known limitation; stronger isolation (gVisor or microVMs on
  dedicated hosts) is required before any multi-user deployment.
- Container start-up adds latency (hundreds of ms) per execution; acceptable
  for the MVP and measured in Milestone 6.
- Security claims are made only for controls covered by automated tests.
