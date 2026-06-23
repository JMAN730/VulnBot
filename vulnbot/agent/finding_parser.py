"""VulnBot Finding Parser - vulnerability detection from LLM responses."""

from __future__ import annotations

import re

from vulnbot.agent.context import ContextManager, VulnerabilityFinding
from vulnbot.agent.runtime_state import RuntimeState
from vulnbot.agent.think_filter import strip_think_tags

PROOF_PATTERNS: list[str] = [
    r"difference[: ]*\d+",
    r"\d+\s*bytes",
    r"(?:status|response code)?[: ]*5\d{2}",
    r"SQL.*error|mysql.*error|sql.*error",
    r"SLEEP\(|BENCHMARK\(|EXTRACTVALUE\(|UPDATEXML\(",
    r"command execution succeeded|whoami|id\s+",
    r"root[:\s]|administrator",
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
    r"CVE-\d{4}-\d{4,}",
    r"successfully extracted|successfully obtained|obtained",
]

NATURAL_LANG_PATTERNS: list[tuple[str, str, str]] = [
    (r"SQL injection|SQLi|injection vulnerability", "High", "SQL Injection"),
    (r"RCE|remote code execution|command injection|command execution", "Critical", "Remote Code Execution"),
    (r"unauthorized|unauthenticated|no authentication|auth bypass|authentication bypass", "High", "Authentication Bypass"),
    (r"SSRF|server-side request forgery", "High", "SSRF"),
    (r"XSS|cross-site scripting|stored XSS|reflected XSS", "Medium", "XSS"),
    (r"CSRF|cross-site request forgery", "Medium", "CSRF"),
    (r"file inclusion|path traversal|LFI|RFI", "Medium", "File Inclusion/Traversal"),
    (r"weak password|default password|default credential|brute force", "Medium", "Weak Password/Brute Force"),
    (r"misconfiguration|configuration weakness|config leak", "Medium", "Misconfiguration"),
    (r"sensitive directory|sensitive file|directory discovered", "Info", "Sensitive Directory/File Discovery"),
    (r"outdated version|middleware version|fingerprint", "Info", "Version Information"),
    (r"CVE-\d{4}-\d{4,}", "High", "Known CVE"),
]

ELEVATION_KEYWORDS: list[tuple[str, str, str]] = [
    (r"leak|sensitive information|data leak|personal information|\d+ records", "High", "Data Exposure"),
    (r"unauthorized|unauthenticated|auth bypass|no authentication", "High", "Unauthorized Access"),
    (r"RCE|command execution|remote code", "Critical", "Remote Code Execution"),
    (r"SQL injection|SQLi|injection", "High", "Injection Vulnerability"),
    (r"CVE-\d{4}-\d{4,}", "High", "Known CVE"),
    (r"weak password|default password|brute", "High", "Weak Password/Brute Force"),
    (r"XSS|cross-site scripting", "Medium", "XSS"),
    (r"file inclusion|path traversal", "High", "File Inclusion/Traversal"),
    (r"200.*not found|200.*empty|empty response", "Medium", "Potential Authorization Bypass"),
    (r"403.*endpoint|endpoint exists.*403", "Medium", "403 Authentication Block"),
]

URL_PATTERN = re.compile(r'https?://[^\s<>"\')\]]+')
PATH_PATTERN = re.compile(r"(?:/[\w%&=?\-]+)+")


def _collect_location_summary(text: str, max_items: int = 4) -> str:
    seen: set[str] = set()
    items: list[str] = []

    for value in re.findall(URL_PATTERN, text):
        if value not in seen:
            seen.add(value)
            items.append(value)
        if len(items) >= max_items:
            return " | ".join(items)

    for value in re.findall(PATH_PATTERN, text):
        if value not in seen:
            seen.add(value)
            items.append(value)
        if len(items) >= max_items:
            break

    return " | ".join(items)


class FindingParser:
    """Parse LLM responses to extract vulnerability findings and discoveries."""

    def __init__(self, context: ContextManager, runtime: RuntimeState) -> None:
        self.context = context
        self.runtime = runtime

    def parse(self, response: str) -> None:
        """Extract findings, discoveries, confirmed facts, and assumptions."""
        existing_titles = {f.title for f in self.context.state.findings}

        severity_patterns = [
            (r"\[Critical\]\s*(.+?)(?:\n|$)", "Critical"),
            (r"\[High\]\s*(.+?)(?:\n|$)", "High"),
            (r"\[Medium\]\s*(.+?)(?:\n|$)", "Medium"),
            (r"\[Low\]\s*(.+?)(?:\n|$)", "Low"),
        ]
        for pattern, severity in severity_patterns:
            for match in re.findall(pattern, response):
                title = re.sub(r"\*+", "", match.strip()).strip(" -")
                if title and title not in existing_titles:
                    self.context.state.add_finding(
                        VulnerabilityFinding(
                            title=title,
                            severity=severity,
                            evidence_level="L1",
                            lifecycle_status="candidate",
                        )
                    )
                    existing_titles.add(title)

        clean_response = strip_think_tags(response)
        notes = self.context.state.notes
        clean_notes = [strip_think_tags(n) for n in notes[-5:]]
        evidence_pool = clean_response + " " + " ".join(clean_notes)

        self._elevate_confirmed_facts(existing_titles, evidence_pool)

        for pattern, severity, vuln_type in NATURAL_LANG_PATTERNS:
            canonical_title = f"[AUTO] {vuln_type}"
            if canonical_title in existing_titles:
                continue

            vuln_matches = re.findall(pattern, clean_response, re.IGNORECASE)
            if not vuln_matches:
                continue

            proof_source = clean_response + " " + " ".join(notes[-3:])
            has_proof = any(re.search(p, proof_source, re.IGNORECASE) for p in PROOF_PATTERNS)
            confirmed_text = " ".join(getattr(self.context.state, "confirmed_facts", []))
            has_confirmed_fact = any(
                re.search(p, confirmed_text, re.IGNORECASE) for p in PROOF_PATTERNS
            )
            if not has_proof and not has_confirmed_fact:
                continue

            proof_snippets: list[str] = []
            for proof_pattern in PROOF_PATTERNS:
                for match in re.finditer(proof_pattern, evidence_pool, re.IGNORECASE):
                    snippet = match.group(0).strip()[:80]
                    if snippet and snippet not in proof_snippets:
                        proof_snippets.append(snippet)
                    if len(proof_snippets) >= 3:
                        break

            location = _collect_location_summary(evidence_pool)
            proof_text = " | ".join(proof_snippets)
            evidence = (
                f"{location} | {proof_text}" if location and proof_text else location or proof_text
            )

            self.context.state.add_finding(
                VulnerabilityFinding(
                    title=canonical_title,
                    severity=severity,
                    vuln_type=vuln_type,
                    description=f"Automatically detected from phrase: {str(vuln_matches[0]).strip()[:100]}",
                    evidence=evidence[:300],
                    evidence_level="L2",
                    lifecycle_status="needs_manual_review"
                    if severity in ("Critical", "High")
                    else "pending_verification",
                )
            )
            existing_titles.add(canonical_title)

        self._capture_notes_and_facts(clean_response)
        self._capture_assumptions(response)

    def _elevate_confirmed_facts(self, existing_titles: set[str], evidence_pool: str) -> None:
        confirmed_facts = getattr(self.context.state, "confirmed_facts", [])
        for fact in confirmed_facts:
            for pattern, severity, vuln_type in ELEVATION_KEYWORDS:
                if not re.search(pattern, fact, re.IGNORECASE):
                    continue
                title = f"[CONFIRMED] {fact.strip()[:120]}"
                if title not in existing_titles:
                    location = _collect_location_summary(evidence_pool)
                    evidence = (
                        f"{location} | Verified by tool output: {fact}"
                        if location
                        else f"Verified by tool output: {fact}"
                    )
                    finding = VulnerabilityFinding(
                        title=title,
                        severity=severity,
                        vuln_type=vuln_type,
                        description=f"Verified by tool output: {fact}",
                        evidence=evidence[:300],
                        evidence_level="L4",
                        lifecycle_status="verified",
                    )
                    finding.mark_verified(note=fact[:200], evidence_level="L4")
                    self.context.state.add_finding(finding)
                    existing_titles.add(title)
                break

    def _capture_notes_and_facts(self, clean_response: str) -> None:
        discovery_markers = [
            r"\[\+\]\s*(.+?)(?:\n|$)",
            r"found[: ]\s*(.+?)(?:\n|$)",
            r"discovered[: ]\s*(.+?)(?:\n|$)",
            r"(flag\{[^}]+\})",
            r"(NSSCTF\{[^}]+\})",
            r"(CTF\{[^}]+\})",
        ]
        for pattern in discovery_markers:
            for match in re.findall(pattern, clean_response, re.IGNORECASE):
                note = match.strip()[:200]
                if note and note not in self.context.state.notes:
                    self.context.state.add_note(note)

        confirmed_markers = [
            r"confirmed[: ]\s*(.+?)(?:\n|$)",
            r"verified[: ]\s*(.+?)(?:\n|$)",
            r"verification succeeded[: ]\s*(.+?)(?:\n|$)",
            r"\[\+\]\s*(.+?confirmed.+?)(?:\n|$)",
            r"payload.*difference[: ]*\s*\d+",
            r"SLEEP\([^)]+\).*elapsed",
            r"successfully extracted[: ]*\s*\S+",
            r"command execution succeeded",
            r"boolean.*success|boolean.*valid",
            r"error-based.*success|error-based.*valid",
            r"UNION.*success|UNION.*valid",
            r"vulnerability confirmed",
        ]
        for pattern in confirmed_markers:
            for match in re.findall(pattern, clean_response, re.IGNORECASE):
                fact = match.strip()[:200]
                if fact and hasattr(self.context.state, "add_confirmed_fact"):
                    self.context.state.add_confirmed_fact(fact)

    def _capture_assumptions(self, response: str) -> None:
        assumption_markers = [
            r"assumption[: ]\s*(.+?)(?:\n|$)",
            r"inference[: ]\s*(.+?)(?:\n|$)",
        ]
        for pattern in assumption_markers:
            for match in re.findall(pattern, response, re.IGNORECASE):
                assumption = match.strip()[:200]
                if assumption and assumption not in self.runtime.unverified_assumptions:
                    self.runtime.unverified_assumptions.append(assumption)
