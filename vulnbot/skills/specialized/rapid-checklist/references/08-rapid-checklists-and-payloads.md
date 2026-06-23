# 08 Rapid Checklists And Payloads

This file is the rapid operator-reference layer of the final skill system.
Use it only after routing is clear. It is meant for fast lookup, not for replacing methodology or workflow selection.

## Use This File For

- rapid validation checklist guidance
- rapid validation checklist guidance payload rapid validation checklist guidance、rapid validation checklist guidance
- rapid validation checklist guidance AI、MCP、rapid validation checklist guidance、WebSocket、JWT、rapid validation checklist guidance、rapid validation checklist guidance、SSRF rapid validation checklist guidance
- rapid validation checklist guidance“rapid validation checklist guidance”rapid validation checklist guidance“rapid validation checklist guidance”

## Do Not Use This File For

- rapid validation checklist guidance `00-usage-and-routing.md` rapid validation checklist guidance
- rapid validation checklist guidance `01-unified-methodology.md` rapid validation checklist guidance
- rapid validation checklist guidance、rapid validation checklist guidance payload rapid validation checklist guidance

## Fast Routing Cards

### Web injection or output execution

- rapid validation checklist guidance `03-web-security-integrated.md`
- rapid validation checklist guidance，rapid validation checklist guidance `SQLi`、`XSS`、`command execution`、`SSTI`、`XXE`
- rapid validation checklist guidance，rapid validation checklist guidance `02-client-api-reverse-and-burp.md`

### Auth, logic, token, or state bugs

- rapid validation checklist guidance `03-web-security-integrated.md`
- rapid validation checklist guidance、rapid validation checklist guidance、rapid validation checklist guidance、rapid validation checklist guidance、rapid validation checklist guidance
- rapid validation checklist guidance token rapid validation checklist guidance，rapid validation checklist guidance

### Browser-side sign, anti-bot, or WebSocket handshake

- rapid validation checklist guidance `browser-js-signing-workflow.md`
- rapid validation checklist guidance `browser-locate-and-request-chain.md`、`browser-recover-and-shell-reduction.md`、`browser-runtime-fit-and-risk.md`、`browser-validation-and-handoff.md`
- rapid validation checklist guidance `03-web-security-integrated.md`

### Android runtime, packet visibility, or sign recovery

- rapid validation checklist guidance `android-external-url-runtime-first-workflow.md`
- rapid validation checklist guidance，rapid validation checklist guidance `android-ui-driven-observation-and-packet-loop.md`
- rapid validation checklist guidance、rapid validation checklist guidance，rapid validation checklist guidance `android-signing-and-crypto-workflow.md`

### AI, agent, or MCP exposure

- rapid validation checklist guidance `04-ai-and-mcp-security-integrated.md`
- rapid validation checklist guidance `prompt injection`、`tool abuse`、`MCP trust boundary`、`memory/state poisoning`、`output approval gaps`
- rapid validation checklist guidance，rapid validation checklist guidance AI/MCP rapid validation checklist guidance

### Intranet, host, or AD work

- rapid validation checklist guidance `06-intranet-and-host-operations-integrated.md`
- rapid validation checklist guidance `05-tools-and-operations-integrated.md`

## Web Rapid Cards

### SQL injection

- rapid validation checklist guidance: `'`, `"`, `)`, rapid validation checklist guidance, rapid validation checklist guidance, rapid validation checklist guidance
- rapid validation checklist guidance: query, body, JSON, header, cookie, WebSocket message
- rapid validation checklist guidance, rapid validation checklist guidance
- rapid validation checklist guidance: inline comments, whitespace variation, keyword case folding, alternate encodings, parameter pollution

### XSS

- rapid validation checklist guidance: reflected, stored, DOM
- rapid validation checklist guidance: HTML body, attribute, JS string, URL, template
- rapid validation checklist guidance: event handlers, SVG, tag breaking, JS context breaking
- rapid validation checklist guidance, rapid validation checklist guidance DOM sink rapid validation checklist guidance CSP rapid validation checklist guidance

### Command execution

- rapid validation checklist guidance: timing, DNS or HTTP OOB, harmless command echo
- rapid validation checklist guidance system shell、template helper、language runtime rapid validation checklist guidance worker sidecar
- rapid validation checklist guidance: separators, whitespace bypass, variablerapid validation checklist guidance, Base64 or hex decode chains

### File and SSRF

- rapid validation checklist guidance: upload, traversal/download, inclusion, parser confusion
- SSRF rapid validation checklist guidance: raw fetch, image proxy, webhook, PDF render, URL preview, cloud metadata reachability
- rapid validation checklist guidance: encoding layers, mixed path separators, alternate IP formats, redirect chaining, protocol pivot

### Modern protocols

- WebSocket: rapid validation checklist guidance、Origin rapid validation checklist guidance、rapid validation checklist guidance、rapid validation checklist guidance
- JWT: rapid validation checklist guidance、rapid validation checklist guidance、`kid` rapid validation checklist guidance `jku` rapid validation checklist guidance
- OAuth/OIDC: rapid validation checklist guidance redirect URI、state、PKCE、rapid validation checklist guidance
- Request smuggling: rapid validation checklist guidance

## AI And MCP Rapid Cards

### Prompt injection

- rapid validation checklist guidance: direct, indirect, retrieval-borne, tool-description-borne, memory-borne
- rapid validation checklist guidance: model prompt, retrieval context, tool metadata, tool output, persisted memory
- rapid validation checklist guidance: role play, instruction override, encoding, multilingual phrasing, hidden text, long-context dilution

### Tool abuse and MCP trust boundary

- rapid validation checklist guidance tool description rapid validation checklist guidance
- rapid validation checklist guidance tool parameters、resource paths、tool outputs rapid validation checklist guidance
- rapid validation checklist guidance: unauthorized resource reads, prompt override in description, hidden instructions, cross-tool request rewriting

### Agent memory and state poisoning

- rapid validation checklist guidance memory rapid validation checklist guidance
- rapid validation checklist guidance、rapid validation checklist guidance
- rapid validation checklist guidance、rapid validation checklist guidance、rapid validation checklist guidance

### Model or data leakage

- rapid validation checklist guidance: system prompt extraction, tool inventory exposure, API or secret leakage, training-data style continuation, RAG source disclosure
- rapid validation checklist guidance direct disclosure rapid validation checklist guidance inference-style leakage

## Container And Sandbox Rapid Cards

### Environment triage

- rapid validation checklist guidance、rapid validation checklist guidance、rapid validation checklist guidance shell rapid validation checklist guidance agent execution sandbox rapid validation checklist guidance
- rapid validation checklist guidance capabilities、namespace、mount、socket、metadata reachability
- rapid validation checklist guidance，rapid validation checklist guidance

### Escape paths

- rapid validation checklist guidance: exposed Docker socket, writable host mounts, privileged container, cgroup abuse, `/proc` traversal, kernel CVE, cloud metadata pivots
- rapid validation checklist guidance，rapid validation checklist guidance

### Persistence or staged foothold

- rapid validation checklist guidance
- rapid validation checklist guidance“rapid validation checklist guidance”rapid validation checklist guidance
- rapid validation checklist guidance: shell rc files, scheduled tasks, service startup, workspace poisoning, SSH keys

## Payload Family Hints

Use families, not copied full lists, unless the current task specifically needs detail from a deeper source.

- SQLi: boolean, time, error, union, second-order
- XSS: reflected, stored, DOM, mutation-based, CSP-aware
- Command execution: separator-based, subshell, whitespace-bypass, encoded launcher, OOB validation
- File bugs: upload extension variants, MIME mismatch, parser confusion, traversal encodings
- SSRF: alternate IP encodings, redirect pivot, protocol pivot, metadata paths
- AI injection: direct override, indirect document-borne, description poisoning, memory poisoning, encoded or multilingual prompts
- Escape and shell: environment triage, breakout path validation, persistence validation, callback channel selection

## Escalation Rule

- If the route is still unclear, go back to `00-usage-and-routing.md`.
- If packet visibility or replay is blocked, go back to `02-client-api-reverse-and-burp.md` or the matching browser or Android workflow.
- If you need exact original payload wording or exhaustive raw examples, open `references/payloads.md`.


