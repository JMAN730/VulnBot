"""VulnBot CLI main entry point with REPL and sub-commands."""

# ruff: noqa: E402

from __future__ import annotations

import asyncio
import os
import sys
import time
from dataclasses import dataclass
from typing import Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory


def _configure_windows_console() -> None:
    """Force UTF-8 console I/O on Windows for reliable Unicode output."""
    if sys.platform != "win32":
        return

    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    os.environ.setdefault("PYTHONUTF8", "1")

    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleCP(65001)
        kernel32.SetConsoleOutputCP(65001)
    except Exception:
        pass

    for stream_name in ("stdin", "stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is None or not hasattr(stream, "reconfigure"):
            continue
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except Exception:
            pass


_configure_windows_console()

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from vulnbot import __version__
from vulnbot.agent.constraint_policy import validate_action_constraints
from vulnbot.agent.input_analysis import extract_task_constraints
from vulnbot.agent.think_filter import format_think_tags, strip_think_tags
from vulnbot.cli.manual import available_topics, render_manual
from vulnbot.cli.tui import run_config_tui
from vulnbot.config.settings import (
    CONFIG_DIR,
    apply_provider_preset,
    list_providers,
    load_config,
    save_config,
    set_config_value,
)
from vulnbot.i18n import _
from vulnbot.orchestrator import run_agent_task
from vulnbot.repl_runner import run_repl_call
from vulnbot.target_state.store import (
    apply_target_state_to_agent,
    clear_target_state,
    diff_target_state_snapshots,
    get_target_state_preview,
    list_target_snapshots,
    load_target_state,
    rollback_target_state,
)

# === Stream Output Renderer ===


class TerminalStreamSink:
    """CLI terminal stream renderer.

    Implements StreamSink protocol for real-time terminal output.
    """

    def __init__(self, console: "Console", show_thinking: bool = False) -> None:
        """Initialize the terminal sink.

        Args:
            console: Rich Console instance
            show_thinking: Whether to show thinking content
        """
        self._console = console
        self._show_thinking = show_thinking
        self._status_printed = False
        self._in_thinking = False

    def on_status(self, message: str) -> None:
        """Display status message like 'Thinking...'."""
        self._console.print(f"[dim]{message}[/dim] ", end="", soft_wrap=True)
        self._status_printed = True

    def on_thinking_token(self, token: str) -> None:
        """Receive thinking token."""
        if self._show_thinking:
            # Print thinking with dim italic style
            self._console.print(f"[dim i]{token}[/]", end="", soft_wrap=True)

    def on_content_token(self, token: str) -> None:
        """Receive content token."""
        # If we printed status and now getting content, move to new line
        if self._status_printed and not self._in_thinking:
            self._console.print()
            self._status_printed = False
        self._console.print(token, end="", soft_wrap=True)

    def on_tool_call(self, tool_name: str, args: str) -> None:
        """Display tool call notification."""
        self._console.print()
        self._console.print(f"[bold cyan]-> Tool call: {tool_name}[/] {args[:100]}")
        self._status_printed = False

    def on_tool_result(self, result_summary: str) -> None:
        """Display tool result summary."""
        self._console.print()
        if len(result_summary) > 200:
            result_summary = result_summary[:200] + "..."
        self._console.print(f"[dim]-> Tool result: {result_summary}[/]")

    def on_stream_end(self) -> None:
        """Handle stream end."""
        if self._status_printed:
            self._status_printed = False
        self._console.print()

app = typer.Typer(
    name="vulnbot",
    help="VulnBot - AI-powered penetration testing CLI (run 'vulnbot tui' for the TUI workbench)",
    no_args_is_help=False,
    add_completion=False,
)

console = Console()
err_console = Console(stderr=True)



ASCII_LOGO = (
    " _    __      __      ____        __ \n"
    "| |  / /_  __/ /___  / __ )____  / /_\n"
    "| | / / / / / / __ \\/ __  / __ \\/ __/\n"
    "| |/ / /_/ / / / / / /_/ / /_/ / /_  \n"
    "|___/\\__,_/_/_/ /_/_____/\\____/\\__/  \n"
)

BANNER_SUBTITLE = f"VulnBot v{__version__} - AI-powered penetration testing CLI"


def _print_banner() -> None:
    logo = Text(ASCII_LOGO, style="bold red")
    subtitle = Text(BANNER_SUBTITLE)
    console.print(logo)
    console.print(subtitle)
    console.print()


def _build_repl_prompt_session() -> PromptSession[str]:
    """Build the REPL input session with persistent command history."""
    history_file = CONFIG_DIR / "repl_history"
    history_file.parent.mkdir(parents=True, exist_ok=True)
    return PromptSession(history=FileHistory(str(history_file)), enable_history_search=True)


def _print_agent_output(output: str, config) -> None:
    """Print agent output with think-tag filtering based on config."""
    from rich.markup import escape as rich_escape

    formatted = format_think_tags(output, show=config.session.show_thinking)
    if formatted:
        # LLM output may contain Rich-style brackets like [/TOOL_CALL] which
        # cause MarkupError.  Escape before printing so they render literally.
        console.print(rich_escape(formatted))
    elif not config.session.show_thinking:
        # Check if the original output had thinking content that was stripped
        stripped = strip_think_tags(output)
        had_thinking = (stripped != output) and not stripped
        if had_thinking:
            console.print("[dim](LLM returned only hidden reasoning and no visible answer.)[/dim]")




def _prepare_repl_target(
    agent, requested_target: str, current_target: Optional[str], current_phase: str
) -> tuple[str, str, bool]:
    """Prepare REPL state for a target switch and optionally restore history."""
    target = requested_target.strip()
    if not target:
        return current_target or "", current_phase, False

    if current_target and current_target != target:
        console.print(
            f"[dim][*] Target switch: {current_target} -> {target}, resetting session context[/]"
        )
        agent.reset_context()
        current_phase = agent.session_state.phase.value

    restore_result = apply_target_state_to_agent(agent, target)
    current_phase = restore_result.phase or agent.session_state.phase.value
    return target, current_phase, restore_result.restored


async def _run_repl_agent_call(agent, *, call, after_result) -> None:
    """Run a REPL agent call and hand each result back to a caller hook."""
    await run_repl_call(call=call, after_result=after_result)


@dataclass
class ReplParallelSettings:
    """Runtime REPL parallel controls copied from persisted session config."""

    enabled: bool
    agents: int
    depth: int
    worker_rounds: int
    surface_limit: int


@dataclass(frozen=True)
class ReplParallelBudget:
    """Effective bounded fan-out settings for one REPL auto-mode run."""

    use_parallel: bool
    discovery_rounds: int
    worker_rounds: int
    max_agents: int
    max_depth: int
    surface_limit: int
    max_rounds: int
    reason: str = ""


def _coerce_int(value, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _repl_parallel_settings_from_config(config) -> ReplParallelSettings:
    session = config.session
    return ReplParallelSettings(
        enabled=bool(getattr(session, "repl_parallel_enabled", True)),
        agents=_coerce_int(getattr(session, "repl_parallel_agents", 3), 3),
        depth=_coerce_int(getattr(session, "repl_parallel_depth", 1), 1),
        worker_rounds=_coerce_int(getattr(session, "repl_parallel_worker_rounds", 3), 3),
        surface_limit=_coerce_int(getattr(session, "repl_parallel_surface_limit", 20), 20),
    )


def _resolve_repl_parallel_budget(
    settings: ReplParallelSettings,
    *,
    max_rounds: int,
) -> ReplParallelBudget:
    """Resolve REPL parallel settings under the total session max-round budget."""
    total_rounds = _coerce_int(max_rounds, 0)
    fallback_rounds = max(0, total_rounds)

    def fallback(reason: str) -> ReplParallelBudget:
        return ReplParallelBudget(
            use_parallel=False,
            discovery_rounds=fallback_rounds,
            worker_rounds=0,
            max_agents=0,
            max_depth=0,
            surface_limit=max(0, settings.surface_limit),
            max_rounds=total_rounds,
            reason=reason,
        )

    if not settings.enabled:
        return fallback("disabled")

    if settings.agents < 1:
        return fallback("child-agent count must be at least 1")
    if settings.depth < 1:
        return fallback("parallel depth must be at least 1")
    if settings.worker_rounds < 1:
        return fallback("worker rounds must be at least 1")
    if settings.surface_limit < 1:
        return fallback("surface limit must be at least 1")
    if total_rounds < 2:
        return fallback("no remaining worker budget")

    discovery_rounds = max(1, int(total_rounds * 0.4))
    remaining_rounds = total_rounds - discovery_rounds
    if remaining_rounds < 1:
        return fallback("no remaining worker budget")

    effective_agents = min(settings.agents, remaining_rounds)
    worker_rounds = min(settings.worker_rounds, max(1, remaining_rounds // effective_agents))
    if effective_agents < 1 or worker_rounds < 1:
        return fallback("no remaining worker budget")

    return ReplParallelBudget(
        use_parallel=True,
        discovery_rounds=discovery_rounds,
        worker_rounds=worker_rounds,
        max_agents=effective_agents,
        max_depth=settings.depth,
        surface_limit=settings.surface_limit,
        max_rounds=total_rounds,
    )


def _flatten_parallel_repl_results(summary) -> list:
    """Return a list-like result for existing REPL completion rendering."""
    if not hasattr(summary, "root_results"):
        return summary

    flattened = []
    root_results = getattr(summary, "root_results", [])
    if isinstance(root_results, list):
        flattened.extend(root_results)
    elif root_results:
        flattened.append(root_results)

    for worker in getattr(summary, "worker_results", []) or []:
        worker_results = worker.get("results") if isinstance(worker, dict) else worker
        if isinstance(worker_results, list):
            flattened.extend(worker_results)
        elif worker_results:
            flattened.append(worker_results)

    return flattened


async def _run_repl_auto_pentest(
    agent,
    config,
    parallel_settings: ReplParallelSettings,
    *,
    user_input: str,
    target: Optional[str],
    on_step,
    stream_sink,
):
    """Run REPL auto-mode, using bounded parallel child agents when enabled."""
    budget = _resolve_repl_parallel_budget(
        parallel_settings,
        max_rounds=config.session.max_rounds,
    )
    if not budget.use_parallel:
        return await agent.auto_pentest(
            user_input,
            target=target,
            max_rounds=config.session.max_rounds,
            on_step=on_step,
            stream_sink=stream_sink,
        )

    from vulnbot.agent.parallel_agents import run_parallel_pentest

    def agent_factory():
        return agent.__class__(config, getattr(agent, "mcp_manager", None))

    summary = await run_parallel_pentest(
        agent,
        agent_factory=agent_factory,
        user_input=user_input,
        target=target,
        discovery_rounds=budget.discovery_rounds,
        worker_rounds=budget.worker_rounds,
        max_agents=budget.max_agents,
        max_depth=budget.max_depth,
        surface_limit=budget.surface_limit,
        stream_sink=stream_sink,
    )

    if hasattr(summary, "surfaces"):
        if summary.surfaces:
            console.print(
                "[dim][*] REPL parallel: "
                f"explored {len(summary.surfaces)} surface(s) across "
                f"{summary.waves_completed} wave(s).[/]"
            )
        else:
            console.print(
                "[dim][*] REPL parallel: no parallel surfaces found; "
                "completed root discovery only.[/]"
            )

    return _flatten_parallel_repl_results(summary)


def _print_repl_parallel_status(settings: ReplParallelSettings, config) -> None:
    budget = _resolve_repl_parallel_budget(settings, max_rounds=config.session.max_rounds)
    enabled = "[green]on[/]" if settings.enabled else "[yellow]off[/]"
    if budget.use_parallel:
        effective = (
            f"{budget.max_agents} child agent(s), depth {budget.max_depth}, "
            f"{budget.discovery_rounds} root round(s), "
            f"{budget.worker_rounds} worker round(s)"
        )
    else:
        effective = f"single-agent auto mode ({budget.reason})"

    console.print(
        Panel(
            f"Enabled: {enabled}\n"
            f"Configured agents: [bold]{settings.agents}[/]\n"
            f"Configured depth: [bold]{settings.depth}[/]\n"
            f"Configured worker rounds: [bold]{settings.worker_rounds}[/]\n"
            f"Surface limit: [bold]{settings.surface_limit}[/]\n"
            f"Max rounds: [bold]{config.session.max_rounds}[/]\n"
            f"Effective: [bold]{effective}[/]",
            title="REPL Parallel",
            border_style="cyan",
        )
    )


def _handle_repl_parallel_command(
    user_input: str,
    settings: ReplParallelSettings,
    config,
) -> tuple[bool, ReplParallelSettings]:
    parts = user_input.strip().split()
    if not parts or parts[0].lower() != "parallel":
        return False, settings

    if len(parts) == 1 or (len(parts) == 2 and parts[1].lower() == "status"):
        _print_repl_parallel_status(settings, config)
        return True, settings

    action = parts[1].lower()
    if action == "on":
        settings.enabled = True
        console.print("[*] REPL parallel auto-mode: [green]on[/]")
        return True, settings
    if action == "off":
        settings.enabled = False
        console.print("[*] REPL parallel auto-mode: [yellow]off[/]")
        return True, settings
    if action == "reset":
        settings = _repl_parallel_settings_from_config(config)
        console.print("[*] REPL parallel controls reset from config.")
        _print_repl_parallel_status(settings, config)
        return True, settings
    if action == "agents":
        if len(parts) != 3:
            console.print("[!] Usage: parallel agents N")
            return True, settings
        agents = _coerce_int(parts[2], 0)
        if agents < 1:
            console.print("[!] parallel agents must be at least 1")
            return True, settings
        settings.agents = agents
        console.print(f"[*] REPL parallel child agents: [bold]{agents}[/]")
        return True, settings

    console.print("[!] Usage: parallel [status|on|off|agents N|reset]")
    return True, settings


def _run_repl() -> None:
    """Run the interactive REPL loop."""
    from vulnbot.agent.core import AgentCore
    from vulnbot.mcp.lifecycle import MCPLifecycleManager

    _print_banner()

    config = load_config()
    if not config.llm.api_key:
        console.print(_("cli.no_api_key"))
        console.print(_("cli.choose_provider"))
        console.print(_("cli.set_env_var"))
        console.print()
        console.print(_("cli.offline_mode"))

    # Initialize MCP lifecycle manager
    mcp_manager = MCPLifecycleManager(config)
    started = mcp_manager.start_enabled_servers()
    console.print(_("cli.mcp_registered", count=started))

    # Initialize agent
    agent = AgentCore(config, mcp_manager)
    repl_session = _build_repl_prompt_session() if sys.stdin.isatty() and sys.stdout.isatty() else None

    console.print(_("cli.welcome"))
    console.print()

    # Track current target
    current_target: Optional[str] = None
    current_phase: str = "Ready"
    exit_requested = False
    auto_mode_active = False
    _last_ctrlc_time = 0.0
    last_auto_input: str = ""
    pending_fresh_recon = False
    repl_parallel_settings = _repl_parallel_settings_from_config(config)

    while True:
        try:
            # Build prompt string
            prompt_parts = []
            if current_target:
                prompt_parts.append(f"[bold cyan]{current_target}[/]")
            prompt_parts.append(f"[dim]{current_phase}[/]")
            if auto_mode_active:
                prompt_parts.append("AUTO")
            prompt_str = " | ".join(prompt_parts) if prompt_parts else "vulnbot"

            # Read input
            if repl_session is not None:
                user_input = repl_session.prompt(f"vulnbot {prompt_str}> ").strip()
            else:
                user_input = console.input(f"vulnbot {prompt_str}> ").strip()

            if not user_input:
                if last_auto_input:
                    user_input = last_auto_input
                    console.print(f"[dim]↻ Resuming auto pentest: {last_auto_input[:60]}...[/]")
                else:
                    continue

            # Handle built-in commands
            cmd_lower = user_input.lower()

            if cmd_lower in ("exit", "quit", "q"):
                console.print(_("cli.bye"))
                break

            elif cmd_lower == "help":
                _print_help()
                continue

            elif cmd_lower == "status":
                _print_status(agent, mcp_manager, current_target, current_phase, config)
                continue

            elif cmd_lower.startswith("target "):
                current_target, current_phase, restored_loaded = _prepare_repl_target(
                    agent,
                    user_input[7:].strip(),
                    current_target,
                    current_phase,
                )
                if restored_loaded:
                    console.print(_("cli.target_restored", target=current_target))
                console.print(_("cli.target_set", target=current_target))
                continue

            elif cmd_lower == "clear":
                current_target = None
                current_phase = "Ready"
                auto_mode_active = False
                last_auto_input = ""
                agent.reset_context()
                console.print(_("cli.conversation_cleared"))
                continue

            elif cmd_lower == "tools":
                tools = mcp_manager.list_available_tools()
                if tools:
                    console.print(_("cli.available_tools"))
                    for tool in tools:
                        console.print(f"  - {tool}")
                else:
                    console.print(_("cli.no_tools"))
                continue

            elif cmd_lower.startswith("report"):
                report_target = user_input[len("report") :].strip() or current_target
                if not report_target:
                    console.print(_("cli.no_target_for_report"))
                    continue

                report_path = _generate_report_for_target(
                    report_target,
                    current_session=agent.session_state
                    if agent.session_state.target == report_target
                    else None,
                    report_format=config.session.report_format,
                )
                console.print(_("cli.report_generated", path=report_path))
                continue

            elif cmd_lower.startswith("rescan"):
                rescan_target = user_input[len("rescan") :].strip() or current_target
                if not rescan_target:
                    console.print(_("cli.no_target_for_report"))
                    continue
                current_target, current_phase, _restored = _prepare_repl_target(
                    agent, rescan_target, current_target, current_phase
                )
                pending_fresh_recon = True
                console.print(_("cli.fresh_recon_armed", target=current_target))
                continue

            elif cmd_lower.startswith("persistent"):
                explicit_target = user_input[len("persistent") :].strip()
                persistent_target = explicit_target or current_target
                if not persistent_target:
                    console.print(
                        "[!] Set a target first with [bold]target <host>[/] or run [bold]persistent <host>[/]."
                    )
                    continue

                current_target, current_phase, restored_loaded = _prepare_repl_target(
                    agent,
                    persistent_target,
                    current_target,
                    current_phase,
                )
                persistent_target = current_target
                if restored_loaded:
                    console.print(_("cli.target_restored", target=persistent_target))

                from vulnbot.agent.core import PersistentCycleResult

                rounds_per_cycle = config.session.persistent_rounds_per_cycle
                max_cycles = config.session.persistent_max_cycles
                auto_report = config.session.persistent_auto_report

                console.print(
                    Panel(
                        f"Target: [bold]{persistent_target}[/]\n"
                        f"Rounds per cycle: [bold]{rounds_per_cycle}[/]\n"
                        f"Max cycles: [bold]{max_cycles}[/]\n"
                        f"Auto report: {'[green]on[/]' if auto_report else '[yellow]off[/]'}",
                        title="Persistent Pentest",
                        border_style="cyan",
                    )
                )

                persistent_prompt = (
                    f"Perform an authorized persistent penetration test against {persistent_target}. "
                    "This target is in scope and explicitly authorized."
                )

                all_cycle_results: list[PersistentCycleResult] = []

                def _on_persistent_step(round_num: int, cycle_num: int, result) -> None:
                    console.print(f"[dim]-- Cycle {cycle_num} | Round {round_num} --[/]")
                    console.print()
                    nonlocal current_target, current_phase
                    if result.target:
                        current_target = result.target
                    if result.phase:
                        current_phase = result.phase

                def _on_persistent_cycle(
                    cycle_num: int, cycle_result: PersistentCycleResult
                ) -> None:
                    all_cycle_results.append(cycle_result)
                    console.print(
                        Panel(
                            f"Cycle {cycle_num} completed\n"
                            f"   Total findings: {cycle_result.total_findings}\n"
                            f"   New findings: {cycle_result.new_findings}\n"
                            f"   Report: {cycle_result.report_path or 'not generated'}",
                            title=f"Cycle {cycle_num}",
                            border_style="green" if cycle_result.new_findings == 0 else "red",
                        )
                    )
                    console.print()

                try:

                    async def _run_persistent():
                        sink = TerminalStreamSink(console, config.session.show_thinking)
                        return await agent.persistent_pentest(
                            user_input=persistent_prompt,
                            target=persistent_target,
                            rounds_per_cycle=rounds_per_cycle,
                            max_cycles=max_cycles,
                            auto_report=auto_report,
                            on_cycle_step=_on_persistent_step,
                            on_cycle_complete=_on_persistent_cycle,
                            stream_sink=sink,
                        )

                    asyncio.run(_run_persistent())
                    if auto_report and not all_cycle_results:
                        partial_report = _generate_report_for_target(
                            persistent_target,
                            current_session=agent.session_state,
                            report_format=config.session.report_format,
                        )
                        console.print(_("cli.partial_report", path=partial_report))
                except KeyboardInterrupt:
                    console.print(f"\n{_('persistent.interrupted_message')}")
                    if agent.session_state.findings:
                        try:
                            final_report = _generate_report_for_target(
                                persistent_target,
                                current_session=agent.session_state,
                                report_format=config.session.report_format,
                            )
                            console.print(_("persistent.final_report", path=final_report))
                        except Exception as exc:
                            console.print(_("persistent.failed_final_report", exc=exc))

                # Summary
                tf = len(agent.session_state.findings)
                console.print(
                    _("persistent.finished_summary", cycles=len(all_cycle_results), findings=tf)
                )
                continue

            elif cmd_lower == "think":
                # Toggle think tag display
                config.session.show_thinking = not config.session.show_thinking
                state_str = (
                    "[green]shown[/]" if config.session.show_thinking else "[yellow]hidden[/]"
                )
                console.print(f"[*] Thinking visibility: {state_str}")
                console.print(_("cli.thinking_toggle_hint"))
                continue

            elif cmd_lower == "think on":
                config.session.show_thinking = True
                console.print(_("cli.thinking_shown"))
                continue

            elif cmd_lower == "think off":
                config.session.show_thinking = False
                console.print(_("cli.thinking_hidden"))
                continue

            handled_parallel, repl_parallel_settings = _handle_repl_parallel_command(
                user_input,
                repl_parallel_settings,
                config,
            )
            if handled_parallel:
                continue

            # Handle auto mode persistence: exit auto mode on explicit commands
            if auto_mode_active and user_input.lower().strip() in (
                "chat", "manual", "exit auto", "single turn",
            ):
                auto_mode_active = False
                last_auto_input = ""
                console.print(_("cli.auto_mode_exited"))
                is_auto_mode = False
            elif auto_mode_active:
                is_auto_mode = True
            else:
                # Route to agent and detect whether this should be an autonomous loop
                is_auto_mode = _should_auto_pentest(user_input, current_target)

            # Detect target switch and reset context if the user mentions a new target
            new_target = _extract_target_from_input(user_input)
            if new_target and current_target and new_target != current_target:
                console.print(_("cli.target_switch", from_target=current_target, to_target=new_target))
                current_target = new_target
                current_phase = "Recon"
                agent.reset_context()
                # Reset auto mode on target switch
                auto_mode_active = False
                last_auto_input = ""

            # Save last auto input for resume on empty Enter
            if is_auto_mode:
                last_auto_input = user_input

            try:
                if is_auto_mode:
                    # Autonomous pentest loop
                    console.print(_("cli.enter_auto_mode"))
                    console.print()

                    async def _run_auto():
                        sink = TerminalStreamSink(console, config.session.show_thinking)
                        async def call():
                            def on_step(round_num, result):
                                nonlocal current_target, current_phase
                                console.print(f"[dim]-- Round {round_num} --[/]")
                                console.print()
                                if result.target:
                                    current_target = result.target
                                if result.phase:
                                    current_phase = result.phase

                            return await _run_repl_auto_pentest(
                                agent,
                                config,
                                repl_parallel_settings,
                                user_input=user_input,
                                target=current_target,
                                on_step=on_step,
                                stream_sink=sink,
                                fresh_recon=pending_fresh_recon,
                            )

                        async def after_result(results):
                            nonlocal current_target, current_phase
                            if results:
                                if agent.session_state.target:
                                    current_target = agent.session_state.target
                                if agent.session_state.phase:
                                    current_phase = agent.session_state.phase.value
                                total_findings = len(agent.session_state.findings)
                                total_steps = len(agent.session_state.executed_steps)
                                if getattr(agent.runtime, "reuse_recon", False):
                                    recon = agent.session_state.recon_data
                                    asset_count = sum(
                                        len(v) for v in recon.values() if isinstance(v, list)
                                    )
                                    console.print(
                                        _(
                                            "cli.recon_reused",
                                            target=current_target or agent.session_state.target,
                                            assets=asset_count,
                                            findings=total_findings,
                                        )
                                    )
                                console.print()
                                console.print(
                                    Panel(
                                        f"{_('auto_pentest.finished')}\n"
                                        f"{_('auto_pentest.rounds', rounds=len(results))}\n"
                                        f"{_('auto_pentest.steps', steps=total_steps)}\n"
                                        f"{_('auto_pentest.findings', findings=total_findings)}",
                                        title=_("auto_pentest.title"),
                                        border_style="green" if total_findings == 0 else "red",
                                    )
                                )

                                if any(
                                    token in user_input.lower()
                                    for token in (
                                        "output",
                                        "save",
                                        "write to",
                                        "export",
                                        "save",
                                        "write",
                                        "export",
                                    )
                                ):
                                    _auto_save_recon_report(agent, user_input, config)

                        await _run_repl_agent_call(agent, call=call, after_result=after_result)

                    asyncio.run(_run_auto())
                    pending_fresh_recon = False
                    auto_mode_active = True
                    console.print(_("cli.auto_mode_hint"))

                else:
                    # Single-turn chat
                    async def _run_agent():
                        sink = TerminalStreamSink(console, config.session.show_thinking)
                        async def call():
                            return await agent.chat(user_input, target=current_target, stream_sink=sink)

                        async def after_result(result):
                            nonlocal current_target, current_phase
                            if result:
                                if result.target:
                                    current_target = result.target
                                if result.phase:
                                    current_phase = result.phase
                                # if result.output:
                                #     _print_agent_output(result.output, config)

                        await _run_repl_agent_call(agent, call=call, after_result=after_result)

                    asyncio.run(_run_agent())

            except KeyboardInterrupt:
                if is_auto_mode:
                    auto_mode_active = False
                    console.print()
                    console.print(_("cli.interrupted"))
                    console.print(_("cli.auto_resume_hint"))
                else:
                    console.print(f"\n{_('cli.interrupted')}")
            except Exception as e:
                # Escape Rich markup chars in exception message to prevent MarkupError
                from rich.markup import escape as rich_escape

                console.print(_("cli.error", msg=rich_escape(str(e))))

        except KeyboardInterrupt:
            now = time.monotonic()
            if exit_requested and (now - _last_ctrlc_time) < 3.0:
                console.print(_("cli.bye"))
                break
            exit_requested = True
            _last_ctrlc_time = now
            console.print(f"\n{_('cli.press_again')}")
        except EOFError:
            break

    # Cleanup - suppress SIGINT to prevent re-trigger during threading shutdown
    import signal

    signal.signal(signal.SIGINT, signal.SIG_IGN)
    mcp_manager.stop_all()
    console.print("[dim]MCP services stopped.[/]")


def _print_help() -> None:
    """Print REPL help."""
    help_text = f"""
 [bold]{_("help.commands")}[/]:
  {_("help.target")}
  {_("help.status")}
  {_("help.tools")}
  {_("help.report")}
  {_("help.rescan")}
  {_("help.parallel")}
  {_("help.think")}
  {_("help.think_on_off")}
  {_("help.persistent")}
  {_("help.persistent_host")}
  {_("help.clear")}
  {_("help.chat")}
  {_("help.help")}
  {_("help.exit")}

 [bold]{_("help.auto_mode")}[/]:
  {_("help.auto_mode_desc")}
  {_("help.auto_mode_example")}
  {_("help.auto_mode_stays")}

 [bold]{_("help.persistent_mode")}[/]:
  {_("help.persistent_mode_desc")}
  {_("help.persistent_cli")}
  {_("help.persistent_repl")}

 [bold]{_("help.examples")}[/]:
  {_("help.example_pentest")}
  {_("help.example_scan")}
  {_("help.example_vuln")}
  {_("help.example_exploit")}
  {_("help.example_report")}
"""
    console.print(Panel(help_text, title=_("help.title"), border_style="cyan"))


def _print_status(agent, mcp_manager, target, phase, config) -> None:
    """Print current session status."""
    think_state = "[green]shown[/]" if config.session.show_thinking else "[yellow]hidden[/]"
    console.print(
        Panel(
            f"{_('status.target', target=target or 'Not set')}\n"
            f"{_('status.phase', phase=phase)}\n"
            f"{_('status.mcp_services', count=mcp_manager.running_count())}\n"
            f"{_('status.tools', count=len(mcp_manager.list_available_tools()))}\n"
            f"{_('status.thinking', state=think_state)}",
            title=_("status.title"),
            border_style="green",
        )
    )


def _generate_report_for_target(
    target: str,
    *,
    current_session=None,
    report_format: str = "markdown",
) -> str:
    """Generate a report for a target using the best available source data."""
    from vulnbot.agent.context import SessionState
    from vulnbot.report.generator import generate_report, generate_report_from_target_state
    from vulnbot.target_state.store import load_target_state

    if current_session is not None and (
        current_session.findings or current_session.executed_steps or current_session.notes
    ):
        path = generate_report(current_session, report_format=report_format)
        return str(path)

    state = load_target_state(target)
    if state:
        path = generate_report_from_target_state(state)
        return str(path)

    session = SessionState(target=target)
    path = generate_report(session, report_format=report_format)
    return str(path)


def _infer_report_format(output_path: str, configured_format: str) -> str:
    """Infer report format from an explicit output path when possible."""
    from pathlib import Path

    suffix = Path(output_path).suffix.lower()
    if suffix in {".html", ".htm"}:
        return "html"
    if suffix in {".md", ".markdown"}:
        return "markdown"
    return configured_format


def _generate_report_output_for_target(
    target: str,
    output_path: str,
    *,
    report_format: str,
) -> str:
    """Generate a CLI report for a target, preferring saved target state."""
    from vulnbot.agent.context import SessionState
    from vulnbot.report.generator import generate_report, generate_report_from_target_state

    effective_format = _infer_report_format(output_path, report_format)
    state = load_target_state(target)
    if state:
        return str(
            generate_report_from_target_state(
                state,
                report_format=effective_format,
                output_path=output_path,
            )
        )

    session = SessionState(target=target)
    return str(
        generate_report(
            session,
            output_path=output_path,
            report_format=effective_format,
        )
    )


def _append_cli_constraints(
    prompt: str,
    only_port: Optional[int],
    only_host: Optional[str],
    only_path: Optional[str],
    blocked_host: Optional[str] = None,
    blocked_path: Optional[str] = None,
) -> str:
    constraints = []
    if only_port is not None:
        constraints.append(f"Only test port {only_port}")
    if only_host:
        constraints.append(f"Only test host {only_host}")
    if only_path:
        constraints.append(f"Only test path {only_path}")
    if blocked_host:
        constraints.append(f"Blocked host {blocked_host}")
    if blocked_path:
        constraints.append(f"Blocked path {blocked_path}")
    if not constraints:
        return prompt
    return f"{prompt} {' '.join(constraints)}."


def _append_cli_constraints_compat(
    prompt: str,
    only_port: Optional[int],
    only_host: Optional[str],
    only_path: Optional[str],
    blocked_host: Optional[str],
    blocked_path: Optional[str],
) -> str:
    """Append scope constraints while preserving older monkeypatch call shapes."""
    try:
        return _append_cli_constraints(
            prompt, only_port, only_host, only_path, blocked_host, blocked_path
        )
    except TypeError as exc:
        if "positional" not in str(exc) and "argument" not in str(exc):
            raise
        return _append_cli_constraints(prompt, only_port, only_host, only_path)


def _append_action_constraints(
    prompt: str, allow_actions: Optional[str], block_actions: Optional[str]
) -> str:
    constraints = []
    if allow_actions:
        constraints.append(f"Only allowed actions: {allow_actions}")
    if block_actions:
        constraints.append(f"Blocked actions: {block_actions}")
    if not constraints:
        return prompt
    return f"{prompt} {' '.join(constraints)}."


async def _run_cli_orchestrated_task(
    *,
    command: str,
    target: str,
    resume: bool,
    snapshot: Optional[str],
    runner,
):
    """Run a CLI task through the shared orchestrator helpers."""
    from vulnbot.agent.core import AgentCore
    from vulnbot.mcp.lifecycle import MCPLifecycleManager

    config = load_config()
    mcp_manager = MCPLifecycleManager(config)
    mcp_manager.start_enabled_servers()
    agent = AgentCore(config, mcp_manager)

    try:

        def on_restored(restore_result) -> None:
            console.print(
                f"[*] Restored saved target state: [bold]{restore_result.target or target}[/]"
            )

        return await run_agent_task(
            agent=agent,
            command=command,
            target=target,
            resume=resume,
            snapshot_id=snapshot,
            on_restored=on_restored,
            runner=lambda shared_agent: runner(shared_agent, config),
        )
    finally:
        import signal

        signal.signal(signal.SIGINT, signal.SIG_IGN)
        mcp_manager.stop_all()




@app.command()
def run(
    target: str = typer.Argument(..., help="Target host/IP/URL"),
    scope: str = typer.Option("full", help="Test scope: full, web, api, mobile"),
    output: Optional[str] = typer.Option(None, help="Output report file path"),
    prompt: Optional[str] = typer.Option(
        None, "--prompt", help="Custom natural language prompt (overrides auto-generated prompt)"
    ),
    only_port: Optional[int] = typer.Option(
        None, "--only-port", help="Restrict testing to a single port"
    ),
    only_host: Optional[str] = typer.Option(
        None, "--only-host", help="Restrict testing to a single host"
    ),
    only_path: Optional[str] = typer.Option(
        None, "--only-path", help="Restrict testing to a single path"
    ),
    blocked_host: Optional[str] = typer.Option(
        None, "--blocked-host", help="Explicitly blocked host"
    ),
    blocked_path: Optional[str] = typer.Option(
        None, "--blocked-path", help="Explicitly blocked path"
    ),
    allow_actions: Optional[str] = typer.Option(
        None, "--allow-actions", help="Comma-separated allowed actions"
    ),
    block_actions: Optional[str] = typer.Option(
        None, "--block-actions", help="Comma-separated blocked actions"
    ),
    resume: bool = typer.Option(True, "--resume/--no-resume", help="Resume previous target state"),
    snapshot: Optional[str] = typer.Option(
        None, "--snapshot", help="Resume from a specific target snapshot id"
    ),
    fresh_recon: bool = typer.Option(
        False, "--fresh-recon", help="Re-run recon from scratch (keeps prior findings)"
    ),
) -> None:
    """Run a full authorized pentest workflow."""
    config = load_config()
    if not config.llm.api_key:
        err_console.print("[!] Configure an LLM API key first.")
        raise typer.Exit(1)

    console.print(f"[*] Target: [bold]{target}[/] | Scope: [bold]{scope}[/]")

    task_prompt = prompt if prompt else (
        f"Perform an authorized {scope} pentest against {target}. "
        "This target is in scope and explicitly authorized."
    )
    task_prompt = _append_cli_constraints_compat(
        task_prompt, only_port, only_host, only_path, blocked_host, blocked_path
    )
    task_prompt = _append_action_constraints(task_prompt, allow_actions, block_actions)
    violation = validate_action_constraints("run", extract_task_constraints(task_prompt))
    if violation is not None:
        err_console.print(f"[!] {violation}")
        raise typer.Exit(1)

    async def _run():
        async def runner(agent, shared_config):
            sink = TerminalStreamSink(console, shared_config.session.show_thinking)
            return await agent.auto_pentest(
                task_prompt,
                target=target,
                max_rounds=shared_config.session.max_rounds,
                on_step=lambda r, res: (
                    _print_agent_output(f"[dim]Round {r}[/]: {res.output[:200]}...", shared_config)
                    if res.output
                    else None
                ),
                stream_sink=sink,
                fresh_recon=fresh_recon,
            )

        result = await _run_cli_orchestrated_task(
            command="run",
            target=target,
            resume=resume,
            snapshot=snapshot,
            runner=runner,
        )
        return result

    orchestrated = asyncio.run(_run())
    total_findings = orchestrated.summary["findings_count"]
    console.print(_("cli.pentest_finished", findings=total_findings))
    if output:
        report_path = _generate_report_output_for_target(
            target,
            output,
            report_format=config.session.report_format,
        )
        console.print(f"[+] Report generated: {report_path}")


@app.command()
def persistent(
    target: str = typer.Argument(..., help="Target host/IP/URL"),
    rounds: int = typer.Option(
        0, "--rounds", "-r", help="Rounds per cycle (0=use config, default 100)"
    ),
    cycles: int = typer.Option(0, "--cycles", "-c", help="Max cycles (0=use config, default 10)"),
    no_report: bool = typer.Option(
        False, "--no-report", help="Disable auto report after each cycle"
    ),
    prompt: Optional[str] = typer.Option(
        None, "--prompt", help="Custom natural language prompt (overrides auto-generated prompt)"
    ),
    only_port: Optional[int] = typer.Option(
        None, "--only-port", help="Restrict testing to a single port"
    ),
    only_host: Optional[str] = typer.Option(
        None, "--only-host", help="Restrict testing to a single host"
    ),
    only_path: Optional[str] = typer.Option(
        None, "--only-path", help="Restrict testing to a single path"
    ),
    blocked_host: Optional[str] = typer.Option(
        None, "--blocked-host", help="Explicitly blocked host"
    ),
    blocked_path: Optional[str] = typer.Option(
        None, "--blocked-path", help="Explicitly blocked path"
    ),
    allow_actions: Optional[str] = typer.Option(
        None, "--allow-actions", help="Comma-separated allowed actions"
    ),
    block_actions: Optional[str] = typer.Option(
        None, "--block-actions", help="Comma-separated blocked actions"
    ),
    resume: bool = typer.Option(True, "--resume/--no-resume", help="Resume previous target state"),
    snapshot: Optional[str] = typer.Option(
        None, "--snapshot", help="Resume from a specific target snapshot id"
    ),
    fresh_recon: bool = typer.Option(
        False, "--fresh-recon", help="Re-run recon from scratch (keeps prior findings)"
    ),
) -> None:
    """Run a persistent authorized pentest across multiple cycles."""
    from vulnbot.agent.core import PersistentCycleResult

    config = load_config()
    if not config.llm.api_key:
        err_console.print("[!] Configure an LLM API key first.")
        raise typer.Exit(1)

    # Resolve parameters (CLI override -> config defaults)
    rounds_per_cycle = rounds if rounds > 0 else config.session.persistent_rounds_per_cycle
    max_cycles = cycles if cycles > 0 else config.session.persistent_max_cycles
    auto_report = config.session.persistent_auto_report and not no_report

    console.print(
        Panel(
            f"Target: [bold]{target}[/]\n"
            f"Rounds per cycle: [bold]{rounds_per_cycle}[/]\n"
            f"Max cycles: [bold]{max_cycles}[/] {'(unlimited)' if max_cycles == 0 else ''}\n"
            f"Auto report: {'[green]on[/]' if auto_report else '[yellow]off[/]'}\n"
            f"Max total rounds: [bold]{rounds_per_cycle * max_cycles if max_cycles > 0 else 'unlimited'}[/]",
            title="Persistent Pentest",
            border_style="cyan",
        )
    )

    task_prompt = prompt if prompt else (
        f"Perform an authorized persistent penetration test against {target}. "
        "This target is in scope and explicitly authorized."
    )
    task_prompt = _append_cli_constraints_compat(
        task_prompt, only_port, only_host, only_path, blocked_host, blocked_path
    )
    task_prompt = _append_action_constraints(task_prompt, allow_actions, block_actions)
    violation = validate_action_constraints("persistent", extract_task_constraints(task_prompt))
    if violation is not None:
        err_console.print(f"[!] {violation}")
        raise typer.Exit(1)

    # Track stats
    all_cycle_results: list[PersistentCycleResult] = []
    interrupted = False

    def _on_cycle_step(round_num: int, cycle_num: int, result) -> None:
        """Real-time output for each step within a cycle."""
        console.print(f"[dim]-- Cycle {cycle_num} | Round {round_num} --[/]")
        console.print()

    def _on_cycle_complete(cycle_num: int, cycle_result: PersistentCycleResult) -> None:
        """Callback after each cycle completes."""
        all_cycle_results.append(cycle_result)
        console.print(
            Panel(
                f"Cycle {cycle_num} completed\n"
                f"   Steps executed: {cycle_result.total_steps}\n"
                f"   Total findings: {cycle_result.total_findings}\n"
                f"   New findings: {cycle_result.new_findings}\n"
                f"   Report: {cycle_result.report_path or 'not generated'}",
                title=f"Cycle {cycle_num} Result",
                border_style="green" if cycle_result.new_findings == 0 else "red",
            )
        )
        console.print()

    async def _run():
        async def runner(agent, _config):
            sink = TerminalStreamSink(console, _config.session.show_thinking)
            return await agent.persistent_pentest(
                user_input=task_prompt,
                target=target,
                rounds_per_cycle=rounds_per_cycle,
                max_cycles=max_cycles,
                auto_report=auto_report,
                on_cycle_step=_on_cycle_step,
                on_cycle_complete=_on_cycle_complete,
                stream_sink=sink,
                fresh_recon=fresh_recon,
            )

        return await _run_cli_orchestrated_task(
            command="persistent",
            target=target,
            resume=resume,
            snapshot=snapshot,
            runner=runner,
        )

    try:
        orchestrated = asyncio.run(_run())
    except KeyboardInterrupt:
        interrupted = True
        console.print("\n[!] User interrupted persistent pentest")
        orchestrated = None

    summary = (
        orchestrated.summary
        if orchestrated
        else {
            "findings_count": 0,
            "executed_steps": 0,
        }
    )
    total_findings = summary["findings_count"]
    total_steps = summary["executed_steps"]
    completed_cycles = len(all_cycle_results)

    console.print()
    console.print(
        Panel(
            f"{'Interrupted by user' if interrupted else 'Testing completed'}\n\n"
            f"  Completed cycles: [bold]{completed_cycles}[/]\n"
            f"  Steps executed: [bold]{total_steps}[/]\n"
            f"  Findings: [bold]{total_findings}[/]",
            title="Persistent Pentest Summary",
            border_style="red" if total_findings > 0 else "green",
        )
    )

    if auto_report and all_cycle_results:
        console.print("\n[bold]Cycle Reports[/]:")
        for cr in all_cycle_results:
            if cr.report_path and "failed" not in str(cr.report_path).lower():
                console.print(f"  Cycle {cr.cycle_num}: {cr.report_path}")


@app.command()
def recon(
    target: str = typer.Argument(..., help="Target host/IP/URL"),
    prompt: Optional[str] = typer.Option(
        None, "--prompt", help="Custom natural language prompt (overrides auto-generated prompt)"
    ),
    only_port: Optional[int] = typer.Option(
        None, "--only-port", help="Restrict testing to a single port"
    ),
    only_host: Optional[str] = typer.Option(
        None, "--only-host", help="Restrict testing to a single host"
    ),
    only_path: Optional[str] = typer.Option(
        None, "--only-path", help="Restrict testing to a single path"
    ),
    blocked_host: Optional[str] = typer.Option(
        None, "--blocked-host", help="Explicitly blocked host"
    ),
    blocked_path: Optional[str] = typer.Option(
        None, "--blocked-path", help="Explicitly blocked path"
    ),
    allow_actions: Optional[str] = typer.Option(
        None, "--allow-actions", help="Comma-separated allowed actions"
    ),
    block_actions: Optional[str] = typer.Option(
        None, "--block-actions", help="Comma-separated blocked actions"
    ),
    resume: bool = typer.Option(True, "--resume/--no-resume", help="Resume previous target state"),
    snapshot: Optional[str] = typer.Option(
        None, "--snapshot", help="Resume from a specific target snapshot id"
    ),
) -> None:
    """Run reconnaissance only."""
    task_prompt = prompt if prompt else f"Perform authorized reconnaissance against {target} without exploitation."
    task_prompt = _append_cli_constraints_compat(
        task_prompt, only_port, only_host, only_path, blocked_host, blocked_path
    )
    task_prompt = _append_action_constraints(task_prompt, allow_actions, block_actions)
    violation = validate_action_constraints("recon", extract_task_constraints(task_prompt))
    if violation is not None:
        err_console.print(f"[!] {violation}")
        raise typer.Exit(1)

    async def _run():
        async def runner(agent, _config):
            sink = TerminalStreamSink(console, _config.session.show_thinking)
            return await agent.chat(task_prompt, target=target, stream_sink=sink)

        await _run_cli_orchestrated_task(
            command="recon",
            target=target,
            resume=resume,
            snapshot=snapshot,
            runner=runner,
        )

    asyncio.run(_run())


@app.command()
def scan(
    target: str = typer.Argument(..., help="Target host/IP/URL"),
    ports: Optional[str] = typer.Option(None, help="Port range, e.g. 80,443,8080"),
    prompt: Optional[str] = typer.Option(
        None, "--prompt", help="Custom natural language prompt (overrides auto-generated prompt)"
    ),
    only_port: Optional[int] = typer.Option(
        None, "--only-port", help="Restrict testing to a single port"
    ),
    only_host: Optional[str] = typer.Option(
        None, "--only-host", help="Restrict testing to a single host"
    ),
    only_path: Optional[str] = typer.Option(
        None, "--only-path", help="Restrict testing to a single path"
    ),
    blocked_host: Optional[str] = typer.Option(
        None, "--blocked-host", help="Explicitly blocked host"
    ),
    blocked_path: Optional[str] = typer.Option(
        None, "--blocked-path", help="Explicitly blocked path"
    ),
    allow_actions: Optional[str] = typer.Option(
        None, "--allow-actions", help="Comma-separated allowed actions"
    ),
    block_actions: Optional[str] = typer.Option(
        None, "--block-actions", help="Comma-separated blocked actions"
    ),
    resume: bool = typer.Option(True, "--resume/--no-resume", help="Resume previous target state"),
    snapshot: Optional[str] = typer.Option(
        None, "--snapshot", help="Resume from a specific target snapshot id"
    ),
) -> None:
    """Run vulnerability scanning only."""
    port_hint = f", focusing on ports {ports}" if ports else ""
    task_prompt = prompt if prompt else f"Perform authorized vulnerability scanning against {target}{port_hint} without exploitation."
    task_prompt = _append_cli_constraints_compat(
        task_prompt, only_port, only_host, only_path, blocked_host, blocked_path
    )
    task_prompt = _append_action_constraints(task_prompt, allow_actions, block_actions)
    violation = validate_action_constraints("scan", extract_task_constraints(task_prompt))
    if violation is not None:
        err_console.print(f"[!] {violation}")
        raise typer.Exit(1)

    async def _run():
        async def runner(agent, _config):
            sink = TerminalStreamSink(console, _config.session.show_thinking)
            return await agent.chat(task_prompt, target=target, stream_sink=sink)

        await _run_cli_orchestrated_task(
            command="scan",
            target=target,
            resume=resume,
            snapshot=snapshot,
            runner=runner,
        )

    asyncio.run(_run())


@app.command("network-scan")
def network_scan(
    target: Optional[str] = typer.Argument(
        None, help="Target host/IP/CIDR. Defaults to the connected Wi-Fi subnet."
    ),
    profile: str = typer.Option(
        "adaptive",
        "--profile",
        help="Network scan profile: adaptive, fast, thorough, stealth",
    ),
    ports: Optional[str] = typer.Option(None, "--ports", help="Port range, e.g. 80,443,1-1000"),
    max_rounds: int = typer.Option(
        0, "--max-rounds", help="Agent follow-up rounds (0=use configured default)"
    ),
    parallel_agents: int = typer.Option(
        1,
        "--parallel-agents",
        min=1,
        help="Number of child agents to fan out across discovered surfaces (1 disables fan-out)",
    ),
    parallel_depth: int = typer.Option(
        1,
        "--parallel-depth",
        min=1,
        help="Bounded number of child-agent surface discovery waves",
    ),
    worker_rounds: int = typer.Option(
        3,
        "--worker-rounds",
        min=1,
        help="Agent rounds per child surface worker",
    ),
    surface_limit: int = typer.Option(
        20,
        "--surface-limit",
        min=1,
        help="Maximum discovered surfaces considered for child-agent fan-out",
    ),
    safe_probes: bool = typer.Option(
        True,
        "--safe-probes/--no-safe-probes",
        help="After nmap, perform only non-destructive verification probes by default",
    ),
    prompt: Optional[str] = typer.Option(
        None, "--prompt", help="Custom natural language prompt (overrides auto-generated prompt)"
    ),
    only_port: Optional[int] = typer.Option(
        None, "--only-port", help="Restrict testing to a single port"
    ),
    only_host: Optional[str] = typer.Option(
        None, "--only-host", help="Restrict testing to a single host"
    ),
    blocked_host: Optional[str] = typer.Option(
        None, "--blocked-host", help="Explicitly blocked host"
    ),
    allow_actions: Optional[str] = typer.Option(
        None, "--allow-actions", help="Comma-separated allowed actions"
    ),
    block_actions: Optional[str] = typer.Option(
        None, "--block-actions", help="Comma-separated blocked actions"
    ),
    resume: bool = typer.Option(True, "--resume/--no-resume", help="Resume previous target state"),
    snapshot: Optional[str] = typer.Option(
        None, "--snapshot", help="Resume from a specific target snapshot id"
    ),
) -> None:
    """Run nmap-based network scanning and weak-link follow-up."""
    normalized_profile = profile.strip().lower()
    if normalized_profile not in {"adaptive", "fast", "thorough", "stealth"}:
        err_console.print("[!] profile must be one of: adaptive, fast, thorough, stealth")
        raise typer.Exit(1)

    detected_wifi = None
    scan_target = target.strip() if target else ""
    if not scan_target:
        from vulnbot.agent.network_scan import detect_connected_wifi_target

        try:
            detected_wifi = detect_connected_wifi_target()
            scan_target = detected_wifi.cidr
        except RuntimeError as exc:
            err_console.print(f"[!] {exc}")
            raise typer.Exit(1)

    port_hint = f" limited to ports {ports}" if ports else ""
    follow_up = (
        "Then prioritize weak links and perform safe, non-destructive verification probes only."
        if safe_probes
        else "Then summarize weak links without running follow-up probes."
    )
    task_prompt = prompt if prompt else (
        f"Perform an authorized {normalized_profile} network scan against {scan_target}{port_hint}. "
        f"Use the nmap_scan tool with profile={normalized_profile}"
        f"{f' and ports={ports}' if ports else ''}. "
        f"{follow_up} Record open services and candidate weak-link findings in target state. "
        "Do not brute force credentials, run destructive payloads, or perform post-exploitation."
    )
    task_prompt = _append_cli_constraints_compat(
        task_prompt,
        only_port,
        only_host,
        None,
        blocked_host,
        None,
    )

    effective_allow_actions = allow_actions
    effective_block_actions = block_actions
    if safe_probes and not allow_actions and not block_actions:
        effective_allow_actions = "recon,scan"
    task_prompt = _append_action_constraints(
        task_prompt, effective_allow_actions, effective_block_actions
    )

    violation = validate_action_constraints("scan", extract_task_constraints(task_prompt))
    if violation is not None:
        err_console.print(f"[!] {violation}")
        raise typer.Exit(1)

    console.print(
        Panel(
            f"Target: [bold]{scan_target}[/]\n"
            + (
                f"Wi-Fi interface: [bold]{detected_wifi.interface}[/] ({detected_wifi.address})\n"
                if detected_wifi
                else ""
            )
            +
            f"Profile: [bold]{normalized_profile}[/]\n"
            f"Ports: [bold]{ports or 'profile default'}[/]\n"
            f"Follow-up: [bold]{'safe probes' if safe_probes else 'summary only'}[/]\n"
            f"Parallel agents: [bold]{parallel_agents}[/]"
            + (
                f" (depth {parallel_depth}, {worker_rounds} rounds/worker)"
                if parallel_agents > 1
                else ""
            ),
            title="Network Scan",
            border_style="cyan",
        )
    )

    async def _run():
        async def runner(agent, _config):
            sink = TerminalStreamSink(console, _config.session.show_thinking)
            rounds = max_rounds if max_rounds > 0 else _config.session.max_rounds
            if parallel_agents > 1:
                from vulnbot.agent.parallel_agents import run_parallel_pentest

                def agent_factory():
                    return agent.__class__(_config, getattr(agent, "mcp_manager", None))

                return await run_parallel_pentest(
                    agent,
                    agent_factory=agent_factory,
                    user_input=task_prompt,
                    target=scan_target,
                    discovery_rounds=rounds,
                    worker_rounds=worker_rounds,
                    max_agents=parallel_agents,
                    max_depth=parallel_depth,
                    surface_limit=surface_limit,
                    stream_sink=sink,
                )
            return await agent.auto_pentest(
                task_prompt,
                target=scan_target,
                max_rounds=rounds,
                stream_sink=sink,
            )

        await _run_cli_orchestrated_task(
            command="network-scan",
            target=scan_target,
            resume=resume,
            snapshot=snapshot,
            runner=runner,
        )

    asyncio.run(_run())


@app.command()
def exploit(
    target: str = typer.Argument(..., help="Target host/IP/URL"),
    cve: Optional[str] = typer.Option(None, help="Specific CVE to exploit"),
    cmd: str = typer.Option("id", help="Command to execute for verification"),
    prompt: Optional[str] = typer.Option(
        None, "--prompt", help="Custom natural language prompt (overrides auto-generated prompt)"
    ),
    only_port: Optional[int] = typer.Option(
        None, "--only-port", help="Restrict testing to a single port"
    ),
    only_host: Optional[str] = typer.Option(
        None, "--only-host", help="Restrict testing to a single host"
    ),
    only_path: Optional[str] = typer.Option(
        None, "--only-path", help="Restrict testing to a single path"
    ),
    blocked_host: Optional[str] = typer.Option(
        None, "--blocked-host", help="Explicitly blocked host"
    ),
    blocked_path: Optional[str] = typer.Option(
        None, "--blocked-path", help="Explicitly blocked path"
    ),
    allow_actions: Optional[str] = typer.Option(
        None, "--allow-actions", help="Comma-separated allowed actions"
    ),
    block_actions: Optional[str] = typer.Option(
        None, "--block-actions", help="Comma-separated blocked actions"
    ),
    resume: bool = typer.Option(True, "--resume/--no-resume", help="Resume previous target state"),
    snapshot: Optional[str] = typer.Option(
        None, "--snapshot", help="Resume from a specific target snapshot id"
    ),
) -> None:
    """Run exploitation only."""
    cve_hint = f" using {cve}" if cve else ""
    task_prompt = prompt if prompt else (
        f"Attempt authorized exploitation against {target}{cve_hint} and verify with command: {cmd}"
    )
    task_prompt = _append_cli_constraints_compat(
        task_prompt, only_port, only_host, only_path, blocked_host, blocked_path
    )
    task_prompt = _append_action_constraints(task_prompt, allow_actions, block_actions)
    violation = validate_action_constraints("exploit", extract_task_constraints(task_prompt))
    if violation is not None:
        err_console.print(f"[!] {violation}")
        raise typer.Exit(1)

    async def _run():
        async def runner(agent, _config):
            sink = TerminalStreamSink(console, _config.session.show_thinking)
            return await agent.chat(task_prompt, target=target, stream_sink=sink)

        await _run_cli_orchestrated_task(
            command="exploit",
            target=target,
            resume=resume,
            snapshot=snapshot,
            runner=runner,
        )

    asyncio.run(_run())


@app.command()
def report(
    session: str = typer.Argument(
        ..., help="Path to session JSON file or target when used with --target"
    ),
    target_mode: bool = typer.Option(
        False, "--target", help="Interpret argument as target and generate report from target state"
    ),
    pdf: bool = typer.Option(
        False, "--pdf", help="Also export the report to PDF (requires the vulnbot[pdf] extra)"
    ),
    pdf_out: str = typer.Option(
        "", "--pdf-out", help="PDF output path (default: the report path with a .pdf suffix)"
    ),
) -> None:
    """Generate a report from a session file or target state."""
    if target_mode:
        from vulnbot.report.generator import generate_report_from_target_state

        state = load_target_state(session)
        if not state:
            err_console.print(f"[!] Target state not found: {session}")
            raise typer.Exit(1)
        report_path = generate_report_from_target_state(state)
    else:
        from vulnbot.report.generator import generate_report_from_file

        report_path = generate_report_from_file(session)
    console.print(f"[+] Report generated: {report_path}")

    if pdf:
        from pathlib import Path

        from vulnbot.report.pdf_exporter import export_pdf

        out = Path(pdf_out) if pdf_out else Path(report_path).with_suffix(".pdf")
        try:
            markdown = Path(report_path).read_text(encoding="utf-8")
            export_pdf(markdown, out, title="VulnBot Report")
        except RuntimeError as exc:
            err_console.print(f"[!] {exc}")
            raise typer.Exit(1) from exc
        console.print(f"[+] PDF exported: {out}")


def _print_cli_manual(topic: Optional[str], output_format: str) -> None:
    """Print the packaged CLI manual, normalizing user-facing errors."""
    try:
        console.out(render_manual(output_format, topic), end="")
    except ValueError as exc:
        err_console.print(f"[!] {exc}")
        err_console.print(f"    Available topics: {', '.join(available_topics())}")
        raise typer.Exit(1) from exc


@app.command("manual")
def manual_command(
    topic: Optional[str] = typer.Argument(
        None, help="Optional manual topic, e.g. run, network-scan, config"
    ),
    output_format: str = typer.Option(
        "text",
        "--format",
        "-f",
        help="Output format: text, markdown, man",
    ),
) -> None:
    """Print the full VulnBot CLI manual."""
    _print_cli_manual(topic, output_format)


@app.command("man")
def man_command(
    topic: Optional[str] = typer.Argument(
        None, help="Optional manual topic, e.g. run, network-scan, config"
    ),
    output_format: str = typer.Option(
        "text",
        "--format",
        "-f",
        help="Output format: text, markdown, man",
    ),
) -> None:
    """Alias for 'vulnbot manual'."""
    _print_cli_manual(topic, output_format)



config_app = typer.Typer(help="Manage configuration")
app.add_typer(config_app, name="config")


@config_app.callback(invoke_without_command=True)
def config_root(ctx: typer.Context) -> None:
    """Open the interactive config editor when no subcommand is provided."""
    if ctx.resilient_parsing or ctx.invoked_subcommand is not None:
        return
    run_config_tui()


@config_app.command("set")
def config_set(
    key: str = typer.Argument(..., help="Config key in dot notation, e.g. llm.api_key"),
    value: str = typer.Argument(..., help="Config value"),
) -> None:
    """Set a config value."""
    set_config_value(key, value)
    console.print(
        f"[+] Set {key} = {'***' if 'key' in key.lower() or 'pass' in key.lower() else value}"
    )


@config_app.command("get")
def config_get(
    key: str = typer.Argument(..., help="Config key in dot notation"),
) -> None:
    """Get a config value."""
    config = load_config()
    parts = key.split(".")
    obj = config
    for part in parts:
        obj = getattr(obj, part)
    value = obj if not hasattr(obj, "model_dump") else obj.model_dump()
    if isinstance(value, str) and ("key" in key.lower() or "pass" in key.lower()):
        value = value[:8] + "..." if len(value) > 8 else "***"
    console.print(f"{key} = {value}")


@config_app.command("list")
def config_list() -> None:
    """List all configuration values."""
    import yaml as _yaml

    config = load_config()
    raw = config.model_dump(mode="json")
    console.print(_yaml.dump(raw, default_flow_style=False, allow_unicode=True))


@config_app.command("provider")
def config_provider(
    name: Optional[str] = typer.Argument(
        None, help="Provider name to switch to (e.g. minimax, deepseek)"
    ),
    list_all: bool = typer.Option(False, "--list", "-l", help="List all available providers"),
) -> None:
    """View or switch the configured LLM provider."""
    if list_all or name is None:
        providers = list_providers()
        current_config = load_config()
        current_provider = current_config.llm.provider

        console.print("[bold]Available LLM Providers[/]")
        console.print()
        for p in providers:
            is_current = p["provider"] == current_provider
            marker = " [green](current)[/]" if is_current else ""
            console.print(f"  [bold cyan]{p['provider']}[/]{marker}")
            console.print(f"    Label: {p['label']}")
            console.print(f"    URL:  [dim]{p['base_url']}[/]")
            console.print(f"    Model: [dim]{p['default_model']}[/]")
            console.print()
        console.print("[dim]Use vulnbot config provider <name> to switch providers.[/]")
        return

    # Switch provider
    from vulnbot.config.schema import PROVIDER_PRESETS, LLMProvider

    # Validate provider name
    try:
        provider_enum = LLMProvider(name.lower())
    except ValueError:
        console.print(f"[!] Unknown provider: [bold]{name}[/]")
        console.print(f"    Available: {', '.join(p.value for p in LLMProvider)}")
        console.print("    Tip: use [bold]custom[/] for a manual base_url and model.")
        raise typer.Exit(1)

    config = load_config()
    config = apply_provider_preset(config, name.lower())
    save_config(config)

    preset = PROVIDER_PRESETS.get(provider_enum, {})
    label = preset.get("label", name)
    console.print(f"[+] Switched LLM provider to [bold cyan]{label}[/]")
    console.print(f"    Base URL: [dim]{config.llm.base_url}[/]")
    console.print(f"    Model:    [dim]{config.llm.model}[/]")

    if not config.llm.api_key:
        console.print()
        console.print(
            "[yellow]Set an API key first: [bold]vulnbot config set llm.api_key <your-key>[/][/]"
        )




@app.command()
def init() -> None:
    """Initialize VulnBot config."""
    from vulnbot.config.settings import ensure_dirs

    ensure_dirs()

    config = load_config()
    save_config(config)
    console.print(_("cli.init.config_created"))
    console.print(_("cli.init.dirs_initialized"))
    console.print(_("cli.init.dir_sessions"))
    console.print(_("cli.init.dir_kb"))
    console.print(_("cli.init.dir_skills"))
    console.print()
    console.print(_("cli.init.next_steps"))
    console.print(_("cli.init.step_provider"))
    console.print(_("cli.init.step_api_key"))
    console.print(_("cli.init.step_cli"))
    console.print(_("cli.init.step_tui"))




@app.command()
def doctor() -> None:
    """Inspect the VulnBot runtime environment."""
    import shutil

    from vulnbot.web.services.mcp_service import get_mcp_diagnostics

    console.print("[bold]VulnBot Environment Check[/]")
    console.print()

    # Check Python
    console.print(f"  Python: [green]{sys.version.split()[0]}[/]")

    # Check Node.js
    node_path = shutil.which("node")
    if node_path:
        import subprocess

        try:
            result = subprocess.run(
                [node_path, "--version"], capture_output=True, text=True, timeout=5
            )
            console.print(f"  Node.js: [green]{result.stdout.strip()}[/]")
        except Exception:
            console.print("  Node.js: [yellow]check failed[/]")
    else:
        console.print("  Node.js: [red]not installed[/] (required for some MCP services)")

    # Check npx
    npx_path = shutil.which("npx")
    console.print(
        f"  npx: [{'green' if npx_path else 'red'}]{'installed' if npx_path else 'missing'}[/]"
    )

    # Check uvx
    uvx_path = shutil.which("uvx")
    console.print(
        f"  uvx: [{'green' if uvx_path else 'yellow'}]{'installed' if uvx_path else 'missing'}[/]"
    )

    # Check nmap
    nmap_path = shutil.which("nmap")
    console.print(
        f"  nmap: [{'green' if nmap_path else 'yellow'}]{'installed' if nmap_path else 'optional/missing'}[/]"
    )

    # Check config
    config = load_config()
    console.print()
    console.print("[bold]LLM Config[/]:")
    has_key = bool(config.llm.api_key)
    console.print(f"  Provider: [bold cyan]{config.llm.provider}[/]")
    console.print(
        f"  API Key: [{'green' if has_key else 'red'}]{'configured' if has_key else 'not set'}[/]"
    )
    console.print(f"  Base URL: [dim]{config.llm.base_url}[/]")
    console.print(f"  Model: [dim]{config.llm.model}[/]")

    # Check MCP servers
    console.print()
    console.print("[bold]MCP Services[/]:")
    mcp_diag = get_mcp_diagnostics()
    console.print(f"  Registered: [bold]{mcp_diag.total_services}[/] services")
    console.print(f"  Tools: [bold]{mcp_diag.tool_count}[/] exposed")

    for item in mcp_diag.services:
        status = "[green]enabled[/]" if item.enabled else "[dim]disabled[/]"
        priority_label = {0: "P0", 1: "P1", 2: "P2"}.get(item.priority, "??")
        running = "[green]running[/]" if item.running else "[yellow]registered[/]"
        capability = "[green]exec[/]" if item.can_execute else "[yellow]schema-only[/]"
        console.print(
            f"  {item.name}: {status} [{priority_label}] {running} mode={item.execution_mode} {capability} tools={item.tool_count}"
        )
        if item.error:
            label = item.last_error_type or "error"
            console.print(f"    [red]{label}[/]: {item.error}")

    console.print(
        "[dim]doctor shows MCP registration state and exposed tools. fetch/memory run in local mode; most other services are still placeholders.[/]"
    )
    console.print(
        "[yellow]python_execute is a high-risk experimental capability. It is not a strong sandbox; use it only in authorized or controlled environments.[/]"
    )
    console.print(
        "[dim]The knowledge-base update flow is live; retrieval enhancements can continue independently.[/]"
    )

    console.print()
    if has_key:
        console.print("[green]Environment ready. Run [bold]vulnbot[/] to start.[/]")
    else:
        console.print(
            "[yellow]Set an API key first: [bold]vulnbot config set llm.api_key <key>[/][/]"
        )



kb_app = typer.Typer(help="Security knowledge base commands")
app.add_typer(kb_app, name="kb")

target_state_app = typer.Typer(help="Manage target history state")
app.add_typer(target_state_app, name="target-state")


@kb_app.command("update")
def kb_update() -> None:
    """Update the knowledge base."""
    console.print("[*] Updating knowledge base...")
    from vulnbot.kb.store import KnowledgeStore
    from vulnbot.kb.updater import seed_knowledge_base

    store = KnowledgeStore()
    before_stats = store.get_stats()
    seed_knowledge_base(store)
    after_stats = store.get_stats()

    before_total = sum(before_stats.values())
    after_total = sum(after_stats.values())
    delta = after_total - before_total
    category_summary = ", ".join(f"{cat}={count}" for cat, count in sorted(after_stats.items()))

    console.print(f"[+] Knowledge base updated: +{delta} entries")
    console.print(f"    Categories: {category_summary or 'empty'}")


@kb_app.command("status")
def kb_status() -> None:
    """Show the knowledge base retrieval backend status."""
    from vulnbot.kb.retriever import KnowledgeRetriever, RetrieverStatus
    from vulnbot.kb.store import KnowledgeStore

    store = KnowledgeStore()
    retriever = KnowledgeRetriever(store=store)
    status = retriever.get_status()
    detail = retriever.get_status_detail()
    stats = store.get_stats()
    total = sum(stats.values())
    category_summary = ", ".join(f"{cat}={count}" for cat, count in sorted(stats.items()))

    if status == RetrieverStatus.CHROMADB_ACTIVE:
        line = "[green]+ Knowledge base enabled (ChromaDB semantic retrieval)[/green]"
    elif status == RetrieverStatus.KEYWORD_FALLBACK:
        line = "[yellow]! Knowledge base using keyword fallback (chromadb not installed)[/yellow]"
    else:
        line = "[red]x Knowledge base disabled (no available data)[/red]"

    console.print(
        Panel(
            f"{line}\n"
            f"Backend: [bold]{status.value}[/]\n"
            f"Detail: {detail or 'n/a'}\n"
            f"Entries: [bold]{total}[/] ({category_summary or 'empty'})\n"
            f"Semantic search: run [bold]pip install vulnbot\\[kb][/] to enable ChromaDB",
            title="KB Status",
            border_style="cyan",
        )
    )


@target_state_app.command("list")
def target_state_list(
    target: str = typer.Argument(..., help="Target host/IP/URL"),
) -> None:
    """List target snapshots."""
    snapshots = list_target_snapshots(target)
    if not snapshots:
        console.print(f"[-] No snapshots found for: {target}")
        raise typer.Exit(1)

    console.print(f"[bold]Target snapshots[/]: {target}")
    for item in snapshots[:20]:
        console.print(
            f"  {item['snapshot_id']} | v{item.get('schema_version', 1)} | {item['last_command']} | "
            f"steps={item['executed_steps']} verified={item['verified_findings']} pending={item['pending_findings']}"
        )


@target_state_app.command("preview")
def target_state_preview_cmd(
    target: str = typer.Argument(..., help="Target host/IP/URL"),
    snapshot_id: Optional[str] = typer.Option(
        None, "--snapshot", help="Preview a specific snapshot id"
    ),
) -> None:
    """Show a resume preview for the target state."""
    preview = get_target_state_preview(target, snapshot_id=snapshot_id)
    if not preview:
        console.print(f"[-] No target state found: {target}")
        raise typer.Exit(1)

    console.print(
        Panel(
            f"Target: [bold]{preview['target']}[/]\n"
            f"Schema: [bold]v{preview['schema_version']}[/]\n"
            f"Phase: [bold]{preview['phase'] or 'unknown'}[/]\n"
            f"Resume strategy: [bold]{preview['resume_strategy'] or 'none'}[/]\n"
            f"Reason: {preview['resume_reason'] or 'n/a'}\n"
            f"Findings: {preview['verified_count']} verified / {preview['pending_count']} pending / {preview['findings_count']} total",
            title="Target Preview",
            border_style="cyan",
        )
    )

    if preview.get("priority_targets"):
        console.print("[bold]Priority targets[/]:")
        for item in preview["priority_targets"][:5]:
            console.print(f"  - {item}")
    if preview.get("priority_recon_assets"):
        console.print("[bold]Priority recon assets[/]:")
        for item in preview["priority_recon_assets"][:5]:
            console.print(f"  - {item}")
    if preview.get("next_actions"):
        console.print("[bold]Next actions[/]:")
        for item in preview["next_actions"][:5]:
            console.print(f"  - {item}")


@target_state_app.command("diff")
def target_state_diff_cmd(
    target: str = typer.Argument(..., help="Target host/IP/URL"),
    from_snapshot_id: str = typer.Argument(..., help="Base snapshot id"),
    to_snapshot_id: Optional[str] = typer.Option(
        None, "--to", help="Compare against another snapshot or current state"
    ),
) -> None:
    """Show differences between two target-state snapshots."""
    diff = diff_target_state_snapshots(target, from_snapshot_id, to_snapshot_id=to_snapshot_id)
    if not diff:
        console.print(f"[-] Unable to diff target state: {target}")
        raise typer.Exit(1)

    console.print(
        Panel(
            f"Target: [bold]{diff['target']}[/]\n"
            f"From: [bold]{diff['from_snapshot_id']}[/] -> To: [bold]{diff['to_snapshot_id']}[/]\n"
            f"Schema: v{diff['schema_version_from']} -> v{diff['schema_version_to']}\n"
            f"Resume strategy: {diff['resume_strategy_from'] or 'none'} -> {diff['resume_strategy_to'] or 'none'}",
            title="Target Diff",
            border_style="magenta",
        )
    )

    for title, items in (
        ("Added findings", diff.get("added_findings", [])),
        ("Removed findings", diff.get("removed_findings", [])),
        ("Updated findings", diff.get("updated_findings", [])),
        ("Added recon assets", diff.get("added_recon_assets", [])),
        ("Removed recon assets", diff.get("removed_recon_assets", [])),
        ("Added steps", diff.get("added_steps", [])),
        ("Removed steps", diff.get("removed_steps", [])),
        ("Added notes", diff.get("added_notes", [])),
        ("Removed notes", diff.get("removed_notes", [])),
    ):
        if items:
            console.print(f"[bold]{title}[/]:")
            for item in items[:10]:
                console.print(f"  - {item}")


@target_state_app.command("rollback")
def target_state_rollback_cmd(
    target: str = typer.Argument(..., help="Target host/IP/URL"),
    snapshot_id: str = typer.Argument(..., help="Snapshot id to restore"),
) -> None:
    """Rollback target state to a snapshot."""
    path = rollback_target_state(target, snapshot_id)
    if not path:
        console.print(f"[-] Snapshot not found: {snapshot_id}")
        raise typer.Exit(1)
    console.print(f"[+] Rolled back target state: {target}")
    console.print(f"    Snapshot: {snapshot_id}")


@target_state_app.command("clear")
def target_state_clear_cmd(
    target: str = typer.Argument(..., help="Target host/IP/URL"),
) -> None:
    """Clear target state."""
    ok = clear_target_state(target)
    if not ok:
        console.print(f"[-] No target state found: {target}")
        raise typer.Exit(1)
    console.print(f"[+] Cleared target state: {target}")


# Default command (no sub-command -> REPL)



def _should_auto_pentest(user_input: str, current_target: Optional[str]) -> bool:
    """Determine if user input should trigger the autonomous pentest loop."""
    input_lower = user_input.lower()

    auto_keywords = [
        "pentest",
        "penetration test",
        "security test",
        "full test",
        "auto",
        "autonomous",
        "get flag",
        "find flag",
        "challenge",
        "ctf",
        "bypass",
        "brute",
        "bruteforce",
        "recon",
        "reconnaissance",
        "osint",
        "intelligence",
        "analyze target",
        "target analysis",
        "asset discovery",
        "directory scan",
        "probe",
        "explore",
        "investigate",
        "enumerate",
        "comprehensive analysis",
        "deep analysis",
        "detailed analysis",
        "full scan",
        "subdomain",
    ]

    single_step_keywords = ["generate report", "report", "help"]

    if any(kw in input_lower for kw in single_step_keywords) and not any(
        kw in input_lower for kw in auto_keywords
    ):
        return False

    if any(kw in input_lower for kw in auto_keywords):
        has_target = bool(current_target) or bool(_extract_target_from_input(user_input))
        return has_target

    has_target = bool(current_target) or bool(_extract_target_from_input(user_input))
    if has_target:
        multi_step_indicators = [
            "and then",
            "then",
            "output",
            "save",
            "write to",
            "export",
            "all",
            "complete",
            "detailed",
        ]
        if any(ind in input_lower for ind in multi_step_indicators):
            return True

    return False

def _extract_target_from_input(user_input: str) -> Optional[str]:
    """Extract target from user input string."""
    import re

    # Try to find URL (with optional port)
    url_match = re.search(r"(https?://[a-zA-Z0-9][-a-zA-Z0-9.:]*)", user_input)
    if url_match:
        return url_match.group(1).rstrip("/")
    # Try to find IP address
    ip_match = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", user_input)
    if ip_match:
        return ip_match.group(1)
    # Try to find domain
    domain_match = re.search(r"([a-zA-Z0-9][-a-zA-Z0-9]*(?:\.[a-zA-Z0-9][-a-zA-Z0-9]*)+)", user_input)
    if domain_match:
        return domain_match.group(1)
    return None


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        help="Show version and exit.",
        is_eager=True,
    ),
    show_manual: bool = typer.Option(
        False,
        "--man",
        "--manual",
        help="Show the full CLI manual and exit.",
        is_eager=True,
    ),
) -> None:
    """Open the classic CLI/REPL by default."""
    if version:
        console.print(__version__)
        raise typer.Exit()
    if show_manual:
        _print_cli_manual(None, "text")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        _run_repl()


def _auto_save_recon_report(agent, user_input: str, config) -> None:
    """Auto-save a recon report after auto_pentest completes when user requested file output."""
    import re
    from datetime import datetime

    try:
        state = agent.session_state
        target = state.target or "unknown"

        # Determine output path
        # Check if user specified a path
        path_match = re.search(
            r"(?:save to|write to|output to|export to)\s+([^\s,]+)",
            user_input,
            re.IGNORECASE,
        )
        if path_match:
            output_path = path_match.group(1)
        else:
            safe_name = re.sub(r"[^\w]", "_", target)[:30]
            date_str = datetime.now().strftime("%Y%m%d_%H%M")
            output_path = str(config.session.output_dir / f"{safe_name}_recon_{date_str}.md")

        from vulnbot.report.generator import generate_report

        generate_report(
            state,
            output_path,
            report_format=config.session.report_format,
        )

        console.print(f"\n[+] Recon report saved: {output_path}")

    except Exception as e:
        console.print(f"\n[!] Failed to auto-save report: {e}")


@app.command()
def repl() -> None:
    """Start the classic natural-language REPL."""
    _run_repl()


@app.command()
def tui(
    target: Optional[str] = typer.Option(
        None,
        "--target",
        "-t",
        help="Pre-fill the authorized target for the TUI.",
    ),
    mode: str = typer.Option(
        "standard",
        "--mode",
        "-m",
        help="Pre-fill check mode: quick, standard, deep, continuous.",
    ),
    only_port: Optional[int] = typer.Option(
        None,
        "--only-port",
        help="Pre-fill a single allowed test port.",
    ),
    only_host: Optional[str] = typer.Option(
        None,
        "--only-host",
        help="Pre-fill a single allowed host.",
    ),
    only_path: Optional[str] = typer.Option(
        None,
        "--only-path",
        help="Pre-fill a single allowed path.",
    ),
    blocked_host: Optional[str] = typer.Option(
        None,
        "--blocked-host",
        help="Pre-fill an explicitly blocked host.",
    ),
    blocked_path: Optional[str] = typer.Option(
        None,
        "--blocked-path",
        help="Pre-fill an explicitly blocked path.",
    ),
    allow_actions: Optional[str] = typer.Option(
        None,
        "--allow-actions",
        help="Pre-fill comma-separated allowed actions.",
    ),
    block_actions: Optional[str] = typer.Option(
        None,
        "--block-actions",
        help="Pre-fill comma-separated blocked actions.",
    ),
    resume: bool = typer.Option(True, "--resume/--no-resume", help="Resume target history."),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Render the launch summary and exit without starting a task.",
    ),
    once: bool = typer.Option(
        False,
        "--once",
        help="Render the TUI dashboard once and exit (useful for smoke tests).",
    ),
) -> None:
    """Open the terminal UI workbench."""
    from vulnbot.cli.tui import (
        MODES,
        build_state_from_options,
        build_task_draft,
        render_task_summary,
        run_tui,
    )

    if mode not in MODES:
        err_console.print("[!] Unknown TUI mode. Use one of: quick, standard, deep, continuous")
        raise typer.Exit(1)

    state = build_state_from_options(
        target=target or "",
        mode=mode,  # type: ignore[arg-type]
        only_host=only_host or "",
        only_port=only_port,
        only_path=only_path or "",
        blocked_host=blocked_host or "",
        blocked_path=blocked_path or "",
        allow_actions=allow_actions,
        block_actions=block_actions,
        resume=resume,
    )

    if dry_run:
        console.out(render_task_summary(build_task_draft(state)), end="")
        return

    if once and target:
        from vulnbot.cli.tui import render_tui_home

        console.out(render_tui_home(state), end="")
        return

    run_tui(once=once, initial_state=state)


@app.command()
def web(
    host: str = typer.Option(
        "127.0.0.1", "--host", help="Web server host (default: localhost only)"
    ),
    port: int = typer.Option(7788, "--port", help="Web server port"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Validate and print launch info without starting the server"
    ),
    allow_remote: bool = typer.Option(
        False, "--allow-remote", help="Explicitly allow binding the Web UI to a non-local address"
    ),
) -> None:
    """Run the local Web UI."""
    if not _is_loopback_bind_host(host):
        if not allow_remote:
            err_console.print(
                "[!] Refusing to bind the Web UI to a non-local address without --allow-remote."
            )
            raise typer.Exit(1)
        console.print(
            "[yellow]Warning: keep the Web UI bound to 127.0.0.1 unless you know what you're doing.[/]"
        )

    from vulnbot.web.app import FASTAPI_AVAILABLE

    console.print(
        Panel(
            f"Host: [bold]{host}[/]\n"
            f"Port: [bold]{port}[/]\n"
            f"FastAPI: [{'green' if FASTAPI_AVAILABLE else 'yellow'}]{'installed' if FASTAPI_AVAILABLE else 'missing'}[/]\n"
            f"URL: [bold]http://{host}:{port}[/]",
            title="VulnBot Web UI",
            border_style="cyan",
        )
    )

    if dry_run:
        console.print("[green]Web UI dry-run completed.[/]")
        return

    if not FASTAPI_AVAILABLE:
        err_console.print(
            "[!] FastAPI is missing. Install with [bold]pip install vulnbot[web][/]."
        )
        raise typer.Exit(1)

    try:
        import uvicorn
    except ImportError:
        err_console.print(
            "[!] uvicorn is missing. Install with [bold]pip install vulnbot[web][/]."
        )
        raise typer.Exit(1)

    from vulnbot.web.app import create_app

    uvicorn.run(create_app(), host=host, port=port, log_level="info")


def _is_loopback_bind_host(host: str) -> bool:
    """Return True when a requested bind host is loopback-only."""
    normalized = host.strip().strip("[]").lower()
    if normalized in {"localhost", "127.0.0.1", "::1"}:
        return True
    try:
        import ipaddress

        return ipaddress.ip_address(normalized).is_loopback
    except ValueError:
        return False


if __name__ == "__main__":
    app()
