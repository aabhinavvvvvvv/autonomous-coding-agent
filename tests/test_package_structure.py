"""Guards the modular-monolith layout described in docs/architecture.md."""

import importlib
import tomllib
from pathlib import Path

import pytest

import agent_platform

PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"

COMPONENTS = [
    "api",
    "worker",
    "orchestrator",
    "llm",
    "workspace",
    "runner",
    "evaluator",
    "db",
]


def test_installed_version_matches_pyproject() -> None:
    declared = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]["version"]

    assert agent_platform.__version__ == declared


@pytest.mark.parametrize("component", COMPONENTS)
def test_component_is_importable_and_documents_its_boundary(component: str) -> None:
    module = importlib.import_module(f"agent_platform.{component}")

    assert module.__doc__, f"agent_platform.{component} must document its responsibility"
