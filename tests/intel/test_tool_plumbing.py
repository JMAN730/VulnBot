import pytest

from clawbot.intel.tools import INTEL_TOOL_NAMES, dispatch_intel_tool, intel_tool_schemas


def test_schemas_expose_cve_lookup():
    names = {s["function"]["name"] for s in intel_tool_schemas()}
    assert "cve_lookup" in names


def test_intel_tool_names_match_schemas():
    schema_names = {s["function"]["name"] for s in intel_tool_schemas()}
    assert schema_names == set(INTEL_TOOL_NAMES)


@pytest.mark.asyncio
async def test_dispatch_unknown_tool_returns_structured_error():
    out = await dispatch_intel_tool(agent=None, tool_name="nope", args={})
    assert "[intel_error]" in out


@pytest.mark.asyncio
async def test_dispatch_cve_lookup_stub_is_structured():
    out = await dispatch_intel_tool(agent=None, tool_name="cve_lookup", args={"query": "openssl"})
    # Stub until the CVE plan lands; must be a structured, non-raising result.
    assert isinstance(out, str) and out
