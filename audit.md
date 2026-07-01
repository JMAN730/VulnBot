# VulnBot Codebase Audit

**Date:** 2026-06-29
**Scope:** All 80 Python modules under `vulnbot/` (~27,800 LoC). Static analysis
(AST cross-reference + `vulture`) followed by manual verification of every flagged
item against the whole repo *including* `tests/`.
**Note:** This is an audit only — **no code was changed.**

## Methodology

1. Inventoried every `def`/`async def` and built a project-wide reference map
   (Name / Attribute / string-literal references) to find functions never called.
2. Filtered out **dynamic-dispatch false positives** — these are *not* dead even
   though a naive scan flags them:
   - FastAPI route handlers (`@app.get/post`) in `web/app.py`
   - Typer commands (`@app.command`) in `cli/main.py`
   - Pydantic hooks/validators (`model_post_init`, `field_validator`, `model_config`)
   - Pydantic model **fields** (vulture reports these as "unused variables" — ignored)
   - Textual callbacks (`compose`, `on_mount`, `on_key`, `on_input_*`, `action_*`)
   - `@_register(...)` crypto ops and `@_rule(...)` remediation handlers (registered
     into dispatch dicts, called via `crypto_decode` / `RemediationEngine`)
   - prompt_toolkit key-binding (`kb.add`) callbacks
3. For each remaining candidate, grepped `vulnbot` + `tests` to confirm it has
   zero call sites (or test-only call sites) before listing it.

Confidence is noted per finding: **High** = verified zero production call sites;
**Med** = reachable only from other dead code; **Low** = stylistic / cosmetic.

---

## 1. Data corruption - garbled tool descriptions (resolved)

**File:** `vulnbot/skills/crypto_tools.py`

The original audit found user-facing placeholder text in several crypto operation
descriptions and optional parameter labels. This was resolved in the public-alpha
hardening pass by replacing the placeholders with explicit English descriptions
for ROT13, Caesar, JWT, AES, and auto-detect decode operations.

Regression coverage now checks operation descriptions and optional parameter help
for the stale placeholder tokens.

---

## 2. Byte-order mark in source file (resolved)

**File:** `vulnbot/config/schema.py:1`

The original audit found a UTF-8 BOM (`U+FEFF`) at the start of the schema module.
The file has been re-saved as plain UTF-8 during the public-alpha hardening pass.

---

## 3. Dead production modules (MED severity)

### 3a. `vulnbot/mcp/router.py` — entire module unused in production
`MCPRouter` is **never imported anywhere in `vulnbot/`** (not even in
`mcp/__init__.py`). Its only references are in `tests/test_mcp.py`. All its
methods are therefore dead production code:
- `route` (:45), `extract_url` (:64), `extract_ip` (:69), `suggest_tools_for_phase` (:74)

This contradicts `CLAUDE.md`, which lists `router.py (NL → tool suggestion)` as a
live part of the MCP toolchain — the doc is stale, or the wiring was dropped.
**Recommendation:** Either wire the router into the agent's tool-suggestion flow or
remove the module + tests and update `CLAUDE.md`.

### 3b. `vulnbot/report/verifier.py` — `VulnerabilityVerifier` never instantiated
`VulnerabilityVerifier` is only re-exported in `report/__init__.py` `__all__` and
exercised by tests; it is never constructed in production code. The following are
all fully-implemented-but-unused:
- `verify_batch` (:304), `get_verified_report_findings` (:347), `get_summary` (:362)

**Recommendation:** Confirm whether report verification is meant to be in the
pipeline. If yes, wire it in; if no, drop the class and its tests.

---

## 4. The prompt_toolkit TUI is dead code (MED severity)

**File:** `vulnbot/cli/tui.py`

`run_tui()` (:340) now delegates entirely to the Textual implementation:
```python
def run_tui(...):
    from vulnbot.cli.tui_textual import run_tui_textual
    run_tui_textual(...)
```
The older prompt_toolkit implementation `_run_pt_tui()` (:351–553) has **zero
callers** (High confidence). Anchored to it is a self-contained island of code that
is reachable only from `_run_pt_tui` (verified each has only 1 call site, inside the
dead path):

- `_build_slash_completer` (:668) incl. the no-op `_SlashCompleter.get_completions` (:672)
- `_dispatch_slash` (:706), `_load_default_bindings` (:554)
- the prompt-state machine: `_set_prompt_input/_choice/_confirm/_message/_chain`
  (:567–583), `_cancel_prompt` (:587), `_handle_prompt_response` (:595)
- the slash-command handlers registered via `@_register_handler`: `_cmd_quit`,
  `_cmd_target`, `_cmd_mode`, `_cmd_scope`, `_cmd_start`, `_cmd_history`,
  `_cmd_report`, `_cmd_diagnostic`, `_cmd_config`, `_cmd_language` (:730–962),
  plus `_do_launch` (:836) and `_apply_language_pt` (:963)

Note `tui.py` is **not** entirely dead — `render_tui_home`, `build_dashboard`,
`build_state_from_options`, `build_command_preview_args`,
`build_runtime_diagnostic_panel`, `run_config_tui`, the config-editing prompts, etc.
are still used by `cli/main.py`, `tui_textual.py`, and tests.

**Recommendation:** Delete the `_run_pt_tui` island (~250 LoC) now that Textual is
the only TUI, or document why it's retained.

---

## 5. Dead AgentCore delegation shims (MED severity)

**File:** `vulnbot/agent/core.py`

`AgentCore` was refactored into thin method wrappers that delegate to extracted
module functions. Most wrappers are still called, but these six are never invoked as
`self._...` anywhere — callers use the underlying module function directly instead:

| Wrapper (dead) | Underlying fn | Where the real fn is actually called |
|---|---|---|
| `_execute_nmap` (:482) | `execute_nmap` | `builtin_tools.py:128` |
| `_is_reserved_ip` (:489) | `is_reserved_ip` | `builtin_tools.py:537,693,724` |
| `_parse_nmap_xml` (:495) | `parse_nmap_xml` | `builtin_tools.py:659`, `topology.py:373` |
| `_execute_python` (:498) | `execute_python` | `builtin_tools.py:112` |
| `_detect_flag_claim` (:423) | `detect_flag_claim` | `ctf_mode.py:55` |
| `_validate_scan_target` (:492) | `validate_scan_target` | **see 5a** |

### 5a. Deeper dead chain — `validate_scan_target`
`builtin_tools.validate_scan_target` (:687) is itself referenced **only** by the
dead `core._validate_scan_target` wrapper (and the import at `core.py:23`). So both
the wrapper *and* the underlying function are unused — an entire validation helper
with no live call path. Worth confirming target validation isn't silently missing
somewhere it was intended.

**Recommendation:** Remove the dead wrappers; investigate 5a (possible missing
validation, not just dead code).

---

## 6. No-op functions (LOW–MED severity)

- **`vulnbot/agent/context.py:871` `ContextManager.add_system_message`** — body is
  just `pass` (with comment "System messages are handled separately"). Never called
  (0 references). A genuine no-op stub. **Recommendation:** remove, or implement if
  the sibling `add_user_message`/`add_assistant_message` imply it should work.
- **`vulnbot/cli/tui.py:672` `_SlashCompleter.get_completions`** — `pass` ("async
  path is used instead"). This is a *required* abstract override from prompt_toolkit's
  `Completer`, so the no-op is intentional — but it's inside the dead island (§4),
  so it dies with that. Low priority on its own.
- **`vulnbot/intel/attack.py:777` `AttackMapper.__init__`** — `pass`. Redundant
  empty constructor; harmless, can be deleted (the class is instantiated and used).
- Legitimate no-ops (not findings, listed for completeness): `StreamSink` Protocol
  stubs (`...`) and `_NullSink` null-object methods in `agent/llm_client.py` —
  these are correct design patterns.

---

## 7. Implemented-but-unused functions (LOW severity)

Each below is a complete, working implementation with **zero call sites in
production code**. Several are still covered by unit tests (noted), which masks the
fact that nothing ships them.

| Function | Location | Status |
|---|---|---|
| `LLMConfig.primary_key` | `config/schema.py:138` | test-only (`test_config.py`) |
| `fetch_provider_models_async` | `config/settings.py:343` | no callers at all |
| `KnowledgeRetriever.get_cve` | `kb/retriever.py:266` | test-only |
| `KnowledgeRetriever.get_tool_guide` | `kb/retriever.py:315` | test-only |
| `KnowledgeRetriever.get_payload` | `kb/retriever.py:319` | test-only |
| `KnowledgeStore.list_categories` | `kb/store.py:182` | test-only |
| `KnowledgeStore.list_entries` | `kb/store.py:186` | test-only |
| `get_framework_controls` | `intel/compliance.py:298` | no callers at all |
| `list_frameworks` | `intel/compliance.py:304` | test-only |
| `annotate_compliance` | `intel/findings.py:96` | test-only |
| `MCPRegistry.get_server_stats` | `mcp/registry.py:165` | test-only |
| `MCPRegistry.unregister_server` | `mcp/registry.py:222` | no callers at all |
| `MCPLifecycleManager._call_stdio_server` | `mcp/lifecycle.py:432` | superseded by `_get_or_create_persistent_stdio_session`; dead |
| `MCPLifecycleManager.health_check` | `mcp/lifecycle.py:574` | test-only |
| `CryptoToolExecutor list_operations` | `skills/crypto_tools.py:672` | test-only |
| `SkillDispatcher.list_all_skills` | `skills/dispatcher.py:143` | no callers at all |
| `list_custom_skills` | `skills/loader.py:110` | no callers at all |
| `extract_findings_section` | `report/filter.py:188` | no callers at all |
| `remove_unverified_findings` | `report/filter.py:202` | no callers at all |
| `ReportContentFilter.is_pure_markdown` | `report/filter.py:161` | no callers at all |
| `_render_verified_finding_details` | `report/generator.py:858` | no callers at all |
| `MemoryStore.list_keys` | `agent/memory.py:57` | test-only |
| `VulnerabilityFinding.mark_manual_review` | `agent/context.py:112` | no callers at all |
| `VulnerabilityFinding.mark_rejected` | `agent/context.py:159` | no callers at all |
| `StepRecord.to_summary` | `agent/context.py:191` | no callers at all |
| `SessionState.add_recon_subdomain` | `agent/context.py:412` | no callers at all |
| `SessionState.add_assumption` | `agent/context.py:769` | no callers at all |
| `build_user_vuln_directive` | `agent/input_analysis.py:276` | explicit "backward-compatible alias", 0 callers |

`AttackMapper.list_tactics/list_techniques/get_technique/get_tool_techniques`
(`intel/attack.py:901–935`) and several `RemediationEngine`/`compliance` query
helpers are similarly test-only or unused — same category.

**Recommendation:** Decide per group whether these are intended public API (keep +
document) or accumulated dead code (remove with their tests). The "backward-compatible
alias" and the `_call_stdio_server` superseded-implementation are the clearest
removals.

---

## 8. Minor / cosmetic (LOW severity)

- **Unused loop/handler parameters** (framework-mandated signatures, safe to ignore
  but flagged by linters): `complete_event` in `cli/tui.py:672`, `exc_type` in
  `mcp/lifecycle.py:56`.
- **`StreamSink` import** at `agent/core.py:36` is only used in *string* annotations
  (`Optional["StreamSink"]`), so `vulture` reports it unused — it's actually needed
  for the forward reference to resolve under type checking. **Not** a real issue;
  noted to pre-empt a wrong "remove unused import" cleanup.
- **Empty `AttackMapper.__init__`** — see §6.

---

## Summary

| Category | Count | Severity |
|---|---|---|
| Garbled tool-description strings (`crypto_tools.py`) | 22 | **High** |
| BOM in `schema.py` | 1 | Low |
| Dead production modules (`mcp/router.py`, `report/verifier.py`) | 2 | Med |
| Dead prompt_toolkit TUI island (`tui.py`) | ~14 fns / ~250 LoC | Med |
| Dead AgentCore delegation shims (+ `validate_scan_target` chain) | 6 (+1) | Med |
| No-op functions | 3 | Low–Med |
| Implemented-but-unused / test-only functions | ~30 | Low |

No functions were found to be *silently broken* (returning wrong results); the
issues are (a) one block of corrupted metadata strings, and (b) a substantial
amount of dead/orphaned code from the refactors (AgentCore extraction, TUI
migration to Textual, MCP router/verifier never being wired in). The single
behavioral item worth a closer look is **§5a** — `validate_scan_target` has no live
call path, which may mean scan-target validation isn't actually running where it was
intended to.

---
---

# Part 2 — Security Audit (deep dive, category B)

**Date:** 2026-06-29 · **Scope:** Security only.
**Tools:** `bandit -r vulnbot -ll -ii` (8 High / 4 Med / 63 Low candidates), plus
manual review of `agent/builtin_tools.py`, `agent/network_scan.py`, `mcp/lifecycle.py`,
`web/app.py`, `web/services/*`, `config/schema.py`. **No code changed.**

Threat model that matters here: VulnBot is an **autonomous LLM agent** that ingests
**attacker-controlled content** (target web pages, banners, HTTP responses) and then
**calls tools / runs code on the operator's host**. So "prompt injection from the
target → agent runs tool" is a realistic, in-scope attack path, not a theoretical one.

## SEC-1 — `python_execute` is arbitrary code execution, on by default (CRITICAL, High confidence)

**File:** `vulnbot/agent/builtin_tools.py:794–978`, defaults in `config/schema.py:172–210`

The `python_execute` tool writes the model-supplied `code` to a temp file and runs it
with `asyncio.create_subprocess_exec(sys.executable, tmp_path, ...)` — i.e. a **real,
unconfined Python subprocess** with full filesystem/network access. The only
"sandbox" is a denylist of **6 regexes over the source string** (`BLOCKED_PATTERNS`,
:37–44). This is bypassable many ways the denylist doesn't cover:

```python
BLOCKED_PATTERNS = [ r"os\.\s*system\s*\(", r"subprocess\.\s*Popen\s*\(",
                     r"shutil\.\s*rmtree\s*\(", r"__import__\s*\(\s*['\"]os['\"]",
                     r"open\s*\(\s*['\"].*vulnbot.*config", r"open\s*\(\s*['\"].*\.vulnbot" ]
```
- `subprocess.run(...)` / `subprocess.call(...)` are **not** blocked (only `Popen`).
- `eval(...)`, `exec(...)`, `compile(...)`, `getattr(os,'sys'+'tem')(...)`,
  `__import__('o'+'s')` — none are blocked.
- The config-file read guard is a literal-string regex; `pathlib.Path('~/.vulnbot/
  config.yaml').read_text()` or `io.open`/`codecs.open` sail past it.

**Default configuration is the most dangerous one (verified in `SafetyConfig`):**
```python
enable_python_execute: bool = Field(default=True, ...)          # ON by default
python_execute_mode:  str  = Field(default="trusted-local", ...) # unrestricted mode
python_execute_restricted: bool = Field(default=False, ...)
```
In `trusted-local` mode `_validate_python_execute_mode` applies **no** extra patterns
(`patterns = [] `, :776), and the child inherits the **full `os.environ`**:
```python
env = {**os.environ, **base_env} if mode == "trusted-local" else base_env   # :909
```
So out of the box, any code the LLM emits runs locally **with the operator's
environment, including the LLM API key** (`os.environ` / `VULNBOT_API_KEY`), which the
injected code can read and exfiltrate. The `safe`/`lab` modes (also regex denylists)
are not the default and are themselves bypassable (regex on source text).

**Impact:** prompt-injected target content → `python_execute` → RCE on the operator
host + credential theft. **Recommendations (in priority order):** default
`enable_python_execute=False`; if kept, default to `safe`; do not pass `os.environ`
to the child (scrub secrets); enforce limits via OS sandboxing (seccomp/nsjail/
container/separate low-priv user) rather than source regexes — a denylist on source
text cannot be made safe. At minimum, document that enabling it grants the agent RCE.

## SEC-2 — Web `provider-models` endpoint: SSRF + API-key exfiltration (HIGH, High confidence)

**Files:** `vulnbot/web/services/provider_service.py:34–74`, `web/app.py:115`,
`config/settings.py:fetch_provider_models`

`POST /api/provider-models` takes `base_url` **straight from the client** and calls
`fetch_provider_models(base_url, api_key)`, which constructs
`OpenAI(api_key=<saved key>, base_url=<client base_url>).models.list()` — the server
makes an **authenticated outbound request to an attacker-chosen URL, carrying the
operator's real LLM API key** in the `Authorization` header.
```python
explicit = (request.base_url or "").strip()
if explicit: return explicit          # no allow-list / no validation  (:36-38)
...
models = fetch_provider_models(base_url, api_key)   # key sent to that base_url (:67)
```
The module docstring claims *"the key is never sent to the browser"* — true, but it is
sent to **any server the requester names**. This is both an SSRF primitive (probe
internal services) and a credential-exfiltration channel. Reachability is gated by the
web bind (see SEC-3); with `--allow-remote` it is directly exploitable by anyone on the
network, and even on localhost it is reachable via DNS-rebinding or any local process.
**Recommendation:** validate `base_url` against the known provider preset allow-list
(or the saved base host); never send the saved key to an arbitrary host; require TLS
verification on this path (see SEC-5).

## SEC-3 — Web backend has no auth, no CORS, no Host pinning (MEDIUM, High confidence)

**File:** `vulnbot/web/app.py:82–246` (no `add_middleware`, no `Depends`, no
`CORSMiddleware`/`TrustedHostMiddleware` anywhere)

The default bind is sensible (`127.0.0.1`, refuses non-local without `--allow-remote`,
`cli/main.py:2489`), **but there is no authentication layer at all** and no
`TrustedHostMiddleware`. The API exposes state-changing operations:
`POST /api/tasks/run` (launches an autonomous pentest run — i.e. drives the agent and,
via SEC-1, code execution), `POST /api/config` (writes `base_url`/`api_key`/output dir),
`POST /api/tasks/{id}/stop`, `DELETE /api/targets/{t}`, `POST /api/targets/{t}/rollback`.

- **`--allow-remote`** binds all of the above to the network with **zero
  authentication** — anyone who can reach the port can launch runs, rewrite the API
  key, and read reports.
- **Localhost + no `TrustedHostMiddleware`** ⇒ vulnerable to **DNS-rebinding**: a web
  page the operator visits can rebind a hostname to `127.0.0.1` and reach these
  endpoints (combine with SEC-2 to exfiltrate the key). Lack of CORS blocks *reading*
  cross-origin JSON responses but does not stop the side effects of the POSTs.

**Recommendation:** add `TrustedHostMiddleware` (pin `Host` to localhost), require a
token/loopback-auth for mutating endpoints, and refuse to start with `--allow-remote`
unless an auth token is configured.

## SEC-4 — MCP `fetch` tool has no SSRF guard (MEDIUM, Med confidence)

**File:** `vulnbot/mcp/lifecycle.py:987–1008`

`_call_fetch` issues `client.request(method, url, headers, content=body)` for an
agent-supplied `url` with **no reserved-IP / cloud-metadata filtering** — unlike the
nmap path, which checks `is_reserved_ip` (`builtin_tools.py:537`). Central
`validate_tool_action` scope checks only help if the operator has configured scope
constraints; with no scope set (the common case), a prompt-injected agent can fetch
`http://169.254.169.254/…` (cloud metadata) or internal services from the operator's
network. `verify=False` (:997) also disables TLS verification on these fetches.
**Recommendation:** apply the same reserved-IP/metadata denylist used for nmap to
`_call_fetch`, and require scope confirmation before fetching private ranges.

## SEC-5 — TLS verification disabled on outbound HTTP (LOW–MED, High confidence)

`verify=False` appears in `agent/builtin_tools.py:1074` (brute-force login),
`mcp/lifecycle.py:997` (fetch), `intel/osint.py:498`, and the generated PoC templates
in `report/verifier.py`. For **pentest targets** this is expected (self-signed certs).
The concern is the paths that are **not** targets: anything carrying the API key or
hitting providers/metadata (SEC-2) should verify TLS. **Recommendation:** keep
`verify=False` only on the explicit target-interaction tools; verify TLS on
provider/credentialed calls.

## SEC-6 — XML parsed with stdlib `ElementTree` (XXE/entity-expansion) (LOW–MED, Med confidence)

`xml.etree.ElementTree.fromstring` is used on external XML in
`agent/builtin_tools.py:712`, `agent/network_scan.py:273`, and **`intel/topology.py:292`**.
nmap-generated XML (the first two) is low risk since VulnBot generates it, but
`topology.py` can parse externally-supplied XML files — stdlib ET is vulnerable to
entity-expansion ("billion laughs") and, on older runtimes, external-entity attacks.
**Recommendation:** parse with `defusedxml` (a soft dependency already fits the
project's optional-import pattern), or call `defusedxml.defuse_stdlib()`.

## SEC-7 — nmap argument-injection (LOW, Med confidence)

**File:** `vulnbot/agent/builtin_tools.py:618–620`

`target` and `custom_ports` flow into the argv list unvalidated
(`cmd.extend(["-p", custom_ports]); cmd.append(target)`). Because they are passed as
**list arguments**, there is **no shell injection**. The residual risk is *nmap-flag*
injection if a value begins with `-` (e.g. a target like `-oN/path`), letting the agent
smuggle nmap options. Low impact (the agent already controls the scan), but worth a
`--`-terminator or a leading-dash reject. The `socket.getaddrinfo` reserved-IP check
silently passes on resolution failure (`except Exception: pass`, :544), so a
flag-shaped target also skips that guard.

## Not security defects (verified — do not "fix")

- **`crypto_tools.py` MD5/SHA1/pyCryptodome AES** (bandit B324/B413): these are
  deliberate offensive/utility crypto operations exposed via `crypto_decode`, not
  security controls. Add `usedforsecurity=False` only to silence linters if desired.
- **`builtin_tools.py:53` "0.0.0.0" (bandit B104)**: false positive — it's an entry in
  the *reserved-IP denylist table*, not a socket bind.
- **`config_view` (`GET /api/config`)**: confirmed it returns `api_key_configured: bool`,
  never the key itself — no leak via that endpoint.

## Security summary

| ID | Issue | Severity | Confidence |
|---|---|---|---|
| SEC-1 | `python_execute` = unconfined RCE, enabled + `trusted-local` by default; regex "sandbox" bypassable; full env (API key) to child | **Critical** | High |
| SEC-2 | `/api/provider-models` SSRF + sends saved API key to client-supplied `base_url` | **High** | High |
| SEC-3 | Web API: no auth / no CORS / no Host pinning; `--allow-remote` = unauthenticated task-launch + config write | **Medium** | High |
| SEC-4 | MCP `fetch` tool: no reserved-IP/metadata SSRF guard | Medium | Med |
| SEC-5 | `verify=False` on credentialed/provider HTTP paths | Low–Med | High |
| SEC-6 | stdlib `ElementTree` XXE/entity-expansion (notably `topology.py`) | Low–Med | Med |
| SEC-7 | nmap flag-injection via leading-dash `target`/`ports` | Low | Med |

**Top priority:** SEC-1 and SEC-2. SEC-1 turns any successful prompt injection into
host RCE + key theft and ships **on by default**; SEC-2 leaks the API key to an
attacker-named URL. Both are fixable without large refactors (flip defaults / scrub
child env for SEC-1; allow-list `base_url` for SEC-2).
