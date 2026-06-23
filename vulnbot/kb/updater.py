"""VulnBot Knowledge Updater - update and seed the knowledge base."""

from __future__ import annotations

from vulnbot.kb.store import KnowledgeStore


def seed_knowledge_base(store: KnowledgeStore) -> None:
    """Seed the knowledge base with essential security knowledge."""
    cves = [
        {
            "id": "CVE-2026-21858",
            "title": "n8n Arbitrary File Read via Public Form",
            "description": "n8n versions >= 1.65.0 and < 1.121.0 allow unauthenticated "
            "arbitrary file read through public form submission endpoints when "
            "a workflow contains a Form Ending node returning a binary file.",
            "severity": "Critical",
            "affected": "n8n >= 1.65.0, < 1.121.0",
            "tags": ["n8n", "file-read", "rce", "critical"],
            "exploitation_steps": [
                "Identify a public form path on the n8n instance",
                "Send a POST request with a forged files object containing filepath",
                "Read server files such as /etc/passwd, config files, or databases",
                "Extract encryption material from configuration files",
                "Use recovered credentials to authenticate where authorized",
                "Create a controlled workflow proof-of-concept to validate RCE impact",
            ],
            "remediation": "Upgrade to n8n >= 1.121.0.",
        },
        {
            "id": "CVE-2025-68613",
            "title": "n8n Authenticated Expression Injection RCE",
            "description": "Authenticated expression injection in n8n allows remote code "
            "execution through malicious workflow expressions.",
            "severity": "Critical",
            "affected": "n8n >= 0.211.0, < 1.120.4",
            "tags": ["n8n", "rce", "expression-injection", "critical"],
            "exploitation_steps": [
                "Authenticate with valid credentials",
                "Create a workflow with manualTrigger and set nodes",
                "Insert an expression payload that invokes a controlled command",
                "Run the workflow",
                "Read the execution result for command output",
            ],
            "remediation": "Upgrade to n8n >= 1.120.4 or >= 1.121.1.",
        },
    ]

    for cve in cves:
        existing = store.get_entry("cve", cve["id"])
        if not existing:
            store.add_entry("cve", cve["id"], cve)

    techniques = [
        {
            "id": "sqli-bypass",
            "title": "SQL Injection Bypass Techniques",
            "description": "Payload construction methods for bypassing SQL injection filters.",
            "tags": ["sqli", "waf-bypass", "web"],
            "bypass_methods": [
                "Mixed case keywords: SeLeCt",
                "Inline comments: S/*!ELECT*/",
                "Double encoding: %2565",
                "Equivalent functions: GROUP_CONCAT instead of concat_ws",
            ],
        },
        {
            "id": "rce-bypass-php",
            "title": "PHP Command Execution Bypass Techniques",
            "description": "Payload construction methods for bypassing PHP command execution filters.",
            "tags": ["rce", "waf-bypass", "php", "web"],
            "bypass_methods": [
                "Base64-decoded function name: $f=base64_decode('c3lzdGVt');$f('id');",
                "String concatenation: $f='sys'.'tem';$f('id');",
                "Split paths: '/va'.'r/ww'.'w/ht'.'ml'",
                "Reversed function name: $f=strrev('metsys');$f('id');",
            ],
        },
        {
            "id": "xss-bypass",
            "title": "XSS Bypass Techniques",
            "description": "Payload construction methods for bypassing WAF and XSS filters.",
            "tags": ["xss", "waf-bypass", "web"],
            "bypass_methods": [
                "Event handlers: <img src=x onerror=alert(1)>",
                "SVG tags: <svg onload=alert(1)>",
                "HTML entity encoding",
                "Unicode encoding",
            ],
        },
        {
            "id": "cmd-injection-bypass",
            "title": "Command Injection Bypass Techniques",
            "description": "Methods for bypassing command injection filters.",
            "tags": ["command-injection", "waf-bypass", "web"],
            "bypass_methods": [
                "Newline separator: id\\nwhoami",
                "Pipe separator: id|whoami",
                "Variable concatenation: a=i;b=d;$a$b",
                "Wildcards: /bin/ca? /etc/pas?d",
            ],
        },
    ]

    for tech in techniques:
        existing = store.get_entry("techniques", tech["id"])
        if not existing:
            store.add_entry("techniques", tech["id"], tech)

    tools = [
        {
            "id": "nmap",
            "title": "Nmap Port Scanning Quick Reference",
            "description": "Common Nmap scan commands and options.",
            "tags": ["nmap", "recon", "scanning"],
            "commands": [
                "nmap -sV -sC -p- TARGET    # full-port scan plus version detection",
                "nmap -sS --top-ports 1000 TARGET   # SYN scan top 1000 ports",
                "nmap --script vuln TARGET   # vulnerability NSE scripts",
                "nmap -sU --top-ports 100 TARGET     # UDP scan",
            ],
        },
        {
            "id": "burp",
            "title": "Burp Suite Workflow",
            "description": "Burp Suite penetration testing workflow.",
            "tags": ["burp", "proxy", "web"],
            "workflow": [
                "Configure the browser proxy to Burp",
                "Browse the target and collect requests",
                "Analyze request parameters and endpoints",
                "Use Intruder for controlled fuzzing",
                "Use Repeater for manual vulnerability validation",
            ],
        },
    ]

    for tool in tools:
        existing = store.get_entry("tools", tool["id"])
        if not existing:
            store.add_entry("tools", tool["id"], tool)
