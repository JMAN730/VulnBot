# Reuse Prior Recon on Resume — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** When resuming a target that already has recon data, the agent builds on the stored recon and starts from Vulnerability Discovery instead of re-running reconnaissance — unless the user explicitly forces a fresh scan.

**Architecture:** Restore already rehydrates `recon_data` and phase via `apply_target_state_to_agent`. We make `auto_pentest` resume-aware so it no longer resets phase to Recon or wipes the recon-complete signal when prior recon exists, surface the concrete restored recon in the round prompt with a "do not re-scan" directive, and add three explicit force-fresh controls (prompt keyword, CLI flag, REPL command).

**Tech Stack:** Python 3.10–3.13, Pydantic models (`SessionState`), Typer CLI, pytest (`asyncio_mode=auto`), ruff (line-length 100, E501 ignored).

## Global Constraints

- Lint must pass: `ruff check vulnbot tests` (line-length 100, E501 ignored).
- Tests must pass: `pytest -q`. Test isolation via `conftest.py` redirects config/temp into `tests/.test-tmp/`; never depend on the real home dir or system `$TMPDIR`.
- Reuse is the **default** when prior recon exists; forcing fresh recon is always explicit (keyword, `--fresh-recon` flag, or `rescan` REPL command).
- `--fresh-recon` keeps restored findings/state but re-runs recon. It is distinct from `--no-resume`, which discards all prior state.
- All user-facing strings go through i18n: add keys to both `vulnbot/i18n/en.json` and `vulnbot/i18n/zh.json`.
- Follow existing patterns: tests build agents with `AgentCore(config)` where `config = VulnBotConfig()`.

---

## File Structure

- `vulnbot/agent/context.py` — add `SessionState.has_prior_recon()` and `SessionState.mark_recon_complete_from_data()`.
- `vulnbot/agent/input_analysis.py` — add `wants_fresh_recon(user_input) -> bool`.
- `vulnbot/agent/runtime_state.py` — add `reuse_recon: bool = False` field to `RuntimeState`.
- `vulnbot/agent/core.py` — add `preserve_recon` param to `_reset_runtime_state`; thread `fresh_recon` through `auto_pentest` / `persistent_pentest` wrappers.
- `vulnbot/agent/loop_controller.py` — resume-aware phase selection + `fresh_recon` param in `auto_pentest`/`persistent_pentest`.
- `vulnbot/agent/prompt_context.py` — render concrete recon assets + reuse directive in `build_round_context`.
- `vulnbot/cli/main.py` — `--fresh-recon` flag on `run`/`persistent` commands; REPL `rescan` command; visible reuse signal.
- `vulnbot/i18n/en.json`, `vulnbot/i18n/zh.json` — new i18n keys.
- `tests/test_agent.py` — tests for all of the above.

---

## Task 1: `SessionState.has_prior_recon()` + `mark_recon_complete_from_data()`

**Files:**
- Modify: `vulnbot/agent/context.py` (add two methods to `SessionState`, near `is_recon_complete` at line ~783)
- Test: `tests/test_agent.py`

**Interfaces:**
- Produces:
  - `SessionState.has_prior_recon() -> bool` — True when `recon_data` holds real assets OR phase is past Recon.
  - `SessionState.mark_recon_complete_from_data() -> None` — sets the three core recon dimensions (`server`, `website`, `domain`) to `True` so `is_recon_complete()` is satisfied on reuse.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_agent.py` (new class near `TestTargetState`):

```python
class TestPriorRecon:
    """Test reuse-of-prior-recon helpers on SessionState."""

    def test_has_prior_recon_false_on_empty(self):
        from vulnbot.agent.context import SessionState

        state = SessionState(target="https://example.com")
        assert state.has_prior_recon() is False

    def test_has_prior_recon_true_with_recon_assets(self):
        from vulnbot.agent.context import SessionState

        state = SessionState(target="https://example.com")
        state.recon_data["network_services"] = [{"port": 80, "service": "http"}]
        assert state.has_prior_recon() is True

    def test_has_prior_recon_true_when_phase_past_recon(self):
        from vulnbot.agent.context import PentestPhase, SessionState

        state = SessionState(target="https://example.com")
        state.phase = PentestPhase.EXPLOITATION
        assert state.has_prior_recon() is True

    def test_has_prior_recon_ignores_empty_lists(self):
        from vulnbot.agent.context import SessionState

        state = SessionState(target="https://example.com")
        state.recon_data["subdomains"] = []
        assert state.has_prior_recon() is False

    def test_mark_recon_complete_from_data(self):
        from vulnbot.agent.context import SessionState

        state = SessionState(target="https://example.com")
        assert state.is_recon_complete() is False
        state.mark_recon_complete_from_data()
        assert state.is_recon_complete() is True
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_agent.py::TestPriorRecon -v`
Expected: FAIL with `AttributeError: 'SessionState' object has no attribute 'has_prior_recon'`

- [ ] **Step 3: Implement the methods**

In `vulnbot/agent/context.py`, add inside `class SessionState`, immediately before `def is_recon_complete(self)` (currently line ~783):

```python
    def has_prior_recon(self) -> bool:
        """Whether this restored session already holds meaningful recon.

        True when recon_data contains real assets in any known category, or
        when the phase has already advanced past Recon. Used to decide whether
        a resumed run should reuse recon instead of re-scanning.
        """
        recon_categories = (
            "network_services",
            "network_scans",
            "subdomains",
            "paths",
            "params",
        )
        for category in recon_categories:
            value = self.recon_data.get(category)
            if isinstance(value, list) and value:
                return True
        return self.phase in (
            PentestPhase.VULN_DISCOVERY,
            PentestPhase.EXPLOITATION,
            PentestPhase.POST_EXPLOITATION,
            PentestPhase.REPORTING,
        )

    def mark_recon_complete_from_data(self) -> None:
        """Mark the core recon dimensions complete when reusing prior recon.

        Sets server/website/domain so is_recon_complete() is satisfied without
        forcing fresh recon rounds. Personnel (dimension 4) is left untouched
        because is_recon_complete() only checks it when recon_dimension4_active.
        """
        for dimension in ("server", "website", "domain"):
            if dimension in self.recon_dimensions_completed:
                self.recon_dimensions_completed[dimension] = True
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_agent.py::TestPriorRecon -v`
Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add vulnbot/agent/context.py tests/test_agent.py
git commit -m "feat(agent): add has_prior_recon and mark_recon_complete_from_data"
```

---

## Task 2: `wants_fresh_recon()` keyword detector

**Files:**
- Modify: `vulnbot/agent/input_analysis.py` (add a module-level function)
- Test: `tests/test_agent.py`

**Interfaces:**
- Produces: `wants_fresh_recon(user_input: str) -> bool` in `vulnbot.agent.input_analysis`.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_agent.py`:

```python
class TestWantsFreshRecon:
    """Test the force-fresh-recon keyword detector."""

    def test_detects_rescan_tokens(self):
        from vulnbot.agent.input_analysis import wants_fresh_recon

        for text in [
            "rescan example.com",
            "please re-scan the host",
            "do a fresh recon",
            "redo recon from scratch",
            "scan again, ignore old data",
            "start over on this target",
        ]:
            assert wants_fresh_recon(text) is True, text

    def test_ignores_ordinary_prompts(self):
        from vulnbot.agent.input_analysis import wants_fresh_recon

        assert wants_fresh_recon("exploit the SQL injection") is False
        assert wants_fresh_recon("continue the pentest") is False
        assert wants_fresh_recon("") is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_agent.py::TestWantsFreshRecon -v`
Expected: FAIL with `ImportError: cannot import name 'wants_fresh_recon'`

- [ ] **Step 3: Implement the function**

In `vulnbot/agent/input_analysis.py`, add after the `detect_phase` function:

```python
_FRESH_RECON_PATTERNS = (
    "rescan",
    "re-scan",
    "re scan",
    "scan again",
    "fresh recon",
    "redo recon",
    "re-recon",
    "redo reconnaissance",
    "fresh reconnaissance",
    "start over",
    "start fresh",
    "from scratch",
)


def wants_fresh_recon(user_input: str) -> bool:
    """Detect an explicit request to re-run reconnaissance from scratch."""
    if not user_input:
        return False
    lowered = user_input.lower()
    return any(pattern in lowered for pattern in _FRESH_RECON_PATTERNS)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_agent.py::TestWantsFreshRecon -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add vulnbot/agent/input_analysis.py tests/test_agent.py
git commit -m "feat(agent): add wants_fresh_recon keyword detector"
```

---

## Task 3: `RuntimeState.reuse_recon` + `_reset_runtime_state(preserve_recon=...)`

**Files:**
- Modify: `vulnbot/agent/runtime_state.py` (add field)
- Modify: `vulnbot/agent/core.py:127` (`_reset_runtime_state` signature + body)
- Test: `tests/test_agent.py`

**Interfaces:**
- Consumes: `SessionState.recon_dimensions_completed` (Task 1 leaves it populated).
- Produces:
  - `RuntimeState.reuse_recon: bool` (default `False`).
  - `AgentCore._reset_runtime_state(user_input="", detected_phase=None, preserve_recon=False)` — when `preserve_recon` is True, does NOT reset `recon_dimensions_completed` and forces `runtime.is_recon_phase = False`.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_agent.py`:

```python
class TestResetRuntimePreservesRecon:
    """Test preserve_recon path of _reset_runtime_state."""

    def test_preserve_recon_keeps_dimensions(self):
        from vulnbot.agent.context import PentestPhase
        from vulnbot.agent.core import AgentCore
        from vulnbot.config.schema import VulnBotConfig

        agent = AgentCore(VulnBotConfig())
        agent.context.state.recon_dimensions_completed = {
            "server": True,
            "website": True,
            "domain": True,
            "personnel": False,
        }
        agent._reset_runtime_state(
            user_input="continue", detected_phase=PentestPhase.VULN_DISCOVERY, preserve_recon=True
        )
        assert agent.context.state.recon_dimensions_completed["server"] is True
        assert agent.runtime.is_recon_phase is False

    def test_default_resets_dimensions(self):
        from vulnbot.agent.context import PentestPhase
        from vulnbot.agent.core import AgentCore
        from vulnbot.config.schema import VulnBotConfig

        agent = AgentCore(VulnBotConfig())
        agent.context.state.recon_dimensions_completed = {
            "server": True,
            "website": True,
            "domain": True,
            "personnel": True,
        }
        agent._reset_runtime_state(user_input="recon", detected_phase=PentestPhase.RECON)
        assert agent.context.state.recon_dimensions_completed["server"] is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_agent.py::TestResetRuntimePreservesRecon -v`
Expected: FAIL with `TypeError: _reset_runtime_state() got an unexpected keyword argument 'preserve_recon'`

- [ ] **Step 3a: Add the `reuse_recon` field to RuntimeState**

In `vulnbot/agent/runtime_state.py`, inside `class RuntimeState` near the `is_recon_phase` field (line ~50), add:

```python
    reuse_recon: bool = False
```

- [ ] **Step 3b: Update `_reset_runtime_state`**

In `vulnbot/agent/core.py`, change the signature (line 127):

```python
    def _reset_runtime_state(
        self,
        user_input: str = "",
        detected_phase: Optional[PentestPhase] = None,
        preserve_recon: bool = False,
    ) -> None:
```

Then, replace the unconditional recon-dimension reset block (currently lines ~167-172):

```python
        self.context.state.recon_dimensions_completed = {
            "server": False,
            "website": False,
            "domain": False,
            "personnel": False,
        }
```

with:

```python
        if preserve_recon:
            self.runtime.is_recon_phase = False
        else:
            self.context.state.recon_dimensions_completed = {
                "server": False,
                "website": False,
                "domain": False,
                "personnel": False,
            }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_agent.py::TestResetRuntimePreservesRecon -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add vulnbot/agent/runtime_state.py vulnbot/agent/core.py tests/test_agent.py
git commit -m "feat(agent): preserve recon completion in _reset_runtime_state"
```

---

## Task 4: Resume-aware `auto_pentest` (+ `fresh_recon` plumbing)

**Files:**
- Modify: `vulnbot/agent/loop_controller.py:18` (`auto_pentest` head) and `:187` (`persistent_pentest` head + cycle-1 call)
- Modify: `vulnbot/agent/core.py:350` (`auto_pentest` wrapper) and `:368` (`persistent_pentest` wrapper)
- Test: `tests/test_agent.py`

**Interfaces:**
- Consumes: `SessionState.has_prior_recon()`, `SessionState.mark_recon_complete_from_data()` (Task 1); `wants_fresh_recon()` (Task 2); `_reset_runtime_state(..., preserve_recon=...)` and `RuntimeState.reuse_recon` (Task 3).
- Produces:
  - `loop_controller.auto_pentest(agent, user_input, target=None, max_rounds=15, on_step=None, *, stream_sink=None, fresh_recon=False)`.
  - `loop_controller.persistent_pentest(..., *, stream_sink=None, fresh_recon=False)`.
  - `AgentCore.auto_pentest(...)` and `AgentCore.persistent_pentest(...)` accept keyword-only `fresh_recon: bool = False`.
  - After phase setup, `agent.runtime.reuse_recon` reflects whether recon was reused this run.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_agent.py`:

```python
class TestAutoPentestResumeAware:
    """Test that auto_pentest reuses recon instead of resetting to Recon."""

    def _make_agent(self, monkeypatch):
        from vulnbot.agent.core import AgentCore
        from vulnbot.config.schema import VulnBotConfig

        agent = AgentCore(VulnBotConfig())

        async def fake_call_llm_auto(_agent, _system, _ctx, stream_sink=None):
            return "Nothing further. [DONE]"

        import vulnbot.agent.loop_controller as lc

        monkeypatch.setattr(lc, "call_llm_auto", fake_call_llm_auto)
        return agent

    async def test_reuses_recon_starts_in_vuln_discovery(self, monkeypatch):
        from vulnbot.agent.context import PentestPhase

        agent = self._make_agent(monkeypatch)
        agent.context.state.target = "https://example.com"
        agent.context.state.recon_data["network_services"] = [{"port": 443, "service": "https"}]

        await agent.auto_pentest("continue the pentest", target="https://example.com", max_rounds=1)

        assert agent.runtime.reuse_recon is True
        assert agent.runtime.is_recon_phase is False
        assert agent.context.state.phase == PentestPhase.VULN_DISCOVERY

    async def test_fresh_recon_keyword_forces_recon(self, monkeypatch):
        from vulnbot.agent.context import PentestPhase

        agent = self._make_agent(monkeypatch)
        agent.context.state.target = "https://example.com"
        agent.context.state.recon_data["network_services"] = [{"port": 443, "service": "https"}]

        await agent.auto_pentest("rescan example.com", target="https://example.com", max_rounds=1)

        assert agent.runtime.reuse_recon is False
        assert agent.context.state.phase == PentestPhase.RECON

    async def test_fresh_recon_flag_forces_recon(self, monkeypatch):
        from vulnbot.agent.context import PentestPhase

        agent = self._make_agent(monkeypatch)
        agent.context.state.target = "https://example.com"
        agent.context.state.recon_data["network_services"] = [{"port": 443, "service": "https"}]

        await agent.auto_pentest(
            "continue", target="https://example.com", max_rounds=1, fresh_recon=True
        )

        assert agent.runtime.reuse_recon is False
        assert agent.context.state.phase == PentestPhase.RECON

    async def test_no_prior_recon_starts_in_recon(self, monkeypatch):
        from vulnbot.agent.context import PentestPhase

        agent = self._make_agent(monkeypatch)
        agent.context.state.target = "https://example.com"

        await agent.auto_pentest("pentest example.com", target="https://example.com", max_rounds=1)

        assert agent.runtime.reuse_recon is False
        assert agent.context.state.phase == PentestPhase.RECON
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_agent.py::TestAutoPentestResumeAware -v`
Expected: FAIL (e.g. `TypeError: auto_pentest() got an unexpected keyword argument 'fresh_recon'`, and phase assertions failing)

- [ ] **Step 3a: Update `loop_controller.auto_pentest`**

In `vulnbot/agent/loop_controller.py`, add the import at the top (with the other `from vulnbot.agent...` imports):

```python
from vulnbot.agent.input_analysis import wants_fresh_recon
```

Change the signature (line 18):

```python
async def auto_pentest(
    agent: Any,
    user_input: str,
    target: str | None = None,
    max_rounds: int = 15,
    on_step: Callable[[int, AgentResult], None] | None = None,
    *,
    stream_sink: Any = None,
    fresh_recon: bool = False,
) -> list[AgentResult]:
```

Replace the phase-setup block (currently lines 29-38):

```python
    detected_target = target or agent._detect_target(user_input)
    detected_phase = agent._detect_phase(user_input) or PentestPhase.RECON

    if detected_target:
        agent.context.state.target = detected_target
    if detected_phase:
        agent.context.state.advance_phase(detected_phase)

    agent.context.add_user_message(user_input)
    agent._reset_runtime_state(user_input=user_input, detected_phase=detected_phase)
```

with:

```python
    detected_target = target or agent._detect_target(user_input)
    if detected_target:
        agent.context.state.target = detected_target

    detected_phase = agent._detect_phase(user_input)
    force_fresh = fresh_recon or wants_fresh_recon(user_input)
    reuse_recon = (not force_fresh) and agent.context.state.has_prior_recon()

    if reuse_recon:
        saved_phase = agent.context.state.phase
        if detected_phase and detected_phase != PentestPhase.RECON:
            target_phase = detected_phase
        elif saved_phase not in (PentestPhase.IDLE, PentestPhase.RECON):
            target_phase = saved_phase
        else:
            target_phase = PentestPhase.VULN_DISCOVERY
        agent.context.state.mark_recon_complete_from_data()
    else:
        target_phase = detected_phase or PentestPhase.RECON

    agent.context.state.advance_phase(target_phase)

    agent.context.add_user_message(user_input)
    agent._reset_runtime_state(
        user_input=user_input, detected_phase=target_phase, preserve_recon=reuse_recon
    )
    agent.runtime.reuse_recon = reuse_recon
```

- [ ] **Step 3b: Thread `fresh_recon` through `persistent_pentest` (loop_controller)**

In `vulnbot/agent/loop_controller.py`, change the `persistent_pentest` signature (line 187) to add `fresh_recon: bool = False` after `stream_sink`:

```python
    *,
    stream_sink: Any = None,
    fresh_recon: bool = False,
) -> list[PersistentCycleResult]:
```

In its inner `agent.auto_pentest(...)` call (line ~235), pass `fresh_recon` only on cycle 1 by adding this argument:

```python
                fresh_recon=fresh_recon if cycle_num == 1 else False,
```

(Add it inside the existing `await agent.auto_pentest(...)` call alongside `stream_sink=stream_sink`.)

- [ ] **Step 3c: Thread `fresh_recon` through the core wrappers**

In `vulnbot/agent/core.py`, update `auto_pentest` (line 350):

```python
    async def auto_pentest(
        self,
        user_input: str,
        target: Optional[str] = None,
        max_rounds: int = 15,
        on_step: Optional[Callable[[int, AgentResult], None]] = None,
        *,
        stream_sink: Optional["StreamSink"] = None,
        fresh_recon: bool = False,
    ) -> list[AgentResult]:
        """Autonomous penetration test loop."""
        return await run_auto_pentest(
            self, user_input, target, max_rounds, on_step,
            stream_sink=stream_sink, fresh_recon=fresh_recon,
        )
```

And `persistent_pentest` (line 368) — add `fresh_recon: bool = False` after `stream_sink` in the signature and pass `fresh_recon=fresh_recon` into the `run_persistent_pentest(...)` call:

```python
        *,
        stream_sink: Optional["StreamSink"] = None,
        fresh_recon: bool = False,
    ) -> list["PersistentCycleResult"]:
        """Persistent penetration test - runs cycles of auto_pentest until stopped."""
        return await run_persistent_pentest(
            self,
            user_input,
            target,
            rounds_per_cycle,
            max_cycles,
            auto_report,
            on_cycle_step,
            on_cycle_complete,
            stream_sink=stream_sink,
            fresh_recon=fresh_recon,
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_agent.py::TestAutoPentestResumeAware -v`
Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add vulnbot/agent/loop_controller.py vulnbot/agent/core.py tests/test_agent.py
git commit -m "feat(agent): resume-aware auto_pentest reuses prior recon"
```

---

## Task 5: Inject concrete recon + reuse directive into the prompt

**Files:**
- Modify: `vulnbot/agent/prompt_context.py` (replace `recon_summary` at line 74; add a render helper)
- Test: `tests/test_agent.py`

**Interfaces:**
- Consumes: `agent.runtime.reuse_recon` (Task 4); `state.recon_data`.
- Produces: `build_round_context` output that, on reuse, includes a "do not re-scan" directive and concrete recon asset lines.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_agent.py`:

```python
class TestRoundContextRecon:
    """Test concrete recon rendering and reuse directive in round context."""

    def _agent_with_recon(self, reuse: bool):
        from vulnbot.agent.core import AgentCore
        from vulnbot.config.schema import VulnBotConfig

        agent = AgentCore(VulnBotConfig())
        agent._reset_runtime_state(user_input="continue")
        agent.runtime.reuse_recon = reuse
        agent.context.state.target = "https://example.com"
        agent.context.state.recon_data["network_services"] = [
            {"port": 443, "service": "https"},
            {"port": 22, "service": "ssh"},
        ]
        agent.context.state.recon_data["subdomains"] = ["api.example.com"]
        return agent

    def test_reuse_includes_directive_and_assets(self):
        from vulnbot.agent.prompt_context import build_round_context

        agent = self._agent_with_recon(reuse=True)
        ctx = build_round_context(agent, round_num=1, max_rounds=5)
        assert "already complete" in ctx.lower()
        assert "do not re-run" in ctx.lower()
        assert "443" in ctx
        assert "api.example.com" in ctx

    def test_no_reuse_omits_directive(self):
        from vulnbot.agent.prompt_context import build_round_context

        agent = self._agent_with_recon(reuse=False)
        ctx = build_round_context(agent, round_num=1, max_rounds=5)
        assert "do not re-run" not in ctx.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_agent.py::TestRoundContextRecon -v`
Expected: FAIL (directive/asset substrings not present)

- [ ] **Step 3a: Add the render helper**

In `vulnbot/agent/prompt_context.py`, add a module-level helper after the imports (top of file):

```python
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
```

- [ ] **Step 3b: Replace the keys-only recon summary**

In `vulnbot/agent/prompt_context.py`, replace line 74:

```python
    recon_summary = f"\nRecon data: {list(state.recon_data.keys())}" if state.recon_data else ""
```

with:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_agent.py::TestRoundContextRecon -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add vulnbot/agent/prompt_context.py tests/test_agent.py
git commit -m "feat(agent): surface concrete recon and reuse directive in round prompt"
```

---

## Task 6: CLI `--fresh-recon` flag, REPL `rescan` command, reuse signal + i18n

**Files:**
- Modify: `vulnbot/cli/main.py` (`run` command ~1104, `persistent` command ~1195, `_run_repl_auto_pentest` ~341, REPL command dispatch ~544, help text ~882)
- Modify: `vulnbot/i18n/en.json`, `vulnbot/i18n/zh.json`
- Test: `tests/test_cli.py` (or `tests/test_agent.py` for i18n key presence)

**Interfaces:**
- Consumes: `AgentCore.auto_pentest(..., fresh_recon=...)`, `AgentCore.persistent_pentest(..., fresh_recon=...)` (Task 4).
- Produces: a `rescan` REPL command and `--fresh-recon` CLI flags; new i18n keys `cli.fresh_recon_armed`, `cli.recon_reused`, `help.rescan`.

- [ ] **Step 1: Write the failing test (i18n keys present in both locales)**

Add to `tests/test_cli.py`:

```python
class TestFreshReconI18n:
    """Force-fresh-recon UI strings exist in both locales."""

    def test_keys_present(self):
        import json
        from pathlib import Path

        import vulnbot

        base = Path(vulnbot.__file__).parent / "i18n"
        en = json.loads((base / "en.json").read_text(encoding="utf-8"))
        zh = json.loads((base / "zh.json").read_text(encoding="utf-8"))
        for key in ("cli.fresh_recon_armed", "cli.recon_reused", "help.rescan"):
            assert key in en, f"missing {key} in en.json"
            assert key in zh, f"missing {key} in zh.json"
```

NOTE: the i18n JSONs use flat dotted keys (e.g. `"cli.target_restored"`). Confirm by opening `vulnbot/i18n/en.json` and matching the existing structure before adding keys.

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py::TestFreshReconI18n -v`
Expected: FAIL with `missing cli.fresh_recon_armed in en.json`

- [ ] **Step 3a: Add i18n keys**

In `vulnbot/i18n/en.json`, add (match the existing flat-key style and trailing-comma rules):

```json
  "cli.fresh_recon_armed": "[*] Fresh recon armed: the next auto run on {target} will re-scan from scratch.",
  "cli.recon_reused": "[*] Reusing prior recon for {target} ({assets} assets, {findings} findings) - skipping re-scan. Type 'rescan' to force fresh recon.",
  "help.rescan": "rescan [host]    - Force the next auto run to redo recon from scratch",
```

In `vulnbot/i18n/zh.json`, add the same keys with Chinese values, e.g.:

```json
  "cli.fresh_recon_armed": "[*] 已启用全新侦察：下一次对 {target} 的自动运行将从头重新扫描。",
  "cli.recon_reused": "[*] 复用 {target} 的历史侦察（{assets} 项资产，{findings} 个发现）- 跳过重新扫描。输入 'rescan' 可强制重新侦察。",
  "help.rescan": "rescan [host]    - 强制下一次自动运行从头重新侦察",
```

- [ ] **Step 3b: Add `fresh_recon` param to `_run_repl_auto_pentest`**

In `vulnbot/cli/main.py`, update `_run_repl_auto_pentest` (line 341) to accept `fresh_recon`:

```python
async def _run_repl_auto_pentest(
    agent,
    config,
    parallel_settings: ReplParallelSettings,
    *,
    user_input: str,
    target: Optional[str],
    on_step,
    stream_sink,
    fresh_recon: bool = False,
):
```

In its non-parallel branch (line ~357), pass `fresh_recon=fresh_recon` to `agent.auto_pentest(...)`:

```python
    if not budget.use_parallel:
        return await agent.auto_pentest(
            user_input,
            target=target,
            max_rounds=config.session.max_rounds,
            on_step=on_step,
            stream_sink=stream_sink,
            fresh_recon=fresh_recon,
        )
```

(The parallel branch below it is unchanged; parallel child agents inherit the parent's `recon_data` by deep copy, so `fresh_recon` applies to the standard loop only — leave a one-line comment noting this.)

- [ ] **Step 3c: Add the `rescan` REPL command and consume the flag**

In `vulnbot/cli/main.py`, near the top of the REPL loop where other locals like `last_auto_input` are initialized, add a one-shot flag:

```python
            pending_fresh_recon = False
```

Place this initialization with the other REPL state variables BEFORE the `while`/input loop (search for where `last_auto_input = ""` is first initialized and add it alongside).

Add a command branch alongside the existing `elif cmd_lower.startswith("target "):` block (line 544):

```python
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
```

In the auto-mode dispatch (the `if is_auto_mode:` block ~760), consume and reset the flag by capturing it before `_run_auto()` and passing it through. Where the closure calls `_run_repl_auto_pentest(...)` (line ~777), add `fresh_recon=pending_fresh_recon`:

```python
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
```

Immediately after the `asyncio.run(_run_auto())` call for auto mode (line ~824), reset the flag:

```python
                    pending_fresh_recon = False
```

- [ ] **Step 3d: Add `--fresh-recon` to the `run` command**

In `vulnbot/cli/main.py`, in the `run` command signature (after `snapshot`, line ~1136), add:

```python
    fresh_recon: bool = typer.Option(
        False, "--fresh-recon", help="Re-run recon from scratch (keeps prior findings)"
    ),
```

In the inner `runner` (line ~1160), pass `fresh_recon=fresh_recon` to `agent.auto_pentest(...)`:

```python
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
```

- [ ] **Step 3e: Add `--fresh-recon` to the `persistent` command**

In `vulnbot/cli/main.py`, add the same `--fresh-recon` option to the `persistent` command signature (after its `snapshot` option, line ~1231), and pass `fresh_recon=fresh_recon` to the `agent.persistent_pentest(...)` call inside that command (search within the `persistent` function body for `persistent_pentest(`).

- [ ] **Step 3f: Add `rescan` to REPL help**

In `_print_help` (line 882), add `{_("help.rescan")}` to the commands list, after `{_("help.report")}`.

- [ ] **Step 4: Run the i18n test + full suite**

Run: `pytest tests/test_cli.py::TestFreshReconI18n -v`
Expected: PASS

Run: `pytest -q`
Expected: PASS (no regressions beyond the 4 known pre-existing failures noted in project memory)

- [ ] **Step 5: Lint and commit**

```bash
ruff check vulnbot tests
git add vulnbot/cli/main.py vulnbot/i18n/en.json vulnbot/i18n/zh.json tests/test_cli.py
git commit -m "feat(cli): --fresh-recon flag, rescan REPL command, recon-reuse signal"
```

---

## Final Verification

- [ ] Run full suite: `pytest -q` (only the 4 documented pre-existing failures may remain).
- [ ] Run lint: `ruff check vulnbot tests` — clean.
- [ ] Manual smoke (optional): in the REPL, `target <host>` on a target with saved state should print the restore line; an auto prompt should print `cli.recon_reused` (wire this print in Task 6 Step 3c's auto block if a visible per-run signal is desired) and proceed in Vulnerability Discovery without re-scanning; `rescan` then an auto prompt should re-run recon.

> **Note on `cli.recon_reused`:** the key is added in Task 6 for the user-facing signal. Emit it from the REPL auto-mode block when `agent.runtime.reuse_recon` is True after the run (in the `after_result` callback, using `agent.session_state` asset/finding counts), and/or from the CLI `on_restored` path. Keep it to a single concise line.

## Self-Review Notes (spec coverage)

- Spec §1 (resume-aware auto_pentest) → Task 4.
- Spec §2 (preserve recon-completion) → Task 3.
- Spec §3 (inject concrete recon + directive) → Task 5.
- Spec §4 (keyword + flag + command) → Task 2 (keyword), Task 4 (plumbing + flag param), Task 6 (CLI flags + REPL command).
- Spec §5 (visible reuse signal + i18n) → Task 6.
- Spec testing section → tests embedded in Tasks 1–6.
- Out-of-scope (browse/listing) → not implemented, by design.
