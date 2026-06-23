"""VulnBot MCP Router - route natural language intents to MCP tool calls."""

from __future__ import annotations

import re
from typing import Any, Optional

INTENT_TOOL_MAP: dict[str, list[dict[str, Any]]] = {
    # Browser automation
    "open page|open url|visit url|visit page|navigate|browse": [
        {"tool": "new_page", "server": "chrome-devtools"},
        {"tool": "navigate", "server": "chrome-devtools"},
    ],
    "screenshot|capture screen|screen capture": [
        {"tool": "screenshot", "server": "chrome-devtools"},
    ],
    "execute js|eval js|run javascript|evaluate javascript": [
        {"tool": "evaluate_js", "server": "chrome-devtools"},
    ],
    # HTTP requests
    "send request|http request|fetch|call api|request endpoint": [
        {"tool": "fetch", "server": "fetch"},
        {"tool": "send_http1_request", "server": "burp"},
    ],
    # Burp Suite
    "proxy history|inspect request|intercept request|proxy": [
        {"tool": "get_proxy_history", "server": "burp"},
    ],
    "modify request|replay|tamper|resend request": [
        {"tool": "send_http1_request", "server": "burp"},
    ],
    # Memory
    "remember|record|save memory": [
        {"tool": "save", "server": "memory"},
    ],
    "recall|retrieve memory|lookup memory": [
        {"tool": "retrieve", "server": "memory"},
    ],
}


class MCPRouter:
    """Routes natural language intents to MCP tool calls."""

    def route(self, user_input: str) -> list[dict[str, Any]]:
        """Analyze user input and return suggested tool calls."""
        input_lower = user_input.lower()
        results = []

        for pattern, tools in INTENT_TOOL_MAP.items():
            keywords = pattern.split("|")
            if any(kw in input_lower for kw in keywords):
                for tool_entry in tools:
                    results.append(
                        {
                            "tool": tool_entry["tool"],
                            "server": tool_entry["server"],
                            "confidence": 0.8,
                        }
                    )

        return results

    def extract_url(self, text: str) -> Optional[str]:
        """Extract URL from text."""
        url_match = re.search(r"(https?://\S+)", text)
        return url_match.group(1) if url_match else None

    def extract_ip(self, text: str) -> Optional[str]:
        """Extract IP address from text."""
        ip_match = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", text)
        return ip_match.group(1) if ip_match else None

    def suggest_tools_for_phase(self, phase: str) -> list[dict[str, Any]]:
        """Suggest tools based on pentest phase."""
        phase_key = phase.strip().lower().replace("_", " ")
        phase_tools = {
            "recon": [
                {"tool": "fetch", "server": "fetch", "reason": "Probe the target over HTTP"},
                {"tool": "new_page", "server": "chrome-devtools", "reason": "Open the target in a browser"},
                {"tool": "screenshot", "server": "chrome-devtools", "reason": "Capture evidence from the target page"},
            ],
            "reconnaissance": [
                {"tool": "fetch", "server": "fetch", "reason": "Probe the target over HTTP"},
                {"tool": "new_page", "server": "chrome-devtools", "reason": "Open the target in a browser"},
                {"tool": "screenshot", "server": "chrome-devtools", "reason": "Capture evidence from the target page"},
            ],
            "vulnerability discovery": [
                {"tool": "fetch", "server": "fetch", "reason": "Send vulnerability probe requests"},
                {"tool": "send_http1_request", "server": "burp", "reason": "Build detection requests through the proxy"},
            ],
            "exploitation": [
                {"tool": "send_http1_request", "server": "burp", "reason": "Build exploit requests"},
                {"tool": "fetch", "server": "fetch", "reason": "Send exploit payloads"},
                {"tool": "evaluate_js", "server": "chrome-devtools", "reason": "Validate browser-side exploit behavior"},
            ],
        }

        return phase_tools.get(phase_key, [])
