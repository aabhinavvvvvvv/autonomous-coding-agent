# Development

## Environment

- **Run everything inside WSL** (Ubuntu 24.04), not from Windows. The repo lives
  at `\\wsl.localhost\Ubuntu-24.04\home\...`; Windows-native tooling is
  unreliable on UNC paths, and a `.venv` created from Windows contains Windows
  binaries that do not work under Linux (and vice versa).
- From a Windows terminal, prefix commands with
  `wsl.exe -d Ubuntu-24.04 -- bash -lc '...'`, or open a WSL shell.
- When passing commands through `wsl.exe`, avoid shell variables (`$x`) in the
  command string: they can be expanded by the outer shell before WSL sees them.

### Prerequisites

| Tool | Used for | Needed from |
|---|---|---|
| Python 3.12 | Platform code | M0 |
| [uv](https://docs.astral.sh/uv/) | Virtual env, dependencies, lockfile | M0 |
| Docker (Desktop with WSL integration enabled) | Sandbox runner | M1 |
| PostgreSQL | Persistence and job queue | M4 |
| Node.js 22 | Web UI | M5 |

## Setup

```bash
cd ~/personal_projects/Autonomous_Coding_Agent
uv sync          # creates .venv and installs locked dev dependencies
cp .env.example .env   # only needed from Milestone 1 onward; never commit .env
```

## Checks (same as CI)

```bash
uv run ruff check .          # lint (includes bandit security rules)
uv run ruff format --check . # formatting; `uv run ruff format .` to fix
uv run mypy                  # strict type checking of src/ and tests/
uv run pytest                # tests
```

## Dependencies

- Add runtime deps with `uv add <pkg>`, dev-only tools with `uv add --dev <pkg>`.
- Add a dependency only in the milestone that first needs it.
- Commit `uv.lock`: it pins exact versions so local runs and CI match.

## Workflow

1. Check `git status` and the branch before changing anything.
2. Small, reviewable changes; run all checks before committing.
3. Review the diff and scan for secrets before every commit.
4. Conventional commit messages: `feat:`, `fix:`, `test:`, `docs:`, `chore:`.
5. Update `docs/roadmap.md` (including the session handoff) at each milestone.
