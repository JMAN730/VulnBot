"""Full CLI manual rendering for VulnBot."""

from __future__ import annotations

from dataclasses import dataclass

from vulnbot import __version__
from vulnbot.config.schema import PROVIDER_PRESETS


@dataclass(frozen=True)
class ManualTopic:
    """A CLI manual topic or command."""

    name: str
    summary: str
    usage: str
    flags: tuple[tuple[str, str], ...] = ()
    notes: tuple[str, ...] = ()
    examples: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()


ROOT_OPTIONS: tuple[tuple[str, str], ...] = (
    ("--help", "Show Typer's short help for the root command or selected subcommand."),
    ("--version", "Print the installed VulnBot version and exit."),
    ("--man, --manual", "Print this full CLI manual and exit."),
)

COMMON_TASK_FLAGS: tuple[tuple[str, str], ...] = (
    (
        "--prompt TEXT",
        "Replace the built-in task prompt entirely. Use this when the default command intent is "
        "close but you need exact wording, credentials context, a lab note, or a custom workflow.",
    ),
    (
        "--only-port PORT",
        "Add a hard scope hint that only this TCP/UDP port is in scope. Valid ports are 1-65535.",
    ),
    (
        "--only-host HOST",
        "Restrict testing to one host even when a URL, CIDR, recon data, or target history points "
        "at related hosts.",
    ),
    (
        "--only-path PATH",
        "Restrict web testing to one path such as /admin. Available on URL-oriented task commands.",
    ),
    (
        "--blocked-host HOST",
        "Mark a host as explicitly out of scope. Tool calls to that host are blocked where VulnBot "
        "can infer the destination.",
    ),
    (
        "--blocked-path PATH",
        "Mark a path as explicitly out of scope. Available on URL-oriented task commands.",
    ),
    (
        "--allow-actions CSV",
        "Comma-separated action allowlist. Common values are recon, scan, exploit, "
        "post_exploitation, report, run, and persistent. If set, commands outside the allowlist "
        "are blocked before the task starts, and tool/phase checks continue during the run.",
    ),
    (
        "--block-actions CSV",
        "Comma-separated action denylist using the same action names as --allow-actions.",
    ),
    (
        "--resume / --no-resume",
        "Resume saved target history by default. Use --no-resume for a clean run that ignores "
        "stored target state.",
    ),
    (
        "--snapshot ID",
        "Resume from a specific target-state snapshot instead of the latest one.",
    ),
)

ACTION_NAMES = (
    "recon",
    "scan",
    "exploit",
    "post_exploitation",
    "report",
    "run",
    "persistent",
)

COMMANDS: tuple[ManualTopic, ...] = (
    ManualTopic(
        name="run",
        summary="Run the full authorized pentest workflow against one target.",
        usage="vulnbot run TARGET [--scope full|web|api|mobile] [--output PATH] [COMMON TASK FLAGS]",
        flags=(
            ("TARGET", "Required host, IP, URL, or other authorized target identifier."),
            (
                "--scope TEXT",
                "High-level test focus. Built-in wording recognizes full, web, api, and mobile, "
                "but the value is passed into the task prompt, so custom labels are possible.",
            ),
            (
                "--output PATH",
                "After the run, generate a report at PATH from the saved target state. A .html "
                "suffix writes HTML; otherwise the configured report format is used.",
            ),
        ),
        notes=(
            "Requires a configured LLM API key before the task starts.",
            "The command uses autonomous rounds from session.max_rounds unless the agent stops earlier.",
            "Use --allow-actions recon,scan when you want broad coverage but no exploitation.",
        ),
        examples=(
            "vulnbot run https://lab.example --scope web --allow-actions recon,scan",
            "vulnbot run 10.10.10.5 --output reports/lab.md --no-resume",
        ),
    ),
    ManualTopic(
        name="persistent",
        summary="Run repeated pentest cycles and optionally write a report after each cycle.",
        usage="vulnbot persistent TARGET [--rounds N] [--cycles N] [--no-report] [COMMON TASK FLAGS]",
        flags=(
            ("TARGET", "Required authorized target."),
            (
                "--rounds N, -r N",
                "Rounds per cycle. 0 means use session.persistent_rounds_per_cycle from config.",
            ),
            (
                "--cycles N, -c N",
                "Maximum number of cycles. 0 means use session.persistent_max_cycles from config; "
                "if that config value is also 0, the run is unlimited until interrupted.",
            ),
            ("--no-report", "Disable the normal persistent-cycle report generation."),
        ),
        notes=(
            "Persistent mode is for long authorized lab or assessment runs where VulnBot should "
            "keep cycling through recon, scan, verification, and reporting.",
            "Use Ctrl+C to interrupt. The command still prints a final summary.",
        ),
        examples=(
            "vulnbot persistent https://lab.example --rounds 25 --cycles 4",
            "vulnbot persistent 10.0.0.0/24 --allow-actions recon,scan --no-report",
        ),
    ),
    ManualTopic(
        name="recon",
        summary="Run reconnaissance only, without exploitation.",
        usage="vulnbot recon TARGET [COMMON TASK FLAGS]",
        flags=(("TARGET", "Required host, IP, URL, CIDR, or domain to investigate."),),
        notes=(
            "The default prompt asks for authorized reconnaissance without exploitation.",
            "Good first command when you only want asset discovery, fingerprinting, and notes.",
        ),
        examples=("vulnbot recon example.com --only-host example.com",),
    ),
    ManualTopic(
        name="scan",
        summary="Run vulnerability discovery without exploitation.",
        usage="vulnbot scan TARGET [--ports PORTS] [COMMON TASK FLAGS]",
        flags=(
            ("TARGET", "Required authorized target."),
            (
                "--ports PORTS",
                "Port list or range hint such as 80,443,8080. This is prompt guidance, not an "
                "nmap-only switch; use network-scan for direct nmap profile control.",
            ),
        ),
        notes=(
            "The default prompt asks VulnBot to identify vulnerabilities without exploitation.",
            "Use --block-actions exploit for an explicit denylist in addition to the scan wording.",
        ),
        examples=("vulnbot scan https://lab.example --ports 80,443 --block-actions exploit",),
    ),
    ManualTopic(
        name="network-scan",
        summary="Run nmap-based network discovery and optional safe follow-up probes.",
        usage=(
            "vulnbot network-scan [TARGET] [--profile adaptive|fast|thorough|stealth] "
            "[--ports PORTS] [--parallel-agents N]"
        ),
        flags=(
            (
                "TARGET",
                "Optional host, IP, or CIDR. If omitted, VulnBot tries to detect the connected "
                "Wi-Fi subnet and scan that CIDR.",
            ),
            (
                "--profile TEXT",
                "nmap scan profile. adaptive uses target history and defaults; fast favors speed; "
                "thorough expands coverage; stealth lowers scan intensity.",
            ),
            ("--ports PORTS", "Port list or range for nmap, for example 22,80,443 or 1-1000."),
            (
                "--max-rounds N",
                "Agent follow-up rounds after nmap. 0 means use session.max_rounds.",
            ),
            (
                "--parallel-agents N",
                "Number of child agents to fan out across discovered surfaces. 1 disables fan-out.",
            ),
            (
                "--parallel-depth N",
                "Number of child-agent discovery waves when --parallel-agents is greater than 1.",
            ),
            ("--worker-rounds N", "Agent rounds per child surface worker."),
            (
                "--surface-limit N",
                "Maximum discovered surfaces considered for child-agent fan-out.",
            ),
            (
                "--safe-probes / --no-safe-probes",
                "With safe probes on, VulnBot defaults to --allow-actions recon,scan and performs "
                "only non-destructive verification probes after nmap. With --no-safe-probes, it "
                "summarizes weak links without follow-up probes.",
            ),
            ("--only-port PORT", "Restrict follow-up analysis to one port."),
            ("--only-host HOST", "Restrict follow-up analysis to one host."),
            ("--blocked-host HOST", "Exclude a host from follow-up analysis."),
            ("--allow-actions CSV", "Override the safe-probe action allowlist."),
            ("--block-actions CSV", "Add an action denylist."),
            ("--resume / --no-resume", "Use or ignore saved target history."),
            ("--snapshot ID", "Resume from a specific target-state snapshot."),
        ),
        notes=(
            "This is the command to use when you want nmap involved directly.",
            "The built-in profile validation accepts adaptive, fast, thorough, and stealth.",
        ),
        examples=(
            "vulnbot network-scan --profile fast",
            "vulnbot network-scan 192.168.56.0/24 --ports 22,80,443 --parallel-agents 3",
        ),
    ),
    ManualTopic(
        name="exploit",
        summary="Run an authorized exploitation-focused task.",
        usage="vulnbot exploit TARGET [--cve CVE-ID] [--cmd CMD] [COMMON TASK FLAGS]",
        flags=(
            ("TARGET", "Required authorized target."),
            ("--cve CVE-ID", "Tell VulnBot to focus on a specific CVE."),
            (
                "--cmd CMD",
                "Verification command for command-execution style findings. Defaults to id.",
            ),
        ),
        notes=(
            "Use only against systems where exploitation is explicitly authorized.",
            "Scope flags still apply and are checked before the command starts.",
        ),
        examples=(
            "vulnbot exploit https://lab.example --cve CVE-2024-1234 --only-path /vulnerable",
        ),
    ),
    ManualTopic(
        name="report",
        summary="Generate a report from a saved session file or from target history.",
        usage="vulnbot report SESSION_JSON [--target] [--pdf] [--pdf-out PATH]",
        flags=(
            (
                "SESSION_JSON",
                "Path to a saved session JSON file. With --target, this argument is interpreted "
                "as a target name instead.",
            ),
            (
                "--target",
                "Generate from the current target-state history rather than a session JSON file.",
            ),
            (
                "--pdf",
                "Also export a PDF. Requires the pdf extra, for example pip install 'vulnbot[pdf]'.",
            ),
            (
                "--pdf-out PATH",
                "PDF output path. Defaults to the generated report path with a .pdf suffix.",
            ),
        ),
        notes=(
            "Reports include verified findings, false-positive/review status, attack path summary, "
            "and recorded scope governance where available.",
        ),
        examples=(
            "vulnbot report ~/.vulnbot/sessions/session_001.json",
            "vulnbot report https://lab.example --target --pdf",
        ),
    ),
    ManualTopic(
        name="config",
        summary="Open the config TUI or manage config values and provider presets.",
        usage=(
            "vulnbot config\n"
            "vulnbot config list\n"
            "vulnbot config get KEY\n"
            "vulnbot config set KEY VALUE\n"
            "vulnbot config provider [NAME|--list]"
        ),
        flags=(
            (
                "no subcommand",
                "Open the interactive configuration editor.",
            ),
            ("set KEY VALUE", "Set a dot-notated config key such as llm.model or session.max_rounds."),
            ("get KEY", "Print one config value. Secret-looking keys are masked."),
            ("list", "Print the full effective config as YAML."),
            ("provider NAME", "Switch provider preset and fill base_url/model defaults."),
            ("provider --list, -l", "List provider presets and show the current provider."),
        ),
        notes=(
            "Useful LLM keys: llm.provider, llm.api_key, llm.api_keys, llm.base_url, llm.model, "
            "llm.max_tokens, llm.max_context_tokens, llm.temperature, llm.reasoning_effort.",
            "Useful session keys: session.output_dir, session.report_format, session.max_rounds, "
            "session.show_thinking, session.persistent_rounds_per_cycle, "
            "session.persistent_max_cycles, session.persistent_auto_report, session.language, "
            "session.repl_parallel_enabled, session.repl_parallel_agents, "
            "session.repl_parallel_depth, session.repl_parallel_worker_rounds, "
            "session.repl_parallel_surface_limit.",
            "Useful safety keys: safety.enable_python_execute, safety.python_execute_mode, "
            "safety.python_execute_max_lines, safety.tool_parallel, safety.tool_max_concurrent.",
        ),
        examples=(
            "vulnbot config",
            "vulnbot config provider --list",
            "vulnbot config provider deepseek",
            "vulnbot config set llm.api_keys 'key-one,key-two,key-three'",
            "vulnbot config set session.max_rounds 25",
            "vulnbot config set session.repl_parallel_agents 2",
        ),
    ),
    ManualTopic(
        name="kb",
        summary="Manage the local security knowledge base.",
        usage="vulnbot kb update\nvulnbot kb status",
        flags=(
            ("update", "Seed or refresh bundled knowledge-base entries."),
            ("status", "Show whether semantic retrieval is active, keyword fallback is active, or no data is available."),
        ),
        notes=(
            "Semantic retrieval requires the kb extra. Without it, VulnBot falls back to keyword retrieval when data exists.",
        ),
        examples=("vulnbot kb update", "vulnbot kb status"),
    ),
    ManualTopic(
        name="target-state",
        summary="Inspect, compare, restore, or clear persisted target history.",
        usage=(
            "vulnbot target-state list TARGET\n"
            "vulnbot target-state preview TARGET [--snapshot ID]\n"
            "vulnbot target-state diff TARGET FROM_ID [--to TO_ID]\n"
            "vulnbot target-state rollback TARGET SNAPSHOT_ID\n"
            "vulnbot target-state clear TARGET"
        ),
        flags=(
            ("list TARGET", "List up to 20 recent snapshots for a target."),
            ("preview TARGET", "Show phase, resume strategy, finding counts, priority assets, and next actions."),
            ("preview --snapshot ID", "Preview a specific snapshot."),
            ("diff TARGET FROM_ID --to TO_ID", "Compare two snapshots, or compare FROM_ID to current state when --to is omitted."),
            ("rollback TARGET SNAPSHOT_ID", "Restore target history to a snapshot."),
            ("clear TARGET", "Delete persisted target history for a target."),
        ),
        notes=(
            "Task commands use target state when --resume is enabled, which is the default.",
            "Use --no-resume on run/recon/scan/exploit/persistent/network-scan to ignore this history.",
        ),
        examples=(
            "vulnbot target-state list https://lab.example",
            "vulnbot target-state preview https://lab.example",
            "vulnbot target-state diff https://lab.example snap-a --to snap-b",
        ),
        aliases=("target", "state", "history"),
    ),
    ManualTopic(
        name="tui",
        summary="Open the terminal workbench for guided task setup.",
        usage="vulnbot tui [--target TARGET] [--mode quick|standard|deep|continuous] [SCOPE FLAGS]",
        flags=(
            ("--target TARGET, -t TARGET", "Pre-fill the authorized target."),
            (
                "--mode MODE, -m MODE",
                "Pre-fill workbench mode. quick maps to recon, standard maps to run, deep maps to "
                "scan, and continuous maps to persistent.",
            ),
            ("--only-port PORT", "Pre-fill a single allowed port."),
            ("--only-host HOST", "Pre-fill a single allowed host."),
            ("--only-path PATH", "Pre-fill a single allowed path."),
            ("--blocked-host HOST", "Pre-fill an excluded host."),
            ("--blocked-path PATH", "Pre-fill an excluded path."),
            ("--allow-actions CSV", "Pre-fill allowed actions."),
            ("--block-actions CSV", "Pre-fill blocked actions."),
            ("--resume / --no-resume", "Pre-fill target history resume behavior."),
            ("--dry-run", "Render the launch summary and exit without starting a task."),
            ("--once", "Render the dashboard once and exit, useful for smoke tests."),
        ),
        notes=(
            "The TUI exposes the same scope and action controls as the CLI task commands.",
        ),
        examples=(
            "vulnbot tui",
            "vulnbot tui --target https://lab.example --mode quick --only-port 443",
            "vulnbot tui --dry-run --target https://lab.example --mode deep",
        ),
    ),
    ManualTopic(
        name="web",
        summary="Start the local FastAPI/React web UI.",
        usage="vulnbot web [--host HOST] [--port PORT] [--dry-run] [--allow-remote]",
        flags=(
            ("--host HOST", "Bind address. Defaults to 127.0.0.1."),
            ("--port PORT", "Bind port. Defaults to 7788."),
            ("--dry-run", "Validate imports and print launch information without starting uvicorn."),
            (
                "--allow-remote",
                "Required when --host is not 127.0.0.1. This prevents accidentally exposing the Web UI.",
            ),
        ),
        notes=(
            "Install the web extra if FastAPI/uvicorn are missing: pip install 'vulnbot[web]'.",
            "Keep the Web UI on localhost unless you intentionally need remote access.",
        ),
        examples=("vulnbot web", "vulnbot web --port 8080 --dry-run"),
    ),
    ManualTopic(
        name="repl",
        summary="Start the classic natural-language REPL.",
        usage="vulnbot repl\nvulnbot",
        flags=(
            ("no arguments", "Running vulnbot with no subcommand opens this REPL by default."),
        ),
        notes=(
            "REPL commands include help, status, target TARGET, tools, report [TARGET], persistent [TARGET], think, clear, parallel, and exit.",
            "Natural-language inputs that include an auto-mode keyword and a target enter autonomous pentest mode.",
            "REPL auto-mode uses bounded parallel child agents by default. Use parallel status, parallel on/off, parallel agents N, or parallel reset for runtime-only controls.",
        ),
        examples=("vulnbot", "vulnbot repl"),
    ),
    ManualTopic(
        name="init",
        summary="Create the VulnBot config directories and initial config file.",
        usage="vulnbot init",
        notes=(
            "Creates ~/.vulnbot by default, unless VULNBOT_CONFIG_DIR points somewhere else.",
        ),
        examples=("vulnbot init",),
    ),
    ManualTopic(
        name="doctor",
        summary="Check runtime readiness and configured integrations.",
        usage="vulnbot doctor",
        notes=(
            "Checks Python, node, npx, uvx, nmap, LLM config, MCP service registration, and exposed tool count.",
            "Use this before a real run when provider, MCP, or frontend tooling feels unclear.",
        ),
        examples=("vulnbot doctor",),
    ),
    ManualTopic(
        name="manual",
        summary="Print this full manual.",
        usage="vulnbot manual [TOPIC] [--format text|markdown|man]\nvulnbot man [TOPIC] [--format text|markdown|man]\nvulnbot --man",
        flags=(
            ("TOPIC", "Optional command/topic name such as scan, network-scan, config, or target-state."),
            ("--format text, -f text", "Human terminal format. This is the default."),
            ("--format markdown, -f markdown", "Markdown suitable for docs or README snippets."),
            ("--format man, -f man", "roff man-page format suitable for saving as vulnbot.1."),
        ),
        notes=(
            "The manual command is packaged with VulnBot, so it works from installed wheels and source checkouts.",
        ),
        examples=(
            "vulnbot manual",
            "vulnbot manual network-scan",
            "vulnbot manual --format man",
        ),
        aliases=("man", "help-man"),
    ),
)

TASK_COMMAND_NAMES = {"run", "persistent", "recon", "scan", "network-scan", "exploit"}


def render_manual(output_format: str = "text", topic: str | None = None) -> str:
    """Render the VulnBot manual in text, markdown, or roff man-page format."""

    fmt = output_format.strip().lower()
    if fmt not in {"text", "markdown", "man"}:
        raise ValueError("manual format must be one of: text, markdown, man")

    topics = _select_topics(topic)
    normalized_topic = _normalize_topic(topic)
    if fmt == "markdown":
        return _render_markdown(topics, normalized_topic)
    if fmt == "man":
        return _render_man(topics, normalized_topic)
    return _render_text(topics, normalized_topic)


def available_topics() -> list[str]:
    """Return the user-facing topic names accepted by the manual command."""

    return [topic.name for topic in COMMANDS]


def _select_topics(topic: str | None) -> tuple[ManualTopic, ...]:
    normalized = _normalize_topic(topic)
    if not normalized:
        return COMMANDS

    by_name = {item.name: item for item in COMMANDS}
    for item in COMMANDS:
        by_name.update({alias: item for alias in item.aliases})

    selected = by_name.get(normalized)
    if not selected:
        raise ValueError(
            f"unknown manual topic '{topic}'. Available topics: {', '.join(available_topics())}"
        )
    return (selected,)


def _normalize_topic(topic: str | None) -> str:
    return (topic or "").strip().lower().replace("_", "-")


def _provider_names() -> str:
    return ", ".join(provider.value for provider in PROVIDER_PRESETS)


def _render_text(topics: tuple[ManualTopic, ...], topic: str) -> str:
    lines: list[str] = [
        "VULNBOT(1) - VulnBot CLI Manual",
        f"Version: {__version__}",
        "",
        "SYNOPSIS",
        "  vulnbot [--help] [--version] [--man] [COMMAND] [ARGS]...",
        "  vulnbot manual [TOPIC] [--format text|markdown|man]",
        "",
        "DESCRIPTION",
        "  VulnBot is an AI-assisted CLI for authorized security testing. It combines",
        "  natural-language tasking, scoped autonomous loops, target history, reports,",
        "  MCP/built-in tools, a terminal workbench, and an optional local Web UI.",
        "",
        "ROOT OPTIONS",
    ]
    lines.extend(_render_text_pairs(ROOT_OPTIONS, indent_spaces=2))
    lines.extend(
        [
            "",
            "FAST START",
            "  vulnbot init",
            "  vulnbot config provider deepseek",
            "  vulnbot config set llm.api_key <key>",
            "  vulnbot doctor",
            "  vulnbot run https://authorized-target.example --allow-actions recon,scan",
            "",
            "COMMAND MAP",
        ]
    )
    for item in COMMANDS:
        lines.append(f"  {item.name:<13} {item.summary}")

    if not topic or any(item.name in TASK_COMMAND_NAMES for item in topics):
        lines.extend(_common_sections_text())

    lines.extend(["", "COMMAND DETAILS"])
    for item in topics:
        lines.extend(_topic_text(item))

    lines.extend(
        [
            "",
            "CONFIG AND ENVIRONMENT",
            f"  Provider presets: {_provider_names()}",
            "  Config directory: ~/.vulnbot by default, or VULNBOT_CONFIG_DIR when set.",
            "  High-value env vars: VULNBOT_LLM_API_KEY, VULNBOT_LLM_API_KEYS,",
            "  VULNBOT_LLM_PROVIDER, VULNBOT_LLM_BASE_URL, VULNBOT_LLM_MODEL,",
            "  VULNBOT_SESSION_OUTPUT_DIR, VULNBOT_SESSION_MAX_ROUNDS,",
            "  VULNBOT_SESSION_SHOW_THINKING, VULNBOT_SAFETY_PYTHON_EXECUTE_ENABLED.",
            "",
            "SAFETY",
            "  VulnBot is for authorized testing only. Scope flags and action constraints",
            "  are there to make allowed boundaries explicit and enforceable, but they do",
            "  not replace written authorization or a clear rules-of-engagement document.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _common_sections_text() -> list[str]:
    lines = [
        "",
        "COMMON TASK FLAGS",
    ]
    lines.extend(_render_text_pairs(COMMON_TASK_FLAGS, indent_spaces=2))
    lines.extend(
        [
            "",
            "ACTION CONSTRAINTS",
            f"  Recognized action names: {', '.join(ACTION_NAMES)}.",
            "  Example: --allow-actions recon,scan blocks direct exploit/report commands",
            "  and also constrains tool and phase transitions during agent execution.",
        ]
    )
    return lines


def _topic_text(topic: ManualTopic) -> list[str]:
    lines = [
        "",
        topic.name.upper(),
        f"  {topic.summary}",
        "",
        "  Usage:",
    ]
    for usage_line in topic.usage.splitlines():
        lines.append(f"    {usage_line}")

    if topic.flags:
        lines.extend(["", "  Arguments and flags:"])
        lines.extend(_render_text_pairs(topic.flags, indent_spaces=4))
    if topic.notes:
        lines.extend(["", "  Notes:"])
        lines.extend(f"    - {note}" for note in topic.notes)
    if topic.examples:
        lines.extend(["", "  Examples:"])
        lines.extend(f"    {example}" for example in topic.examples)
    return lines


def _render_text_pairs(pairs: tuple[tuple[str, str], ...], indent_spaces: int) -> list[str]:
    pad = " " * indent_spaces
    lines: list[str] = []
    for name, description in pairs:
        lines.append(f"{pad}{name}")
        lines.append(f"{pad}  {description}")
    return lines


def _render_markdown(topics: tuple[ManualTopic, ...], topic: str) -> str:
    lines: list[str] = [
        "# VulnBot CLI Manual",
        "",
        f"Version: `{__version__}`",
        "",
        "## Synopsis",
        "",
        "```bash",
        "vulnbot [--help] [--version] [--man] [COMMAND] [ARGS]...",
        "vulnbot manual [TOPIC] [--format text|markdown|man]",
        "```",
        "",
        "## Description",
        "",
        "VulnBot is an AI-assisted CLI for authorized security testing. It combines natural-language tasking, scoped autonomous loops, target history, reports, MCP/built-in tools, a terminal workbench, and an optional local Web UI.",
        "",
        "## Root Options",
        "",
    ]
    lines.extend(_markdown_table(["Option", "Meaning"], ROOT_OPTIONS))
    lines.extend(
        [
            "",
            "## Fast Start",
            "",
            "```bash",
            "vulnbot init",
            "vulnbot config provider deepseek",
            "vulnbot config set llm.api_key <key>",
            "vulnbot doctor",
            "vulnbot run https://authorized-target.example --allow-actions recon,scan",
            "```",
            "",
            "## Command Map",
            "",
        ]
    )
    lines.extend(_markdown_table(["Command", "Summary"], tuple((c.name, c.summary) for c in COMMANDS)))

    if not topic or any(item.name in TASK_COMMAND_NAMES for item in topics):
        lines.extend(
            [
                "",
                "## Common Task Flags",
                "",
            ]
        )
        lines.extend(_markdown_table(["Flag", "Meaning"], COMMON_TASK_FLAGS))
        lines.extend(
            [
                "",
                "## Action Constraints",
                "",
                f"Recognized action names: `{', '.join(ACTION_NAMES)}`.",
                "",
                "Example: `--allow-actions recon,scan` blocks direct exploit/report commands and also constrains tool and phase transitions during agent execution.",
            ]
        )

    lines.extend(["", "## Command Details", ""])
    for item in topics:
        lines.extend(_topic_markdown(item))

    lines.extend(
        [
            "",
            "## Config And Environment",
            "",
            f"Provider presets: `{_provider_names()}`.",
            "",
            "Config directory: `~/.vulnbot` by default, or `VULNBOT_CONFIG_DIR` when set.",
            "",
            "High-value env vars: `VULNBOT_LLM_API_KEY`, `VULNBOT_LLM_API_KEYS`, `VULNBOT_LLM_PROVIDER`, `VULNBOT_LLM_BASE_URL`, `VULNBOT_LLM_MODEL`, `VULNBOT_SESSION_OUTPUT_DIR`, `VULNBOT_SESSION_MAX_ROUNDS`, `VULNBOT_SESSION_SHOW_THINKING`, `VULNBOT_SAFETY_PYTHON_EXECUTE_ENABLED`.",
            "",
            "## Safety",
            "",
            "VulnBot is for authorized testing only. Scope flags and action constraints make allowed boundaries explicit and enforceable, but they do not replace written authorization or a clear rules-of-engagement document.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _topic_markdown(topic: ManualTopic) -> list[str]:
    lines = [
        f"### `{topic.name}`",
        "",
        topic.summary,
        "",
        "```bash",
        *topic.usage.splitlines(),
        "```",
    ]
    if topic.flags:
        lines.extend(["", "Arguments and flags:", ""])
        lines.extend(_markdown_table(["Name", "Meaning"], topic.flags))
    if topic.notes:
        lines.extend(["", "Notes:", ""])
        lines.extend(f"- {note}" for note in topic.notes)
    if topic.examples:
        lines.extend(["", "Examples:", "", "```bash", *topic.examples, "```"])
    lines.append("")
    return lines


def _markdown_table(headers: list[str], rows: tuple[tuple[str, str], ...]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for left, right in rows:
        lines.append(f"| `{left}` | {right} |")
    return lines


def _render_man(topics: tuple[ManualTopic, ...], topic: str) -> str:
    lines = [
        f'.TH VULNBOT 1 "" "VulnBot {__version__}" "VulnBot Manual"',
        ".SH NAME",
        "vulnbot \\- AI-assisted authorized security-testing CLI",
        ".SH SYNOPSIS",
        ".B vulnbot",
        "[--help] [--version] [--man] [COMMAND] [ARGS]...",
        ".br",
        ".B vulnbot manual",
        "[TOPIC] [--format text|markdown|man]",
        ".SH DESCRIPTION",
        "VulnBot combines natural-language tasking, scoped autonomous loops, target history, reports, MCP and built-in tools, a terminal workbench, and an optional local Web UI.",
        ".SH ROOT OPTIONS",
    ]
    lines.extend(_roff_pairs(ROOT_OPTIONS))
    lines.extend(
        [
            ".SH COMMAND MAP",
        ]
    )
    lines.extend(_roff_pairs(tuple((item.name, item.summary) for item in COMMANDS)))

    if not topic or any(item.name in TASK_COMMAND_NAMES for item in topics):
        lines.extend([".SH COMMON TASK FLAGS"])
        lines.extend(_roff_pairs(COMMON_TASK_FLAGS))
        lines.extend(
            [
                ".SH ACTION CONSTRAINTS",
                f"Recognized action names: {', '.join(ACTION_NAMES)}.",
            ]
        )

    lines.append(".SH COMMAND DETAILS")
    for item in topics:
        lines.extend(_topic_roff(item))

    lines.extend(
        [
            ".SH CONFIG AND ENVIRONMENT",
            f"Provider presets: {_provider_names()}.",
            ".PP",
            "Config directory: ~/.vulnbot by default, or VULNBOT_CONFIG_DIR when set.",
            ".PP",
            "High-value env vars: VULNBOT_LLM_API_KEY, VULNBOT_LLM_API_KEYS, VULNBOT_LLM_PROVIDER, VULNBOT_LLM_BASE_URL, VULNBOT_LLM_MODEL, VULNBOT_SESSION_OUTPUT_DIR, VULNBOT_SESSION_MAX_ROUNDS, VULNBOT_SESSION_SHOW_THINKING, VULNBOT_SAFETY_PYTHON_EXECUTE_ENABLED.",
            ".SH SAFETY",
            "VulnBot is for authorized testing only. Scope flags and action constraints make allowed boundaries explicit and enforceable, but they do not replace written authorization or a clear rules-of-engagement document.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _topic_roff(topic: ManualTopic) -> list[str]:
    lines = [
        ".SS " + _roff_escape(topic.name),
        _roff_escape(topic.summary),
        ".PP",
        ".B Usage:",
    ]
    for usage_line in topic.usage.splitlines():
        lines.extend([".br", _roff_escape(usage_line)])
    if topic.flags:
        lines.extend([".PP", ".B Arguments and flags:"])
        lines.extend(_roff_pairs(topic.flags))
    if topic.notes:
        lines.extend([".PP", ".B Notes:"])
        for note in topic.notes:
            lines.extend([".IP \\[bu] 2", _roff_escape(note)])
    if topic.examples:
        lines.extend([".PP", ".B Examples:"])
        for example in topic.examples:
            lines.extend([".br", _roff_escape(example)])
    return lines


def _roff_pairs(pairs: tuple[tuple[str, str], ...]) -> list[str]:
    lines: list[str] = []
    for name, description in pairs:
        lines.extend(
            [
                f".TP\n.B {_roff_escape(name)}",
                _roff_escape(description),
            ]
        )
    return lines


def _roff_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("-", "\\-")
