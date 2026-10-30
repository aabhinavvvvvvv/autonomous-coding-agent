"""Autonomous coding agent platform.

A modular monolith: one codebase, deployed as an API process and a worker
process. Untrusted generated code never runs in either process; it runs only
inside ephemeral sandbox containers created by the ``runner`` component.
See docs/architecture.md for component boundaries.
"""

from importlib.metadata import version

__version__ = version("agent-platform")
