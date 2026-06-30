"""Prompt/round-context helpers for AgentCore."""

from __future__ import annotations

from typing import Any


def _render_recon_assets(recon_data: dict[str, Any], limit: int = 10) -> str:
    """Render concrete restored recon assets for the round prompt."""
    lines: list[str] = []

    services = recon_data.get("network_services")
    if isinstance(services, list) and services:
        rendered = []
        for item in services[:limit]:
            if isinstance(item, dict):
                port = item.get("port", "?")
                name = item.get("service", item.get("name", ""))
                rendered.append(f"{port}/{name}".rstrip("/"))
            else:
                rendered.append(str(item))
        lines.append(f"  - Open services: {', '.join(rendered)}")

    for category, label in (("subdomains", "Subdomains"), ("paths", "Paths"), ("params", "Params")):
        values = recon_data.get(category)
        if isinstance(values, list) and values:
            shown = ", ".join(str(v) for v in values[:limit])
            lines.append(f"  - {label}: {shown}")

    return "\n".join(lines)


def build_round_context(agent: Any, round_num: int, max_rounds: int) -> str:
    """Build the context string for the current autonomous loop round."""
    state = agent.context.state
    constraints_block = (
        state.get_constraints_prompt_block()
        if hasattr(state, "get_constraints_prompt_block")
        else ""
    )
    constraints_summary = f"\n\n{constraints_block}" if constraints_block else ""

    findings_summary = ""
    if state.findings:
        findings_summary = f"\nFindings discovered: {len(state.findings)}"
        for finding in state.findings[-5:]:
            findings_summary += (
                f"\n  - [{finding.severity}] {finding.title}: {finding.evidence[:100]}"
            )

    user_hint_directive = ""
    if round_num <= agent.runtime.user_vuln_hint_rounds and agent.runtime.user_vuln_hint:
        user_hint_directive = (
            f"\n\n{'=' * 50}\n"
            f"[Explicit user hint - round {round_num}/{agent.runtime.user_vuln_hint_rounds}]\n"
            f"{agent.runtime.user_vuln_hint}\n"
            f"{'=' * 50}\n"
        )
        agent.runtime.user_vuln_hint_rounds -= 1

    steps_summary = ""
    if state.executed_steps:
        recent_steps = state.executed_steps[-8:]
        steps_summary = f"\nRecent executed steps: {len(state.executed_steps)} total"
        for step in recent_steps:
            steps_summary += f"\n  - {step[:150]}"

    failed_summary = ""
    if state.executed_steps:
        failure_markers = [
            "failed",
            "failure",
            "no ",
            "same response",
            "blocked",
            "404",
            "invalid",
            "error",
            "still",
            "not found",
            "no result",
            "timeout",
            "forbidden",
            "denied",
            "unreachable",
            "cannot",
            "wrong",
        ]
        failed_attempts = [
            step[:150]
            for step in state.executed_steps
            if any(marker in step.lower() for marker in failure_markers)
        ]
        if failed_attempts:
            failed_summary = "\nFailed history (do not repeat these actions):"
            for failure in failed_attempts[-10:]:
                failed_summary += f"\n  - {failure}"

    if getattr(agent.runtime, "reuse_recon", False) and state.recon_data:
        recon_assets = _render_recon_assets(state.recon_data)
        recon_summary = (
            "\n\nRecon for this target is already complete (results below). "
            "Do NOT re-run port scans or re-enumerate hosts/directories unless a "
            "concrete gap is identified — start from Vulnerability Discovery and "
            "build on this data."
            f"\nExisting recon assets:\n{recon_assets}"
        )
    elif state.recon_data:
        recon_summary = f"\nRecon data: {list(state.recon_data.keys())}"
    else:
        recon_summary = ""
    resume_summary = f"\n\n{state.resume_summary}" if getattr(state, "resume_summary", "") else ""
    notes_summary = f"\nImportant notes: {'; '.join(state.notes[-5:])}" if state.notes else ""

    facts_summary = ""
    if hasattr(state, "confirmed_facts") and state.confirmed_facts:
        facts_summary = "\nConfirmed facts (verified by tools):"
        for fact in state.confirmed_facts[-8:]:
            facts_summary += f"\n  - {fact[:150]}"

    assumptions_summary = ""
    if hasattr(state, "unverified_assumptions") and state.unverified_assumptions:
        assumptions_summary = "\nUnverified assumptions (may be wrong):"
        for assumption in state.unverified_assumptions[-5:]:
            assumptions_summary += f"\n  - {assumption[:150]}"
        assumptions_summary += (
            "\nIf an assumption is wrong, reasoning built on it is invalid. "
            "Verify the most important assumption first."
        )

    path_warning = ""
    if state.executed_steps:
        recent = state.executed_steps[-8:]
        if len(recent) >= 5:
            recent_text = " ".join(recent).lower()
            stuck_indicators = ["get=", "post=", "payload", "parameter", "attempt"]
            if any(recent_text.count(indicator) >= 3 for indicator in stuck_indicators):
                path_warning = (
                    "\n\nYou have spent several rounds on the same path without a breakthrough."
                    "\nRe-check the source and evidence for simpler exploitation paths."
                    "\nList the plausible paths and switch to the simplest different one."
                )

    path_switch_warning = ""
    same_path_fails = agent.runtime.same_path_fail_count
    if same_path_fails >= 3:
        path_switch_warning = (
            f"\n\nForced path switch: the same attack path has failed {same_path_fails} times."
            "\nImmediately do the following:"
            "\n1. Stop and list at least three materially different attack paths."
            "\n2. Sort the alternatives from easiest to hardest."
            "\n3. Start with the simplest alternative."
            "\n4. Spend one round verifying the new assumption before exploiting it."
            "\nDo not keep changing only payload values on the same path."
        )
        agent.runtime.same_path_fail_count = 0
        agent.runtime.path_switch_forced = True

    assumption_reminder = ""
    if round_num > 2 and round_num % 3 == 0:
        assumption_reminder = (
            "\n\nAssumption checkpoint:"
            "\n1. What assumptions does the current reasoning depend on?"
            "\n2. Which assumptions were verified by tools?"
            "\n3. Would a wrong assumption invalidate the current path?"
            "\n4. Can one request verify the most important assumption?"
        )

    python_timeout_warning = ""
    if agent.runtime.python_timeout_rounds >= 1:
        python_timeout_warning = (
            "\n\nCode execution warning: the previous Python script timed out."
            "\nDo not write complex scripts longer than 10 lines."
            "\nPrefer existing tools such as fetch or python_execute over ad hoc crawlers/parsers."
            "\nDo not repeat the same large script."
        )

    blocked_targets_warning = ""
    blocked_targets = agent.runtime.blocked_targets
    if blocked_targets:
        targets = "\n".join(f"  - {target}: confirmed unreachable" for target in blocked_targets)
        blocked_targets_warning = (
            "\n\nUnreachable target warning: these targets failed repeatedly and must not be retried:"
            f"\n{targets}"
            "\nStop accessing them, focus on live targets, and switch to deeper validation if no "
            "other live target exists."
        )

    dead_loop_warning = ""
    rounds_no_progress = agent.runtime.rounds_without_progress
    stale_threshold = agent.config.session.stale_rounds_threshold
    if rounds_no_progress >= stale_threshold:
        dead_loop_warning = (
            f"\n\nSevere warning: {rounds_no_progress} consecutive rounds produced no new findings."
            "\nYou are likely looping. Immediately change strategy:"
            "\n1. Re-fetch relevant source or responses if current evidence is insufficient."
            "\n2. Try a materially different attack path."
            "\n3. Use a different parameter, method, or tool where appropriate."
            "\n4. Review failed history and stop repeating identical operations."
        )
    elif rounds_no_progress >= max(stale_threshold // 2, 2):
        dead_loop_warning = (
            f"\n\nWarning: {rounds_no_progress} consecutive rounds produced no new findings."
            "\nCheck whether you are repeating the same operation and switch methods if needed."
        )

    flag_warning = ""
    claimed_flag = agent.runtime.claimed_flag
    flag_verified = agent.runtime.flag_verified
    if claimed_flag and flag_verified:
        flag_warning = (
            f"\n\nFLAG verified: {claimed_flag}"
            "\nThe task is complete. Summarize the solve path and mark [DONE]."
            "\nDo not repeat verification or send duplicate requests."
        )
    elif claimed_flag and not flag_verified:
        flag_warning = (
            f"\n\nYou previously claimed a flag: {claimed_flag}"
            "\nIt is not independently verified. Re-send the payload with a tool, cross-check it "
            "with a different method, or reject it and continue."
            "\nDo not mark [DONE] until verification is complete."
        )

    ctf_mode_warning = ""
    if agent.runtime.is_ctf_mode and not claimed_flag:
        ctf_mode_warning = (
            "\n\nCTF mode: find and verify the flag."
            "\nNo flag has been found yet, so do not mark [DONE]."
            "\nUse the current evidence to choose the most likely attack path, and switch paths if blocked."
        )
    elif agent.runtime.is_ctf_mode and claimed_flag and not flag_verified:
        ctf_mode_warning = (
            "\n\nCTF mode: a flag was claimed but not verified."
            "\nVerify it with a tool before marking [DONE]. If verification fails, continue searching."
        )

    recon_dim_status = ""
    if agent.runtime.is_recon_phase:
        dim_status_text = state.get_recon_status_text()
        is_complete = state.is_recon_complete()
        rounds_no_progress = agent.runtime.rounds_without_progress

        recon_dim_status = f"\n\nRecon dimension completion:\n{dim_status_text}"
        if not is_complete:
            recon_dim_status += (
                "\n\nRecon is incomplete. Do not mark [DONE] while required dimensions remain unchecked."
                "\nContinue checking the missing dimensions and ensure each active dimension has at least one pass."
            )
        elif (is_complete and rounds_no_progress >= 3) or (rounds_no_progress >= 8 + 5):
            output_dir = str(agent.config.session.output_dir.resolve())
            trigger_reason = (
                f"all dimensions are complete and {rounds_no_progress} rounds had no progress"
                if is_complete
                else f"{rounds_no_progress} rounds had no progress (8+5 safety threshold)"
            )
            recon_dim_status += (
                "\n\nForced Recon -> Exploitation transition."
                f"\nReason: {trigger_reason}."
                "\nSwitch immediately to vulnerability discovery or exploitation."
                "\nDo not save another recon report or call more information-gathering tools."
                "\nUse the collected target profile, adjacent hosts, leaked APIs, and high-value attack surfaces."
                f"\nOutput directory: {output_dir}"
            )
        if round_num < 8:
            recon_dim_status += (
                f"\n\nRecon minimum-round guard: this is round {round_num}; "
                "continue deeper recon until at least round 8."
            )

    return (
        f"\n\n[Autonomous loop round {round_num}/{max_rounds}]"
        f"\nCurrent target: {state.target or 'not set'}"
        f"\nCurrent phase: {state.phase.value}"
        f"\nOutput directory: {agent.config.session.output_dir.resolve()}"
        f"{constraints_summary}"
        f"{user_hint_directive}"
        f"{findings_summary}"
        f"{facts_summary}"
        f"{assumptions_summary}"
        f"{steps_summary}"
        f"{failed_summary}"
        f"{recon_summary}"
        f"{resume_summary}"
        f"{notes_summary}"
        f"{path_warning}"
        f"{path_switch_warning}"
        f"{assumption_reminder}"
        f"{python_timeout_warning}"
        f"{blocked_targets_warning}"
        f"{dead_loop_warning}"
        f"{flag_warning}"
        f"{ctf_mode_warning}"
        f"{recon_dim_status}"
        "\n\nUse the current state and all previous findings to decide the next action."
        "\nDo not repeat operations already attempted; focus on advancing to the next useful step."
        "\nIf you find an important lead or complete the test, append [DONE] at the end of the response."
    )


async def generate_attack_summary(agent: Any) -> str:
    """Generate a detailed attack path summary for the cycle report."""
    state = agent.context.state

    steps = state.executed_steps[-30:] if state.executed_steps else []
    steps_text = "\n".join(f"{i + 1}. {step}" for i, step in enumerate(steps)) if steps else "(no steps)"

    notes = state.notes[-20:] if state.notes else []
    notes_text = "\n".join(f"- {note}" for note in notes) if notes else "(no observations)"

    findings = state.findings
    if findings:
        lines = []
        for finding in findings:
            evidence = (finding.evidence or "")[:150].strip()
            lines.append(f"[{finding.severity}] {finding.title} | evidence: {evidence or 'none'}")
        findings_text = "\n".join(lines)
    else:
        findings_text = "none"

    prompt = (
        f"Target: {state.target or '?'} | Current phase: {state.phase.value}\n"
        f"\n=== Executed Steps ===\n{steps_text}\n"
        f"\n=== Key Observations / Results ===\n{notes_text}\n"
        f"\n=== Vulnerability Findings ===\n{findings_text}\n\n"
        "Write a detailed English attack-path narrative that includes:\n"
        "1. Specific tested URLs or paths, such as https://target.com/admin/login.\n"
        "2. Concrete techniques or tools used at each step, such as SQLMap blind injection, "
        "directory enumeration, or nmap port scanning.\n"
        "3. Important response characteristics, such as length differences or HTTP 500 output.\n"
        "4. How each vulnerability relates to the attack surface.\n"
        "5. Subdomain discovery context if relevant.\n"
        "Format: natural paragraphs, no bullet list, 200-400 English words, no <thinking> tags."
    )

    try:
        client = agent._get_client()
        messages = [{"role": "user", "content": prompt}]
        from vulnbot.agent.llm_client import build_chat_completion_kwargs

        response = client.chat.completions.create(
            **build_chat_completion_kwargs(
                agent,
                messages,
                max_tokens=800,
                temperature=0.3,
            )
        )
        if response and response.choices:
            raw = response.choices[0].message.content or ""
            from vulnbot.agent.think_filter import strip_think_tags

            return strip_think_tags(raw).strip()
    except Exception:
        pass
    return ""
