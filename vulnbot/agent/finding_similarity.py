"""Lightweight semantic deduplication for vulnerability findings.

This module intentionally avoids external NLP dependencies. It complements exact
finding-id hashing by catching likely duplicates that describe the same issue in
slightly different English wording.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Optional
from urllib.parse import parse_qs, urlsplit

if TYPE_CHECKING:
    from vulnbot.agent.context import VulnerabilityFinding


_VULN_TYPE_ALIASES: dict[str, str] = {
    "sqli": "sql_injection",
    "sql injection": "sql_injection",
    "blind sqli": "sql_injection",
    "blind sql injection": "sql_injection",
    "injection": "sql_injection",
    "sql_injection": "sql_injection",
    "xss": "cross_site_scripting",
    "reflected xss": "cross_site_scripting",
    "stored xss": "cross_site_scripting",
    "cross site scripting": "cross_site_scripting",
    "cross_site_scripting": "cross_site_scripting",
    "ssrf": "server_side_request_forgery",
    "server side request forgery": "server_side_request_forgery",
    "server_side_request_forgery": "server_side_request_forgery",
    "rce": "remote_code_execution",
    "command execution": "remote_code_execution",
    "command injection": "remote_code_execution",
    "remote code execution": "remote_code_execution",
    "remote_code_execution": "remote_code_execution",
    "lfi": "local_file_inclusion",
    "rfi": "local_file_inclusion",
    "file inclusion": "local_file_inclusion",
    "path traversal": "local_file_inclusion",
    "directory traversal": "local_file_inclusion",
    "local file inclusion": "local_file_inclusion",
    "local_file_inclusion": "local_file_inclusion",
    "idor": "insecure_direct_object_reference",
    "broken object level authorization": "insecure_direct_object_reference",
    "horizontal privilege escalation": "insecure_direct_object_reference",
    "vertical privilege escalation": "insecure_direct_object_reference",
    "insecure direct object reference": "insecure_direct_object_reference",
    "insecure_direct_object_reference": "insecure_direct_object_reference",
    "csrf": "cross_site_request_forgery",
    "cross site request forgery": "cross_site_request_forgery",
    "cross_site_request_forgery": "cross_site_request_forgery",
    "auth bypass": "auth_bypass",
    "authentication bypass": "auth_bypass",
    "unauthorized access": "auth_bypass",
    "missing authentication": "auth_bypass",
    "info disclosure": "info_disclosure",
    "information disclosure": "info_disclosure",
    "data exposure": "info_disclosure",
    "sensitive information disclosure": "info_disclosure",
}


def normalize_vuln_type(vuln_type: str) -> str:
    """Normalize common vulnerability type aliases to canonical names."""
    if not vuln_type:
        return ""
    key = re.sub(r"\s+", " ", vuln_type.strip().lower())
    if key in _VULN_TYPE_ALIASES:
        return _VULN_TYPE_ALIASES[key]
    underscore = key.replace(" ", "_")
    if underscore in _VULN_TYPE_ALIASES:
        return _VULN_TYPE_ALIASES[underscore]
    spaced = key.replace("_", " ")
    if spaced in _VULN_TYPE_ALIASES:
        return _VULN_TYPE_ALIASES[spaced]
    return underscore


_URL_RE = re.compile(r'https?://[^\s<>"\')\]]+', re.IGNORECASE)
_TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)
_NOISE_TAGS = ("[auto]", "[confirmed]", "[unverified]")


def _normalize_url_path(url: str) -> str:
    """Normalize URL strings to host plus path for text comparison."""
    try:
        parts = urlsplit(url)
    except ValueError:
        return url.lower()
    host = (parts.hostname or "").lower()
    path = parts.path or ""
    if len(path) > 1:
        path = path.rstrip("/")
    return f"{host}{path}"


def normalize_text(text: str) -> str:
    """Normalize free text before token-based similarity scoring."""
    if not text:
        return ""
    result = text
    for tag in _NOISE_TAGS:
        result = result.replace(tag, " ")
    result = _URL_RE.sub(lambda m: _normalize_url_path(m.group(0)), result)
    result = result.lower()
    result = re.sub(r"\s+", " ", result).strip()
    return result


def _tokenize(text: str) -> set[str]:
    """Split normalized text into tokens."""
    return set(_TOKEN_RE.findall(text))


def text_similarity(a: str, b: str) -> float:
    """Return Jaccard similarity for two pieces of text."""
    na, nb = normalize_text(a), normalize_text(b)
    if not na and not nb:
        return 1.0
    if not na or not nb:
        return 0.0
    ta, tb = _tokenize(na), _tokenize(nb)
    if not ta and not tb:
        return 1.0
    if not ta or not tb:
        return 0.0
    union = len(ta | tb)
    return len(ta & tb) / union if union else 0.0


def url_similarity(a: str, b: str) -> float:
    """Compare two URL-like locations by host, path, and query parameter names."""
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0

    pa, pb = urlsplit(a.strip()), urlsplit(b.strip())
    if not (pa.scheme or pa.netloc) and not (pb.scheme or pb.netloc):
        return text_similarity(a, b)

    ha, hb = (pa.hostname or "").lower(), (pb.hostname or "").lower()
    if not ha and not hb:
        host_sim = 1.0
    elif not ha or not hb:
        host_sim = 0.0
    else:
        host_sim = 1.0 if ha == hb else 0.0

    seg_a = {s for s in pa.path.split("/") if s}
    seg_b = {s for s in pb.path.split("/") if s}
    if not seg_a and not seg_b:
        path_sim = 1.0
    elif not seg_a or not seg_b:
        path_sim = 0.0
    else:
        path_sim = len(seg_a & seg_b) / len(seg_a | seg_b)

    qa = set(parse_qs(pa.query).keys())
    qb = set(parse_qs(pb.query).keys())
    if not qa and not qb:
        query_sim = 1.0
    elif not qa or not qb:
        query_sim = 0.0
    else:
        query_sim = len(qa & qb) / len(qa | qb)

    return host_sim * 0.3 + path_sim * 0.4 + query_sim * 0.3


_LOCATION_RE = re.compile(r'(?:https?://[^\s<>"\')\]]+)|(?:/[\w%&=?\-./]+)')


def _extract_location(finding: "VulnerabilityFinding") -> str:
    """Extract the first URL or path from finding evidence or description."""
    for field in (finding.evidence or "", finding.description or ""):
        if not field:
            continue
        match = _LOCATION_RE.search(field)
        if match:
            return match.group(0)
    return ""


def _vuln_type_similarity(a: str, b: str) -> float:
    """Score vulnerability type similarity."""
    raw_a, raw_b = (a or "").strip().lower(), (b or "").strip().lower()
    if raw_a and raw_b and raw_a == raw_b:
        return 1.0
    norm_a, norm_b = normalize_vuln_type(a), normalize_vuln_type(b)
    if norm_a and norm_b and norm_a == norm_b:
        return 0.8
    return 0.0


def finding_similarity(a: "VulnerabilityFinding", b: "VulnerabilityFinding") -> float:
    """Return a combined similarity score for two vulnerability findings."""
    type_sim = _vuln_type_similarity(a.vuln_type, b.vuln_type)

    loc_a, loc_b = _extract_location(a), _extract_location(b)
    loc_sim = 0.5 if not loc_a and not loc_b else url_similarity(loc_a, loc_b)

    desc_a = f"{a.title} {a.description}".strip()
    desc_b = f"{b.title} {b.description}".strip()
    desc_sim = text_similarity(desc_a, desc_b)

    return type_sim * 0.3 + loc_sim * 0.4 + desc_sim * 0.3


_EVIDENCE_LEVEL_RANK = {"L1": 1, "L2": 2, "L3": 3, "L4": 4}
_LIFECYCLE_RANK = {
    "rejected": 0,
    "candidate": 1,
    "pending_verification": 2,
    "needs_manual_review": 3,
    "verified": 4,
}


def _evidence_strength(finding: "VulnerabilityFinding") -> tuple[int, int, int, int]:
    """Build a comparable evidence-strength tuple for duplicate resolution."""
    return (
        1 if finding.verified else 0,
        _LIFECYCLE_RANK.get(finding.lifecycle_status, 1),
        _EVIDENCE_LEVEL_RANK.get(finding.evidence_level, 1),
        len(finding.evidence or ""),
    )


def deduplicate_findings(
    findings: list["VulnerabilityFinding"], threshold: float = 0.75
) -> list["VulnerabilityFinding"]:
    """Deduplicate findings while keeping the stronger-evidence entry."""
    kept: list["VulnerabilityFinding"] = []
    for candidate in findings:
        duplicate_index: Optional[int] = None
        for index, existing in enumerate(kept):
            if finding_similarity(candidate, existing) >= threshold:
                duplicate_index = index
                break
        if duplicate_index is None:
            kept.append(candidate)
            continue
        if _evidence_strength(candidate) > _evidence_strength(kept[duplicate_index]):
            kept[duplicate_index] = candidate
    return kept
