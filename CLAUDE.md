# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

VulnBot is an AI-driven penetration-testing CLI. A user gives a natural-language
instruction; an LLM agent drives an autonomous multi-round loop (Recon → Vuln
Discovery → Exploitation → Reporting) by calling tools, then emits a Markdown
report and a Python PoC. It speaks the OpenAI-compatible protocol and supports
many provider presets. **Authorized security testing only.**

Note: the product was renamed ClawBot/Vulnbot → **VulnBot**. The Python package
is `vulnbot`, the config dir is `~/.vulnbot/`, and env vars use the `VULNBOT_`
prefix. The README and CONTRIBUTING.md still contain stale `VULNCLAW_*` / `vulnclaw`
references in places — trust the code (`vulnbot/config/settings.py`) over the docs
for env-var names.

## Commands

```bash
pip install -e ".[dev,web,pdf,osint]"   # full dev install (matches CI)
pytest -q                                # run all tests (asyncio_mode=auto)
pytest tests/test_agent.py -q            # single file
pytest tests/test_agent.py::test_name    # single test
pytest tests/intel -q                    # the intel-module subsuite
ruff check vulnbot tests                  # lint (line-length 100, E501 ignored)

# Frontend (React + Vite, in frontend/)
cd frontend && npm ci && npx tsc -b      # install + typecheck (CI gate)
npm run build                             # tsc -b && vite build

vulnbot doctor                            # check runtime env (Python/Node/nmap/LLM/MCP)
```

CI (`.github/workflows/ci.yml`) runs on Ubuntu + Windows × Python 3.10–3.13:
`ruff check` → frontend `tsc -b` → `pytest -q`. Both ruff and tsc are hard gates.

### Test isolation

`conftest.py` redirects config and all temp output into `tests/.test-tmp/` and
overrides the `tmp_path` fixture to a project-local dir (the default pytest
`tmp_path` is intentionally replaced). Don't write tests that depend on the real
home directory or system `$TMPDIR`.

## Architecture

The entrypoint is `vulnbot/cli/main.py` (Typer app, registered as the `vulnbot`
script). It owns argument binding, REPL/TUI launchers, `doctor`, and user output
only — **no pentest logic lives here**.

The flow goes: **CLI/TUI/Web → orchestrator → AgentCore → loop_controller → tools**.

The classic `vulnbot` REPL now uses bounded parallel child-agent fan-out by default for auto-mode prompts. The runtime `parallel` commands only affect the current REPL session; persist defaults through `vulnbot config set session.repl_parallel_* ...` or the config TUI.

- **`vulnbot/orchestrator.py`** — the shared task lifecycle (`restore → run →
  save → summarize`) used identically by CLI, REPL, and Web. `repl_runner.py`
  is the interactive-shell driver. Put cross-surface task behavior here, not in
  any one frontend.

- **`vulnbot/agent/`** — the brain. `core.py` (`AgentCore`) is now a thin
  coordinator that wires together many single-responsibility modules:
  - `loop_controller.py` — the actual autonomous (`auto_pentest`) and
    `persistent_pentest` round loops.
  - `system_prompt.py` + `prompts.py` + `prompt_context.py` — dynamic system-prompt
    assembly (identity + contract + skills + MCP tools + per-round context).
  - `input_analysis.py` — target/phase detection and vuln-hint extraction from NL.
  - `anti_loop.py`, `ctf_mode.py`, `loop_controller.py` — completion signals,
    dead-loop detection (stale-rounds threshold), CTF flag state machine.
  - `context.py` — `SessionState`, `PentestPhase`, `TaskConstraints` (phase,
    findings, step records, allowed/blocked actions).
  - `builtin_tools.py` — the agent-callable tools that don't need MCP: `nmap`
    execution + XML parsing, `python_execute` (the experimental sandbox), target
    validation / reserved-IP + blocked-pattern guards, OpenAI tool-schema building.
  - `llm_client.py` — provider calls + streaming; `finding_parser.py` /
    `finding_similarity.py` — finding extraction and dedup; `token_counter.py`,
    `think_filter.py` (strips `<think>` output unless enabled).

- **`vulnbot/mcp/`** — MCP toolchain: `registry.py` (service/tool registration),
  `lifecycle.py` (attach/probe/call/degrade), `router.py` (NL → tool suggestion).
  Most services are `preview`/`placeholder`; only `fetch`/`memory` run in stable
  `local` mode pending a session-lifecycle manager.

- **`vulnbot/skills/`** — auto-dispatched pentest skills. `loader.py` +
  `dispatcher.py` route user intent to skills; `core/*.md` are flat-format core
  flows, `specialized/` holds knowledge bases with `references/` docs loaded on
  demand via the `load_skill_reference` tool. `crypto_tools.py` registers ~29
  encode/decode/crypto ops as the built-in `crypto_decode` tool.

- **`vulnbot/intel/`** — intelligence modules (CVE, OSINT, topology, compliance,
  findings, remediation) ported from HackBot, exposed to the agent via
  `intel/tools.py`. Has its own test subsuite under `tests/intel/`.

- **`vulnbot/target_state/`** — per-target persistence: snapshots, resume, diff,
  merge rules, rollback, target-level reports. This is what `orchestrator.py`
  restores from and saves to.

- **`vulnbot/config/`** — `schema.py` (Pydantic models, provider presets) +
  `settings.py` (YAML load/save + env overrides). Precedence: **env vars > config
  file (`~/.vulnbot/config.yaml`) > built-in defaults**. Don't hand-parse config
  elsewhere. REPL parallel settings live under `session.repl_parallel_enabled`,
  `session.repl_parallel_agents`, `session.repl_parallel_depth`,
  `session.repl_parallel_worker_rounds`, and `session.repl_parallel_surface_limit`.

- **`vulnbot/report/`** — Markdown/HTML report rendering + Python/bash PoC
  generation (`generator.py`, `poc_builder.py`, `pdf_exporter.py` behind the
  `pdf` extra).

- **`vulnbot/web/`** — FastAPI backend (behind the `web` extra): `app.py` routes,
  `schemas.py` (the frontend/backend contract — keep `frontend/` aligned with it),
  `task_manager.py`, `stream.py`, and a `services/` layer. `frontend/` is the
  React/Vite SPA.

## Conventions

- Optional features degrade gracefully behind `try/except` imports (KB retriever,
  dnspython, reportlab, chromadb) — follow that pattern rather than hard-failing
  when an extra isn't installed.
- Version source of truth is `pyproject.toml`; `vulnbot/__init__.py` is a fallback.
- The default `vulnbot` (no args) opens the classic REPL; the TUI opens *only*
  via explicit `vulnbot tui`. Don't change that default.
- In the REPL, `parallel` controls are runtime-only unless changed through config
  persistence.
