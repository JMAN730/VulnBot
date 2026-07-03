"""TUI helpers for the VulnBot CLI."""


from __future__ import annotations

import io
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Literal, Optional

from rich import box
from rich.console import Console, Group
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text

from vulnbot.config.schema import MCPServerConfig, MCPTransportConfig
from vulnbot.config.settings import (
    BUILTIN_MCP_SERVERS,
    apply_provider_preset,
    fetch_provider_models,
    list_providers,
    load_config,
    save_config,
)
from vulnbot.i18n import _, init_i18n
from vulnbot.skills.dispatcher import SkillDispatcher
from vulnbot.skills.loader import load_skill_by_name
from vulnbot.target_state.store import get_target_state_preview, list_target_snapshots

# -- opencode-inspired colour palette --
C_PRIMARY = "#fab283"         # warm peach  – key indicators, selections
C_SECONDARY = "#5c9cf5"       # soft blue   – info, mode labels
C_ACCENT = "#9d7cd8"          # purple      – titles, headings
C_SUCCESS = "#7fd88f"         # green       – ok / configured
C_WARNING = "#f5a742"         # orange      – attention needed
C_ERROR = "#e06c75"           # red         – errors
C_MUTED = "#808080"           # muted gray  – secondary / dim text
C_TEXT = "#eeeeee"            # near-white  – body text
C_BORDER = "#484848"          # mid-gray    – panel borders
C_BORDER_SUBTLE = "#3c3c3c"   # dark-gray   – inner / subtle borders

# -- i18n boot --
_config_holder = [None]


def _init_tui_i18n() -> None:
    """Initialize i18n for TUI with config language setting."""
    config = load_config()
    _config_holder[0] = config
    session_lang = getattr(config.session, "language", "auto") if config else "auto"
    init_i18n(lang=session_lang if session_lang != "auto" else None, config=config)


_init_tui_i18n()


def rebuild_translations() -> None:
    """Rebuild MODES, SLASH_COMMANDS, MENU_ITEMS after i18n language switch.

    Call this after init_i18n() with a new language to update all
    module-level globals that were built with _() translations.
    """
    global MODES, MENU_ITEMS, SLASH_COMMANDS
    MODES = _build_modes()
    MENU_ITEMS = _build_menu_items()
    SLASH_COMMANDS = _build_slash_commands()


CheckMode = Literal["quick", "standard", "deep", "continuous"]
TaskCommand = Literal["recon", "run", "scan", "persistent"]


@dataclass(frozen=True)
class TuiMode:
    key: CheckMode
    label: str
    command: TaskCommand
    description: str
    allow_actions: tuple[str, ...]
    block_actions: tuple[str, ...] = ()
    needs_extra_confirm: bool = False


@dataclass
class TuiState:
    target: str = ""
    mode: CheckMode = "standard"
    only_host: str = ""
    only_port: str = ""
    only_path: str = ""
    blocked_host: str = ""
    blocked_path: str = ""
    allow_actions: list[str] = field(default_factory=list)
    block_actions: list[str] = field(default_factory=list)
    resume: bool = True


@dataclass(frozen=True)
class TuiTargetOverview:
    """Small, safe-to-render summary of the selected target history."""

    target: str
    has_history: bool
    snapshot_count: int = 0
    phase: str = "unknown"
    findings_count: int = 0
    verified_count: int = 0
    pending_count: int = 0
    constraints_summary: str = field(default_factory=lambda: _("tui.constraints_not_recorded"))
    violations_count: int = 0
    last_command: str = ""
    error: str = ""


@dataclass(frozen=True)
class TuiRuntimeDiagnostic:
    """Runtime readiness summary shown inside the TUI."""

    python_version: str
    node_version: str = "missing"
    npx_status: str = "missing"
    uvx_status: str = "missing"
    nmap_status: str = "optional/missing"
    provider: str = "unknown"
    model: str = "unknown"
    api_key_configured: bool = False
    mcp_total_services: int = 0
    mcp_running_services: int = 0
    mcp_local_services: int = 0
    mcp_placeholder_services: int = 0
    mcp_tool_count: int = 0
    mcp_error: str = ""


@dataclass(frozen=True)
class TuiTaskDraft:
    command: TaskCommand
    target: str
    only_host: str | None = None
    only_port: int | None = None
    only_path: str | None = None
    blocked_host: str | None = None
    blocked_path: str | None = None
    allow_actions: tuple[str, ...] = ()
    block_actions: tuple[str, ...] = ()
    resume: bool = True

    @property
    def command_line(self) -> str:
        """Return a copyable command line for the current draft."""
        return " ".join(build_command_preview_args(self))


TaskLauncher = Callable[[TuiTaskDraft], None]


def _build_modes() -> dict[CheckMode, TuiMode]:
    """Build MODES dict with translated labels and descriptions."""
    return {
        "quick": TuiMode(
            key="quick",
            label=_("tui.mode_quick"),
            command="recon",
            description=_("tui.mode_quick_desc"),
            allow_actions=("recon",),
            block_actions=("exploit", "persistent", "post_exploitation"),
        ),
        "standard": TuiMode(
            key="standard",
            label=_("tui.mode_standard"),
            command="run",
            description=_("tui.mode_standard_desc"),
            allow_actions=("recon", "scan"),
            block_actions=("post_exploitation",),
        ),
        "deep": TuiMode(
            key="deep",
            label=_("tui.mode_deep"),
            command="scan",
            description=_("tui.mode_deep_desc"),
            allow_actions=("recon", "scan", "exploit"),
            needs_extra_confirm=True,
        ),
        "continuous": TuiMode(
            key="continuous",
            label=_("tui.mode_continuous"),
            command="persistent",
            description=_("tui.mode_continuous_desc"),
            allow_actions=("recon", "scan"),
            block_actions=("post_exploitation",),
            needs_extra_confirm=True,
        ),
    }


def _build_menu_items() -> dict[str, str]:
    """Build MENU_ITEMS dict with translated labels."""
    return {
        "1": _("tui.menu_set_target"),
        "2": _("tui.menu_select_mode"),
        "3": _("tui.menu_set_scope"),
        "4": _("tui.menu_start"),
        "5": _("tui.menu_history"),
        "6": _("tui.menu_report"),
        "7": _("tui.menu_diagnostic"),
        "8": _("tui.menu_config"),
        "q": _("tui.menu_exit"),
    }


MODES: dict[CheckMode, TuiMode] = _build_modes()
MENU_ITEMS: dict[str, str] = _build_menu_items()


def render_tui_home(state: TuiState | None = None, *, width: int = 110) -> str:
    """Render the TUI home surface into plain text for tests and dry-runs."""
    console = Console(
        file=io.StringIO(),
        record=True,
        width=width,
        force_terminal=False,
        color_system=None,
    )
    config = load_config()
    console.print(build_dashboard(config, state or TuiState()))
    return console.export_text()


def build_state_from_options(
    *,
    target: str = "",
    mode: CheckMode = "standard",
    only_host: str = "",
    only_port: str | int | None = "",
    only_path: str = "",
    blocked_host: str = "",
    blocked_path: str = "",
    allow_actions: str | tuple[str, ...] | list[str] | None = None,
    block_actions: str | tuple[str, ...] | list[str] | None = None,
    resume: bool = True,
) -> TuiState:
    """Build a TUI state object from CLI flags or tests."""
    return TuiState(
        target=target.strip(),
        mode=mode,
        only_host=only_host.strip(),
        only_port=str(only_port or "").strip(),
        only_path=only_path.strip(),
        blocked_host=blocked_host.strip(),
        blocked_path=blocked_path.strip(),
        allow_actions=_parse_action_csv(allow_actions),
        block_actions=_parse_action_csv(block_actions),
        resume=resume,
    )


def build_dashboard(config, state: TuiState) -> Group:
    """Build the first-screen VulnBot TUI dashboard."""
    mode = MODES[state.mode]
    provider = getattr(config.llm, "provider", "unknown")
    model = getattr(config.llm, "model", "unknown")
    api_ready = bool(getattr(config.llm, "api_key", ""))
    overview = build_target_overview(state.target)

    title = Text(" VulnBot TUI", style=f"bold {C_ACCENT}")
    subtitle = Text(f"  {_('tui.desc')}", style=f"{C_MUTED}")
    header = Panel(
        Group(title, subtitle),
        border_style=C_BORDER,
        box=box.ROUNDED,
        padding=(1, 2),
    )

    status = Table.grid(expand=True)
    status.add_column(ratio=1)
    status.add_column(ratio=1)
    status.add_column(ratio=1)
    status.add_row(
        _metric_panel(_("tui.authorized_target"), state.target or _("tui.target_not_set"), C_WARNING if not state.target else C_SUCCESS),
        _metric_panel(_("tui.check_mode"), f"{mode.label}  ·  {mode.command}", C_SECONDARY),
        _metric_panel(_("tui.ai_model"), f"{provider}  ·  {model}", C_SUCCESS if api_ready else C_WARNING),
    )

    scope_table = Table(box=box.ROUNDED, expand=True, show_header=True, border_style=C_BORDER_SUBTLE)
    scope_table.add_column(_("tui.test_scope"), style=f"bold {C_PRIMARY}")
    scope_table.add_column(_("tui.current_value"), style=C_TEXT)
    scope_table.add_row(_("tui.only_host"), state.only_host or _("tui.only_host_default"))
    scope_table.add_row(_("tui.only_port"), state.only_port or _("tui.only_port_default"))
    scope_table.add_row(_("tui.only_path"), state.only_path or _("tui.only_path_default"))
    scope_table.add_row(_("tui.blocked_host"), state.blocked_host or _("tui.blocked_host_default"))
    scope_table.add_row(_("tui.blocked_path"), state.blocked_path or _("tui.blocked_path_default"))
    scope_table.add_row(_("tui.allowed_actions"), ", ".join(_effective_allow_actions(state)) or _("tui.not_set"))
    scope_table.add_row(_("tui.blocked_actions"), ", ".join(_effective_block_actions(state)) or _("tui.not_set"))

    overview_table = Table(box=box.ROUNDED, expand=True, show_header=True, border_style=C_BORDER_SUBTLE)
    overview_table.add_column(_("tui.workbench_overview"), style=f"bold {C_PRIMARY}")
    overview_table.add_column(_("tui.current_status"), style=C_TEXT)
    overview_table.add_row(_("tui.model_key"), _("tui.model_key_configured") if api_ready else _("tui.model_key_not_configured"))
    overview_table.add_row(_("tui.history_resume"), _("tui.history_resume_on") if state.resume else _("tui.history_resume_off"))
    overview_table.add_row(_("tui.target_history"), _format_target_history_line(overview))
    overview_table.add_row(_("tui.risk_overview"), _format_findings_line(overview))
    overview_table.add_row(_("tui.persistent_constraints"), overview.constraints_summary)
    overview_table.add_row(_("tui.constraints_violations"), f"{overview.violations_count} {_('tui.times')}")
    if overview.last_command:
        overview_table.add_row(_("tui.last_command"), overview.last_command)
    if overview.error:
        overview_table.add_row(_("tui.history_error"), overview.error)

    command_preview = _draft_from_state(state).command_line
    footer_body = Text()
    footer_body.append(_("tui.command_preview"), style=f"bold {C_TEXT}")
    footer_body.append("\n")
    footer_body.append("|  ", style=C_MUTED)
    footer_body.append(command_preview, style=C_MUTED)
    footer_body.append("\n\n")
    footer_body.append(_("tui.cli_note"), style=C_MUTED)

    footer = Panel(
        footer_body,
        title=_("tui.confirm_title"),
        title_align="left",
        border_style=C_SUCCESS if state.target else C_WARNING,
        box=box.ROUNDED,
    )

    return Group(
        header,
        Text(),
        status,
        Text(),
        Panel(overview_table, title=_("tui.overview_title"), title_align="left", border_style=C_BORDER, box=box.ROUNDED),
        Panel(scope_table, title=_("tui.boundary_title"), title_align="left", border_style=C_BORDER, box=box.ROUNDED),
        footer,
    )


def build_skills_panel() -> Group:
    """Build the skills-browser view listing all available skills."""
    skills = SkillDispatcher().list_all_skills()

    table = Table(box=box.ROUNDED, expand=True, show_header=True, border_style=C_BORDER_SUBTLE)
    table.add_column(_("tui.skills_col_name"), style=f"bold {C_PRIMARY}", no_wrap=True)
    table.add_column(_("tui.skills_col_type"), style=C_SECONDARY, no_wrap=True)
    table.add_column(_("tui.skills_col_desc"), style=C_TEXT)
    for skill in skills:
        table.add_row(
            skill.get("name", ""),
            skill.get("type", ""),
            skill.get("description", "") or "—",
        )

    hint = Text(f"  {_('tui.skills_hint', count=len(skills))}", style=C_MUTED)
    return Group(
        Panel(table, title=_("tui.skills_title"), title_align="left", border_style=C_BORDER, box=box.ROUNDED),
        hint,
    )


def build_skill_detail_panel(skill: dict[str, Any]) -> Group:
    """Build the detail view for a single skill."""
    meta = Text()
    meta.append(f"{_('tui.skills_col_name')}: ", style=f"bold {C_PRIMARY}")
    meta.append(f"{skill.get('name', '')}\n", style=C_TEXT)
    meta.append(f"{_('tui.skills_detail_format')}: ", style=f"bold {C_PRIMARY}")
    meta.append(f"{skill.get('format', '')}\n", style=C_TEXT)
    meta.append(f"{_('tui.skills_col_desc')}: ", style=f"bold {C_PRIMARY}")
    meta.append(f"{skill.get('description', '') or '—'}\n", style=C_TEXT)

    references = skill.get("references") or []
    if references:
        meta.append(f"{_('tui.skills_detail_refs')}:\n", style=f"bold {C_PRIMARY}")
        for ref in references:
            meta.append(f"  · {ref}\n", style=C_MUTED)

    content = (skill.get("content") or "").strip()
    preview = content[:1500]
    if len(content) > 1500:
        preview += "\n…"
    body = Text(preview or "—", style=C_TEXT)

    hint = Text(f"  {_('tui.skills_detail_hint')}", style=C_MUTED)
    return Group(
        Panel(meta, title=_("tui.skills_detail_title"), title_align="left", border_style=C_BORDER, box=box.ROUNDED),
        Panel(body, title=_("tui.skills_detail_content"), title_align="left", border_style=C_BORDER_SUBTLE, box=box.ROUNDED),
        hint,
    )


def _render_view(view: tuple, session: dict[str, Any]) -> Group:
    """Render the active transient view, falling back to the dashboard."""
    kind = view[0]
    if kind == "skills_list":
        return build_skills_panel()
    if kind == "skill_detail":
        return build_skill_detail_panel(view[1])
    return build_dashboard(session["config"], session["state"])


def run_tui(
    *,
    launcher: TaskLauncher | None = None,
    once: bool = False,
    initial_state: TuiState | None = None,
) -> None:
    """Run the interactive terminal UI loop (Textual-powered)."""
    from vulnbot.cli.tui_textual import run_tui_textual
    run_tui_textual(launcher=launcher, once=once, initial_state=initial_state)



def render_task_summary(draft: TuiTaskDraft, *, width: int = 100) -> str:
    """Render a launch summary for dry-run output and tests."""
    console = Console(
        file=io.StringIO(),
        record=True,
        width=width,
        force_terminal=False,
        color_system=None,
    )
    console.print(_build_task_summary_panel(draft))
    return console.export_text()


def build_task_draft(state: TuiState) -> TuiTaskDraft:
    """Public wrapper for converting TUI state into an executable task draft."""
    return _draft_from_state(state)


def build_target_overview(target: str) -> TuiTargetOverview:
    """Build a safe target-history overview for the TUI dashboard."""
    normalized = target.strip()
    if not normalized:
        return TuiTargetOverview(target="", has_history=False)

    try:
        preview = get_target_state_preview(normalized)
        snapshots = list_target_snapshots(normalized)
    except Exception as exc:
        return TuiTargetOverview(
            target=normalized,
            has_history=False,
            error=f"Read failed: {exc}",
        )

    if preview is None:
        return TuiTargetOverview(target=normalized, has_history=False)

    violations = preview.get("constraint_violations", [])
    if not isinstance(violations, list):
        violations = []

    return TuiTargetOverview(
        target=str(preview.get("target") or normalized),
        has_history=True,
        snapshot_count=len(snapshots),
        phase=str(preview.get("phase") or "unknown"),
        findings_count=_safe_int(preview.get("findings_count")),
        verified_count=_safe_int(preview.get("verified_count")),
        pending_count=_safe_int(preview.get("pending_count")),
        constraints_summary=_format_constraints_summary(preview.get("constraints")),
        violations_count=len(violations),
        last_command=str(preview.get("last_command") or ""),
    )


def build_runtime_diagnostic(config) -> TuiRuntimeDiagnostic:
    """Collect runtime readiness without leaving the TUI."""
    provider = str(getattr(config.llm, "provider", "unknown"))
    model = str(getattr(config.llm, "model", "unknown"))
    api_key_configured = bool(getattr(config.llm, "api_key", ""))

    node_version = _command_version("node", "--version") or "missing"
    npx_status = "installed" if shutil.which("npx") else "missing"
    uvx_status = "installed" if shutil.which("uvx") else "missing"
    nmap_status = "installed" if shutil.which("nmap") else "optional/missing"

    try:
        from vulnbot.web.services.mcp_service import get_mcp_diagnostics

        mcp_diag = get_mcp_diagnostics()
        return TuiRuntimeDiagnostic(
            python_version=sys.version.split()[0],
            node_version=node_version,
            npx_status=npx_status,
            uvx_status=uvx_status,
            nmap_status=nmap_status,
            provider=provider,
            model=model,
            api_key_configured=api_key_configured,
            mcp_total_services=mcp_diag.total_services,
            mcp_running_services=mcp_diag.running_services,
            mcp_local_services=mcp_diag.local_services,
            mcp_placeholder_services=mcp_diag.placeholder_services,
            mcp_tool_count=mcp_diag.tool_count,
        )
    except Exception as exc:
        return TuiRuntimeDiagnostic(
            python_version=sys.version.split()[0],
            node_version=node_version,
            npx_status=npx_status,
            uvx_status=uvx_status,
            nmap_status=nmap_status,
            provider=provider,
            model=model,
            api_key_configured=api_key_configured,
            mcp_error=f"MCP diagnostics failed: {exc}",
        )


def build_runtime_diagnostic_panel(config) -> Panel:
    """Render the runtime diagnostic panel used by menu item 7."""
    diagnostic = build_runtime_diagnostic(config)
    table = Table(box=box.ROUNDED, expand=True, show_header=True, border_style=C_BORDER_SUBTLE)
    table.add_column(_("tui.diagnostic_item"), style=f"bold {C_PRIMARY}")
    table.add_column(_("tui.diagnostic_status"), style=C_TEXT)
    table.add_row("Python", diagnostic.python_version)
    table.add_row("Node.js", diagnostic.node_version)
    table.add_row("npx", diagnostic.npx_status)
    table.add_row("uvx", diagnostic.uvx_status)
    table.add_row("nmap", diagnostic.nmap_status)
    table.add_row("LLM Provider", diagnostic.provider)
    table.add_row("LLM Model", diagnostic.model)
    table.add_row("API Key", _("tui.model_key_configured") if diagnostic.api_key_configured else _("tui.model_key_not_configured"))
    table.add_row(
        "MCP Services",
        (
            f"{diagnostic.mcp_total_services} registered / "
            f"{diagnostic.mcp_running_services} running / "
            f"{diagnostic.mcp_local_services} local / "
            f"{diagnostic.mcp_placeholder_services} placeholder"
        ),
    )
    table.add_row("MCP Tools", str(diagnostic.mcp_tool_count))
    if diagnostic.mcp_error:
        table.add_row("MCP Error", diagnostic.mcp_error)

    footer = _("tui.diagnostic_footer")
    return Panel(
        Group(table, Text(f"\n[{C_MUTED}]{footer}[/]")),
        title=_("tui.diagnostic_title"),
        title_align="left",
        border_style=C_BORDER,
        box=box.ROUNDED,
    )


def _command_version(command: str, *args: str) -> str:
    path = shutil.which(command)
    if not path:
        return ""
    try:
        result = subprocess.run(
            [path, *args],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except Exception:
        return "check failed"
    return (result.stdout or result.stderr).strip() or "installed"


def _metric_panel(label: str, value: str, style: str) -> Panel:
    return Panel(
        f"[{C_MUTED}]{label}[/]\n[bold {style}]{value}[/]",
        box=box.ROUNDED,
        border_style=C_BORDER_SUBTLE,
        padding=(1, 2),
    )


def _safe_int(value: object) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0


def _format_target_history_line(overview: TuiTargetOverview) -> str:
    if not overview.target:
        return _("tui.no_target")
    if overview.error:
        return _("tui.read_error_short")
    if not overview.has_history:
        return _("tui.no_history")
    return f"{overview.snapshot_count} {_('tui.snapshots')} / {_('tui.phase')} {overview.phase}"


def _format_findings_line(overview: TuiTargetOverview) -> str:
    if not overview.has_history:
        return _("tui.no_findings")
    return (
        f"{overview.findings_count} {_('tui.risks')}"
        f"({_('tui.verified')} {overview.verified_count} / {_('tui.pending')} {overview.pending_count})"
    )


def _format_constraints_summary(raw: object) -> str:
    if not isinstance(raw, dict) or not raw:
        return _("tui.constraints_not_recorded")

    parts: list[str] = []
    mapping = [
        ("allowed_hosts", _("tui.allowed_hosts")),
        ("allowed_ports", _("tui.allowed_ports")),
        ("allowed_paths", _("tui.allowed_paths")),
        ("blocked_hosts", _("tui.blocked_hosts")),
        ("blocked_paths", _("tui.blocked_paths")),
        ("allowed_actions", _("tui.allowed_actions")),
        ("blocked_actions", _("tui.blocked_actions")),
    ]
    for key, label in mapping:
        value = raw.get(key)
        if isinstance(value, list) and value:
            parts.append(f"{label}: {', '.join(str(item) for item in value)}")
        elif value:
            parts.append(f"{label}: {value}")

    if raw.get("strict_mode"):
        parts.append(_("tui.strict_mode"))

    return "；".join(parts) if parts else _("tui.constraints_not_recorded")


def _effective_allow_actions(state: TuiState) -> tuple[str, ...]:
    return tuple(state.allow_actions) or MODES[state.mode].allow_actions


def _effective_block_actions(state: TuiState) -> tuple[str, ...]:
    return tuple(state.block_actions) or MODES[state.mode].block_actions


def _parse_action_csv(value: str | tuple[str, ...] | list[str] | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return [str(item).strip() for item in value if str(item).strip()]


def _parse_optional_port(value: str) -> int | None:
    value = value.strip()
    if not value:
        return None
    try:
        port = int(value)
    except ValueError as exc:
        raise ValueError(_("tui.error_invalid_port")) from exc
    if port < 1 or port > 65535:
        raise ValueError(_("tui.error_invalid_port"))
    return port


def _draft_from_state(state: TuiState) -> TuiTaskDraft:
    mode = MODES[state.mode]
    return TuiTaskDraft(
        command=mode.command,
        target=state.target.strip() or "<target>",
        only_host=state.only_host.strip() or None,
        only_port=_parse_optional_port(state.only_port),
        only_path=state.only_path.strip() or None,
        blocked_host=state.blocked_host.strip() or None,
        blocked_path=state.blocked_path.strip() or None,
        allow_actions=_effective_allow_actions(state),
        block_actions=_effective_block_actions(state),
        resume=state.resume,
    )


def _build_command_preview_args(draft: TuiTaskDraft) -> list[str]:
    return build_command_preview_args(draft)


def build_command_preview_args(draft: TuiTaskDraft, nl_text: str | None = None) -> list[str]:
    """Build a copyable CLI command from a TUI task draft."""
    args = ["vulnbot", draft.command, draft.target]
    if nl_text:
        args.extend(["--prompt", nl_text])
    if not draft.resume:
        args.append("--no-resume")
    if draft.only_port is not None:
        args.extend(["--only-port", str(draft.only_port)])
    if draft.only_host:
        args.extend(["--only-host", draft.only_host])
    if draft.only_path:
        args.extend(["--only-path", draft.only_path])
    if draft.blocked_host:
        args.extend(["--blocked-host", draft.blocked_host])
    if draft.blocked_path:
        args.extend(["--blocked-path", draft.blocked_path])
    if draft.allow_actions:
        args.extend(["--allow-actions", ",".join(draft.allow_actions)])
    if draft.block_actions:
        args.extend(["--block-actions", ",".join(draft.block_actions)])
    return args


def _prompt_target(state: TuiState) -> None:
    state.target = Prompt.ask(_("tui.enter_target"), default=state.target).strip()


def _prompt_mode(state: TuiState) -> None:
    choices = list(MODES.keys())
    table = Table(title=_("tui.check_mode"), box=box.ROUNDED, border_style=C_BORDER_SUBTLE)
    table.add_column("Key", style=f"bold {C_PRIMARY}")
    table.add_column(_("tui.name"), style=C_TEXT)
    table.add_column(_("tui.description"), style=C_MUTED)
    for key in choices:
        mode = MODES[key]
        table.add_row(key, mode.label, mode.description)
    Console().print(table)
    state.mode = Prompt.ask(_("tui.select_mode"), choices=choices, default=state.mode)  # type: ignore[assignment]


def _prompt_llm_config(screen: Console, config):
    provider_table = Table(title=_("tui.available_providers"), box=box.ROUNDED, border_style=C_BORDER_SUBTLE)
    provider_table.add_column("Provider", style=f"bold {C_PRIMARY}")
    provider_table.add_column("Default Model", style=C_TEXT)
    provider_table.add_column("Base URL", style=C_MUTED)
    for item in list_providers():
        marker = " *" if item["provider"] == config.llm.provider else ""
        provider_table.add_row(
            f"{item['provider']}{marker}",
            item.get("default_model", ""),
            item.get("base_url", ""),
        )
    screen.print(provider_table)

    provider = Prompt.ask(
        _("tui.select_provider"),
        default=config.llm.provider,
    ).strip()
    if provider and provider != config.llm.provider:
        config = apply_provider_preset(config, provider)

    base_url = Prompt.ask("Base URL", default=config.llm.base_url).strip()
    if base_url:
        config.llm.base_url = base_url

    current_key = _("tui.api_key_configured") if config.llm.api_key else _("tui.api_key_not_configured")
    api_key = Prompt.ask(f"API Key ({current_key})", default="").strip()
    if api_key:
        config.llm.api_key = api_key

    effective_base_url = config.llm.base_url
    effective_api_key = config.llm.api_key
    model = config.llm.model

    if effective_base_url and effective_api_key:
        Console().print(f"  [{C_MUTED}]{_('tui.fetching_models')}[/]")
        models = fetch_provider_models(effective_base_url, effective_api_key)
        if models:
            model_table = Table(title=_("tui.prompt_select_model", model=model), box=box.ROUNDED, border_style=C_BORDER_SUBTLE)
            model_table.add_column("#", style=f"bold {C_PRIMARY}", width=4)
            model_table.add_column("Model", style=C_TEXT)
            for i, m in enumerate(models, 1):
                marker = " *" if m == model else ""
                model_table.add_row(str(i), f"{m}{marker}")
            screen.print(model_table)
            model = Prompt.ask(
                _("tui.prompt_select_model", model=model),
                default=model,
            ).strip()
        else:
            model = Prompt.ask(
                _("tui.prompt_enter_model_fallback", model=model),
                default=model,
            ).strip()
    else:
        model = Prompt.ask("Model", default=model).strip()

    if model:
        config.llm.model = model
    save_config(config)

    screen.print(
        Panel(
            f"Provider: [bold {C_PRIMARY}]{config.llm.provider}[/]\n"
            f"Base URL: [{C_MUTED}]{config.llm.base_url}[/]\n"
            f"Model: [{C_MUTED}]{config.llm.model}[/]\n"
            f"API Key: {_('tui.updated') if api_key else current_key}",
            title=_("tui.config_saved"),
            border_style=C_SUCCESS,
            box=box.ROUNDED,
        )
    )
    Prompt.ask(_("tui.press_enter"), default="")
    return config


def _split_csv_items(raw: str) -> list[str]:
    """Split a comma/newline separated string into cleaned items."""
    return [item.strip() for item in raw.replace("\n", ",").split(",") if item.strip()]


def _prompt_text_value(screen: Console, label: str, current: str) -> str:
    """Prompt for a string value, keeping the current value on blank input."""
    raw = Prompt.ask(label, default=current, console=screen).strip()
    if raw == "!clear":
        return ""
    return current if raw == "" else raw


def _prompt_choice_value(screen: Console, label: str, choices: list[str], current: str) -> str:
    """Prompt for a choice value with a stable default."""
    default = current if current in choices else choices[0]
    return Prompt.ask(label, choices=choices, default=default, console=screen).strip()


def _prompt_bool_value(screen: Console, label: str, current: bool) -> bool:
    """Prompt for a boolean value."""
    return Confirm.ask(label, default=current, console=screen)


def _prompt_int_value(screen: Console, label: str, current: int) -> int:
    """Prompt for an integer value, keeping the current value on blank input."""
    while True:
        raw = Prompt.ask(label, default=str(current), console=screen).strip()
        if not raw:
            return current
        try:
            return int(raw)
        except ValueError:
            screen.print(f"[{C_ERROR}]Enter a whole number.[/]")


def _prompt_float_value(screen: Console, label: str, current: float) -> float:
    """Prompt for a float value, keeping the current value on blank input."""
    while True:
        raw = Prompt.ask(label, default=str(current), console=screen).strip()
        if not raw:
            return current
        try:
            return float(raw)
        except ValueError:
            screen.print(f"[{C_ERROR}]Enter a number.[/]")


def _prompt_list_value(screen: Console, label: str, current: list[str]) -> list[str]:
    """Prompt for a comma-separated list value."""
    raw = Prompt.ask(label, default=", ".join(current), console=screen).strip()
    if raw == "!clear":
        return []
    if not raw:
        return current
    return _split_csv_items(raw)


def _prompt_env_value(screen: Console, label: str, current: dict[str, str] | None) -> dict[str, str]:
    """Prompt for key=value pairs separated by commas."""
    current_text = ", ".join(f"{k}={v}" for k, v in sorted((current or {}).items()))
    raw = Prompt.ask(label, default=current_text, console=screen).strip()
    if raw == "!clear":
        return {}
    if not raw:
        return current or {}

    result: dict[str, str] = {}
    for item in _split_csv_items(raw):
        if "=" not in item:
            raise ValueError("Environment entries must look like KEY=value")
        key, value = item.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError("Environment keys cannot be blank")
        result[key] = value.strip()
    return result


def _render_config_summary(screen: Console, config) -> None:
    """Render a compact summary of the editable config sections."""
    llm = Table(title="LLM", box=box.ROUNDED, border_style=C_BORDER_SUBTLE)
    llm.add_column("Field", style=f"bold {C_PRIMARY}")
    llm.add_column("Value", style=C_TEXT)
    llm.add_row("Provider", config.llm.provider)
    llm.add_row("Model", config.llm.model)
    llm.add_row("Base URL", config.llm.base_url)
    llm.add_row("API keys", ", ".join(config.llm.api_keys) if config.llm.api_keys else "(single key)")
    llm.add_row("Reasoning", config.llm.reasoning_effort)

    session = Table(title="Session", box=box.ROUNDED, border_style=C_BORDER_SUBTLE)
    session.add_column("Field", style=f"bold {C_SECONDARY}")
    session.add_column("Value", style=C_TEXT)
    session.add_row("Output dir", str(config.session.output_dir))
    session.add_row("Max rounds", str(config.session.max_rounds))
    session.add_row(
        "REPL parallel",
        "yes" if config.session.repl_parallel_enabled else "no",
    )
    session.add_row("REPL parallel agents", str(config.session.repl_parallel_agents))
    session.add_row("REPL parallel depth", str(config.session.repl_parallel_depth))
    session.add_row("Language", config.session.language)
    session.add_row("Show thinking", "yes" if config.session.show_thinking else "no")
    session.add_row("Persistent cycles", str(config.session.persistent_max_cycles))

    safety = Table(title="Safety", box=box.ROUNDED, border_style=C_BORDER_SUBTLE)
    safety.add_column("Field", style=f"bold {C_ACCENT}")
    safety.add_column("Value", style=C_TEXT)
    safety.add_row("Python execute", "yes" if config.safety.enable_python_execute else "no")
    safety.add_row("Restricted", "yes" if config.safety.python_execute_restricted else "no")
    safety.add_row("Mode", config.safety.python_execute_mode)
    safety.add_row("Parallel tools", "yes" if config.safety.tool_parallel else "no")

    mcp = Table(title="MCP Servers", box=box.ROUNDED, border_style=C_BORDER_SUBTLE)
    mcp.add_column("Name", style=f"bold {C_PRIMARY}")
    mcp.add_column("Status", style=C_TEXT)
    mcp.add_column("Transport", style=C_MUTED)
    for name, server in config.mcp.servers.items():
        transport = server.transport
        if transport.type == "stdio":
            details = " ".join(
                part for part in [transport.command or "", " ".join(transport.args or [])] if part
            ).strip()
            summary = f"stdio {details}".strip()
        else:
            summary = f"sse {transport.url or ''}".strip()
        status = "enabled" if server.enabled else "disabled"
        if name in BUILTIN_MCP_SERVERS:
            status += ", builtin"
        mcp.add_row(name, status, summary)

    screen.print(
        Panel(
            Group(llm, session, safety, mcp),
            title="Config Draft",
            border_style=C_BORDER,
            box=box.ROUNDED,
        )
    )


def _edit_llm_config(screen: Console, config):
    """Edit LLM configuration fields in-place."""
    screen.print(Panel("Edit LLM settings", border_style=C_BORDER_SUBTLE, box=box.ROUNDED))
    providers = [item["provider"] for item in list_providers()]
    provider = _prompt_choice_value(screen, "Provider", providers, config.llm.provider)
    if provider != config.llm.provider:
        config = apply_provider_preset(config, provider)

    config.llm.base_url = _prompt_text_value(screen, "Base URL", config.llm.base_url)
    config.llm.model = _prompt_text_value(screen, "Model", config.llm.model)
    config.llm.api_keys = _prompt_list_value(
        screen,
        "API keys (comma-separated, !clear to empty)",
        config.llm.api_keys,
    )
    config.llm.api_key = _prompt_text_value(
        screen,
        "Single API key fallback (!clear to empty)",
        config.llm.api_key,
    )
    config.llm.max_tokens = _prompt_int_value(screen, "Max tokens", config.llm.max_tokens)
    config.llm.max_context_tokens = _prompt_int_value(
        screen, "Max context tokens", config.llm.max_context_tokens
    )
    config.llm.temperature = _prompt_float_value(screen, "Temperature", config.llm.temperature)
    config.llm.reasoning_effort = _prompt_text_value(
        screen, "Reasoning effort", config.llm.reasoning_effort
    )
    return config


def _edit_session_config(screen: Console, config):
    """Edit session configuration fields in-place."""
    screen.print(Panel("Edit session settings", border_style=C_BORDER_SUBTLE, box=box.ROUNDED))
    config.session.output_dir = Path(
        _prompt_text_value(screen, "Output directory", str(config.session.output_dir))
    )
    config.session.auto_save = _prompt_bool_value(screen, "Auto save", config.session.auto_save)
    config.session.report_format = _prompt_text_value(
        screen, "Report format", config.session.report_format
    )
    config.session.poc_language = _prompt_text_value(
        screen, "PoC language", config.session.poc_language
    )
    config.session.max_rounds = _prompt_int_value(screen, "Max rounds", config.session.max_rounds)
    config.session.show_thinking = _prompt_bool_value(
        screen, "Show thinking", config.session.show_thinking
    )
    config.session.repl_parallel_enabled = _prompt_bool_value(
        screen,
        "REPL parallel auto-mode",
        config.session.repl_parallel_enabled,
    )
    config.session.repl_parallel_agents = _prompt_int_value(
        screen,
        "REPL parallel child agents",
        config.session.repl_parallel_agents,
    )
    config.session.repl_parallel_depth = _prompt_int_value(
        screen,
        "REPL parallel depth",
        config.session.repl_parallel_depth,
    )
    config.session.repl_parallel_worker_rounds = _prompt_int_value(
        screen,
        "REPL parallel worker rounds",
        config.session.repl_parallel_worker_rounds,
    )
    config.session.repl_parallel_surface_limit = _prompt_int_value(
        screen,
        "REPL parallel surface limit",
        config.session.repl_parallel_surface_limit,
    )
    config.session.stale_rounds_threshold = _prompt_int_value(
        screen, "Stale rounds threshold", config.session.stale_rounds_threshold
    )
    config.session.persistent_rounds_per_cycle = _prompt_int_value(
        screen,
        "Persistent rounds per cycle",
        config.session.persistent_rounds_per_cycle,
    )
    config.session.persistent_max_cycles = _prompt_int_value(
        screen, "Persistent max cycles", config.session.persistent_max_cycles
    )
    config.session.persistent_auto_report = _prompt_bool_value(
        screen, "Persistent auto report", config.session.persistent_auto_report
    )
    config.session.language = _prompt_choice_value(
        screen, "Language", ["auto", "en", "zh"], config.session.language
    )
    return config


def _edit_safety_config(screen: Console, config):
    """Edit safety configuration fields in-place."""
    screen.print(Panel("Edit safety settings", border_style=C_BORDER_SUBTLE, box=box.ROUNDED))
    config.safety.enable_python_execute = _prompt_bool_value(
        screen, "Enable python execute", config.safety.enable_python_execute
    )
    config.safety.python_execute_restricted = _prompt_bool_value(
        screen, "Python execute restricted", config.safety.python_execute_restricted
    )
    config.safety.python_execute_mode = _prompt_choice_value(
        screen,
        "Python execute mode",
        ["safe", "lab", "trusted-local"],
        config.safety.python_execute_mode,
    )
    config.safety.python_execute_max_lines = _prompt_int_value(
        screen, "Python execute max lines", config.safety.python_execute_max_lines
    )
    config.safety.python_execute_show_warning = _prompt_bool_value(
        screen, "Show python execute warning", config.safety.python_execute_show_warning
    )
    config.safety.python_execute_max_output_chars = _prompt_int_value(
        screen,
        "Python execute max output chars",
        config.safety.python_execute_max_output_chars,
    )
    config.safety.python_execute_audit_enabled = _prompt_bool_value(
        screen, "Python execute audit enabled", config.safety.python_execute_audit_enabled
    )
    config.safety.tool_parallel = _prompt_bool_value(
        screen, "Parallel tool calls", config.safety.tool_parallel
    )
    config.safety.tool_max_concurrent = _prompt_int_value(
        screen, "Max concurrent tools", config.safety.tool_max_concurrent
    )
    return config


def _prompt_mcp_transport(screen: Console, transport: MCPTransportConfig) -> MCPTransportConfig:
    """Edit transport settings for an MCP server."""
    transport.type = _prompt_choice_value(screen, "Transport type", ["stdio", "sse"], transport.type)
    transport.command = _prompt_text_value(screen, "Transport command", transport.command or "")
    transport.args = _prompt_list_value(
        screen,
        "Transport args (comma-separated, !clear to empty)",
        transport.args or [],
    )
    transport.url = _prompt_text_value(screen, "Transport URL", transport.url or "")
    transport.env = _prompt_env_value(screen, "Transport env (KEY=value, !clear to empty)", transport.env)
    transport.startup_timeout = _prompt_int_value(
        screen, "Transport startup timeout", transport.startup_timeout
    )
    transport.tool_timeout = _prompt_int_value(
        screen, "Transport tool timeout", transport.tool_timeout
    )
    return transport


def _prompt_mcp_server(screen: Console, config, *, server: MCPServerConfig | None = None) -> tuple[str, MCPServerConfig]:
    """Create or edit a single MCP server definition."""
    is_new = server is None
    current_name = server.name if server else ""
    while True:
        if is_new:
            name = _prompt_text_value(screen, "Server name", current_name)
            if not name:
                screen.print(f"[{C_ERROR}]Server name cannot be blank.[/]")
                continue
            if name in config.mcp.servers:
                screen.print(f"[{C_ERROR}]Server '{name}' already exists.[/]")
                continue
        else:
            name = current_name
        break

    current = server or MCPServerConfig(
        name=name,
        enabled=True,
        priority=1,
        transport=MCPTransportConfig(type="stdio"),
    )
    current.name = name
    current.enabled = _prompt_bool_value(screen, f"Enabled [{name}]", current.enabled)
    current.priority = _prompt_int_value(screen, f"Priority [{name}]", current.priority)
    current.description = _prompt_text_value(screen, f"Description [{name}]", current.description)
    current.transport = _prompt_mcp_transport(screen, current.transport)
    return name, current


def _edit_mcp_config(screen: Console, config):
    """Edit MCP server configuration."""
    while True:
        screen.print(
            Panel("Edit MCP servers", border_style=C_BORDER_SUBTLE, box=box.ROUNDED)
        )
        table = Table(box=box.SIMPLE, border_style=C_BORDER_SUBTLE)
        table.add_column("Server", style=f"bold {C_PRIMARY}")
        table.add_column("Enabled", style=C_TEXT)
        table.add_column("Priority", style=C_TEXT)
        table.add_column("Transport", style=C_MUTED)
        for name, server in config.mcp.servers.items():
            if server.transport.type == "stdio":
                transport = "stdio"
            else:
                transport = "sse"
            marker = "builtin" if name in BUILTIN_MCP_SERVERS else "custom"
            table.add_row(name, "yes" if server.enabled else "no", str(server.priority), f"{transport} / {marker}")
        screen.print(table)

        action = Prompt.ask(
            "Action",
            choices=["add", "edit", "delete", "back"],
            default="back",
            console=screen,
        ).strip()

        if action == "back":
            return config
        if action == "add":
            name, server = _prompt_mcp_server(screen, config)
            config.mcp.servers[name] = server
            continue
        if action == "edit":
            if not config.mcp.servers:
                screen.print(f"[{C_WARNING}]No MCP servers to edit.[/]")
                continue
            name = Prompt.ask(
                "Server to edit",
                choices=list(config.mcp.servers.keys()),
                default=next(iter(config.mcp.servers)),
                console=screen,
            ).strip()
            current = config.mcp.servers[name]
            _, server = _prompt_mcp_server(screen, config, server=current)
            config.mcp.servers[name] = server
            continue
        if action == "delete":
            if not config.mcp.servers:
                screen.print(f"[{C_WARNING}]No MCP servers to delete.[/]")
                continue
            name = Prompt.ask(
                "Server to delete",
                choices=list(config.mcp.servers.keys()),
                default=next(iter(config.mcp.servers)),
                console=screen,
            ).strip()
            if name in BUILTIN_MCP_SERVERS:
                screen.print(f"[{C_WARNING}]Built-in servers are seeded defaults and cannot be deleted here.[/]")
                continue
            if Confirm.ask(f"Delete MCP server '{name}'?", default=False, console=screen):
                config.mcp.servers.pop(name, None)
            continue


def run_config_tui() -> None:
    """Run the interactive config editor."""
    screen = Console()
    config = load_config()

    while True:
        screen.print()
        screen.print(Panel("VulnBot Config", border_style=C_BORDER, box=box.ROUNDED))
        _render_config_summary(screen, config)
        action = Prompt.ask(
            "Section",
            choices=["llm", "session", "safety", "mcp", "save", "quit"],
            default="save",
            console=screen,
        ).strip()

        if action == "llm":
            config = _edit_llm_config(screen, config)
        elif action == "session":
            config = _edit_session_config(screen, config)
        elif action == "safety":
            config = _edit_safety_config(screen, config)
        elif action == "mcp":
            config = _edit_mcp_config(screen, config)
        elif action == "save":
            save_config(config)
            screen.print(Panel("Config saved.", border_style=C_SUCCESS, box=box.ROUNDED))
            return
        elif action == "quit":
            screen.print(Panel("Discarded changes.", border_style=C_WARNING, box=box.ROUNDED))
            return


def _prompt_scope(state: TuiState) -> None:
    state.only_host = Prompt.ask(_("tui.enter_only_host"), default=state.only_host).strip()
    while True:
        state.only_port = Prompt.ask(_("tui.enter_only_port"), default=state.only_port).strip()
        try:
            _parse_optional_port(state.only_port)
            break
        except ValueError as exc:
            Console().print(f"[{C_ERROR}]{exc}[/]")
    state.only_path = Prompt.ask(_("tui.enter_only_path"), default=state.only_path).strip()
    state.blocked_host = Prompt.ask(_("tui.enter_blocked_host"), default=state.blocked_host).strip()
    state.blocked_path = Prompt.ask(_("tui.enter_blocked_path"), default=state.blocked_path).strip()
    state.allow_actions = _parse_action_csv(
        Prompt.ask(
            _("tui.enter_allowed_actions"),
            default=",".join(state.allow_actions),
        )
    )
    state.block_actions = _parse_action_csv(
        Prompt.ask(
            _("tui.enter_blocked_actions"),
            default=",".join(state.block_actions),
        )
    )
    state.resume = Confirm.ask(_("tui.resume_history"), default=state.resume)


def _confirm_and_launch(state: TuiState, launcher: TaskLauncher) -> None:
    if not state.target.strip():
        Console().print(Panel(_("tui.please_set_target"), border_style=C_WARNING, box=box.ROUNDED))
        Prompt.ask(_("tui.press_enter"), default="")
        return

    mode = MODES[state.mode]
    if mode.needs_extra_confirm:
        ok = Confirm.ask(
            _("tui.confirm_deep_mode", mode=mode.label),
            default=False,
        )
        if not ok:
            return

    draft = _draft_from_state(state)
    Console().print(_build_task_summary_panel(draft, title=_("tui.launch_summary")))
    if Confirm.ask(_("tui.start_check"), default=False):
        Console().print(_("tui.enter_task_mode"))
        launcher(draft)
        Prompt.ask(_("tui.task_returned"), default="")


def _build_task_summary_panel(draft: TuiTaskDraft, *, title: str | None = None) -> Panel:
    if title is None:
        title = _("tui.launch_summary_title")
    lines = [
        f"{_('tui.target')}: [bold {C_PRIMARY}]{draft.target}[/]",
        f"{_('tui.command')}: [bold {C_SECONDARY}]{draft.command}[/]",
        f"{_('tui.resume_history')}: {_('tui.yes') if draft.resume else _('tui.no')}",
        f"{_('tui.only_host')}: {draft.only_host or _('tui.unrestricted')}",
        f"{_('tui.only_port')}: {draft.only_port if draft.only_port is not None else _('tui.unrestricted')}",
        f"{_('tui.only_path')}: {draft.only_path or _('tui.unrestricted')}",
        f"{_('tui.blocked_host')}: {draft.blocked_host or _('tui.not_set')}",
        f"{_('tui.blocked_path')}: {draft.blocked_path or _('tui.not_set')}",
        f"{_('tui.allowed_actions')}: {', '.join(draft.allow_actions) or _('tui.not_set')}",
        f"{_('tui.blocked_actions')}: {', '.join(draft.block_actions) or _('tui.not_set')}",
        "",
        f"[bold {C_TEXT}]{_('tui.copyable_command')}[/]",
        f"[{C_MUTED}]  {draft.command_line}[/]",
    ]
    return Panel("\n".join(lines), title=title, title_align="left", border_style=C_WARNING, box=box.ROUNDED)


def _show_target_history(screen: Console, state: TuiState) -> None:
    if not state.target.strip():
        screen.print(Panel(_("tui.please_set_target"), border_style=C_WARNING, box=box.ROUNDED))
        Prompt.ask(_("tui.press_enter"), default="")
        return

    preview = get_target_state_preview(state.target)
    snapshots = list_target_snapshots(state.target)
    if preview is None:
        screen.print(Panel(_("tui.no_history_for_target"), title=_("tui.history_status"), border_style=C_WARNING, box=box.ROUNDED))
    else:
        screen.print(
            Panel(
                f"{_('tui.target')}: [bold {C_PRIMARY}]{preview.get('target', state.target)}[/]\n"
                f"{_('tui.phase')}: [bold {C_SECONDARY}]{preview.get('phase', 'unknown')}[/]\n"
                f"{_('tui.findings_count')}: [bold {C_TEXT}]{preview.get('findings_count', 0)}[/]\n"
                f"{_('tui.snapshot_count')}: [bold {C_TEXT}]{len(snapshots)}[/]",
                title=_("tui.history_status"),
                title_align="left",
                border_style=C_BORDER,
                box=box.ROUNDED,
            )
        )
    Prompt.ask(_("tui.press_enter"), default="")


def _generate_target_report(screen: Console, state: TuiState) -> None:
    if not state.target.strip():
        screen.print(Panel(_("tui.please_set_target"), border_style=C_WARNING, box=box.ROUNDED))
        Prompt.ask(_("tui.press_enter"), default="")
        return

    from vulnbot.cli.main import _generate_report_for_target

    report_path = _generate_report_for_target(state.target)
    screen.print(Panel(report_path, title=_("tui.report_generated"), title_align="left", border_style=C_SUCCESS, box=box.ROUNDED))
    Prompt.ask(_("tui.press_enter"), default="")


def _default_launcher(draft: TuiTaskDraft) -> None:
    from vulnbot.cli import main as cli_main

    allow_actions = ",".join(draft.allow_actions) if draft.allow_actions else None
    block_actions = ",".join(draft.block_actions) if draft.block_actions else None

    common = {
        "target": draft.target,
        "only_port": draft.only_port,
        "only_host": draft.only_host,
        "only_path": draft.only_path,
        "blocked_host": draft.blocked_host,
        "blocked_path": draft.blocked_path,
        "allow_actions": allow_actions,
        "block_actions": block_actions,
        "resume": draft.resume,
        "snapshot": None,
    }

    if draft.command == "recon":
        cli_main.recon(**common)
    elif draft.command == "scan":
        cli_main.scan(ports=None, **common)
    elif draft.command == "persistent":
        cli_main.persistent(rounds=0, cycles=0, no_report=False, **common)
    else:
        cli_main.run(scope="full", output=None, **common)
