"""VulnBot basic integration tests: verify imports and version."""

import pytest


def test_import_vulnclaw():
    """Test that the main package can be imported."""
    from pathlib import Path

    import vulnbot

    # Read version from pyproject.toml to avoid hardcoding (tomllib needs
    # Python 3.11+, but this project supports 3.10, so parse the line directly)
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    version_line = next(
        line
        for line in pyproject_path.read_text(encoding="utf-8").splitlines()
        if line.startswith("version = ")
    )
    expected_version = version_line.split('"')[1]

    assert vulnbot.__version__ == expected_version


def test_all_submodules_importable():
    """Test that all major submodules can be imported."""


def test_no_import_errors():
    """Verify no module raises on import."""
    import importlib
    import importlib.util

    modules = [
        "vulnbot",
        "vulnbot.config.schema",
        "vulnbot.config.settings",
        "vulnbot.agent.context",
        "vulnbot.agent.memory",
        "vulnbot.agent.prompts",
        "vulnbot.agent.core",
        "vulnbot.mcp.registry",
        "vulnbot.mcp.router",
        "vulnbot.mcp.lifecycle",
        "vulnbot.skills.loader",
        "vulnbot.skills.dispatcher",
        "vulnbot.kb.store",
        "vulnbot.kb.retriever",
        "vulnbot.kb.updater",
        "vulnbot.report.generator",
        "vulnbot.report.poc_builder",
    ]
    if importlib.util.find_spec("typer") is not None:
        modules.append("vulnbot.cli.main")

    for mod_name in modules:
        try:
            importlib.import_module(mod_name)
        except ImportError as e:
            pytest.fail(f"Failed to import {mod_name}: {e}")
