# ClawBot — Unified AI Pentest Product (v1) — Design Spec

**Date:** 2026-06-22
**Status:** Approved (design); pending implementation plan
**Working name:** ClawBot (placeholder — swap before release)

## 1. Summary

ClawBot merges two existing MIT-licensed AI pentest CLIs into one shippable
product:

- **VulnClaw** (base) — supplies the agent core, MCP toolchain, markdown skill
  orchestration, target-state store, config, and CLI/TUI/web surfaces.
- **HackBot** (capability donor) — supplies deep intelligence modules
  (CVE/NVD, OSINT, topology, compliance/MITRE, findings risk-scoring/diff,
  remediation, PDF reporting).

The merge keeps **VulnClaw's architecture intact** and ports a curated subset of
HackBot's modules into a new `intel/` subpackage, rewritten to VulnClaw
conventions and exposed to the agent as **native builtin tools** plus
**methodology skills**.

## 2. Locked decisions

| Decision | Choice | Rationale |
|---|---|---|
| Goal | Ship a real, maintained product | Drives clean deps, attribution, naming |
| Combine level | Level 2 — single unified package | Not a loose adapter shim; one installable tool |
| Base | VulnClaw | Cleaner agent kernel; grafting capabilities onto it is cheaper than the reverse |
| Migration | C — selective extraction & rewrite | One coherent codebase; no inherited HackBot dep tree |
| Agent integration | Native `builtin_tools` + markdown skills | Fastest path, no IPC; matches VulnClaw's tool model |
| Branding | New combined name | Clean break, both upstreams credited |
| Findings store | VulnClaw `target_state` is canonical | One store, not two; HackBot scoring/diff ported as enrichment |

## 3. v1 scope

**In:** Intel modules (CVE/NVD lookup + exploit-PoC discovery, OSINT, network
topology) · Findings & compliance (risk scoring + dedup, PCI/NIST/OWASP/ISO +
MITRE ATT&CK mapping, diff reports) · Reporting depth (PDF export + remediation
advisor).

**Out (future specs):** desktop GUI (pywebview), Telegram bot, zero-day engines
(`zeroday.py`/`zeroday_active.py`), proxy, active scanning engine, multi-target
campaigns, plugin system.

## 4. Target architecture

```
clawbot/
  agent/          VulnClaw, unchanged — loop, anti_loop, constraint_policy,
                  token_counter, llm_client, builtin_tools (extended registry)
  mcp/            VulnClaw, unchanged — lifecycle, registry, router
  skills/         VulnClaw skills + NEW methodology skills:
                    cve-triage.md, compliance-mapping.md, osint-recon (exists),
                    topology-mapping.md
  intel/          NEW — ported HackBot modules, VulnClaw conventions:
      cve.py            NVD/CVE lookup + exploit-PoC discovery (httpx)
      osint.py          subdomain / DNS / WHOIS / email / tech fingerprint
      topology.py       nmap/masscan output -> graph data
      compliance.py     PCI/NIST/OWASP/ISO + MITRE ATT&CK mapping
      findings.py       risk scoring + remediation status (on target_state)
      remediation.py    remediation advisor
      tools.py          builtin-tool schemas + dispatchers for the above
  report/         VulnClaw pipeline + NEW pdf_exporter.py
  target_state/   VulnClaw — canonical findings store (enriched by intel/findings)
  config/         VulnClaw pydantic settings + NEW intel keys/toggles
  cli/  web/      VulnClaw surfaces, unchanged
```

The rename `vulnclaw/ -> clawbot/` is mechanical (package dir + imports +
`pyproject` name + entrypoint + config dir `~/.vulnclaw` -> `~/.clawbot`).

**Physical location:** the new product lives in a fresh sibling directory
`C:\Users\jo\github\clawbot` as its own git repo, seeded by copying the VulnClaw
working tree (no `.git`). Neither upstream clone (`hackbot/`, `VulnClaw/`) is
mutated by the merge — they remain read-only donors. HackBot modules are copied
file-by-file from the `hackbot/` clone during their port steps.

## 5. Component design

### 5.1 Intel tool registration & dispatch
VulnClaw builds its OpenAI tool list by appending schema dicts (in
`agent/builtin_tools.py`) and dispatches calls by name in
`execute_mcp_tool(agent, tool_name, args)`. Each intel module exposes pure
async functions; `intel/tools.py` provides:

- `intel_tool_schemas() -> list[dict]` — OpenAI tool schemas for `cve_lookup`,
  `osint_recon`, `topology_build`, `compliance_map`, `remediation_advice`.
- `dispatch_intel_tool(agent, tool_name, args) -> str` — routes to the module.

`builtin_tools.py` is extended at two seams only: extend the tool-list builder
with `intel_tool_schemas()`, and add an `if tool_name in INTEL_TOOLS` branch in
`execute_mcp_tool` calling `dispatch_intel_tool`. Read-only intel tools
(`cve_lookup`, `compliance_map`, `remediation_advice`) are registered so
`constraint_policy.validate_tool_action` treats them as safe (no network egress
to the target, no host-changing actions).

### 5.2 Findings reconciliation
VulnClaw's `target_state/store.py` persists findings per target (sha256-keyed
dir under `TARGETS_DIR`), with `planner.compute_finding_confidence` and
semantic dedup via `finding_similarity`. HackBot's `vulndb.py` (SQLite) is **not
ported as a store**. Instead `intel/findings.py` provides pure functions that
operate on VulnClaw finding dicts:

- `score_risk(finding) -> RiskScore` — CVSS/severity-derived risk (ported logic).
- `annotate_compliance(finding) -> finding` — attach PCI/NIST/OWASP/ISO + ATT&CK.
- `diff_assessments(old_state, new_state) -> DiffReport` — new/fixed/persistent,
  operating on two `target_state` snapshots (VulnClaw already keeps snapshots).

No second database. Risk/remediation/diff are computed over the canonical store.

### 5.3 Reporting
HackBot's `pdf_report.py` becomes `report/pdf_exporter.py`: a function
`export_pdf(report_model, out_path)` that consumes VulnClaw's existing report
model (from `report/generator.py`) — not a parallel report builder. `reportlab`,
`matplotlib`, `Pillow` move to an optional `[pdf]` extra; the exporter raises a
clear "install clawbot[pdf]" error if imported without the extra.

### 5.4 Config
Extend the pydantic config schema with an `intel` section: optional API keys
(`nvd_api_key`, `shodan_api_key`, `censys_api_id`/`censys_api_secret`) and
feature toggles. All optional; modules **degrade gracefully** when a key is
absent (keyless NVD already works in HackBot). Reachable via existing
dot-notation setter (`clawbot config set intel.nvd_api_key ...`).

## 6. Dependencies

Base = VulnClaw's current set (typer, rich, prompt_toolkit, httpx, openai,
pydantic, pydantic-settings, pyyaml, toml, jinja2, textual, beautifulsoup4,
lxml, pycryptodome). Python floor **3.10+**.

New optional extras:
- `[pdf]` — reportlab, matplotlib, Pillow
- `[osint]` — dnspython, shodan, censys (beautifulsoup4/lxml already in base)
- `[kb]`, `[web]`, `[dev]` — unchanged from VulnClaw

`python-nmap` is **not** added; `topology.py` parses nmap/masscan XML directly
with stdlib `xml.etree` (VulnClaw already does this in `builtin_tools`).

All ported HackBot HTTP code is rewritten from `requests`/`aiohttp` to `httpx`.

## 7. Data flow

The agent loop is unchanged. Intel tools are just new callable tools:

1. Agent calls e.g. `cve_lookup` -> `intel/cve.py` (httpx -> NVD) -> structured
   tool result string back into the loop.
2. Confirmed vulns land in `target_state` via the normal finding path.
3. `intel/findings.py` enriches stored findings with risk score + compliance/ATT&CK.
4. `report/generator.py` reads `target_state`; `pdf_exporter.py` renders the
   same model to PDF; `diff_assessments` compares two snapshots on demand.

## 8. Error handling

- Intel tools return VulnClaw's structured tool-result convention (error in the
  result string, never raise into the agent loop).
- All network calls use httpx with explicit timeouts and bounded retries.
- Missing API key -> degraded-mode result message, not a failure.
- PDF/optional-extra missing -> actionable install hint.

## 9. Testing

- Unit tests per ported module under VulnClaw's `pytest` + `asyncio_mode=auto`:
  mock httpx for `cve`/`osint`; golden-file tests for `compliance` mapping and
  `findings` risk scoring; a smoke test for `pdf_exporter` (skipped without `[pdf]`).
- One agent integration test: run the loop with intel tools registered but
  network stubbed, assert tool dispatch + finding enrichment + report render.
- CI: ruff + pytest on 3.10–3.13 (carry VulnClaw's config forward).

## 10. Licensing & attribution

Both projects are MIT. Ship a top-level `NOTICE` crediting **Yashab Alam**
(HackBot) and **UncleC** (VulnClaw); retain both upstream LICENSE texts;
README credits both upstreams and links their repos. Each ported file carries a
header noting its HackBot origin.

## 11. Risks & mitigations

| Risk | Mitigation |
|---|---|
| Findings model mismatch between the two projects | §5.2 — single canonical store; intel logic adapts to VulnClaw dicts, no second DB |
| HackBot `requests`/`aiohttp` idioms leak in | Migration C rewrites each module to httpx + VulnClaw conventions during port |
| Dep bloat from PDF/OSINT libs | Optional extras; core install stays light |
| Rename churn breaks imports | Mechanical rename done as its own first step with full test pass before any port |
| Scope creep (GUI/Telegram/zeroday) | Explicitly deferred to future specs |

## 12. Sequencing (each becomes a plan step)

0. **Scaffold & rename** — fork VulnClaw into the new package, rename to
   `clawbot`, config dir, entrypoint, NOTICE/attribution; full test pass.
1. **Tool plumbing** — `intel/tools.py` skeleton + the two `builtin_tools.py`
   seams + constraint registration; one trivial intel tool end-to-end.
2. **CVE module** — port `cve.py` to httpx + `cve_lookup` tool + `cve-triage.md`.
3. **OSINT module** — port `osint.py` + `osint_recon` tool.
4. **Topology module** — port `topology.py` + `topology_build` tool.
5. **Findings enrichment** — `intel/findings.py` (risk scoring + diff) on target_state.
6. **Compliance/MITRE** — port `compliance.py` + `compliance_map` tool + skill.
7. **Remediation** — port `remediation.py` + `remediation_advice` tool.
8. **PDF export** — `report/pdf_exporter.py` + `[pdf]` extra.
9. **Integration & release prep** — agent integration test, README, CI matrix,
   version, packaging smoke (`pip install .` + `clawbot --help`).

## 13. Definition of done (v1)

- `pip install clawbot` exposes the `clawbot` CLI; `clawbot --help` works.
- Agent can call all five intel tools; results enrich `target_state`.
- A run produces a Markdown report and (with `[pdf]`) a PDF; diff works across
  two snapshots; findings carry risk + compliance/ATT&CK annotations.
- ruff clean; pytest green on 3.10–3.13; NOTICE + dual attribution present.

## 14. Implementation notes & status (foundation, 2026-06-22)

The foundation (spec §12 steps 0–1) is implemented in `C:\Users\jo\github\clawbot`
(fresh git repo, branch `master`). Decisions made during execution:

- **Seeded from VulnClaw's clean committed HEAD** (`a3f364c`), not its dirty
  working tree — the working tree had deleted skill-reference files and
  in-progress edits that broke tests. Clean HEAD gives a reproducible base.
- **Minimal namespace rename only.** Renamed the import package `vulnclaw ->
  clawbot` (dirs, imports, entrypoint command, PyPI name) and added Yashab Alam
  to authors. User-facing **branding was intentionally NOT changed yet** (config
  dir `~/.vulnclaw`, CLI banners/prog-name, prompts, report brand, frontend,
  static HTML). Half-rebranding broke brand-assertion tests; a full, consistent
  **rebranding sweep across all surfaces (py + ts + html + json) + tests** is
  deferred to its own plan before release.
- **Intel seam live:** `clawbot/intel/` + `intel/tools.py` registry; wired into
  `agent/builtin_tools.py` at two seams (schema list + dispatch); read-only intel
  tools classified as passive `recon` in `constraint_policy`.
- **Plan 2 (CVE) DONE:** `clawbot/intel/cve.py` ports HackBot's CVE module to
  async httpx — NVD keyword + CVE-ID lookup, best-effort GitHub PoC discovery,
  markdown formatting. The `cve_lookup` stub is replaced by the real handler; a
  `cve-triage` methodology skill ships alongside. Tested via `httpx.MockTransport`
  (no network).
- **Verification:** `pip install -e .[dev]` + `clawbot` import OK; **532 passed,
  1 skipped**. `clawbot/intel` is ruff-clean; **5 pre-existing upstream ruff nits**
  remain in VulnClaw files (cli/tui_textual, mcp/router, skills/crypto_tools,
  skills/dispatcher, tests/test_basic) — tracked for the cleanup/rebranding sweep.
- **Known pre-existing failure (NOT from the merge):**
  `tests/test_web.py::...test_web_target_service_lists_targets` fails because
  VulnClaw's finding-dedup drops a second empty-ID finding during target-state
  save (`[DEDUP] Skipping duplicate finding`). The code is byte-identical to
  upstream modulo the namespace rename; it reproduces on upstream HEAD under
  Python 3.14.4 + pydantic 2.13.4. Tracked as an upstream/compat issue, out of
  scope for the rename foundation.

**Done:** Foundation (steps 0–1) · CVE (Plan 2) · OSINT (Plan 3) · Topology (Plan 4).
**Deferred plans (each authored at port time):** Rebranding sweep · Findings ·
Compliance/MITRE · Remediation · PDF export · Integration & release
(spec §12 steps 5–9).

Topology notes: `clawbot/intel/topology.py` — pure/offline parser (nmap text+XML,
masscan) → host/port/service/subnet graph; markdown/ascii/json render; read-only
`topology_build` tool. Suite: **558 passed, 1 skipped**. Intel tools live:
`cve_lookup`, `osint_recon`, `topology_build`.

OSINT notes: `clawbot/intel/osint.py` — async httpx for crt.sh CT, RDAP WHOIS,
tech fingerprint; blocking DNS/socket-WHOIS/TLS via `asyncio.to_thread`;
`dnspython` optional (`clawbot[osint]`) with socket fallback. HackBot's
search-engine email scraping was dropped (unreliable/ToS-fragile) for
deterministic MX-based candidates. `osint_recon` classified as active `recon`.
Suite: **546 passed, 1 skipped** (same pre-existing dedup failure).
