"""ClawBot basic integration tests: verify imports and version."""

import pytest


def test_import_vulnclaw():
    """Test that the main package can be imported."""
    from pathlib import Path

    import tomllib

    import clawbot

    # Read version from pyproject.toml to avoid hardcoding
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    expected_version = pyproject["project"]["version"]

    assert clawbot.__version__ == expected_version


def test_all_submodules_importable():
    """Test that all major submodules can be imported."""


def test_no_import_errors():
    """Verify no module raises on import."""
    import importlib
    import importlib.util

    modules = [
        "clawbot",
        "clawbot.config.schema",
        "clawbot.config.settings",
        "clawbot.agent.context",
        "clawbot.agent.memory",
        "clawbot.agent.prompts",
        "clawbot.agent.core",
        "clawbot.mcp.registry",
        "clawbot.mcp.router",
        "clawbot.mcp.lifecycle",
        "clawbot.skills.loader",
        "clawbot.skills.dispatcher",
        "clawbot.kb.store",
        "clawbot.kb.retriever",
        "clawbot.kb.updater",
        "clawbot.report.generator",
        "clawbot.report.poc_builder",
    ]
    if importlib.util.find_spec("typer") is not None:
        modules.append("clawbot.cli.main")

    for mod_name in modules:
        try:
            importlib.import_module(mod_name)
        except ImportError as e:
            pytest.fail(f"Failed to import {mod_name}: {e}")
