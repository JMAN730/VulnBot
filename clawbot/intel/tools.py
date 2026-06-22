"""Intel tool schemas (OpenAI format) and name->dispatcher routing.

Each real module (cve/osint/topology/compliance/remediation) registers its
async handler in ``_HANDLERS`` as its port lands. Until then, a tool's handler
is a structured stub so the dispatch path is testable end-to-end.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable

# Read-only tools the constraint policy may treat as passive: no egress to the
# target, no host-changing action.
READ_ONLY_INTEL_TOOLS: set[str] = {"cve_lookup", "compliance_map", "remediation_advice"}


def intel_tool_schemas() -> list[dict[str, Any]]:
    """OpenAI tool schemas for all intel tools."""
    return [
        {
            "type": "function",
            "function": {
                "name": "cve_lookup",
                "description": (
                    "Look up CVEs by keyword or CVE-ID against NVD, with optional "
                    "exploit-PoC discovery. Read-only; safe to call during recon."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": (
                                "Keyword (e.g. 'openssl 3.0') or a CVE-ID "
                                "(e.g. CVE-2024-3094)."
                            ),
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results.",
                            "default": 5,
                        },
                    },
                    "required": ["query"],
                },
            },
        },
    ]


INTEL_TOOL_NAMES: list[str] = [s["function"]["name"] for s in intel_tool_schemas()]


async def _stub(tool_name: str, args: dict[str, Any]) -> str:
    return f"[intel_pending] {tool_name} is not yet implemented in this build."


def _build_handlers() -> dict[str, Callable[[Any, dict[str, Any]], Awaitable[str]]]:
    """Map tool name -> async handler. Each ported module registers here."""
    from clawbot.intel.cve import cve_lookup_tool

    return {
        "cve_lookup": cve_lookup_tool,
    }


# Handlers are filled in by each module's port. Tools in the schema list without
# a handler fall back to a structured stub so dispatch stays testable.
_HANDLERS: dict[str, Callable[[Any, dict[str, Any]], Awaitable[str]]] = _build_handlers()


async def dispatch_intel_tool(agent: Any, tool_name: str, args: dict[str, Any]) -> str:
    """Route an intel tool call to its handler; structured error on unknown name."""
    if tool_name not in INTEL_TOOL_NAMES:
        return f"[intel_error] unknown intel tool: {tool_name}"
    handler = _HANDLERS.get(tool_name)
    if handler is None:
        return await _stub(tool_name, args)
    return await handler(agent, args)
