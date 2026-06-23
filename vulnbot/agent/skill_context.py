"""Skill context selection helpers for AgentCore."""

from __future__ import annotations

from typing import Optional


def get_active_skill_context(user_input: Optional[str] = None) -> Optional[str]:
    """Get context from the most relevant Skill based on user input."""
    if user_input:
        try:
            from vulnbot.skills.dispatcher import SkillDispatcher

            dispatcher = SkillDispatcher()
            skill = dispatcher.dispatch(user_input)
            if skill:
                context = skill.get("content", "")
                refs = skill.get("references", [])
                if refs:
                    ref_list = ", ".join(refs[:10])
                    if len(refs) > 10:
                        ref_list += f", ... ({len(refs)} total)"
                    context += f"\n\n## Available Reference Documents\nThese references can be loaded with load_skill_reference when needed: {ref_list}"
                return context
        except Exception:
            pass

    try:
        from vulnbot.skills.loader import load_skill_by_name

        skill = load_skill_by_name("pentest-flow")
        if skill:
            return skill.get("content", "")
    except Exception:
        pass
    return None
