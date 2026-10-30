"""Sandbox runner: executes commands in ephemeral, hardened containers.

Must not: bind-mount host directories, pass host environment variables, or
expose the Docker socket to the container. See docs/security.md.
"""
