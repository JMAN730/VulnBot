"""Recon dimension tracking helpers for AgentCore."""

from __future__ import annotations

from typing import Any

RECON_MIN_ROUNDS = 8  # Minimum recon rounds before [DONE] is accepted.

# Include both tool-result signatures and natural-language descriptions from
# notes/confirmed_facts so recon progress survives summarization.
RECON_DIM_KEYWORDS: dict[str, list[str]] = {
    "server": [
        "port",
        "nmap",
        "open",
        "service version",
        "service",
        "real ip",
        "origin ip",
        "cdn",
        "operating system",
        "os detection",
        "ttl",
        "middleware",
        "database",
        "mysql",
        "redis",
        "scan",
        "port scan",
        "ip address",
        "host discovery",
        "live host",
        "apache",
        "nginx",
        "tomcat",
        "iis",
        "jetty",
        "linux",
        "windows",
        "ubuntu",
        "centos",
    ],
    "website": [
        "waf",
        "web application firewall",
        "sensitive directory",
        "directory scan",
        "dirsearch",
        "gobuster",
        "source leak",
        ".git",
        ".svn",
        ".ds_store",
        ".env",
        "backup file",
        ".bak",
        "adjacent host",
        "same ip",
        "same subnet",
        "fingerprint",
        "cms",
        "framework",
        "architecture",
        "technology stack",
        "web fingerprint",
        "website",
        "web",
        "javascript",
        "js file",
        "api endpoint",
        "wordpress",
        "dedecms",
        "phpcms",
        "discuz",
        "login",
        "admin",
        "page",
        "url",
        "directory",
        "file",
    ],
    "domain": [
        "whois",
        "registrant",
        "registrar",
        "icp",
        "subdomain",
        "dns record",
        "cname",
        "mx record",
        "txt record",
        "certificate transparency",
        "crt.sh",
        "certificate information",
        "ssl certificate",
        "domain",
        "dns",
        "registration information",
        "certificate",
    ],
    "personnel": [
        "github_id",
        "followers",
        "following",
        "public_repos",
        "twitter",
        "social engineering",
        "personnel information",
        "author tracking",
        "person profile",
        "employee",
    ],
}


def update_recon_dimension_completion(agent: Any, response: str) -> None:
    """Auto-detect which recon dimensions have been explored.

    The response parameter is kept for call-signature compatibility, but the
    logic intentionally uses notes, confirmed facts, and executed steps instead
    of raw reasoning text.
    """
    del response
    note_text = " ".join(agent.context.state.notes[-15:]).lower()
    fact_text = " ".join(getattr(agent.context.state, "confirmed_facts", [])[-15:]).lower()
    step_text = " ".join(agent.context.state.executed_steps[-15:]).lower()

    for dim, keywords in RECON_DIM_KEYWORDS.items():
        if dim == "personnel":
            if not agent.context.state.recon_dimension4_active:
                continue
            source_text = fact_text
        else:
            source_text = f"{fact_text} {note_text} {step_text}"

        if not source_text.strip():
            continue

        if not agent.context.state.recon_dimensions_completed.get(dim, False):
            if any(kw.lower() in source_text for kw in keywords):
                agent.context.state.mark_recon_dimension(dim)
