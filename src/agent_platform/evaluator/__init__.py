"""Evaluator: a deterministic verdict from execution evidence.

Must not: call the model provider. Success is decided only from exit codes,
parsed test reports, baseline comparison, and protected-file integrity.
"""
