# Repository Guidelines

## Project Structure & Module Organization

VulnBot is a Python 3.10+ package with an optional Vite/React web UI. Core source lives in `vulnbot/`: `agent/` handles the LLM loop and tools, `cli/` exposes Typer and TUI entrypoints, `web/` contains FastAPI routes and services, `report/` renders reports, and `skills/` stores built-in pentest skills. Tests live in `tests/`, with focused Intel tests under `tests/intel/`. Frontend code is in `frontend/src/`, static fallback UI is in `vulnbot/web/static/`, release helpers are in `scripts/`, docs are in `docs/`, and images are in `assets/`.

## Build, Test, and Development Commands

- `make install`: install Python dev extras and frontend dependencies.
- `make test`: run the backend pytest suite configured in `pyproject.toml`.
- `make lint`: run Ruff checks for imports and basic Python style.
- `make build`: build Python distributions and the frontend.
- `make release-preflight`: run release-oriented validation before packaging.
- `make dev-web`: start the Vite development server.

Direct equivalents remain available, including `python -m pytest`, `python -m ruff check .`, and `npm --prefix frontend run build`.

The classic `vulnbot` REPL now defaults to bounded parallel auto-mode fan-out when a natural-language auto task is detected. Use the runtime `parallel` command family inside the REPL to inspect or override that behavior for the current session; persist long-lived defaults through `vulnbot config set session.repl_parallel_* ...` or the config TUI.

## Coding Style & Naming Conventions

Python uses 4-space indentation, type hints where they clarify contracts, and `snake_case` for modules, functions, and variables. Keep CLI and route handlers thin; put reusable behavior in service or helper modules. Ruff uses a 100-character line length, Python 3.10 target, import sorting, and E/F/I/W lint rules. React components use PascalCase filenames such as `SettingsPage.tsx`; hooks and utilities use camelCase or descriptive module names.

## Testing Guidelines

Use pytest for backend, CLI, report, MCP, and web-service coverage. Name tests `test_*.py` and keep fixtures in `conftest.py` or the nearest test package. Add or update tests beside changed behavior, especially for agent parsing, report output, configuration, web schemas, skill dispatch, and REPL orchestration. For frontend changes, run `npm --prefix frontend run build`.

## Commit & Pull Request Guidelines

Recent history uses concise Conventional Commit-style subjects, for example `feat(web): ...`, `style: ...`, `docs: ...`, and `rebrand: ...`. Keep commits scoped and imperative. Pull requests should explain the user-visible change, list tests run, link relevant issues, and include screenshots or short clips for UI changes.

## Security & Configuration Tips

This is an authorized security-testing tool. Do not commit API keys, target secrets, generated session data, or local config. Document provider setup with commands like `vulnbot config provider deepseek` and `vulnbot config set llm.api_key ...`, not hard-coded values. REPL parallel defaults are configurable through `session.repl_parallel_enabled`, `session.repl_parallel_agents`, `session.repl_parallel_depth`, `session.repl_parallel_worker_rounds`, and `session.repl_parallel_surface_limit`.
