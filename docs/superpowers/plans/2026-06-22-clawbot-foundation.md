# ClawBot Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up the `clawbot` package as a clean fork of VulnClaw (renamed, tests green, attribution in place) with the `intel/` tool-plumbing seam wired into the agent, ready for per-module ports.

**Architecture:** Copy the VulnClaw working tree into a fresh sibling repo `C:\Users\jo\github\clawbot`, mechanically rename `vulnclaw` -> `clawbot` (package, imports, entrypoint, config dir), then add an `intel/` subpackage whose tool schemas/dispatch are registered at two seams in `agent/builtin_tools.py`. A stub `cve_lookup` tool proves the dispatch path end-to-end via TDD; real modules replace stubs in later plans.

**Tech Stack:** Python 3.10+, hatchling, typer, httpx, pydantic, pytest (`asyncio_mode=auto`), ruff. Source donors (read-only): `C:\Users\jo\github\VulnClaw`, `C:\Users\jo\github\hackbot`.

**Source-of-truth spec:** `docs/superpowers/specs/2026-06-22-clawbot-unified-design.md` (in the hackbot repo).

---

## File Structure

| Path (under `clawbot/` repo root) | Responsibility |
|---|---|
| `clawbot/` | Renamed package (was `vulnclaw/`) — agent, mcp, skills, report, target_state, config, cli, web |
| `clawbot/intel/__init__.py` | New subpackage marker |
| `clawbot/intel/tools.py` | Intel tool schemas + name->dispatcher routing |
| `clawbot/agent/builtin_tools.py` | Extended at two seams (schema list + dispatch branch) |
| `tests/intel/test_tool_plumbing.py` | Tests dispatch routing + schema exposure |
| `NOTICE` | Dual attribution (Yashab Alam, UncleC) |
| `pyproject.toml` | Renamed project + entrypoint `clawbot = "clawbot.cli.main:app"` |

---

## Task 1: Scaffold the clawbot repo from VulnClaw

**Files:**
- Create: `C:\Users\jo\github\clawbot\` (entire tree, copied from VulnClaw)

- [ ] **Step 1: Copy the VulnClaw working tree (excluding git/caches) to the new sibling dir**

Run (Bash tool):
```bash
SRC=/c/Users/jo/github/VulnClaw
DST=/c/Users/jo/github/clawbot
mkdir -p "$DST"
rsync -a --exclude='.git' --exclude='__pycache__' --exclude='.pytest_cache' \
  --exclude='.test-tmp' --exclude='.vs' --exclude='dist' --exclude='build' \
  --exclude='frontend/node_modules' "$SRC"/ "$DST"/
ls "$DST"
```
Expected: top-level listing shows `vulnclaw/  tests/  pyproject.toml  README.md ...` (no `.git`).

> If `rsync` is unavailable on this Windows host, use `cp -a "$SRC"/. "$DST"/` then `find "$DST" -name __pycache__ -type d -prune -exec rm -rf {} +` and `rm -rf "$DST/.git"`.

- [ ] **Step 2: Initialize a fresh git repo**

Run:
```bash
cd /c/Users/jo/github/clawbot && git init -q && git add -A && git commit -q -m "chore: seed ClawBot from VulnClaw working tree" && git branch --show-current
```
Expected: prints `master` or `main`; one commit exists.

---

## Task 2: Mechanical package rename vulnclaw -> clawbot

**Files:**
- Modify: every `*.py` under `clawbot/` repo (import strings), `pyproject.toml`, rename dir `vulnclaw/ -> clawbot/`

- [ ] **Step 1: Rename the package directory**

Run:
```bash
cd /c/Users/jo/github/clawbot && git mv vulnclaw clawbot && ls clawbot/__init__.py
```
Expected: `clawbot/__init__.py` exists.

- [ ] **Step 2: Rewrite import + string references**

Run (covers `from vulnclaw`, `import vulnclaw`, `vulnclaw.`, the env var, and the config dir):
```bash
cd /c/Users/jo/github/clawbot
grep -rl --include='*.py' --include='*.toml' --include='*.md' 'vulnclaw\|VulnClaw\|VULNCLAW' . | while read -r f; do
  sed -i 's/from vulnclaw/from clawbot/g; s/import vulnclaw/import clawbot/g; s/\bvulnclaw\./clawbot./g; s/VULNCLAW_CONFIG_DIR/CLAWBOT_CONFIG_DIR/g; s/\.vulnclaw\b/.clawbot/g' "$f"
done
grep -rn 'from vulnclaw\|import vulnclaw\|vulnclaw\.' --include='*.py' clawbot | head
```
Expected: final grep prints nothing (no residual code references).

- [ ] **Step 3: Update pyproject project name, entrypoint, and packages**

Edit `pyproject.toml`:
```toml
[project]
name = "clawbot"
# ...
[project.scripts]
clawbot = "clawbot.cli.main:app"

[tool.hatch.build.targets.wheel]
packages = ["clawbot"]
```
Also update `[tool.hatch.build.targets.sdist] include` entry `/vulnclaw` -> `/clawbot`.

- [ ] **Step 4: Update the config dir constant**

In `clawbot/config/settings.py`, confirm Step 2 produced:
```python
CONFIG_DIR = Path(os.environ.get("CLAWBOT_CONFIG_DIR", str(Path.home() / ".clawbot")))
```
If not, edit it to match.

- [ ] **Step 5: Commit the rename**

```bash
cd /c/Users/jo/github/clawbot && git add -A && git commit -q -m "refactor: rename package vulnclaw -> clawbot" && echo ok
```
Expected: `ok`.

---

## Task 3: Verify the renamed base installs and tests pass

**Files:** none (verification only)

- [ ] **Step 1: Editable install into VulnClaw's venv (or a fresh one)**

Run (PowerShell tool):
```powershell
cd C:\Users\jo\github\clawbot
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -q -e ".[dev]"
.\.venv\Scripts\python.exe -c "import clawbot; from clawbot.cli.main import app; print('import ok')"
```
Expected: `import ok`.

- [ ] **Step 2: Run the carried-over test suite**

Run:
```powershell
cd C:\Users\jo\github\clawbot
.\.venv\Scripts\python.exe -m pytest -q
```
Expected: same pass count as VulnClaw upstream (no import errors from the rename). If any test hard-codes `vulnclaw` paths/config dir, fix those tests to `clawbot` and note it.

- [ ] **Step 3: Verify the CLI entrypoint**

Run:
```powershell
.\.venv\Scripts\clawbot.exe --help
```
Expected: typer help text renders with `clawbot` as the program name.

- [ ] **Step 4: Commit any test fixups**

```bash
cd /c/Users/jo/github/clawbot && git add -A && git commit -q -m "test: fix residual vulnclaw references after rename" && echo ok || echo "nothing to commit"
```

---

## Task 4: Attribution & licensing

**Files:**
- Create: `NOTICE`
- Modify: `README.md`, `README_EN.md` (credit block)

- [ ] **Step 1: Write NOTICE**

Create `C:\Users\jo\github\clawbot\NOTICE`:
```
ClawBot
=======
ClawBot is a derivative work combining two MIT-licensed projects:

  VulnClaw  — Copyright (c) UncleC   — https://github.com/Unclecheng-li/VulnClaw
  HackBot   — Copyright (c) Yashab Alam — https://github.com/yashab-cyber/hackbot

ClawBot uses VulnClaw as its base (agent core, MCP toolchain, skills, CLI/TUI/web)
and ports selected intelligence modules from HackBot (CVE, OSINT, topology,
compliance/MITRE, findings scoring, remediation, PDF reporting).

The full text of each upstream MIT license is retained below.
```
Append both upstream LICENSE texts under this header (read `VulnClaw/LICENSE` and `hackbot/LICENSE`).

- [ ] **Step 2: Add a credits block near the top of README_EN.md**

Insert after the badges:
```markdown
> **ClawBot** merges [VulnClaw](https://github.com/Unclecheng-li/VulnClaw) (base)
> and intelligence modules from [HackBot](https://github.com/yashab-cyber/hackbot).
> Both are MIT-licensed; see [`NOTICE`](NOTICE).
```

- [ ] **Step 3: Commit**

```bash
cd /c/Users/jo/github/clawbot && git add -A && git commit -q -m "docs: add NOTICE and dual upstream attribution" && echo ok
```

---

## Task 5: Intel subpackage skeleton + tool registry

**Files:**
- Create: `clawbot/intel/__init__.py`
- Create: `clawbot/intel/tools.py`
- Test: `tests/intel/test_tool_plumbing.py`

- [ ] **Step 1: Write the failing test**

Create `tests/intel/test_tool_plumbing.py`:
```python
import pytest

from clawbot.intel.tools import INTEL_TOOL_NAMES, dispatch_intel_tool, intel_tool_schemas


def test_schemas_expose_cve_lookup():
    names = {s["function"]["name"] for s in intel_tool_schemas()}
    assert "cve_lookup" in names


def test_intel_tool_names_match_schemas():
    schema_names = {s["function"]["name"] for s in intel_tool_schemas()}
    assert schema_names == set(INTEL_TOOL_NAMES)


@pytest.mark.asyncio
async def test_dispatch_unknown_tool_returns_structured_error():
    out = await dispatch_intel_tool(agent=None, tool_name="nope", args={})
    assert "[intel_error]" in out


@pytest.mark.asyncio
async def test_dispatch_cve_lookup_stub_is_structured():
    out = await dispatch_intel_tool(agent=None, tool_name="cve_lookup", args={"query": "openssl"})
    # Stub until the CVE plan lands; must be a structured, non-raising result.
    assert isinstance(out, str) and out
```

- [ ] **Step 2: Run it to confirm it fails**

Run: `.\.venv\Scripts\python.exe -m pytest tests/intel/test_tool_plumbing.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'clawbot.intel'`.

- [ ] **Step 3: Create the subpackage marker**

Create `clawbot/intel/__init__.py`:
```python
"""ClawBot intelligence modules ported from HackBot (CVE, OSINT, topology,
compliance, findings, remediation). Exposed to the agent as builtin tools."""
```

- [ ] **Step 4: Implement the tool registry with a cve_lookup stub**

Create `clawbot/intel/tools.py`:
```python
"""Intel tool schemas (OpenAI format) and name->dispatcher routing.

Each real module (cve/osint/topology/compliance/remediation) registers its
async handler here. Until a module's port lands, its handler is a structured
stub so the dispatch path is testable end-to-end.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable

# Read-only tools the constraint policy may treat as safe (no target egress,
# no host-changing action).
READ_ONLY_INTEL_TOOLS: set[str] = {"cve_lookup", "compliance_map", "remediation_advice"}


def intel_tool_schemas() -> list[dict[str, Any]]:
    """OpenAI tool schemas for all intel tools."""
    return [
        {
            "type": "function",
            "function": {
                "name": "cve_lookup",
                "description": (
                    "Look up CVEs by keyword or CVE-ID against NVD, with optional "
                    "exploit-PoC discovery. Read-only."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Keyword (e.g. 'openssl 3.0') or a CVE-ID (e.g. CVE-2024-3094).",
                        },
                        "limit": {"type": "integer", "description": "Max results.", "default": 5},
                    },
                    "required": ["query"],
                },
            },
        },
    ]


INTEL_TOOL_NAMES: list[str] = [s["function"]["name"] for s in intel_tool_schemas()]


async def _stub(tool_name: str, args: dict[str, Any]) -> str:
    return f"[intel_pending] {tool_name} is not yet implemented in this build."


# Handlers are filled in by each module's port plan. Stubs keep dispatch testable.
_HANDLERS: dict[str, Callable[[Any, dict[str, Any]], Awaitable[str]]] = {}


async def dispatch_intel_tool(agent: Any, tool_name: str, args: dict[str, Any]) -> str:
    """Route an intel tool call to its handler; structured error on unknown name."""
    if tool_name not in INTEL_TOOL_NAMES:
        return f"[intel_error] unknown intel tool: {tool_name}"
    handler = _HANDLERS.get(tool_name)
    if handler is None:
        return await _stub(tool_name, args)
    return await handler(agent, args)
```

- [ ] **Step 5: Run the test to confirm it passes**

Run: `.\.venv\Scripts\python.exe -m pytest tests/intel/test_tool_plumbing.py -q`
Expected: 4 passed.

- [ ] **Step 6: Commit**

```bash
cd /c/Users/jo/github/clawbot && git add -A && git commit -q -m "feat(intel): add intel subpackage + tool registry with cve_lookup stub" && echo ok
```

---

## Task 6: Wire intel tools into the agent (two seams)

**Files:**
- Modify: `clawbot/agent/builtin_tools.py` (tool-list builder + `execute_mcp_tool` dispatch)
- Test: `tests/intel/test_agent_seam.py`

- [ ] **Step 1: Confirm the two seam points (already located against upstream)**

The builder is `build_openai_tools(mcp_manager: Any) -> list[dict]` (def ~line 263, `return tools` ~line 479). The dispatcher is `execute_mcp_tool(agent, tool_name, args)` (def ~line 70). Re-run to confirm line numbers after the rename:
```bash
cd /c/Users/jo/github/clawbot
grep -n 'def build_openai_tools\|def execute_mcp_tool\|return tools' clawbot/agent/builtin_tools.py
```
Expected: prints `build_openai_tools`, `execute_mcp_tool`, and `return tools`.

- [ ] **Step 2: Write the failing test**

Create `tests/intel/test_agent_seam.py`:
```python
import pytest

from clawbot.agent import builtin_tools as bt


def test_builder_includes_intel_schemas():
    schemas = bt.build_openai_tools(mcp_manager=None)
    names = {s["function"]["name"] for s in schemas}
    assert "cve_lookup" in names


@pytest.mark.asyncio
async def test_execute_routes_intel_tool():
    out = await bt.execute_mcp_tool(agent=_FakeAgent(), tool_name="cve_lookup", args={"query": "x"})
    assert isinstance(out, str) and out


class _FakeAgent:
    session_state = None
```

> `build_openai_tools(None)` must tolerate a `None` mcp_manager for the test. If it dereferences the manager before the intel `tools.extend`, guard the manager access or pass a minimal fake with an empty tool list (confirm against the code in Step 1).

- [ ] **Step 3: Run it to confirm it fails**

Run: `.\.venv\Scripts\python.exe -m pytest tests/intel/test_agent_seam.py -q`
Expected: FAIL — `cve_lookup` not in builtin schema names.

- [ ] **Step 4: Add seam A — extend the tool-list builder**

In `clawbot/agent/builtin_tools.py`, add at the top of the module:
```python
from clawbot.intel.tools import (
    INTEL_TOOL_NAMES,
    dispatch_intel_tool,
    intel_tool_schemas,
)
```
Then, immediately before the builder's `return tools`, add:
```python
    tools.extend(intel_tool_schemas())
```

- [ ] **Step 5: Add seam B — route dispatch in execute_mcp_tool**

In `execute_mcp_tool`, after the constraint-validation block and before the `if tool_name == "python_execute":` branch, add:
```python
    if tool_name in INTEL_TOOL_NAMES:
        return await dispatch_intel_tool(agent, tool_name, args)
```

- [ ] **Step 6: Run both intel test files**

Run: `.\.venv\Scripts\python.exe -m pytest tests/intel -q`
Expected: all passed.

- [ ] **Step 7: Run the full suite to confirm no regression**

Run: `.\.venv\Scripts\python.exe -m pytest -q`
Expected: prior pass count + the new intel tests, all green.

- [ ] **Step 8: Commit**

```bash
cd /c/Users/jo/github/clawbot && git add -A && git commit -q -m "feat(agent): register intel tools in builtin tool list + dispatch" && echo ok
```

---

## Task 7: Constraint-policy classification for read-only intel tools

**Files:**
- Modify: `clawbot/agent/constraint_policy.py` (treat `READ_ONLY_INTEL_TOOLS` as safe)
- Test: `tests/intel/test_constraints.py`

- [ ] **Step 1: Inspect how actions are inferred**

Run:
```bash
cd /c/Users/jo/github/clawbot
grep -n 'def infer_tool_action\|def validate_tool_action' clawbot/agent/constraint_policy.py
```
Expected: both function locations.

- [ ] **Step 2: Write the failing test**

Create `tests/intel/test_constraints.py`:
```python
from clawbot.agent.constraint_policy import infer_tool_action


def test_cve_lookup_is_passive():
    action = infer_tool_action("cve_lookup", {"query": "x"})
    # Read-only intel must not be classified as an active/intrusive action.
    assert action in {"passive", "recon", "read", "info"}
```

> Adjust the expected action label set to match the project's actual taxonomy discovered in Step 1.

- [ ] **Step 3: Run to confirm it fails**

Run: `.\.venv\Scripts\python.exe -m pytest tests/intel/test_constraints.py -q`
Expected: FAIL (likely classified as unknown/active).

- [ ] **Step 4: Classify read-only intel tools as passive**

In `infer_tool_action`, add an early branch using the shared set:
```python
    from clawbot.intel.tools import READ_ONLY_INTEL_TOOLS
    if tool_name in READ_ONLY_INTEL_TOOLS:
        return "passive"  # use the project's passive/recon label
```

- [ ] **Step 5: Run to confirm it passes**

Run: `.\.venv\Scripts\python.exe -m pytest tests/intel/test_constraints.py -q`
Expected: PASS.

- [ ] **Step 6: Full suite + ruff**

Run:
```powershell
cd C:\Users\jo\github\clawbot
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check clawbot tests
```
Expected: tests green; ruff clean (fix any import-order/lint nits).

- [ ] **Step 7: Commit**

```bash
cd /c/Users/jo/github/clawbot && git add -A && git commit -q -m "feat(agent): classify read-only intel tools as passive for constraint policy" && echo ok
```

---

## Subsequent plans (authored per-module at port time)

Each reads the full HackBot source for the module, ports it to httpx + ClawBot
conventions, replaces the corresponding entry in `_HANDLERS`, adds its tool
schema(s) to `intel_tool_schemas()`, adds a methodology skill, and ships unit
tests. They follow this plan's template:

- **Plan 2 — CVE** (`hackbot/hackbot/core/cve.py` -> `clawbot/intel/cve.py`): real `cve_lookup`, NVD via httpx, `skills/.../cve-triage.md`.
- **Plan 3 — OSINT** (`core/osint.py` -> `intel/osint.py`): `osint_recon` tool, `[osint]` extra.
- **Plan 4 — Topology** (`core/topology.py` -> `intel/topology.py`): `topology_build`, stdlib XML parse.
- **Plan 5 — Findings** (`core/vulndb.py` logic -> `intel/findings.py`): `score_risk`, `annotate_compliance`, `diff_assessments` over `target_state`.
- **Plan 6 — Compliance/MITRE** (`core/compliance.py` -> `intel/compliance.py`): `compliance_map`, `compliance-mapping.md`.
- **Plan 7 — Remediation** (`core/remediation.py` -> `intel/remediation.py`): `remediation_advice`.
- **Plan 8 — PDF export** (`core/pdf_report.py` -> `report/pdf_exporter.py`): `[pdf]` extra, golden-file smoke test.
- **Plan 9 — Integration & release** (agent integration test, README, CI matrix 3.10–3.13, packaging smoke).

---

## Self-Review

**Spec coverage (foundation portion):** rename/scaffold (spec §4, §12.0) -> Tasks 1-3; attribution (spec §10) -> Task 4; tool plumbing + constraint classification (spec §5.1, §12.1) -> Tasks 5-7. Module ports (spec §12.2-9) -> deferred per-module plans, listed above. ✓

**Placeholder scan:** No "TBD/TODO/handle errors" left vague — the one intentional stub (`cve_lookup` returning `[intel_pending]`) is explicit, tested, and replaced in Plan 2. ✓

**Type consistency:** `intel_tool_schemas()`, `INTEL_TOOL_NAMES`, `dispatch_intel_tool(agent, tool_name, args)`, `READ_ONLY_INTEL_TOOLS` used identically across Tasks 5-7 and the agent seam. Builder/handler names flagged for verification against the real `builtin_tools.py` in Task 6 Step 1 (the only place the exact upstream name must be confirmed). ✓
