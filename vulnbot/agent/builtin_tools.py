"""Agent built-in tools and OpenAI tool schema helpers."""

from __future__ import annotations

import asyncio
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from typing import Any
from urllib.parse import urlparse

from vulnbot.agent.constraint_policy import host_matches_allowed_scope, validate_tool_action
from vulnbot.agent.network_scan import (
    attach_network_scan_to_session,
    build_nmap_command,
    build_nmap_plan,
    deescalate_nmap_argv,
    nmap_failure_needs_deescalation,
    nmap_has_raw_socket_access,
    parse_nmap_xml_structured,
    summarize_network_scan,
    target_is_private_literal,
    without_privileged_nmap_args,
)
from vulnbot.intel.tools import (
    INTEL_TOOL_NAMES,
    dispatch_intel_tool,
    intel_tool_schemas,
)

BLOCKED_PATTERNS: list[str] = [
    r"os\.\s*system\s*\(",
    r"subprocess\.\s*Popen\s*\(",
    r"shutil\.\s*rmtree\s*\(",
    r"__import__\s*\(\s*['\"]os['\"]",
    r"open\s*\(\s*['\"].*vulnbot.*config",
    r"open\s*\(\s*['\"].*\.vulnbot",
]

RESERVED_IP_RANGES: list[tuple[str, str, str]] = [
    ("198.18.0.0", "198.19.255.255", "RFC 2544 benchmarking range"),
    ("10.0.0.0", "10.255.255.255", "RFC 1918 private range"),
    ("172.16.0.0", "172.31.255.255", "RFC 1918 private range"),
    ("192.168.0.0", "192.168.255.255", "RFC 1918 private range"),
    ("127.0.0.0", "127.255.255.255", "RFC 1122 loopback range"),
    ("169.254.0.0", "169.254.255.255", "RFC 3927 link-local range"),
    ("0.0.0.0", "0.255.255.255", "RFC 1122 current-network range"),
    ("224.0.0.0", "239.255.255.255", "RFC 5771 multicast range"),
    ("240.0.0.0", "255.255.255.255", "RFC 1112 reserved range"),
]

SAFE_MODE_PATTERNS: list[str] = [
    r"open\s*\(",
    r"with\s+open\s*\(",
    r"socket\.",
    r"urllib",
    r"http\.client",
    r"ftplib",
    r"smtplib",
    r"requests\.",
    r"import\s+os",
    r"from\s+os\s+import",
    r"import\s+subprocess",
    r"from\s+subprocess\s+import",
    r"import\s+shutil",
    r"from\s+shutil\s+import",
    r"import\s+pathlib",
    r"from\s+pathlib\s+import",
    r"__import__",
]

LAB_MODE_PATTERNS: list[str] = [
    r"import\s+subprocess",
    r"from\s+subprocess\s+import",
    r"os\.\s*system\s*\(",
    r"subprocess\.\s*Popen\s*\(",
    r"shutil\.\s*rmtree\s*\(",
]


async def execute_mcp_tool(agent: Any, tool_name: str, args: dict[str, Any]) -> str:
    """Execute a tool call via MCP manager or built-in tools."""
    session = getattr(agent, "session_state", None)
    constraints = getattr(session, "task_constraints", None)
    if constraints is not None:
        tool_violation = validate_tool_action(tool_name, args, constraints)
        if tool_violation is not None:
            if session is not None and hasattr(session, "add_constraint_violation_event"):
                from vulnbot.agent.constraint_policy import infer_tool_action

                session.add_constraint_violation_event(
                    source="tool",
                    action=infer_tool_action(tool_name, args),
                    tool_name=tool_name,
                    code="tool_action_blocked",
                    severity="high",
                    summary=tool_violation,
                    detail=json.dumps(args, ensure_ascii=False)[:500],
                )
            return f"[constraint_violation] {tool_violation}"

    if tool_name in INTEL_TOOL_NAMES:
        return await dispatch_intel_tool(agent, tool_name, args)

    if tool_name == "python_execute":
        return await execute_python(agent, args)

    if tool_name == "load_skill_reference":
        try:
            from vulnbot.skills.loader import load_skill_reference

            skill_name = args.get("skill_name", "")
            ref_name = args.get("reference_name", "")
            content = load_skill_reference(skill_name, ref_name)
            if content:
                return content
            return f"[!] Reference document not found: {skill_name}/{ref_name}"
        except Exception as e:
            return f"[!] Error loading reference document: {e}"

    if tool_name == "nmap_scan":
        return await execute_nmap(agent, args)

    if tool_name == "crypto_decode":
        try:
            from vulnbot.skills.crypto_tools import execute as crypto_execute

            operation = args.get("operation", "")
            input_str = args.get("input", "")
            kwargs: dict[str, Any] = {}
            for key in ("key", "iv", "shift", "secret", "header", "algorithm"):
                if key in args and args[key]:
                    kwargs[key] = args[key]
                    if key == "shift":
                        kwargs[key] = int(args[key])
            result = crypto_execute(operation=operation, input_str=input_str, **kwargs)
            if result.get("success"):
                return f"[+] {operation} result:\n{result['result']}"
            return f"[!] {operation} failed: {result.get('error', 'unknown error')}"
        except Exception as e:
            return f"[!] Crypto tool execution error: {e}"

    if tool_name == "brute_force_login":
        return await execute_brute_force(agent, args)

    if not agent.mcp_manager:
        return f"[!] MCP manager is not initialized; cannot execute tool: {tool_name}"

    try:
        result = await agent.mcp_manager.call_tool(tool_name, args)
        if isinstance(result, dict):
            if result.get("ok", False):
                content = result.get("content")
                structured = result.get("structured_content")
                summary_parts: list[str] = []
                if content is not None:
                    summary_parts.append(str(content))
                if isinstance(structured, dict) and structured:
                    summary_parts.append(
                        f"[structured] {json.dumps(structured, ensure_ascii=False)}"
                    )
                if summary_parts:
                    return "\n".join(summary_parts)
                return f"[tool:{tool_name}] completed"

            message = str(result.get("message") or "")
            suggestion = str(result.get("suggestion") or "")
            error_type = str(result.get("error_type") or "error")
            if suggestion:
                return f"[{error_type}] {message}\n[suggestion] {suggestion}".strip()
            return f"[{error_type}] {message}".strip()

        return str(result)
    except Exception as e:
        return f"[!] Tool execution error ({tool_name}): {e}"


def enforce_port_constraints(agent: Any, ports: list[int], *, target: str = "") -> str | None:
    """Return a user-facing violation message when requested ports are out of scope."""
    session = getattr(agent, "session_state", None)
    constraints = getattr(session, "task_constraints", None)
    if constraints is None or constraints.is_empty():
        return None

    if constraints.allowed_ports:
        disallowed = [port for port in ports if port not in constraints.allowed_ports]
        if disallowed:
            allowed = ", ".join(str(p) for p in constraints.allowed_ports)
            denied = ", ".join(str(p) for p in disallowed)
            suffix = f" for target {target}" if target else ""
            return f"[constraint_violation] Port(s) {denied} are outside allowed scope [{allowed}]{suffix}."

    blocked = [port for port in ports if port in constraints.blocked_ports]
    if blocked:
        denied = ", ".join(str(p) for p in blocked)
        suffix = f" for target {target}" if target else ""
        return f"[constraint_violation] Port(s) {denied} are blocked by task constraints{suffix}."

    return None


def enforce_host_path_constraints(
    agent: Any, *, host: str = "", path: str = "", target: str = ""
) -> str | None:
    """Return a user-facing violation when host/path are out of scope."""
    session = getattr(agent, "session_state", None)
    constraints = getattr(session, "task_constraints", None)
    if constraints is None or constraints.is_empty():
        return None

    if constraints.allowed_hosts and host and not host_matches_allowed_scope(
        host, constraints.allowed_hosts
    ):
        allowed = ", ".join(constraints.allowed_hosts)
        return f"[constraint_violation] Host {host} is outside allowed scope [{allowed}] for target {target or host}."

    if host and host in constraints.blocked_hosts:
        return f"[constraint_violation] Host {host} is blocked by task constraints for target {target or host}."

    if constraints.allowed_paths and path and path not in constraints.allowed_paths:
        allowed = ", ".join(constraints.allowed_paths)
        return f"[constraint_violation] Path {path} is outside allowed scope [{allowed}] for target {target or host}."

    if path and path in constraints.blocked_paths:
        return f"[constraint_violation] Path {path} is blocked by task constraints for target {target or host}."

    return None


def infer_ports_from_nmap_args(args: dict[str, Any]) -> list[int]:
    """Infer concrete target ports from nmap arguments for constraint checks."""
    custom_ports = str(args.get("ports", "") or "").strip()
    scan_type = str(args.get("scan_type", "top_ports") or "top_ports")
    profile = str(args.get("profile", "") or "").strip()

    if custom_ports:
        ports: list[int] = []
        for chunk in custom_ports.split(","):
            chunk = chunk.strip()
            if not chunk:
                continue
            if "-" in chunk:
                start_text, end_text = chunk.split("-", 1)
                try:
                    start = int(start_text)
                    end = int(end_text)
                except ValueError:
                    continue
                if 0 < start <= end <= 65535:
                    ports.extend(range(start, end + 1))
                continue
            try:
                port = int(chunk)
            except ValueError:
                continue
            if 0 < port <= 65535:
                ports.append(port)
        return sorted(set(ports))

    if profile:
        plan = build_nmap_plan(
            profile=profile,
            scan_type=str(args.get("scan_type", "") or ""),
            ports="",
            timing=int(args.get("timing", 3) or 3),
        )
        return infer_ports_from_nmap_args({**args, "ports": plan.ports, "profile": ""})

    if scan_type == "top_ports":
        return []
    return []


def infer_port_from_url(url: str) -> int | None:
    """Infer request port from URL."""
    try:
        parsed = urlparse(url)
    except Exception:
        return None
    if parsed.port:
        return parsed.port
    if parsed.scheme == "https":
        return 443
    if parsed.scheme == "http":
        return 80
    return None


def build_openai_tools(mcp_manager: Any) -> list[dict[str, Any]]:
    """Build OpenAI function calling schema from MCP tools + built-in tools."""
    tools: list[dict[str, Any]] = []

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "load_skill_reference",
                "description": "Load a reference document for a specific Skill to retrieve detailed pentest methodology, workflows, or command references. Use this when the system prompt mentions available reference documents.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "skill_name": {
                            "type": "string",
                            "description": "Skill name, such as client-reverse, web-security-advanced, ai-mcp-security, intranet-pentest-advanced, pentest-tools, rapid-checklist, crypto-toolkit, ctf-web, ctf-crypto, ctf-misc, osint-recon, secknowledge-skill, cve-triage",
                        },
                        "reference_name": {
                            "type": "string",
                            "description": "Reference document filename, such as 02-client-api-reverse-and-burp.md, web-injection.md, encoding-cheatsheet.md",
                        },
                    },
                    "required": ["skill_name", "reference_name"],
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "python_execute",
                "description": (
                    "Execute a Python code snippet for building complex HTTP requests, parsing responses, "
                    "encoding conversions, data processing, batch payload tests, response-difference checks, "
                    "and calculations. Code runs in a restricted environment with a 30 second timeout. "
                    "Preinstalled libraries include requests, beautifulsoup4, pycryptodome, base64, json, and re. "
                    "Important: use this tool for HTTP requests instead of guessing response content."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Python code to execute. Multiline code is supported and can import the standard library plus requests/bs4.",
                        },
                        "purpose": {
                            "type": "string",
                            "description": "Brief execution purpose for audit logs, such as 'build HTTP request to test weak comparison bypass'",
                        },
                    },
                    "required": ["code"],
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "crypto_decode",
                "description": (
                    "Encoding, decoding, hashing, and encryption helper. Use it for base64/hex/URL/HTML/Unicode "
                    "strings, hash calculation, AES/DES decryption, JWT parsing, and similar tasks. "
                    "Important: do not guess decoded output; use this tool for accuracy. "
                    "Supported operations: base64_encode/decode, base32_encode/decode, base58_encode/decode, "
                    "hex_encode/decode, url_encode/decode, html_encode/decode, unicode_encode/decode, "
                    "rot13_encode/decode, caesar_encode/decode, morse_encode/decode, "
                    "md5_hash, sha1_hash, sha256_hash, sha512_hash, "
                    "aes_encrypt/decrypt, jwt_decode/encode, auto_decode"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {"type": "string", "description": "Operation name"},
                        "input": {
                            "type": "string",
                            "description": "Input string to encode, decode, hash, encrypt, or decrypt",
                        },
                        "key": {
                            "type": "string",
                            "description": "Encryption/decryption key for AES/DES, usually 16/24/32 bytes",
                        },
                        "iv": {"type": "string", "description": "AES initialization vector, 16 bytes, optional"},
                        "shift": {
                            "type": "integer",
                            "description": "Caesar cipher shift, default 3; omitted decode shift brute-forces all shifts",
                        },
                        "secret": {"type": "string", "description": "JWT signing secret"},
                    },
                    "required": ["operation", "input"],
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "nmap_scan",
                "description": (
                    "nmap network port scanner. Use during recon to discover open ports, service versions, "
                    "and OS fingerprints.\n"
                    "Examples:\n"
                    "  Common ports: scan_type=top_ports, target=1.2.3.4\n"
                    "  SYN scan: scan_type=syn, target=1.2.3.4 (administrator/root may be required)\n"
                    "  Service detection: scan_type=service, target=1.2.3.4\n"
                    "  Vulnerability scripts: scan_type=vuln, target=1.2.3.4\n"
                    "  Full scan: scan_type=full, target=1.2.3.4\n"
                    "Prefer nmap_scan over ad hoc socket scanning in python_execute."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target": {
                            "type": "string",
                            "description": "Target IP address or domain, required; e.g. 192.168.1.1 or scanme.nmap.org",
                        },
                        "scan_type": {
                            "type": "string",
                            "description": "Scan type: top_ports/syn/tcp/service/os/vuln/full",
                        },
                        "ports": {
                            "type": "string",
                            "description": "Optional ports or range, such as 80,443,8080 or 1-1000",
                        },
                        "timing": {
                            "type": "integer",
                            "description": "Timing template 0-5, default 4; higher is faster but noisier",
                        },
                        "profile": {
                            "type": "string",
                            "description": "Optional network scan profile: adaptive/fast/thorough/stealth. Profiles tune ports, timing, service detection, and safe scripts.",
                        },
                    },
                    "required": ["target"],
                },
            },
        }
    )

    tools.append(
        {
            "type": "function",
            "function": {
                "name": "brute_force_login",
                "description": (
                    "Brute-force a login form. Automatically manages session cookies, extracts and updates "
                    "CSRF tokens, and determines login success/failure. Completes all password attempts in one "
                    "call and returns per-password results."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "Login page URL",
                        },
                        "username_field": {
                            "type": "string",
                            "description": "Username field name, such as 'username'",
                        },
                        "password_field": {
                            "type": "string",
                            "description": "Password field name, such as 'password'",
                        },
                        "csrf_field": {
                            "type": "string",
                            "description": "CSRF token field name, such as 'user_token'",
                        },
                        "username": {
                            "type": "string",
                            "description": "Username to test",
                        },
                        "passwords": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Passwords to try, max 20",
                        },
                        "success_keyword": {
                            "type": "string",
                            "description": "Keyword expected after successful login, such as 'Welcome' or 'Dashboard'",
                        },
                        "failure_keyword": {
                            "type": "string",
                            "description": "Keyword expected after failed login, such as 'Login failed'",
                        },
                        "submit_action": {
                            "type": "string",
                            "description": "Optional form submission URL; extracted from form action if omitted",
                        },
                        "extra_data": {
                            "type": "object",
                            "description": "Additional form fields, such as {\"Login\": \"Login\"}",
                        },
                    },
                    "required": ["url", "password_field", "passwords"],
                },
            },
        }
    )

    if mcp_manager:
        for schema in mcp_manager.get_tool_schemas():
            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": schema.get("name", ""),
                        "description": schema.get("description", ""),
                        "parameters": schema.get(
                            "inputSchema", {"type": "object", "properties": {}}
                        ),
                    },
                }
            )

    tools.extend(intel_tool_schemas())

    return tools


async def execute_nmap(agent: Any, args: dict[str, Any]) -> str:
    target = args.get("target", "").strip()
    if not target:
        return "[!] nmap_scan requires the target parameter (IP address or domain)"

    host_violation = enforce_host_path_constraints(agent, host=target.lower(), target=target)
    if host_violation:
        return host_violation

    violation = enforce_port_constraints(agent, infer_ports_from_nmap_args(args), target=target)
    if violation:
        return violation

    try:
        ips = socket.getaddrinfo(target, None, socket.AF_INET)
        if ips:
            ip = ips[0][4][0]
            is_reserved, reason = is_reserved_ip(ip)
            if is_reserved and not target_is_private_literal(target):
                return (
                    f"[SKIP] Target {target} resolves to a reserved/private address ({reason}, IP: {ip})\n"
                    f"Skipping nmap scan. Prefer web fingerprinting, directory enumeration, or other "
                    f"application-layer recon instead of spending rounds on reserved addresses."
                )
    except Exception:
        pass

    scan_type = args.get("scan_type", "top_ports")
    custom_ports = args.get("ports", "")
    timing = int(args.get("timing", 4))
    profile = str(args.get("profile", "") or "").strip().lower()

    nmap_cmd = shutil.which("nmap")
    if not nmap_cmd:
        try:
            result = subprocess.run(
                ["where.exe", "nmap"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                nmap_cmd = result.stdout.strip().split("\n")[0]
        except Exception:
            pass
    if not nmap_cmd:
        return "[!] nmap is not installed or not in PATH. Install nmap and ensure it is on the system PATH."

    if profile:
        plan = build_nmap_plan(
            profile=profile,
            scan_type=str(scan_type or ""),
            ports=str(custom_ports or ""),
            timing=timing,
            prior_recon=getattr(getattr(agent, "session_state", None), "recon_data", {}),
        )
        privileged = nmap_has_raw_socket_access()
        cmd = build_nmap_command(nmap_cmd, target, plan, privileged=privileged)
        deescalated_note = (
            ""
            if privileged or plan.args == without_privileged_nmap_args(plan.args)
            else "[i] Running without root: skipped OS fingerprinting (-O) and downgraded SYN scan to connect scan (-sT).\n"
        )
    else:
        plan = None
        privileged = nmap_has_raw_socket_access()
        deescalated_note = ""
        cmd = [nmap_cmd, "-v" if scan_type == "full" else "-q", f"-T{max(0, min(5, timing))}"]
        if scan_type == "top_ports":
            cmd.extend(["--top-ports", "100", "-oX", "-"])
        elif scan_type == "syn":
            cmd.extend(["-sS" if privileged else "-sT", "-oX", "-"])
            if not privileged:
                deescalated_note = "[i] Running without root: using connect scan (-sT) instead of SYN scan (-sS).\n"
        elif scan_type == "tcp":
            cmd.extend(["-sT", "-oX", "-"])
        elif scan_type == "service":
            cmd.extend(["-sV", "-oX", "-"])
        elif scan_type == "os":
            if privileged:
                cmd.extend(["-O", "-oX", "-"])
            else:
                cmd.extend(["-sV", "-oX", "-"])
                deescalated_note = (
                    "[i] Running without root: OS fingerprinting (-O) unavailable; "
                    "using service detection (-sV) instead.\n"
                )
        elif scan_type == "vuln":
            cmd.extend(["--script", "vuln", "-oX", "-"])
        elif scan_type == "full":
            if privileged:
                cmd.extend(["-sS", "-O", "-sV", "--script", "default,safe", "-oX", "-"])
            else:
                cmd.extend(["-sT", "-sV", "--script", "default,safe", "-oX", "-"])
                deescalated_note = (
                    "[i] Running without root: skipped OS fingerprinting (-O) and "
                    "downgraded SYN scan to connect scan (-sT).\n"
                )
        else:
            cmd.extend(["-sV", "-oX", "-"])

        if custom_ports:
            cmd.extend(["-p", custom_ports])
        cmd.append(target)

    try:
        kwargs: dict[str, Any] = {
            "capture_output": True,
            "text": True,
            "encoding": "utf-8",
            "errors": "replace",
            "timeout": 120,
        }
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            kwargs["startupinfo"] = startupinfo
        result = subprocess.run(cmd, **kwargs)
        if (
            result.returncode != 0
            and not result.stdout
            and nmap_failure_needs_deescalation(result.stderr or "")
        ):
            fallback_cmd = deescalate_nmap_argv(cmd)
            if fallback_cmd != cmd:
                fallback = subprocess.run(fallback_cmd, **kwargs)
                if fallback.returncode == 0 or fallback.stdout:
                    result = fallback
                    deescalated_note = (
                        "[i] Retried without privileged nmap flags after permission error.\n"
                    )
    except subprocess.TimeoutExpired:
        return "[!] nmap scan timed out (120s); reduce scan scope or use faster timing"
    except PermissionError:
        return "[!] nmap execution was denied due to insufficient permissions. On Windows, run the terminal as administrator."
    except Exception as e:
        return f"[!] nmap execution error: {e}"

    if result.returncode != 0 and not result.stdout:
        return f"[!] nmap scan failed ({result.returncode}): {result.stderr[:500]}"
    output = result.stdout or result.stderr
    human_summary = parse_nmap_xml(output, target)
    structured = parse_nmap_xml_structured(output, target)
    if getattr(agent, "session_state", None) is not None:
        attach_network_scan_to_session(
            agent.session_state,
            structured,
            profile=profile or str(scan_type or "top_ports"),
            safe_probes=profile != "vuln",
        )
    if profile:
        network_summary = summarize_network_scan(structured)
        return f"{deescalated_note}{human_summary}\n\n{network_summary}"
    return f"{deescalated_note}{human_summary}"


def is_reserved_ip(ip: str) -> tuple[bool, str]:
    try:
        import ipaddress

        addr = ipaddress.ip_address(ip)
        for start, end, desc in RESERVED_IP_RANGES:
            if ipaddress.ip_address(start) <= addr <= ipaddress.ip_address(end):
                return True, desc
        return False, ""
    except Exception:
        return False, ""


def validate_scan_target(target: str) -> str:
    try:
        ips = socket.getaddrinfo(target, None, socket.AF_INET)
        if not ips:
            return ""
        ip = ips[0][4][0]
        is_reserved, reason = is_reserved_ip(ip)
        if is_reserved:
            return (
                f"\n\n[!] **Warning: target {target} resolves to a reserved/private address ({reason})\n"
                f"   IP: {ip}\n"
                f"   Scanning this address does not represent the security state of a real external system.\n"
                f"   Ports in the nmap result may be unrelated to the intended target.**"
            )
    except Exception:
        pass
    return ""


def parse_nmap_xml(xml_output: str, target: str) -> str:
    if not xml_output or "<nmaprun" not in xml_output:
        lines = xml_output.strip().splitlines()[:80]
        return "nmap raw output:\n" + "\n".join(lines)

    try:
        root = ET.fromstring(xml_output)
    except ET.ParseError:
        lines = xml_output.strip().splitlines()[:80]
        return "nmap raw output:\n" + "\n".join(lines)

    lines = [f"nmap scan results - {target}", "=" * 60]
    for host in root.findall(".//host"):
        hostname = host.find(".//hostname[@type='user']")
        addrs = [a.get("addr", "") for a in host.findall("address")]
        status = host.find("status")
        status_val = status.get("state", "unknown") if status is not None else "unknown"
        host_ip = addrs[0] if addrs else target
        reserved, reason = is_reserved_ip(host_ip)
        if reserved:
            host_str = (
                f"\n[Host] {host_ip} [!] **Reserved address ({reason}); test-network results do not represent real target security state**"
            )
        else:
            host_str = f"\n[Host] {host_ip}"
        if hostname is not None:
            host_str += f" ({hostname.get('name', '')})"
        host_str += f" - {status_val}"
        lines.append(host_str)

        for port in host.findall(".//port"):
            port_id = port.get("portid", "")
            proto = port.get("protocol", "tcp")
            port_state = port.find("state")
            svc = port.find("service")
            state_val = port_state.get("state", "unknown") if port_state is not None else "unknown"
            svc_name = svc.get("name", "") if svc is not None else ""
            svc_product = svc.get("product", "") if svc is not None else ""
            svc_version = svc.get("version", "") if svc is not None else ""
            lines.append(
                f"  {proto.upper():5} {port_id}/{'s' if svc is not None and svc.get('tunnel') == 'ssl' else ''} "
                f"{state_val:8}{svc_name:15}{(svc_product + ' ' + svc_version).rstrip()}"
            )
            for script in port.findall("script"):
                lines.append(f"    | {script.get('id', '')}: {script.get('output', '')[:120]}")

    runstats = root.find(".//runstats")
    if runstats is not None:
        finished = runstats.find("finished")
        if finished is not None:
            elapsed = finished.get("elapsed", "")
            summary = finished.get("summary", "")
            lines.append(f"\nFinished in: {elapsed}s | {summary}")
    return "\n".join(lines) or f"nmap scan completed with no output: {target}"


def _resolve_python_execute_mode(agent: Any) -> str:
    safety = getattr(agent.config, "safety", None)
    if safety is None:
        return "trusted-local"

    mode = str(getattr(safety, "python_execute_mode", "") or "").strip().lower()
    if not mode and getattr(safety, "python_execute_restricted", False):
        return "safe"
    if mode in {"safe", "lab", "trusted-local"}:
        return mode
    return "trusted-local"


def _validate_python_execute_mode(mode: str, code: str) -> str | None:
    patterns = SAFE_MODE_PATTERNS if mode == "safe" else LAB_MODE_PATTERNS if mode == "lab" else []
    for pattern in patterns:
        if re.search(pattern, code, re.IGNORECASE):
            return pattern
    return None


def _write_python_audit(
    agent: Any,
    *,
    purpose: str,
    code: str,
    mode: str,
    outcome: str,
    blocked_reason: str = "",
) -> None:
    safety = getattr(agent.config, "safety", None)
    if safety is None or not getattr(safety, "python_execute_audit_enabled", True):
        return

    try:
        from datetime import datetime

        from vulnbot.config.settings import PYTHON_EXECUTE_AUDIT_FILE, ensure_dirs

        ensure_dirs()
        record = {
            "timestamp": datetime.now().isoformat(),
            "target": getattr(getattr(agent, "session_state", None), "target", None),
            "mode": mode,
            "purpose": purpose,
            "outcome": outcome,
            "blocked_reason": blocked_reason,
            "code_preview": code[:300],
            "code_lines": code.count("\n") + 1,
        }
        with open(PYTHON_EXECUTE_AUDIT_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        return


async def execute_python(agent: Any, args: dict[str, Any]) -> str:
    code = args.get("code", "")
    purpose = args.get("purpose", "")
    if not code.strip():
        return "[!] Code is empty; nothing executed"

    url_matches = re.findall(r"https?://([a-zA-Z0-9._:-]+)(/[^\s'\"`]*)?", code)
    for host, path in url_matches:
        host_violation = enforce_host_path_constraints(
            agent,
            host=host.lower(),
            path=(path or "").rstrip("/"),
            target=host,
        )
        if host_violation:
            return host_violation

    safety = getattr(agent.config, "safety", None)
    if safety is None or not safety.enable_python_execute:
        return (
            "[!] python_execute is disabled. Set safety.enable_python_execute = true to enable it"
        )

    mode = _resolve_python_execute_mode(agent)
    max_lines = getattr(safety, "python_execute_max_lines", 50)
    if code.count("\n") + 1 > max_lines:
        _write_python_audit(
            agent,
            purpose=purpose,
            code=code,
            mode=mode,
            outcome="blocked",
            blocked_reason="max_lines",
        )
        return f"[!] Code exceeds the max line limit ({max_lines})"

    show_warning = getattr(safety, "python_execute_show_warning", True)
    warning_prefix = ""
    if show_warning:
        warning_prefix = (
            f"[!] Security warning: python_execute runs local Python code in {mode} mode.\n"
            "Review the code carefully before execution.\n"
            "---\n"
        )

    recon_keywords = ["recon", "crawl", "spider", "scan", "enum", "probe"]
    timeout_seconds = 60 if any(kw in purpose.lower() for kw in recon_keywords) else 30

    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, code):
            _write_python_audit(
                agent,
                purpose=purpose,
                code=code,
                mode=mode,
                outcome="blocked",
                blocked_reason=pattern,
            )
            return f"[!] Code contains a blocked operation pattern: {pattern}"

    blocked_pattern = _validate_python_execute_mode(mode, code)
    if blocked_pattern:
        _write_python_audit(
            agent,
            purpose=purpose,
            code=code,
            mode=mode,
            outcome="blocked",
            blocked_reason=blocked_pattern,
        )
        if mode == "safe":
            return f"[!] safe mode blocked operation: {blocked_pattern}"
        return f"[!] lab mode blocked operation: {blocked_pattern}"

    max_output_chars = getattr(safety, "python_execute_max_output_chars", 8000)
    tmp_path = ""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            preamble = (
                "import sys, json, re, os, base64, hashlib, itertools, collections, datetime, struct, binascii, textwrap\n"
                "try:\n    import requests\nexcept ImportError:\n    pass\n"
                "try:\n    from bs4 import BeautifulSoup\nexcept ImportError:\n    pass\n"
                "try:\n    from Crypto.Cipher import AES\nexcept ImportError:\n    pass\n\n"
            )
            f.write(preamble)
            f.write(code)
            tmp_path = f.name

        base_env = {"PYTHONIOENCODING": "utf-8"}
        env = {**os.environ, **base_env} if mode == "trusted-local" else base_env

        proc = await asyncio.create_subprocess_exec(
            sys.executable,
            tmp_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=tempfile.gettempdir(),
            env=env,
        )
        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(), timeout=timeout_seconds
            )
        except asyncio.TimeoutError:
            try:
                proc.kill()
            except ProcessLookupError:
                pass
            await proc.wait()
            raise

        try:
            os.unlink(tmp_path)
        except OSError:
            pass

        output_parts: list[str] = []
        stdout_text = stdout_bytes.decode("utf-8", errors="replace") if stdout_bytes else ""
        stderr_text = stderr_bytes.decode("utf-8", errors="replace") if stderr_bytes else ""
        if stdout_text:
            output_parts.append(stdout_text)
        if stderr_text:
            stderr_lines = [
                line
                for line in stderr_text.splitlines()
                if "ImportError" not in line and "No module named" not in line
            ]
            if stderr_lines:
                output_parts.append("[stderr]\n" + "\n".join(stderr_lines))

        if not output_parts:
            _write_python_audit(agent, purpose=purpose, code=code, mode=mode, outcome="success")
            return f"{warning_prefix}[+] Python executed successfully with no output"

        output = "\n".join(output_parts)
        for sig in ["[DONE]", "[COMPLETE]"]:
            output = output.replace(sig, f"[BLOCKED_{sig[1:-1]}]")
        if len(output) > max_output_chars:
            clip = max_output_chars // 2
            output = output[:clip] + "\n...[truncated]...\n" + output[-clip:]
        _write_python_audit(agent, purpose=purpose, code=code, mode=mode, outcome="success")
        return f"{warning_prefix}[+] Python execution result ({mode}):\n{output}"
    except (subprocess.TimeoutExpired, asyncio.TimeoutError):
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        agent.runtime.python_timeout_rounds += 1
        _write_python_audit(agent, purpose=purpose, code=code, mode=mode, outcome="timeout")
        return f"[!] Python execution timed out after {timeout_seconds} seconds"
    except Exception as e:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        _write_python_audit(
            agent, purpose=purpose, code=code, mode=mode, outcome="error", blocked_reason=str(e)
        )
        return f"[!] Python execution error: {e}"


def _sync_cookies_to_shared_jar(
    agent: Any, cookies: list[tuple[str, str, str, str]]
) -> None:
    """Copy session cookies into the agent's shared _fetch_cookies jar.

    This allows the ``fetch`` tool (which uses ``_fetch_cookies``) to
    immediately use the authenticated session obtained by
    ``brute_force_login`` without requiring a separate re-login.
    """
    if not agent or not cookies:
        return
    mcp = getattr(agent, "mcp_manager", None)
    if not mcp:
        return
    try:
        import httpx

        jar = getattr(mcp, "_fetch_cookies", None)
        if jar is None:
            jar = httpx.Cookies()
            mcp._fetch_cookies = jar
        for name, value, domain, path in cookies:
            if name and value:
                jar.set(name, value, domain=domain or "", path=path or "/")
    except Exception:
        pass


async def execute_brute_force(agent: Any, args: dict[str, Any]) -> str:
    """Execute a login brute-force with automatic CSRF/session management.

    Handles the full flow in one call:
    GET login page -> extract CSRF + session -> POST passwords -> detect result
    """
    import asyncio
    import re
    import time

    url = str(args.get("url", "") or "").strip()
    password_field = str(args.get("password_field", "") or "").strip()
    csrf_field = str(args.get("csrf_field", "") or "").strip()
    username_field = str(args.get("username_field", "") or "").strip()
    username = str(args.get("username", "") or "").strip()
    passwords = args.get("passwords", [])
    success_keyword = str(args.get("success_keyword", "") or "").strip()
    failure_keyword = str(args.get("failure_keyword", "") or "").strip()
    submit_action = str(args.get("submit_action", "") or "").strip()
    extra_data = args.get("extra_data", {}) or {}
    submit_url = submit_action or url

    if not url or not password_field or not passwords:
        return "[!] Missing required parameters: url, password_field, passwords"

    if not isinstance(passwords, list) or not passwords:
        return "[!] passwords must be a non-empty list"

    passwords = passwords[:20]
    total = len(passwords)

    try:
        import httpx
    except ImportError:
        return "[!] httpx is not installed; cannot run brute-force login"

    def extract_csrf(html: str, field_name: str) -> str | None:
        """Extract CSRF token from HTML input field."""
        if not field_name:
            return None
        pattern = re.compile(
            rf'name=["\']{re.escape(field_name)}["\'][^>]*value=["\']([^"\']+)',
            re.IGNORECASE,
        )
        m = pattern.search(html)
        if m:
            return m.group(1)
        # Try alternative: value before name
        pattern2 = re.compile(
            rf'value=["\']([^"\']+)[^>]*name=["\']{re.escape(field_name)}',
            re.IGNORECASE,
        )
        m = pattern2.search(html)
        return m.group(1) if m else None

    results: list[str] = []
    start_time = time.time()
    attempts = 0
    found_password: str | None = None

    # Collect cookies from the internal client so we can sync them
    # back to the shared _fetch_cookies jar after a successful login.
    session_cookies: list[tuple[str, str, str, str]] = []  # name, value, domain, path

    async with httpx.AsyncClient(
        verify=False,
        timeout=30.0,
        follow_redirects=True,
    ) as client:
        # Step 1: Get login page for initial CSRF and session
        try:
            resp = await asyncio.wait_for(
                client.get(url),
                timeout=30.0,
            )
            html = resp.text
        except Exception as e:
            return f"[!] Failed to fetch login page: {e}"

        csrf_token = extract_csrf(html, csrf_field)
        if csrf_token is None and csrf_field:
            results.append(f"[!] Warning: CSRF field '{csrf_field}' was not found on the login page")

        # Auto-detect submit button values from login page HTML.
        # Many forms (DVWA, etc.) check isset($_POST['SubmitButtonName'])
        # before processing authentication. Without the button's name=value,
        # the server skips auth and just re-renders the page.
        auto_fields: dict[str, str] = {}
        for input_match in re.finditer(
            r'<(?:input|button)\s[^>]*type=["\']submit["\'][^>]*>',
            html,
            re.IGNORECASE,
        ):
            tag = input_match.group()
            name_m = re.search(r'name\s*=\s*["\']([^"\']+)["\']', tag, re.IGNORECASE)
            val_m = re.search(r'value\s*=\s*["\']([^"\']*)["\']', tag, re.IGNORECASE)
            if name_m:
                auto_fields[name_m.group(1)] = val_m.group(1) if val_m else name_m.group(1)

        # Step 2: Try each password
        for i, password in enumerate(passwords, 1):
            form_data: dict[str, str] = {}
            if username_field and username:
                form_data[username_field] = username
            form_data[password_field] = password
            if csrf_token and csrf_field:
                form_data[csrf_field] = csrf_token
            # Auto-detected submit buttons come first so they can be
            # overridden by explicit extra_data if needed.
            form_data.update(auto_fields)
            form_data.update({k: str(v) for k, v in extra_data.items()})

            try:
                resp = await asyncio.wait_for(
                    client.post(submit_url, data=form_data),
                    timeout=30.0,
                )
                attempts += 1
                response_html = resp.text
                status = resp.status_code

                # Determine success or failure
                is_success = False
                reason = ""
                csrf_markers = ["csrf token is incorrect", "csrf token mismatch",
                                "token mismatch", "invalid token"]

                if success_keyword and success_keyword.lower() in response_html.lower():
                    is_success = True
                    reason = f"'{success_keyword}'"
                elif failure_keyword and failure_keyword.lower() in response_html.lower():
                    is_success = False
                    reason = f"'{failure_keyword}'"
                elif any(m in response_html.lower() for m in csrf_markers):
                    is_success = False
                    reason = "CSRF token error (new token synchronized automatically)"
                elif status == 302:
                    is_success = True
                    reason = "Status 302 (redirect)"
                elif "logout" in response_html.lower() or "welcome" in response_html.lower():
                    is_success = True
                    reason = "Detected authenticated state"
                else:
                    # Include a short snippet from the response so the model
                    # can diagnose what the server actually returned.
                    snippet = response_html.strip()[:200].replace("\n", " ")
                    is_success = False
                    reason = snippet

                prefix = "[+]" if is_success else "[-]"
                pw_preview = password[:40].replace("\n", "\\n")
                results.append(f"{prefix} {pw_preview} -> {'success' if is_success else 'failure'} ({reason})")

                # Extract new CSRF from response for next attempt
                new_token = extract_csrf(response_html, csrf_field)
                if new_token:
                    csrf_token = new_token

                # Stop early on success if keyword matched
                if is_success and success_keyword:
                    found_password = password
                    break

            except Exception as e:
                pw_preview = password[:30].replace("\n", "\\n")
                results.append(f"[!] {pw_preview} -> request failed: {e}")
                continue

        # Save cookies from the internal client for potential sharing with
        # the fetch tool's cookie jar.
        try:
            for cookie in client.cookies.jar:
                session_cookies.append(
                    (cookie.name, cookie.value, cookie.domain, cookie.path)
                )
        except Exception:
            pass

    elapsed = time.time() - start_time

    # Sync session cookies to the shared _fetch_cookies jar so that
    # subsequent `fetch` calls from the agent are already authenticated.
    if found_password and session_cookies:
        _sync_cookies_to_shared_jar(agent, session_cookies)

    summary = [
        f"[+] Brute force completed - {url}",
        f"    User: {username or '(not specified)'}",
        "",
        "    Results:",
    ]
    for r in results:
        summary.append(f"    {r}")
    summary.append("")
    summary.append(f"    Elapsed: {elapsed:.1f}s")
    summary.append(f"    Attempts: {attempts}/{total}")

    return "\n".join(summary)
