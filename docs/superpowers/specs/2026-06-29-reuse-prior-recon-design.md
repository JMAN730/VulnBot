# Reuse Prior Recon on Resume (No Redundant Re-Scan)

**Date:** 2026-06-29
**Status:** Approved design, pending implementation plan

## Problem

When a user pentests target A, stops, moves to target B, then returns to target
A, the agent re-runs full reconnaissance from scratch even though prior recon
data was persisted and restored. This wastes time and LLM rounds repeating
scans whose results already exist.

The per-target persistence layer (`vulnbot/target_state/store.py`) already
saves and restores `recon_data`, `findings`, phase, and a resume plan. The
restore path (`apply_target_state_to_agent`) faithfully rehydrates this state.
The bug is that `auto_pentest` immediately clobbers the restored phase and the
"recon complete" signal, and the prompt never surfaces the concrete restored
recon, so the LLM re-scans.

## Root Cause (the four clobbers)

1. **`loop_controller.py:30`** — `auto_pentest` sets
   `detected_phase = agent._detect_phase(user_input) or PentestPhase.RECON`. A
   generic "continue pentest" prompt detects no phase, defaults to `RECON`, and
   `advance_phase(RECON)` resets a restored Exploitation/Vuln-Discovery phase
   back to Recon.
2. **`core.py:167` (`_reset_runtime_state`)** — unconditionally resets
   `recon_dimensions_completed` to all-`False`, erasing the restored
   "recon done" signal so `is_recon_complete()` returns `False`.
3. **`loop_controller.py:100` (`RECON_MIN_ROUNDS = 8`)** — combined with
   `is_recon_complete()` being `False`, this forces at least 8 fresh recon
   rounds.
4. **`prompt_context.py:74`** — injects only recon *key names*
   (`Recon data: ['subdomains','paths']`), never the concrete ports / services
   / hosts, and never tells the model recon is already complete. The LLM has
   nothing concrete to build on and re-runs nmap / enumeration.

## Goal

When resuming a target that already has meaningful recon, the agent builds on
the stored recon and starts from Vulnerability Discovery — it does **not**
re-run port scans or re-enumerate — unless the user explicitly requests a fresh
scan. Reuse is the default; forcing a fresh re-scan is explicit.

## Design

### 1. Resume-aware `auto_pentest` (`vulnbot/agent/loop_controller.py`)

- Add `SessionState.has_prior_recon()` (in `context.py`): returns `True` when
  restored `recon_data` contains real assets (non-empty `network_services` /
  `network_scans` / `subdomains` / `paths` / `params`) **or** the restored
  `phase` is past `RECON`.
- Before the `or PentestPhase.RECON` default, branch:
  - If `has_prior_recon()` is true **and** `wants_fresh_recon(user_input)` is
    false: do **not** reset phase to `RECON`. Use the restored phase; if the
    restored phase is `RECON` (but recon is complete), start at
    `PentestPhase.VULN_DISCOVERY`. Honor `resume_meta.recommended_phase` when
    present and further along.
  - Otherwise: current behavior (default to / honor detected `RECON`).
- Pass a `reuse_recon: bool` into `_reset_runtime_state` so it preserves the
  recon-complete signal on the reuse path.

**Decision (confirmed):** on reuse, default the starting phase to Vulnerability
Discovery when the saved phase was Recon-but-complete; otherwise honor the exact
saved phase (so a target saved mid-Exploitation resumes in Exploitation).

### 2. Preserve recon-completion on reuse (`vulnbot/agent/core.py`)

- Add `preserve_recon: bool = False` to `_reset_runtime_state`.
- When `preserve_recon` is true: do **not** reset `recon_dimensions_completed`
  to all-`False`; keep the restored mapping. Also set
  `runtime.is_recon_phase = False` so the `RECON_MIN_ROUNDS` gate
  (`loop_controller.py:100`) does not force 8 recon rounds.
- For robustness with older snapshots that lack populated
  `recon_dimensions_completed`, `has_prior_recon()`-driven reuse marks the
  relevant dimensions complete (derive from which `recon_data` categories are
  populated) so `is_recon_complete()` is satisfied.

### 3. Inject concrete recon into the prompt (`vulnbot/agent/prompt_context.py`)

- Replace the keys-only `Recon data: [...]` line (line 74) with a compact
  rendering of the concrete high-value restored assets: open ports / services,
  subdomains, and paths/params, each capped (e.g. top 8–10). Reuse the ranking
  approach already in `store.py` (`_top_recon_assets_for_summary`) or render
  directly from `recon_data`.
- When reusing recon, prepend an explicit directive to the round context:
  > "Recon for this target is already complete (results below). Do NOT re-run
  > port scans or re-enumerate hosts/directories unless a concrete gap is
  > identified — start from Vulnerability Discovery and build on this data."
  Continue to include the existing `resume_summary`.

### 4. Force-fresh controls — keyword + flag + command

- **Keyword** (`vulnbot/agent/input_analysis.py`): add
  `wants_fresh_recon(user_input) -> bool` matching tokens such as `rescan`,
  `re-scan`, `fresh recon`, `redo recon`, `scan again`, `start over`. When true,
  `auto_pentest` forces `RECON` phase and wipes recon completion (the original
  behavior).
- **CLI flag** (`vulnbot/cli/main.py`): add `--fresh-recon` (default off) to the
  `pentest` and `persistent` commands. It keeps restored findings/state
  (`--resume` semantics) but forces recon to re-run. This is distinct from the
  existing `--no-resume`, which discards all prior state including findings.
  The flag threads through to `auto_pentest` (e.g. by injecting a rescan signal
  or an explicit parameter).
- **REPL command** (`vulnbot/cli/main.py`): add a `rescan [host]` command that
  sets a one-shot "force fresh recon" flag consumed by the next auto-mode run
  (mirrors how `target`/`persistent` commands are dispatched in the REPL loop).

### 5. Visible reuse signal (UX + i18n)

- When reuse kicks in, print a line such as:
  > "Reusing prior recon for `<target>` (N assets, M findings) — skipping
  > re-scan. Type `rescan` to force fresh recon."
- Add new keys to `vulnbot/i18n/en.json` and `vulnbot/i18n/zh.json` (follow the
  existing `cli.target_restored` pattern).

## Testing

Follow the existing `tests/test_agent.py` style (asyncio_mode=auto, test
isolation via `conftest.py`).

- `SessionState.has_prior_recon()`: true when `recon_data` has real assets or
  phase past Recon; false on an empty session.
- `wants_fresh_recon()`: matches the rescan tokens; ignores ordinary prompts.
- `_reset_runtime_state(preserve_recon=True)`: leaves
  `recon_dimensions_completed` untouched and sets `is_recon_phase=False`;
  `preserve_recon=False` retains the existing reset behavior.
- `prompt_context`: on reuse, the round context contains concrete recon assets
  and the "do not re-scan" directive; without reuse, it does not.
- `auto_pentest`: with a restored state containing `recon_data`, starts in
  Vulnerability Discovery (not Recon) and does not force recon rounds; with a
  `rescan` keyword in the prompt, starts in Recon.

## Out of Scope

- A "browse previous reports / targets" listing surface. The user explicitly
  chose auto-reuse over a discovery/listing UI. Existing helpers
  (`list_target_snapshots`, `get_target_state_preview`) remain unused by this
  change.
- No change to the persistence schema beyond what already serializes
  `recon_dimensions_completed` (already a `SessionState` field).
