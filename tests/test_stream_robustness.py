"""streaming behavior tool_calls streaming behavior。

streaming behavior：
- streaming behavior chunk streaming behavior tool_calls streaming behavior（index streaming behavior、arguments streaming behavior）
- function name / arguments streaming behavior chunk streaming behavior
- streaming behavior id streaming behavior（function streaming behavior None）—— provider streaming behavior
- streaming behavior delta / None tc_delta / streaming behavior index streaming behavior
- streaming behavior tool_call（streaming behavior JSON / streaming behavior id / streaming behavior name）streaming behavior
- streaming behavior content streaming behavior
- reasoning_content streaming behavior content streaming behavior
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from vulnbot.agent.llm_client import (
    _assemble_tool_calls,
    _collect_tool_call_deltas,
    _validate_tool_call,
    call_llm_auto_stream,
    call_llm_stream,
)

# === streaming behavior mock streaming behavior（streaming behavior OpenAI streaming behavior delta streaming behavior） ===


class _Func:
    def __init__(self, name=None, arguments=None):
        self.name = name
        self.arguments = arguments


class _TCDelta:
    """streaming behavior tool_call streaming behavior（delta.tool_calls[i]）。"""

    def __init__(self, index=0, id=None, name=None, arguments=None, function="set"):
        self.index = index
        self.id = id
        # function="none" streaming behavior id streaming behavior（streaming behavior provider）
        if function == "none":
            self.function = None
        else:
            self.function = _Func(name=name, arguments=arguments)


class _Delta:
    def __init__(self, content=None, reasoning=None, tool_calls=None):
        self.content = content
        self.reasoning_content = reasoning
        self.tool_calls = tool_calls


class _Choice:
    def __init__(self, delta):
        self.delta = delta


class _Chunk:
    def __init__(self, content=None, reasoning=None, tool_calls=None, choices=None):
        if choices is not None:
            self.choices = choices
        else:
            self.choices = [_Choice(_Delta(content=content, reasoning=reasoning, tool_calls=tool_calls))]


class _SyncStream:
    def __init__(self, chunks):
        self._chunks = chunks

    def __iter__(self):
        return iter(self._chunks)


class _BreakingStream:
    """streaming behavior chunk，streaming behavior。"""

    def __init__(self, chunks, exc):
        self._chunks = list(chunks)
        self._exc = exc

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._chunks:
            return self._chunks.pop(0)
        raise self._exc


class SpySink:
    def __init__(self):
        self.calls: list[tuple[str, str]] = []

    def on_status(self, message):
        self.calls.append(("status", message))

    def on_thinking_token(self, token):
        self.calls.append(("thinking", token))

    def on_content_token(self, token):
        self.calls.append(("content", token))

    def on_tool_call(self, tool_name, args):
        self.calls.append(("tool_call", f"{tool_name}:{args}"))

    def on_tool_result(self, result_summary):
        self.calls.append(("tool_result", result_summary))

    def on_stream_end(self):
        self.calls.append(("end", ""))


def _make_agent():
    agent = MagicMock()
    mock_client = MagicMock()
    agent._get_client.return_value = mock_client
    agent.config.llm.provider = "openai"
    agent.config.llm.model = "gpt-4"
    agent.config.llm.max_tokens = None
    agent.config.llm.temperature = None
    agent.config.llm.max_context_tokens = None
    agent.context.get_messages.return_value = []
    agent._build_openai_tools.return_value = []
    return agent, mock_client


# === _collect_tool_call_deltas streaming behavior ===


class TestCollectToolCallDeltas:
    def test_none_delta_tool_calls(self):
        """delta.tool_calls streaming behavior None streaming behavior。"""
        chunks: list[dict] = []
        _collect_tool_call_deltas(_Delta(tool_calls=None), chunks)
        assert chunks == []

    def test_none_entry_in_tool_calls_skipped(self):
        """tool_calls streaming behavior None streaming behavior。"""
        chunks: list[dict] = []
        _collect_tool_call_deltas(_Delta(tool_calls=[None]), chunks)
        assert chunks == []

    def test_id_only_chunk_function_none(self):
        """streaming behavior id streaming behavior（function=None）streaming behavior。"""
        chunks: list[dict] = []
        delta = _Delta(tool_calls=[_TCDelta(index=0, id="call_abc", function="none")])
        _collect_tool_call_deltas(delta, chunks)
        assert chunks == [
            {"index": 0, "id": "call_abc", "function": {"name": "", "arguments": ""}}
        ]

    def test_missing_index_defaults_zero(self):
        """index streaming behavior None streaming behavior 0。"""
        chunks: list[dict] = []
        delta = _Delta(tool_calls=[_TCDelta(index=None, name="t", arguments="{}")])
        _collect_tool_call_deltas(delta, chunks)
        assert chunks[0]["index"] == 0

    def test_name_and_args_separate_chunks(self):
        """name streaming behavior arguments streaming behavior。"""
        chunks: list[dict] = []
        _collect_tool_call_deltas(
            _Delta(tool_calls=[_TCDelta(index=0, id="c1", name="scan", arguments="")]), chunks
        )
        _collect_tool_call_deltas(
            _Delta(tool_calls=[_TCDelta(index=0, name="", arguments='{"t":1}')]), chunks
        )
        assert len(chunks) == 2
        assert chunks[0]["function"]["name"] == "scan"
        assert chunks[1]["function"]["arguments"] == '{"t":1}'


# === _validate_tool_call streaming behavior ===


class TestValidateToolCall:
    def _tc(self, id="c1", name="scan", arguments="{}"):
        return MagicMock(id=id, function=MagicMock(name=name, arguments=arguments))

    def test_valid_json_args(self):
        tc = MagicMock(id="c1")
        tc.function.name = "scan"
        tc.function.arguments = '{"target": "x"}'
        assert _validate_tool_call(tc) is True

    def test_empty_args_allowed(self):
        tc = MagicMock(id="c1")
        tc.function.name = "scan"
        tc.function.arguments = ""
        assert _validate_tool_call(tc) is True

    def test_missing_id_rejected(self):
        tc = MagicMock(id="")
        tc.function.name = "scan"
        tc.function.arguments = "{}"
        assert _validate_tool_call(tc) is False

    def test_missing_name_rejected(self):
        tc = MagicMock(id="c1")
        tc.function.name = ""
        tc.function.arguments = "{}"
        assert _validate_tool_call(tc) is False

    def test_truncated_json_rejected(self):
        """streaming behavior JSON streaming behavior。"""
        tc = MagicMock(id="c1")
        tc.function.name = "scan"
        tc.function.arguments = '{"target": "exam'
        assert _validate_tool_call(tc) is False

    def test_none_function_rejected(self):
        tc = MagicMock(id="c1", function=None)
        assert _validate_tool_call(tc) is False


# === _assemble_tool_calls streaming behavior ===


class TestAssembleToolCalls:
    def test_empty(self):
        assert _assemble_tool_calls([]) == []

    def test_cross_chunk_assembly(self):
        """streaming behavior id/name/arguments streaming behavior index streaming behavior。"""
        chunks = [
            {"index": 0, "id": "call_", "function": {"name": "nmap", "arguments": ""}},
            {"index": 0, "id": "123", "function": {"name": "", "arguments": '{"target":'}},
            {"index": 0, "id": "", "function": {"name": "", "arguments": '"x"}'}},
        ]
        result = _assemble_tool_calls(chunks)
        assert len(result) == 1
        assert result[0].id == "call_123"
        assert result[0].function.name == "nmap"
        assert result[0].function.arguments == '{"target":"x"}'

    def test_multiple_indices(self):
        """streaming behavior index streaming behavior tool_call streaming behavior。"""
        chunks = [
            {"index": 0, "id": "a", "function": {"name": "t0", "arguments": "{}"}},
            {"index": 1, "id": "b", "function": {"name": "t1", "arguments": "{}"}},
        ]
        result = _assemble_tool_calls(chunks)
        assert len(result) == 2
        names = {tc.function.name for tc in result}
        assert names == {"t0", "t1"}

    def test_incomplete_json_discarded(self):
        """arguments JSON streaming behavior。"""
        chunks = [
            {"index": 0, "id": "ok", "function": {"name": "good", "arguments": "{}"}},
            {"index": 1, "id": "bad", "function": {"name": "broken", "arguments": '{"t":'}},
        ]
        result = _assemble_tool_calls(chunks)
        assert len(result) == 1
        assert result[0].function.name == "good"

    def test_missing_id_discarded(self):
        """streaming behavior id streaming behavior。"""
        chunks = [
            {"index": 0, "id": "", "function": {"name": "noid", "arguments": "{}"}},
        ]
        result = _assemble_tool_calls(chunks)
        assert result == []

    def test_missing_name_discarded(self):
        """streaming behavior name streaming behavior。"""
        chunks = [
            {"index": 0, "id": "c1", "function": {"name": "", "arguments": "{}"}},
        ]
        result = _assemble_tool_calls(chunks)
        assert result == []


# === streaming behavior ===


class TestStreamEndToEnd:
    @pytest.mark.asyncio
    async def test_tool_call_id_only_in_first_chunk(self):
        """provider streaming behavior chunk streaming behavior tool_call.id，streaming behavior arguments。

        streaming behavior provider delta streaming behavior。
        """
        agent, mock_client = _make_agent()
        spy = SpySink()

        chunks = [
            # streaming behavior：id + name，function streaming behavior arguments streaming behavior
            _Chunk(tool_calls=[_TCDelta(index=0, id="call_xyz", name="recon", arguments="")]),
            # streaming behavior：streaming behavior id，streaming behavior arguments streaming behavior
            _Chunk(tool_calls=[_TCDelta(index=0, id=None, name=None, arguments='{"host":')]),
            _Chunk(tool_calls=[_TCDelta(index=0, id=None, name=None, arguments='"a.com"}')]),
        ]
        mock_client.chat.completions.create.return_value = _SyncStream(chunks)

        captured = {}

        async def fake_handle(agent_obj, message):
            captured["tool_calls"] = list(message.tool_calls)
            return "tool done"

        import vulnbot.agent.llm_client as mod

        orig = mod.handle_tool_calls
        mod.handle_tool_calls = fake_handle
        try:
            await call_llm_stream(agent, "sys", stream_sink=spy)
        finally:
            mod.handle_tool_calls = orig

        assert "tool_calls" in captured
        tcs = captured["tool_calls"]
        assert len(tcs) == 1
        assert tcs[0].id == "call_xyz"
        assert tcs[0].function.name == "recon"
        assert tcs[0].function.arguments == '{"host":"a.com"}'

    @pytest.mark.asyncio
    async def test_incomplete_tool_call_dropped_end_to_end(self):
        """streaming behavior arguments → streaming behavior JSON streaming behavior → streaming behavior。"""
        agent, mock_client = _make_agent()
        spy = SpySink()

        chunks = [
            _Chunk(tool_calls=[_TCDelta(index=0, id="c1", name="scan", arguments='{"t":')]),
        ]
        mock_client.chat.completions.create.return_value = _SyncStream(chunks)

        called = {"handle": False}

        async def fake_handle(agent_obj, message):
            called["handle"] = True
            return "x"

        import vulnbot.agent.llm_client as mod

        orig = mod.handle_tool_calls
        mod.handle_tool_calls = fake_handle
        try:
            result = await call_llm_stream(agent, "sys", stream_sink=spy)
        finally:
            mod.handle_tool_calls = orig

        # streaming behavior，streaming behavior，streaming behavior full_text
        assert called["handle"] is False
        assert result == ""

    @pytest.mark.asyncio
    async def test_partial_content_preserved_on_disconnect(self):
        """streaming behavior ConnectionError streaming behavior，streaming behavior（fallback）streaming behavior。

        streaming behavior streaming-marker streaming behavior，streaming behavior —— streaming behavior
        streaming behavior content streaming behavior sink streaming behavior。
        """
        agent, mock_client = _make_agent()
        spy = SpySink()

        breaking = _BreakingStream(
            [_Chunk(content="partial ")], RuntimeError("connection reset")
        )

        # streaming behavior（streaming behavior）streaming behavior；fallback streaming behavior
        non_stream_msg = MagicMock()
        non_stream_msg.content = "recovered"
        non_stream_msg.tool_calls = None
        non_stream_resp = MagicMock(choices=[MagicMock(message=non_stream_msg)])
        mock_client.chat.completions.create.side_effect = [breaking, non_stream_resp, non_stream_resp]

        with pytest.raises(RuntimeError):
            await call_llm_stream(agent, "sys", stream_sink=spy)

        # streaming behavior content token streaming behavior
        content_calls = [c for c in spy.calls if c[0] == "content"]
        assert content_calls == [("content", "partial ")]

    @pytest.mark.asyncio
    async def test_content_emitted_exactly_once(self):
        """streaming behavior token streaming behavior on_content_token streaming behavior，streaming behavior。"""
        agent, mock_client = _make_agent()
        spy = SpySink()

        chunks = [_Chunk(content="A"), _Chunk(content="B"), _Chunk(content="C")]
        mock_client.chat.completions.create.return_value = _SyncStream(chunks)

        result = await call_llm_stream(agent, "sys", stream_sink=spy)

        content_calls = [c for c in spy.calls if c[0] == "content"]
        assert content_calls == [("content", "A"), ("content", "B"), ("content", "C")]
        assert result == "ABC"

    @pytest.mark.asyncio
    async def test_reasoning_not_mixed_into_content(self):
        """reasoning_content streaming behavior thinking streaming behavior，streaming behavior token。"""
        agent, mock_client = _make_agent()
        spy = SpySink()

        chunks = [
            _Chunk(reasoning="let me think"),
            _Chunk(content="final answer"),
        ]
        mock_client.chat.completions.create.return_value = _SyncStream(chunks)

        result = await call_llm_stream(agent, "sys", stream_sink=spy)

        thinking = [c for c in spy.calls if c[0] == "thinking"]
        content = [c for c in spy.calls if c[0] == "content"]
        assert thinking == [("thinking", "let me think")]
        assert content == [("content", "final answer")]
        # streaming behavior token streaming behavior reasoning streaming behavior
        assert "let me think" not in "".join(c[1] for c in content)
        # full_text streaming behavior <thinking> streaming behavior + streaming behavior
        assert "<thinking>" in result and "final answer" in result


class TestAutoStreamRobustness:
    @pytest.mark.asyncio
    async def test_reasoning_buffer_reset_between_rounds(self):
        """streaming behavior reasoning streaming behavior（streaming behavior）。"""
        agent, mock_client = _make_agent()
        spy = SpySink()

        # streaming behavior：reasoning streaming behavior（streaming behavior content streaming behavior flush）+ tool_call
        first_round = _SyncStream([
            _Chunk(reasoning="round1 reasoning"),
            _Chunk(tool_calls=[_TCDelta(index=0, id="c1", name="t", arguments="{}")]),
        ])
        # streaming behavior：streaming behavior reasoning + content
        second_round = _SyncStream([
            _Chunk(reasoning="round2 reasoning"),
            _Chunk(content="summary"),
        ])
        mock_client.chat.completions.create.side_effect = [first_round, second_round]

        async def fake_handle(agent_obj, message):
            return [{"tool_call_id": "c1", "content": "result"}], []

        import vulnbot.agent.llm_client as mod

        orig = mod.handle_tool_calls_with_results
        mod.handle_tool_calls_with_results = fake_handle
        try:
            result = await call_llm_auto_stream(agent, "sys", "ctx", stream_sink=spy)
        finally:
            mod.handle_tool_calls_with_results = orig

        # round1 streaming behavior reasoning streaming behavior
        assert result.count("round1 reasoning") <= 1
        # streaming behavior
        assert "summary" in result
        # round2 reasoning streaming behavior
        assert result.count("round2 reasoning") == 1
