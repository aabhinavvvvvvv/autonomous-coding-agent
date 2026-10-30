# Learning Log

## 2026-10-29 — Planning and Milestone 0

### The core principle: the LLM proposes, the system verifies
An agent saying "fixed it" is a claim, not evidence. Success is decided by
deterministic code reading exit codes and parsed test reports. An LLM judge
can misread output or be manipulated by text inside it (a test can print
"ALL TESTS PASSED" and then crash).

### Evaluation gaming
If the agent can edit tests, it can "pass" by deleting a test or changing an
expected value to match buggy output. Defences: hash protected test files,
compare the collected test count to a baseline run, and check for regressions.
Hashes cannot tell a legitimate test edit from a cheat, so for the MVP existing
tests are read-only; serious benchmarks use hidden reference tests.

### Why Postgres instead of BullMQ/Redis (for now)
BullMQ fit the uptime monitor: many small, scheduled, repeatable jobs. Here,
jobs are few and long-running, and run state must live in Postgres anyway. Two
stores means dual writes ("queue says done, DB says running"). One source of
truth with `SKIP LOCKED` + heartbeats avoids that. See ADR-003.

### Verify, don't trust configuration output
`docker info` said seccomp was `unconfined`, but `/proc/self/status` inside a
container showed `Seccomp: 2` (filter active). Security properties must be
tested from inside the sandbox, not inferred from a summary.

### A test must be seen failing
A new test that has only ever passed proves little. We emptied one component's
docstring, watched the structure test fail, then restored it.

### Debugging: shell variables through `wsl.exe`
`wsl.exe ... bash -lc '... f=x && cp $f ...'` failed with a syntax error:
`$f` was expanded to empty by an outer shell before WSL's bash ran. Lesson:
when a command passes through more than one shell, each layer may interpret
`$`, quotes, and escapes. Use literal paths or a script file.

### Line endings across Windows and Linux
`.gitattributes` with `* text=auto eol=lf` prevents CRLF conversions that cause
whole-file diffs and break shell scripts inside Linux containers.

### Lockfiles
`uv.lock` pins exact versions of every dependency (including transitive ones).
CI runs `uv sync --locked`, which fails if the lockfile is stale, so CI tests
the same versions as local development.

## Open questions
- Which model provider for the first real adapter (M3)?
- Is gVisor worth moving from Docker Desktop to native Docker Engine later?
