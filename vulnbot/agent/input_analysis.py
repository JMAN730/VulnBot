"""Input analysis helpers for AgentCore."""

from __future__ import annotations

import re
from typing import Optional

from vulnbot.agent.context import PentestPhase, TaskConstraints


def detect_phase(user_input: str) -> Optional[PentestPhase]:
    """Detect pentest phase from user input using keyword matching."""
    input_lower = user_input.lower()
    phase_keywords = {
        PentestPhase.POST_EXPLOITATION: [
            "post-exploitation",
            "post exploitation",
            "pivot",
            "lateral movement",
            "privilege escalation",
            "tunnel",
            "proxy",
        ],
        PentestPhase.EXPLOITATION: [
            "exploit",
            "exploitation",
            "poc",
            "verify vulnerability",
            "command execution",
            "rce",
            "getshell",
            "try to exploit",
        ],
        PentestPhase.VULN_DISCOVERY: [
            "vulnerability discovery",
            "vulnerability scan",
            "security check",
            "cve",
            "vulnerability",
            "vulnerabilities",
            "weakness",
            "weaknesses",
            "sql injection",
            "sqli",
            "xss",
        ],
        PentestPhase.REPORTING: [
            "report",
            "summary",
            "summarize",
            "write report",
            "generate report",
        ],
        PentestPhase.RECON: [
            "recon",
            "reconnaissance",
            "information gathering",
            "asset discovery",
            "port scan",
            "subdomain",
            "fingerprint",
            "directory scan",
            "nmap",
            "scan",
        ],
    }
    for phase, keywords in phase_keywords.items():
        if any(keyword in input_lower for keyword in keywords):
            return phase
    for pattern in (r"\d{1,3}(?:\.\d{1,3}){3}", r"https?://\S+"):
        if re.search(pattern, user_input):
            return PentestPhase.RECON
    return None


_FRESH_RECON_PATTERNS = (
    "rescan",
    "re-scan",
    "re scan",
    "scan again",
    "fresh recon",
    "fresh reconnaissance",
    "redo recon",
    "redo reconnaissance",
    "re-recon",
    "start over",
    "start fresh",
    "from scratch",
)


def wants_fresh_recon(user_input: str) -> bool:
    """Detect an explicit request to re-run reconnaissance from scratch.

    Returns True when the prompt contains a force-fresh-recon keyword such as
    "rescan", "fresh recon", or "start over"; False for empty or ordinary input.
    """
    if not user_input:
        return False
    input_lower = user_input.lower()
    return any(pattern in input_lower for pattern in _FRESH_RECON_PATTERNS)


def detect_target(user_input: str) -> Optional[str]:
    """Extract target from user input."""
    for pattern in (
        r"(https?://[a-zA-Z0-9][-a-zA-Z0-9.:]*)",
        r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2})",
        r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})",
        r"([a-zA-Z0-9][-a-zA-Z0-9]*(?:\.[a-zA-Z0-9][-a-zA-Z0-9]*)+)",
    ):
        match = re.search(pattern, user_input)
        if match:
            return match.group(1).rstrip("/.") if match.groups() else match.group(0)
    return None


def extract_task_constraints(user_input: str) -> TaskConstraints:
    """Extract structured hard constraints from natural-language user input."""
    text = user_input or ""
    lowered = text.lower()
    constraints = TaskConstraints()
    detected_target = detect_target(text)

    allowed_port_patterns = [
        r"(?:only|just)\s+(?:test|scan)\s+(?:port\s+)?(\d{1,5})",
    ]
    for pattern in allowed_port_patterns:
        for match in re.findall(pattern, text, flags=re.IGNORECASE):
            port = int(match)
            if 0 < port <= 65535 and port not in constraints.allowed_ports:
                constraints.allowed_ports.append(port)

    blocked_group_patterns = [
        r"(?:do not|don't|never)\s+(?:test|scan|touch)\s+ports?\s*([0-9,\s]+)",
    ]
    for pattern in blocked_group_patterns:
        for group in re.findall(pattern, text, flags=re.IGNORECASE):
            for match in re.findall(r"\d{1,5}", group):
                port = int(match)
                if 0 < port <= 65535 and port not in constraints.blocked_ports:
                    constraints.blocked_ports.append(port)

    if any(token in lowered for token in ["recon only", "only recon", "only information gathering"]):
        constraints.allowed_actions = ["recon"]
    if any(token in lowered for token in ["do not exploit", "no exploit"]):
        constraints.blocked_actions.append("exploit")

    allow_match = re.search(r"only allowed actions:\s*([a-z_,\s-]+)", lowered)
    if allow_match:
        constraints.allowed_actions = [
            item.strip() for item in allow_match.group(1).split(",") if item.strip()
        ]

    block_match = re.search(r"blocked actions:\s*([a-z_,\s-]+)", lowered)
    if block_match:
        constraints.blocked_actions.extend(
            [
                item.strip()
                for item in block_match.group(1).split(",")
                if item.strip() and item.strip() not in constraints.blocked_actions
            ]
        )

    if any(
        token in lowered
        for token in ["only this path", "only test this path", "path only"]
    ):
        path_match = re.search(r"https?://[^\s]+(/[^\s?#]*)", text)
        if not path_match:
            path_match = re.search(r"(/[A-Za-z0-9._/\-]+)", text)
        if not path_match:
            url_match = re.search(r"https?://[^\s]+", text)
            if url_match:
                from urllib.parse import urlsplit

                path = urlsplit(url_match.group(0)).path.rstrip("/")
                if path and path not in constraints.allowed_paths:
                    constraints.allowed_paths.append(path)
        if path_match:
            path = path_match.group(1).rstrip("/")
            if path and path not in constraints.allowed_paths:
                constraints.allowed_paths.append(path)

    blocked_host_match = re.search(r"blocked host\s+([a-z0-9.-]+)", lowered)
    if blocked_host_match:
        host = blocked_host_match.group(1).strip()
        if host and host not in constraints.blocked_hosts:
            constraints.blocked_hosts.append(host)

    blocked_path_match = re.search(r"blocked path\s+(/[^\s]+)", lowered)
    if blocked_path_match:
        path = blocked_path_match.group(1).rstrip("/")
        if path and path not in constraints.blocked_paths:
            constraints.blocked_paths.append(path)

    if detected_target:
        target_lower = detected_target.lower()
        if target_lower.startswith("http://") or target_lower.startswith("https://"):
            host_match = re.search(r"^https?://([^/:?#]+)", target_lower)
            if host_match:
                host = host_match.group(1)
                if host and host not in constraints.allowed_hosts:
                    constraints.allowed_hosts.append(host)
        elif "." in target_lower and target_lower not in constraints.allowed_hosts:
            constraints.allowed_hosts.append(target_lower)

    if (
        constraints.allowed_ports
        or constraints.blocked_ports
        or constraints.allowed_hosts
        or constraints.blocked_hosts
        or constraints.allowed_paths
        or constraints.blocked_paths
        or constraints.allowed_actions
        or constraints.blocked_actions
    ):
        constraints.strict_mode = True

    return constraints


def extract_user_vuln_hint(user_input: str) -> str:
    """Extract explicit vulnerability hints from user input."""
    vuln_keywords = [
        "SQL injection",
        "SQLi",
        "XSS",
        "RCE",
        "command injection",
        "file inclusion",
        "path traversal",
        "LFI",
        "RFI",
        "SSRF",
        "CSRF",
        "weak password",
        "brute force",
        "auth bypass",
        "unauthorized",
        "information disclosure",
    ]
    user_lower = user_input.lower()
    found_vulns = [v for v in vuln_keywords if v.lower() in user_lower]
    if not found_vulns:
        return ""
    url_match = re.search(r"https?://\S+", user_input)
    path_match = re.search(r"/[\w\-./?=&%#]+", user_input)
    target = url_match.group(0) if url_match else (path_match.group(0) if path_match else "")
    vuln_str = "/".join(found_vulns[:3])
    if target:
        return (
            "[Explicit user hint - first round]\n"
            f"The user explicitly indicated that {target} may have {vuln_str}.\n\n"
            "Build and send a minimal PoC request immediately. Use real target responses, "
            "not local guesses, and verify the result independently.\n\n"
            f"{get_payload_examples(found_vulns, target)}"
        )
    return (
        "[Explicit user hint]\n"
        f"The user asked to test for {vuln_str}. Build a focused PoC from known target context."
    )


def get_payload_examples(found_vulns: list[str], target: str) -> str:
    """Return concrete PoC payload examples for the given vulnerability types."""
    lines = ["[PoC payload examples]"]
    for vuln in found_vulns[:2]:
        lower = vuln.lower()
        if "sql" in lower:
            lines += [
                "SQL injection checks:",
                f"  GET {target}?id=1' AND 1=1--",
                f"  GET {target}?id=1' AND 1=2--",
                f"  GET {target}?id=1' AND EXTRACTVALUE(1,CONCAT(0x7e,version()))--",
            ]
        elif "xss" in lower:
            lines += [
                "XSS checks:",
                f"  GET {target}?q=<script>alert(1)</script>",
                f"  GET {target}?q=<img src=x onerror=alert(1)>",
            ]
        elif "rce" in lower or "command" in lower:
            lines += [
                "RCE / command injection checks:",
                f"  GET {target}?cmd=whoami",
                f"  GET {target}?c=whoami",
            ]
        elif "file" in lower or "path" in lower or "lfi" in lower or "rfi" in lower:
            lines += [
                "File inclusion / path traversal checks:",
                f"  GET {target}?f=/etc/passwd",
                f"  GET {target}?f=../../../../etc/passwd",
            ]
        elif "ssrf" in lower:
            lines += [
                "SSRF checks:",
                f"  GET {target}?url=http://127.0.0.1",
                f"  GET {target}?url=http://169.254.169.254/latest/meta-data/",
            ]
    return "\n".join(lines[:12])


def build_user_vuln_directive(user_input: str) -> str:
    """Backward-compatible alias for explicit vulnerability hint extraction."""
    return extract_user_vuln_hint(user_input)
