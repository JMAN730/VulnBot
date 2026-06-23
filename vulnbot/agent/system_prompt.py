"""Dynamic system prompt assembly for AgentCore."""

from __future__ import annotations

from typing import Optional

from vulnbot.agent.prompts import AUTO_PENTEST_INSTRUCTION, RECON_INSTRUCTION, build_system_prompt


def build_dynamic_system_prompt(
    *,
    target: Optional[str],
    phase: Optional[str],
    skill_context: Optional[str],
    mcp_tools: list[dict],
    enable_personnel_dim: bool,
    auto_mode: bool,
    user_input: Optional[str],
    kb_context: str,
) -> str:
    """Build the dynamic system prompt for one turn."""
    prompt = build_system_prompt(
        target=target,
        phase=phase,
        skill_context=skill_context,
        mcp_tools=mcp_tools,
        enable_personnel_dim=enable_personnel_dim,
    )

    if auto_mode:
        prompt += "\n\n" + AUTO_PENTEST_INSTRUCTION

    if user_input:
        recon_triggers = [
            "collect",
            "information gathering",
            "recon",
            "reconnaissance",
            "osint",
            "social engineering",
            "investigate",
            "author",
            "person",
            "intelligence",
            "analyze target",
            "target analysis",
            "asset discovery",
            "subdomain",
        ]
        if any(trigger in user_input.lower() for trigger in recon_triggers):
            recon_instruction = RECON_INSTRUCTION
            if not enable_personnel_dim:
                recon_instruction = recon_instruction.replace(
                    "### Dimension 4: Personnel Information (conditional)",
                    "### Dimension 4: Personnel Information (inactive - no personnel request)",
                )
                recon_instruction = (
                    recon_instruction.replace(
                        "- [ ] Names and roles",
                        "- [x] Names and roles (inactive, skipped)",
                    )
                    .replace(
                        "- [ ] Birthdays and phone numbers",
                        "- [x] Birthdays and phone numbers (inactive, skipped)",
                    )
                    .replace(
                        "- [ ] Email addresses",
                        "- [x] Email addresses (inactive, skipped)",
                    )
                    .replace(
                        "- [ ] Social media accounts",
                        "- [x] Social media accounts (inactive, skipped)",
                    )
                    .replace(
                        "- [ ] Cross-platform correlation",
                        "- [x] Cross-platform correlation (inactive, skipped)",
                    )
                )
            prompt += "\n\n" + recon_instruction

    if kb_context:
        prompt += "\n\n" + kb_context

    return prompt
