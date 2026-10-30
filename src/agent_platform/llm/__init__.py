"""Model provider adapter: a provider-neutral interface plus implementations.

Must not: leak provider SDK types to callers. Model output is untrusted data
and is validated against a schema before the orchestrator acts on it.
"""
