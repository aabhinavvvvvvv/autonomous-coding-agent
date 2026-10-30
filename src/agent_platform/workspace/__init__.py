"""Run workspaces: per-run copies of a project and path-safe file operations.

Must not: follow symlinks, accept absolute or parent-relative paths, write
outside the run's root, or modify protected files such as existing tests.
"""
