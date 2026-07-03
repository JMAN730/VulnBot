"""Tests for the Textual TUI slash-command handlers."""

from __future__ import annotations

import pytest

pytest.importorskip("textual")

import vulnbot.cli.tui_textual as tui_textual  # noqa: E402
from vulnbot.skills.dispatcher import SkillDispatcher  # noqa: E402


def test_textual_skills_command_opens_list_view():
    session: dict = {}
    result = tui_textual._dispatch(session, "/skills")

    assert result is None
    assert session["_view"] == ("skills_list", None)


def test_textual_skills_command_opens_detail_view_for_known_skill():
    skills = SkillDispatcher().list_all_skills()
    assert skills, "expected at least one built-in skill"
    name = skills[0]["name"]

    session: dict = {}
    tui_textual._dispatch(session, f"/skills {name}")

    kind, skill = session["_view"]
    assert kind == "skill_detail"
    assert skill["name"] == name


def test_textual_skills_command_reports_unknown_skill():
    session: dict = {}
    tui_textual._dispatch(session, "/skills definitely-not-a-real-skill")

    assert session.get("_view") is None
    assert "definitely-not-a-real-skill" in session["_message"]


def test_textual_skills_registered_in_shared_palette():
    assert "skills" in tui_textual._tui.SLASH_COMMANDS
    assert "skills" in tui_textual._SLASH_HANDLERS
