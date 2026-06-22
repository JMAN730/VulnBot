# Contributing to VulnClaw

Thanks for contributing to VulnClaw.

This guide is meant to help contributors understand the current code structure quickly, make changes at the right layer, and avoid adding behavior that works locally but makes the architecture harder to maintain.

---

## Project Structure

```text
VulnClaw/
|-- vulnclaw/
|   |-- __init__.py              # Package version and base metadata
|   |-- orchestrator.py          # Shared CLI / Web task orchestration entrypoint
|   |-- repl_runner.py           # Shared REPL execution helper
|   |-- agent/                   # Agent core logic
|   |   |-- core.py              # AgentCore coordination shell
|   |   |-- llm_client.py        # LLM calls, retries, and tool-summary feedback
|   |   |-- tool_call_manager.py # Tool-call deduplication, execution, and result wrapping
|   |   |-- builtin_tools.py     # python_execute / nmap_scan / MCP bridge
|   |   |-- context.py           # Session state, findings, steps, and lifecycle state
|   |   |-- runtime_state.py     # Runtime loop state
|   |   |-- loop_controller.py   # Auto and persistent main loops
|   |   |-- finding_parser.py    # Finding extraction, evidence levels, and lifecycle grouping
|   |   |-- prompt_context.py    # Round context and attack summaries
|   |   |-- prompts.py           # Prompt construction helpers
|   |   |-- system_prompt.py     # Dynamic system prompt composition
|   |   |-- input_analysis.py    # Target, phase, and vulnerability hint extraction
|   |   |-- anti_loop.py         # Anti-loop logic, failed goals, and attack-path tracking
|   |   |-- recon_tracker.py     # Recon dimension completion tracking
|   |   |-- ctf_mode.py          # CTF flag detection and verification
|   |   |-- skill_context.py     # Skill context selection
|   |   |-- kb_context.py        # Knowledge-base context injection
|   |   `-- think_filter.py      # Think-tag display and hiding
|   |-- cli/
|   |   |-- main.py              # CLI commands, doctor, web launcher, target-state CLI
|   |   |-- tui.py               # TUI data classes, dashboard rendering, and color constants
|   |   `-- tui_textual.py       # Textual-powered TUI workbench
|   |-- config/                  # Config schema, loading, saving, and env overrides
|   |-- kb/                      # Knowledge-base storage, retrieval, and updates
|   |-- mcp/
|   |   |-- lifecycle.py         # attach / probe / call / degrade behavior
|   |   |-- registry.py          # Service status, health, attach state, and tool registry
|   |   `-- router.py            # Natural-language intent to MCP tool suggestions
|   |-- report/                  # Report generation, filtering, and PoC generation
|   |-- skills/                  # Built-in markdown skills, loader, and dispatcher
|   |   |-- core/                # Core flat-format skills
|   |   |-- specialized/         # Directory-format specialized skills
|   |   |-- crypto_tools.py      # crypto_decode built-in tool implementation
|   |   |-- dispatcher.py        # Natural-language intent to Skill routing
|   |   `-- loader.py            # Flat and directory Skill loading plus reference reads
|   |-- target_state/            # Target history, preview, diff, rollback, and resume plans
|   |-- web/
|   |   |-- app.py               # FastAPI routes and static frontend serving
|   |   |-- schemas.py           # Web API request and response models
|   |   |-- task_manager.py      # Web task status and history persistence
|   |   |-- stream.py            # SSE event encoding
|   |   |-- services/            # config / report / target / task / MCP service layer
|   |   `-- static/              # Static fallback page when the frontend dist is absent
|   `-- warstories/              # Built-in markdown case studies
|-- frontend/
|   |-- src/
|   |   |-- pages/               # Dashboard / Tasks / Target / Snapshots / Reports / Settings
|   |   |-- api/                 # Frontend API wrappers
|   |   |-- hooks/               # React Query hooks
|   |   `-- types/               # Shared frontend types
|   `-- package.json             # Frontend build and development scripts
|-- scripts/                     # Release preflight and dist validation scripts
|-- tests/                       # Backend, CLI, MCP, release, web, and report tests
|-- .github/workflows/           # CI, preflight, and release workflows
|-- README.md                    # Main project documentation
|-- README_EN.md                 # English documentation mirror
|-- pyproject.toml               # Package metadata and Hatch build rules
`-- CONTRIBUTING.md              # This file
```

---

## Finding The Right Code

### 1. Agent Behavior

Start in `vulnclaw/agent/` when changing autonomous or persistent penetration-testing loops, tool-call orchestration, LLM request and response handling, recon, CTF mode, anti-loop logic, finding lifecycle logic, evidence levels, or result parsing.

`core.py` is primarily a coordination shell. Unless the change is truly entrypoint-level behavior, prefer updating the focused helper module instead of adding more logic back into `core.py`.

### 2. Shared Task Flow

Start in `vulnclaw/orchestrator.py` and `vulnclaw/repl_runner.py` when changing shared CLI, Web, or REPL task lifecycle behavior, including restore -> run -> save -> summarize flows.

When the same behavior appears in both CLI and Web code, consolidate it here instead of duplicating logic in `cli/main.py` and `web/services/task_service.py`.

### 3. CLI And REPL Behavior

Use `vulnclaw/cli/main.py` for Typer commands, REPL experience, `doctor` output, the `web` launcher, and `target-state` subcommands.

This layer owns entrypoints, argument binding, and user output. It should not carry the core penetration-testing logic.

### 3.1 TUI Workbench

Use `vulnclaw/cli/tui.py` and `vulnclaw/cli/tui_textual.py` for TUI dashboard layout, slash commands, command-palette interactions, prompt and confirmation state machines, and terminal color themes.

Architecture:

```text
main.py (Typer CLI)
  -> tui.py (run_tui delegation)
       -> tui_textual.py (run_tui_textual -> Textual App)
            -> DashboardScreen
               -> CommandPalette
               -> SecondaryPopup
               -> RichLog + spinner
            -> VulnClawApp
```

| File | Responsibility |
|------|----------------|
| `tui.py` | `TuiState`, `TuiMode`, `TuiTaskDraft`, Rich dashboard rendering, color constants, slash command registry, and `run_tui()` |
| `tui_textual.py` | Textual app implementation, dashboard layout, command palette, secondary popup, CSS, slash command handlers, prompt state machine, and subprocess execution engine |

Slash commands are registered with `@_register_handler("...")`. `_dispatch()` routes based on input. Handler signature: `fn(session: dict, args: str) -> str | None`.

Return values:

- `"quit"` exits the TUI.
- `"launch"` starts a penetration-testing task inside the TUI subprocess runner.
- `None` sets prompt state and opens a secondary popup.

Inline arguments are supported, for example `/target example.com`, `/mode deep`, and `/scope host=1.2.3.4`. Without arguments, a secondary popup collects interactive input.

Prompt state uses `session["_prompt"]`:

- `("input", label, callback, default)` shows a label and input box.
- `("choice", label, choices, callback)` shows a choice list.
- `("confirm", label, callback)` shows a yes/no prompt.
- `("message", text)` shows a dismissible message.
- `("chain", fields, idx, callback)` collects multiple fields in sequence.

The command palette extends `ListView`. Typing `/` opens it above the input field. Arrow keys move the highlighted item, and `Tab` or `Enter` completes the command.

`SecondaryPopup` opens automatically when a slash command needs missing arguments. Escape closes the active popup, then the command palette, then the prompt state. Idle Escape no longer exits the TUI; use `/quit` or `Ctrl+C`.

Execution mode starts when `/run` or `/start` returns `"launch"`:

1. Hide the dashboard and show the `RichLog` output area.
2. Show the spinner beside the input.
3. Disable input and start `python -m vulnclaw.cli.main <cmd> <args>` with UTF-8 output decoding.
4. Read subprocess stdout on a background thread and write it into `RichLog`.
5. On completion, hide the spinner, enable input, and reload configuration.
6. `Ctrl+Shift+C` copies the output log to the system clipboard.

### 4. Configuration

Use `vulnclaw/config/` for configuration model definitions, load/save behavior, environment overrides, and directory paths. Avoid hand-written config parsing in business logic.

### 5. Reports

Use `vulnclaw/report/` for Markdown and HTML report rendering, report content filtering, PoC generation, verification summaries, and source-location information.

`generator.py` is the main entrypoint, and it affects both target-state reports and persistent-cycle reports.

### 6. MCP Behavior

Use `vulnclaw/mcp/` for service status, health, attach state, tool registration, attach/probe/call/degrade logic, and natural-language intent to MCP tool suggestions.

Current state:

- `fetch` and `memory` run locally.
- `chrome-devtools` and `burp` have real stdio attach support, dynamic tool discovery, and persistent-session scaffolding.
- Other services mostly degrade to structured placeholders.

When changing MCP behavior, also check diagnostics display, `error_type` classification, and degraded behavior after attach failures.

### 7. Target State

Use `vulnclaw/target_state/` for target-state persistence, merge rules, preview, diff, rollback, resume strategy, and summary generation.

This package owns sharing results across commands for the same target. Do not move this logic back into `core.py` or duplicate it in UI code.

### 8. Web Backend

Use `vulnclaw/web/` for FastAPI routes, request and response schemas, web task status, task history, and the config/report/target/task/MCP service layer.

Prefer putting logic in `web/services/` so route functions stay thin.

### 9. Web UI

Use `frontend/` for Dashboard, Task Console, Target State, Snapshots, Reports, Settings, React Query hooks, frontend API bindings, console interactions, and styling.

Keep frontend/backend contracts aligned with `vulnclaw/web/schemas.py`.

### 10. Packaging And Release

Use `scripts/`, `.github/workflows/`, and `pyproject.toml` for local preflight, dist validation, CI/release workflows, build include/exclude rules, and package metadata.

The version source of truth is `pyproject.toml`; `vulnclaw/__init__.py` is a fallback.

### 11. Skills

Use `vulnclaw/skills/` when adding or changing core penetration-testing flows, specialized knowledge bases, reference documents, natural-language skill dispatch rules, or `load_skill_reference` datasets.

Skill formats:

| Format | Location | Purpose |
|--------|----------|---------|
| flat-format | `vulnclaw/skills/core/*.md` | Core flow skills such as `pentest-flow`, `recon`, and `reporting` |
| directory-format | `vulnclaw/skills/specialized/<skill-name>/` | Specialized skills with `SKILL.md` and optional references |

Directory-format conventions:

- `SKILL.md` uses YAML frontmatter with at least `name` and `description`.
- `references/` may contain `.md`, `.yaml`, or `.yml` files.
- References should be split by topic instead of putting an entire knowledge base into `SKILL.md`.
- Add strong routing keywords in `dispatcher.py` when a new skill needs to trigger automatically.
- Update `tests/test_skills.py` and the README skill table after adding or changing a skill.

`secknowledge-skill` is the external knowledge-base integration example:

- Location: `vulnclaw/skills/specialized/secknowledge-skill/`
- Source: `Pa55w0rd/secknowledge-skill`
- Content: upstream references plus VulnClaw-specific routing notes
- Triggers: SRC, vulnerability research, bug bounty, GAARM, OWASP LLM/ASI/WSTG, and Web+AI security testing signals

When syncing external skills, preserve source, license, and integration notes, and compare file lists to ensure references are not missing.

---

## Contribution Tips

- Change the right module instead of moving separated responsibilities back into `core.py`.
- For shared task flow, prefer `orchestrator.py` or `repl_runner.py`.
- Add or update tests when changing behavior.
- For packaging or release changes, check `pyproject.toml`, `scripts/`, and `.github/workflows/`.
- Keep documentation aligned with real implementation, especially around MCP, sandboxing, and security boundaries.

---

## Before Opening A PR

Check at minimum:

1. Relevant tests pass.
2. Documentation matches the implementation.
3. New logic lives in the right module instead of a large catch-all file.
4. Version, CLI output, README, and packaging docs are updated when affected.

---

## Web UI Notes

When changing Web UI behavior, start with:

- `vulnclaw/web/`
- `frontend/`

The Web side includes backend APIs, task status persistence, target preview and diff, MCP diagnostics, and Settings safety-mode configuration.

Principles:

- Reuse the existing agent, target-state, and report layers.
- Do not duplicate a separate recovery flow in the Web layer.
- Do not let the frontend hold sensitive keys directly.

---

## Suggested Preflight

Before submitting, run at least:

```bash
python scripts/release_preflight.py
python scripts/release_preflight.py --build
```

The preflight checks:

- Version consistency between `pyproject.toml` and `vulnclaw.__version__`
- Backend `pytest -q`
- Frontend `npx tsc -b`
- Optional build and dist artifact validation
