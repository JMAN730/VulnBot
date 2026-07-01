"""Tests for multi-key failover rotation in the LLM call retry loop."""

import sys
from types import ModuleType, SimpleNamespace

import pytest

from vulnbot.agent.llm_client import (
    _call_with_persistent_retries,
    _is_key_exhausted_error,
)


class FakeAgent:
    """Minimal stand-in exposing the key-pool surface the retry loop uses."""

    def __init__(self, keys):
        self._key_pool = list(keys)
        self._key_index = 0

    def current_key(self):
        return self._key_pool[self._key_index]

    def rotate_api_key(self) -> bool:
        if len(self._key_pool) > 1:
            self._key_index = (self._key_index + 1) % len(self._key_pool)
            return True
        return False


def _ok_response():
    return SimpleNamespace(choices=[object()])


class TestIsKeyExhaustedError:
    def test_detects_rate_limit_and_quota_signals(self):
        for text in [
            "error code: 429 too many requests",
            "rate limit exceeded",
            "rate_limit_exceeded",
            "your quota has been exhausted",
            "deepseek: insufficient balance (402)",
            "账户余额不足",
            "code 1302 concurrency limit",
            "code 1113 balance",
        ]:
            assert _is_key_exhausted_error(text.lower()) is True, text

    def test_ignores_unrelated_errors(self):
        for text in [
            "connection reset by peer",
            "model not found",
            "invalid function arguments json string",
        ]:
            assert _is_key_exhausted_error(text.lower()) is False, text


class TestRotateApiKey:
    def test_rotate_advances_index(self):
        agent = FakeAgent(["k1", "k2"])
        assert agent.current_key() == "k1"
        assert agent.rotate_api_key() is True
        assert agent.current_key() == "k2"

    def test_rotate_single_key_is_noop(self):
        agent = FakeAgent(["only"])
        assert agent.rotate_api_key() is False
        assert agent.current_key() == "only"


class TestFailover:
    async def test_rotates_past_rate_limited_key(self):
        agent = FakeAgent(["bad", "good"])

        def request_fn():
            if agent.current_key() == "bad":
                raise RuntimeError("Error code: 429 - rate limit exceeded")
            return _ok_response()

        response, _ = await _call_with_persistent_retries(agent, request_fn, "test")
        assert response.choices
        assert agent.current_key() == "good"

    async def test_rotates_past_invalid_key_then_succeeds(self):
        agent = FakeAgent(["bad", "good"])

        def request_fn():
            if agent.current_key() == "bad":
                raise RuntimeError("invalid api key provided")
            return _ok_response()

        response, _ = await _call_with_persistent_retries(agent, request_fn, "test")
        assert response.choices
        assert agent.current_key() == "good"

    async def test_raises_when_all_keys_invalid(self):
        agent = FakeAgent(["bad1", "bad2"])

        def request_fn():
            raise RuntimeError("invalid api key provided")

        with pytest.raises(RuntimeError):
            await _call_with_persistent_retries(agent, request_fn, "test")

    async def test_single_key_auth_error_raises_fast(self):
        agent = FakeAgent(["only"])

        def request_fn():
            raise RuntimeError("unauthorized: invalid api key")

        with pytest.raises(RuntimeError):
            await _call_with_persistent_retries(agent, request_fn, "test")


class TestAgentCoreRotation:
    def _agent(self, **llm):
        from vulnbot.agent.core import AgentCore
        from vulnbot.config.schema import VulnBotConfig

        config = VulnBotConfig()
        for k, v in llm.items():
            setattr(config.llm, k, v)
        return AgentCore(config)

    def test_pool_from_api_keys(self):
        agent = self._agent(api_keys=["k1", "k2"])
        assert agent._key_pool == ["k1", "k2"]
        assert agent._current_api_key() == "k1"

    def test_pool_falls_back_to_single_key(self):
        agent = self._agent(api_key="solo")
        assert agent._key_pool == ["solo"]
        assert agent.rotate_api_key() is False

    def test_rotate_advances_and_invalidates_client(self, monkeypatch):
        fake_openai = ModuleType("openai")

        class FakeOpenAI:
            def __init__(self, **kwargs):
                self.kwargs = kwargs

        fake_openai.OpenAI = FakeOpenAI
        monkeypatch.setitem(sys.modules, "openai", fake_openai)

        agent = self._agent(api_keys=["k1", "k2"])
        agent._get_client()
        assert agent._client is not None
        assert agent.rotate_api_key() is True
        assert agent._client is None
        assert agent._current_api_key() == "k2"
