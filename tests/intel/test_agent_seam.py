import pytest

from clawbot.agent import builtin_tools as bt


def test_builder_includes_intel_schemas():
    schemas = bt.build_openai_tools(mcp_manager=None)
    names = {s["function"]["name"] for s in schemas}
    assert "cve_lookup" in names


@pytest.mark.asyncio
async def test_execute_routes_intel_tool():
    out = await bt.execute_mcp_tool(agent=_FakeAgent(), tool_name="cve_lookup", args={"query": "x"})
    assert isinstance(out, str) and out


class _FakeAgent:
    session_state = None
