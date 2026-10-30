"""HTTP API: request validation, run submission, history and metrics queries.

Must not: execute code, call the model provider, or talk to Docker. It only
reads and writes the database; the worker does all agent work.
"""
