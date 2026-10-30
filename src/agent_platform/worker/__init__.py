"""Worker process: claims queued runs, drives the orchestrator, sends heartbeats.

Must not: run generated code in its own process, or import files from a run
workspace. It holds Docker access, so it is the most privileged component.
"""
