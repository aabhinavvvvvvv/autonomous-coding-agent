# Security

> Status: **threat model and planned controls**. No code execution exists yet
> (Milestone 0). Nothing here is claimed as implemented until the roadmap marks
> it done with passing security tests.

## Why this matters

The platform executes code written by a language model, influenced by
repository content we do not control. That code is **untrusted**: it may be
buggy, resource-hungry, or deliberately malicious (e.g. via prompt injection).

## Assets

- Host / WSL filesystem.
- Secrets: model API key, database credentials.
- The Docker daemon (root-equivalent on its host).
- Other runs' workspaces and history.
- Host CPU, memory, disk.
- Third parties on the internet (we must not be an attack source).

## Threats

1. **Malicious or runaway code:** fork bombs, memory exhaustion, infinite loops,
   disk filling, network exfiltration, container escape.
2. **Prompt injection:** instructions hidden in task text, source files,
   comments, or test output that try to redirect the agent.
3. **Unsafe file operations:** `../` traversal, absolute paths, symlinks out of
   the workspace.
4. **Output attacks:** huge or crafted stdout/stderr that floods storage or the
   next prompt.
5. **Evaluation gaming:** the agent deleting, skipping, or rewriting tests to
   fake success.

## Planned controls

### Sandbox container (per execution, Milestone 1)

| Control | Setting |
|---|---|
| Network | `network_mode="none"` |
| User | non-root `65534:65534` |
| Privileges | drop all capabilities; `no-new-privileges`; **explicit** seccomp profile; never privileged |
| Filesystem | read-only root; `/workspace` and `/tmp` as size-limited tmpfs; files copied in by archive — **no host bind mounts** |
| Resources | memory 256 MiB (swap = memory), 1 CPU, PID limit 64, file-size/open-file ulimits |
| Time | orchestrator-enforced deadline; container killed; result flagged `timed_out` |
| Output | streamed and capped per stream; flagged `truncated` |
| Environment | empty; no secrets; Docker socket never mounted |
| Image | built by us, pinned by digest, dependencies pre-installed; no runtime installs |
| Cleanup | removal in `finally` + reaper for labelled orphan containers |

### Outside the sandbox

- Path validation in `workspace`: resolve against the run root; reject absolute
  paths, `..`, and symlinks; deny writes to protected paths (existing tests).
- The worker never imports or evaluates workspace files or model output as code.
- Untrusted content enters prompts inside clearly delimited data blocks. The
  primary defence against prompt injection is **capability limiting**: a
  hijacked model can only write files into a throw-away copy that runs with no
  network and no secrets.
- Deterministic evaluator with protected-file hashes and baseline comparison.

## Known limitations (honest)

- **Shared kernel.** Containers share the Linux kernel with the WSL VM that
  also runs our worker, database, and secrets. A kernel exploit could escape.
  Hardening reduces attack surface; it does not remove this risk.
- **gVisor not available.** A user-space kernel (gVisor `runsc`) would add a
  strong layer, but it is not practical on Docker Desktop, which this
  environment uses. Revisit if moving to native Docker Engine or a Linux host.
- **Privileged worker.** Docker API access is root-equivalent. A compromised
  worker compromises the WSL VM. Hence: no in-process execution of model output.
- **Scope.** This design targets local development use. A public multi-user
  service would need VM-level isolation (Firecracker/gVisor) on separate runner
  hosts, plus authentication and tenant isolation.

## Environment observations (verified 2026-10-29)

On this machine (Docker Desktop 28.1.1, reached from WSL):

- `docker info` reports `seccomp, profile=unconfined` and cgroup v1, yet a
  default container reports `Seccomp: 2` (a filter **is** active). The summary
  and the reality disagree, so the runner will pass an explicit profile and the
  test suite will verify blocked syscalls rather than trust configuration output.
- A manual smoke container with the planned flags showed: uid 65534, all
  effective capabilities 0, `NoNewPrivs: 1`, read-only root (`touch /x` failed),
  no network (DNS lookup failed). This was a one-off probe, not an automated test.

## How controls will be verified (Milestone 1)

An automated malicious-fixture suite, run against the real sandbox, asserting:
outbound network fails; writes outside `/workspace` and `/tmp` fail; a fork bomb
hits the PID limit; a 1 GiB allocation is OOM-killed and categorised; an
infinite loop is killed at the deadline; 50 MB of output is truncated; `env`
contains no secrets; the process is non-root; `/var/run/docker.sock` is absent;
no containers are left behind. Path-traversal and symlink cases get unit tests
in Milestone 2.
