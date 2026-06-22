from clawbot.agent.constraint_policy import infer_tool_action
from clawbot.intel.tools import READ_ONLY_INTEL_TOOLS


def test_read_only_intel_tools_are_recon():
    # Read-only intel tools must be classified as passive recon, never as an
    # active scan/exploit action (the default fallback is "scan").
    for tool in READ_ONLY_INTEL_TOOLS:
        assert infer_tool_action(tool, {"query": "x"}) == "recon"


def test_cve_lookup_specifically_is_recon():
    assert infer_tool_action("cve_lookup", {"query": "openssl"}) == "recon"
