"""Persistence: schema, migrations, and repositories for runs and their history.

Postgres is the single source of truth for run state and also serves as the
job queue (see docs/decisions/ADR-003-postgres-job-queue.md).
"""
