"""LLM client helpers for AgentCore."""

from __future__ import annotations

import asyncio
import inspect
import json
import sys
from typing import Any, Optional, Protocol, runtime_checkable

from vulnbot.agent.token_counter import estimate_tokens, truncate_messages
from vulnbot.agent.tool_call_manager import (
    handle_tool_calls,
    handle_tool_calls_with_results,
)

_CONTEXT_USABLE_RATIO = 0.9


def _fit_context_window(agent: Any, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Truncate messages to fit the configured context window (90% usable budget)."""
    llm = getattr(agent, "config", None)
    llm = getattr(llm, "llm", None) if llm is not None else None
    max_context = getattr(llm, "max_context_tokens", None)
    if not isinstance(max_context, (int, float)) or isinstance(max_context, bool):
        return messages
    if max_context <= 0:
        return messages

    budget = int(max_context * _CONTEXT_USABLE_RATIO)
    current = estimate_tokens(messages)
    if current <= budget:
        return messages

    trimmed = truncate_messages(messages, budget, preserve_system=True)
    try:
        from rich.console import Console

        Console().print(
            f"[yellow][!] Context is about {current} tokens, above budget {budget}; "
            f"truncated to about {estimate_tokens(trimmed)} tokens[/yellow]"
        )
    except Exception:
        print(f"[!] Context truncated: {current} -> {estimate_tokens(trimmed)} tokens (budget {budget})")
    return trimmed


def extract_response(message: Any) -> str:
    """Extract the actual response text from an LLM message.

    Handles:
    1. Normal content (no thinking)
    2. Content with inline <thinking> tags (open/closed)
    3. Separate reasoning_content field (DeepSeek R1, etc.)
    """
    content = message.content or ""
    reasoning = getattr(message, "reasoning_content", None) or ""
    if reasoning and not content:
        content = f"<thinking>\n{reasoning}\n</thinking>\n"
    elif reasoning and content:
        content = f"<thinking>\n{reasoning}\n</thinking>\n{content}"
    return content


def _is_non_retriable_llm_error(error_text: str) -> bool:
    """Return True for configuration/auth errors that should fail fast."""
    hard_fail_markers = [
        "bad_request_error",
        "incorrect api key",
        "invalid api key",
        "invalid chat setting",
        "invalid function arguments json string",
        "tool_call_id",
        "authentication",
        "unauthorized",
        "permission denied",
        "model not found",
        "no such model",
        "invalid_request_error",
        "unsupported parameter",
    ]
    return any(marker in error_text for marker in hard_fail_markers)


def _is_key_exhausted_error(error_text: str) -> bool:
    """Return True for errors that mean the *current* API key is unusable.

    These are rate-limit / quota / balance exhaustion signals where switching to
    a different key is the right recovery. Covers OpenAI-style 429/quota plus
    deepseek (402 insufficient balance) and zhipu (codes 1302/1113, 余额) errors.
    """
    exhausted_markers = [
        "rate limit",
        "rate_limit",
        "too many requests",
        "429",
        "quota",
        "insufficient balance",
        "余额",  # zhipu/deepseek: account balance insufficient
        "402",
        "1302",  # zhipu: concurrency / rate limit
        "1113",  # zhipu: account balance insufficient
    ]
    return any(marker in error_text for marker in exhausted_markers)


def _is_openai_reasoning_model(provider: str, model: str) -> bool:
    """Return True for OpenAI models that use the newer reasoning parameter set."""
    if provider.lower() != "openai":
        return False
    normalized = model.lower()
    return normalized.startswith(("o1", "o3", "o4", "gpt-5"))


def build_chat_completion_kwargs(
    agent: Any,
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None = None,
    *,
    max_tokens: int | None = None,
    temperature: float | None = None,
) -> dict[str, Any]:
    """Build provider-compatible Chat Completions kwargs.

    OpenAI reasoning/GPT-5 models reject the legacy max_tokens field and expect
    max_completion_tokens instead. Other OpenAI-compatible providers may still
    require the older field, so keep the switch scoped to OpenAI's newer model
    families.
    """
    llm = agent.config.llm
    provider = str(getattr(llm, "provider", "") or "").lower()
    model = str(getattr(llm, "model", "") or "")
    token_limit = max_tokens if max_tokens is not None else getattr(llm, "max_tokens", None)
    temp = temperature if temperature is not None else getattr(llm, "temperature", None)
    uses_reasoning_params = _is_openai_reasoning_model(provider, model)

    kwargs: dict[str, Any] = {
        "model": model,
        "messages": messages,
    }
    if token_limit is not None:
        if uses_reasoning_params:
            kwargs["max_completion_tokens"] = token_limit
        else:
            kwargs["max_tokens"] = token_limit
    if temp is not None and not uses_reasoning_params:
        kwargs["temperature"] = temp
    if tools:
        kwargs["tools"] = tools
    if uses_reasoning_params:
        reasoning_effort = getattr(llm, "reasoning_effort", None)
        if reasoning_effort:
            kwargs["reasoning_effort"] = reasoning_effort
    return kwargs


async def _call_with_persistent_retries(
    agent: Any, request_fn, stage_label: str
) -> tuple[Any, int]:
    """Keep retrying retriable LLM calls until success or manual interruption.

    Returns:
        (response, retry_attempts)
    """
    retry_attempts = 0
    pool_size = len(getattr(agent, "_key_pool", None) or [])
    can_rotate = pool_size > 1 and callable(getattr(agent, "rotate_api_key", None))
    keys_tried: set[int] = set()

    while True:
        try:
            maybe_response = request_fn()
            response = await maybe_response if inspect.isawaitable(maybe_response) else maybe_response
            if response is not None and getattr(response, "choices", None):
                return response, retry_attempts

            retry_attempts += 1
            print(
                f"[!] {stage_label} LLM API returned an abnormal response; retry {retry_attempts} in 5s...",
                file=sys.stdout,
                flush=True,
            )
            await asyncio.sleep(5)
        except asyncio.CancelledError:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            error_text = str(exc).lower()
            is_exhausted = _is_key_exhausted_error(error_text)
            is_auth = _is_non_retriable_llm_error(error_text)

            # Multi-key failover: rotate past a rate-limited / quota-drained /
            # invalid key to the next one before falling back to plain retry.
            if can_rotate and (is_exhausted or is_auth):
                keys_tried.add(getattr(agent, "_key_index", 0))
                if len(keys_tried) < pool_size:
                    agent.rotate_api_key()
                    retry_attempts += 1
                    print(
                        f"[!] {stage_label} key failed ({exc}); rotating to next API key "
                        f"and retrying...",
                        file=sys.stdout,
                        flush=True,
                    )
                    continue
                # Every key has now failed in this burst.
                if is_auth and not is_exhausted:
                    # All keys are invalid/unauthorized -> nothing to recover.
                    raise
                # All keys rate-limited: keep cycling, but back off first so we
                # never hard-fail on transient quota limits.
                keys_tried.clear()
                agent.rotate_api_key()
                retry_attempts += 1
                print(
                    f"[!] {stage_label} all API keys rate-limited; retry {retry_attempts} in 5s...",
                    file=sys.stdout,
                    flush=True,
                )
                await asyncio.sleep(5)
                continue

            if is_auth and not is_exhausted:
                raise

            retry_attempts += 1
            print(
                f"[!] {stage_label} LLM connection error; retry {retry_attempts} in 5s... ({exc})",
                file=sys.stdout,
                flush=True,
            )
            await asyncio.sleep(5)


def _prepend_retry_notice(text: str, retry_attempts: int) -> str:
    """Annotate a successful response if retries happened within the same round."""
    if retry_attempts <= 0:
        return text
    return f"[LLM recovered] This round recovered after retry {retry_attempts}.\n{text}"


def _format_tool_results_fallback(
    tool_results: list[dict[str, Any]], skipped_info: list[str]
) -> str:
    """Build a plain-text fallback summary when provider tool-summary format is incompatible."""
    parts = [
        "[tool results processed] Current provider is incompatible with standard tool-summary "
        "messages; falling back to plain-text result summary:"
    ]
    for item in tool_results:
        content = item.get("content", "") if isinstance(item, dict) else str(item)
        if len(content) > 800:
            content = content[:400] + "\n...[middle omitted]...\n" + content[-400:]
        parts.append(content)
    if skipped_info:
        parts.append("[!] Skipped this round: " + "; ".join(skipped_info))
    return "\n".join(parts)


async def call_llm(
    agent: Any,
    system_prompt: str,
    *,
    stream_sink: Optional["StreamSink"] = None,
) -> str:
    """Call the LLM with the current context and system prompt (single turn)."""
    if stream_sink is not None:
        return await call_llm_stream(agent, system_prompt, stream_sink)

    client = agent._get_client()

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(agent.context.get_messages())
    messages = _fit_context_window(agent, messages)
    tools = agent._build_openai_tools()

    kwargs = build_chat_completion_kwargs(agent, messages, tools)

    response, retry_attempts = await _call_with_persistent_retries(
        agent,
        lambda: client.chat.completions.create(**kwargs),
        "single-turn",
    )

    choice = response.choices[0]
    if choice.message.tool_calls:
        return _prepend_retry_notice(await handle_tool_calls(agent, choice.message), retry_attempts)
    return _prepend_retry_notice(extract_response(choice.message), retry_attempts)


async def call_llm_auto(
    agent: Any,
    system_prompt: str,
    round_context: str,
    *,
    stream_sink: Optional["StreamSink"] = None,
) -> str:
    """Call the LLM in auto-pentest mode with round context appended."""
    if stream_sink is not None:
        return await call_llm_auto_stream(agent, system_prompt, round_context, stream_sink)

    client = agent._get_client()

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(agent.context.get_messages())
    messages.append({"role": "user", "content": round_context})
    messages = _fit_context_window(agent, messages)
    tools = agent._build_openai_tools()

    kwargs = build_chat_completion_kwargs(agent, messages, tools)

    response, retry_attempts = await _call_with_persistent_retries(
        agent,
        lambda: client.chat.completions.create(**kwargs),
        "autonomous loop",
    )

    choice = response.choices[0]
    if choice.message.tool_calls:
        tool_results, skipped_info = await handle_tool_calls_with_results(agent, choice.message)

        executed_tcs = []
        for tc in tool_results:
            if not isinstance(tc, dict) or "tool_call" not in tc:
                import sys

                print(f"[!] Skipping abnormal tool result: {type(tc).__name__} {str(tc)[:100]}", file=sys.stderr)
                continue
            executed_tcs.append(tc["tool_call"])

        assistant_msg = {
            "role": "assistant",
            "content": choice.message.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in executed_tcs
            ],
        }
        messages.append(assistant_msg)

        for tool_result in tool_results:
            if isinstance(tool_result, dict) and "tool_call_id" in tool_result:
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_result["tool_call_id"],
                        "content": tool_result.get("content", ""),
                    }
                )

        tool_summary_parts = []
        for tc in executed_tcs:
            try:
                args_str = str(tc.function.arguments)[:200]
            except Exception:
                args_str = "<unreadable>"
            tool_summary_parts.append(f"Tool call: {tc.function.name}({args_str})")
        for tr in tool_results:
            content = tr.get("content", "") if isinstance(tr, dict) else str(tr)
            if len(content) > 1000:
                content = content[:500] + "\n...[middle omitted]...\n" + content[-500:]
            tool_summary_parts.append(f"Tool result: {content}")
            if (
                isinstance(tr, dict)
                and isinstance(tr.get("structured_content"), dict)
                and tr["structured_content"]
            ):
                structured = json.dumps(tr["structured_content"], ensure_ascii=False)
                if len(structured) > 1000:
                    structured = structured[:500] + "\n...[middle omitted]...\n" + structured[-500:]
                tool_summary_parts.append(f"Structured result: {structured}")
        if skipped_info:
            tool_summary_parts.append(f"[!] Skipped this round: {'; '.join(skipped_info)}")

        try:
            kwargs["messages"] = _fit_context_window(agent, messages)
            response2, second_retry_attempts = await _call_with_persistent_retries(
                agent,
                lambda: client.chat.completions.create(**kwargs),
                "tool summary",
            )
            final_text = extract_response(response2.choices[0].message)
            # Context is written by loop_controller/core; avoid duplication here.
            return _prepend_retry_notice(final_text, retry_attempts + second_retry_attempts)
        except Exception as e2:
            error_text = str(e2).lower()
            if _is_non_retriable_llm_error(error_text):
                fallback = _format_tool_results_fallback(tool_results, skipped_info)
                # Same as above: do not write context here.
                return fallback
            return f"[tool results processed] Continued analysis error: {e2}"

    return _prepend_retry_notice(extract_response(choice.message), retry_attempts)


# === Stream LLM Call Helpers ===


class _AsyncIterWrapper:
    """Wrap sync iterable as async iterable for unified async for usage.

    OpenAI sync client -> sync Stream, wrapped for async iteration.
    Test mocks and async clients -> async Stream, consumed directly.
    """

    def __init__(self, iterable):
        self._iter = iter(iterable)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self._iter)
        except StopIteration:
            raise StopAsyncIteration


def _ensure_async_iter(response):
    """Return an async iterable compatible with sync and async streams.

    Order: async iterable -> sync iterable -> None for fallback.
    """
    if hasattr(response, "__aiter__"):
        return response
    if hasattr(response, "__iter__"):
        return _AsyncIterWrapper(response)
    return None  # Not iterable; caller should use fallback path.


def _collect_tool_call_deltas(delta: Any, tool_calls_chunks: list[dict]) -> None:
    """Extract tool_call chunks from a streaming delta and append them.

    Handles provider differences:
    - Some providers only include id in the first chunk.
    - Some providers stream name and arguments in separate chunks.
    - Missing/None index falls back to 0.
    - tc_delta itself can be None.
    """
    tc = getattr(delta, "tool_calls", None)
    if not tc:
        return
    for tc_delta in tc:
        if tc_delta is None:
            continue
        # function can be None in the first id-only chunk.
        func = getattr(tc_delta, "function", None)
        if func is not None:
            name = getattr(func, "name", None) or ""
            arguments = getattr(func, "arguments", None) or ""
        else:
            name = ""
            arguments = ""
        index = getattr(tc_delta, "index", None)
        if index is None:
            index = 0
        tool_calls_chunks.append({
            "index": index,
            "id": getattr(tc_delta, "id", None) or "",
            "function": {"name": name, "arguments": arguments},
        })


def _validate_tool_call(tool_call: Any) -> bool:
    """Validate that an assembled tool_call is complete enough to use.

    Requirements:
    - Non-empty id.
    - Non-empty function.name.
    - arguments are valid JSON or an empty string.
    """
    tc_id = getattr(tool_call, "id", None)
    if not tc_id:
        return False
    func = getattr(tool_call, "function", None)
    if func is None or not getattr(func, "name", None):
        return False
    arguments = getattr(func, "arguments", None)
    if arguments in (None, ""):
        return True
    try:
        json.loads(arguments)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def _build_tool_call(tc_id: str, name: str, arguments: str) -> Any:
    """Build a tool_call object.

    Prefer OpenAI's official pydantic type in production. If unavailable, fall
    back to a lightweight object exposing only the attributes used downstream.
    """
    try:
        from openai.types.chat.chat_completion_message_tool_call import (
            ChatCompletionMessageToolCall,
            Function,
        )

        return ChatCompletionMessageToolCall(
            id=tc_id,
            type="function",
            function=Function(name=name, arguments=arguments),
        )
    except Exception:
        func = type("Function", (), {"name": name, "arguments": arguments})()
        return type("ToolCall", (), {"id": tc_id, "type": "function", "function": func})()


def _assemble_tool_calls(tool_calls_chunks: list[dict]) -> list[Any]:
    """Assemble accumulated streaming chunks into complete tool_calls by index.

    id/name/arguments chunks are concatenated per index and invalid calls are discarded.
    """
    if not tool_calls_chunks:
        return []

    # Align by index while preserving first-seen order.
    tc_by_index: dict[int, dict] = {}
    for tc_chunk in tool_calls_chunks:
        idx = tc_chunk["index"]
        if idx not in tc_by_index:
            tc_by_index[idx] = {"id": "", "function": {"name": "", "arguments": ""}}
        tc_by_index[idx]["id"] += tc_chunk["id"]
        tc_by_index[idx]["function"]["name"] += tc_chunk["function"]["name"]
        tc_by_index[idx]["function"]["arguments"] += tc_chunk["function"]["arguments"]

    tool_calls: list[Any] = []
    for tc_data in tc_by_index.values():
        candidate = _build_tool_call(
            tc_data["id"],
            tc_data["function"]["name"],
            tc_data["function"]["arguments"],
        )
        if not _validate_tool_call(candidate):
            print(
                f"[!] Dropping incomplete streaming tool_call: id={tc_data['id']!r} "
                f"name={tc_data['function']['name']!r} "
                f"args={tc_data['function']['arguments'][:80]!r}",
                file=sys.stderr,
                flush=True,
            )
            continue
        tool_calls.append(candidate)

    return tool_calls


async def call_llm_stream(
    agent: Any,
    system_prompt: str,
    stream_sink: Optional["StreamSink"] = None,
) -> str:
    """Call the LLM with streaming output.

    Args:
        agent: AgentCore instance
        system_prompt: System prompt
        stream_sink: Output sink for streaming (None = silent)

    Returns:
        Full response text (same as non-streaming version)
    """
    if stream_sink is None:
        stream_sink = _NullSink()

    client = agent._get_client()

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(agent.context.get_messages())
    messages = _fit_context_window(agent, messages)
    tools = agent._build_openai_tools()

    kwargs = build_chat_completion_kwargs(agent, messages, tools)

    try:
        stream_sink.on_status("Thinking...")
        response = client.chat.completions.create(**kwargs, stream=True)

        full_text = ""
        reasoning_buffer = ""
        tool_calls_chunks: list[dict] = []

        # Auto-adapt sync/async streams. Sync streams are wrapped with _AsyncIterWrapper.
        _stream = _ensure_async_iter(response)
        if _stream is None:
            raise ValueError("LLM response is not a valid stream object")
        async for chunk in _stream:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta

                # Handle reasoning_content (DeepSeek R1, etc.)
                reasoning = getattr(delta, "reasoning_content", None) or ""
                if reasoning:
                    reasoning_buffer += reasoning
                    stream_sink.on_thinking_token(reasoning)

                # Handle content
                content = getattr(delta, "content", None) or ""
                if content:
                    if reasoning_buffer:
                        full_text += f"<thinking>\n{reasoning_buffer}\n</thinking>\n"
                        reasoning_buffer = ""
                    stream_sink.on_content_token(content)
                    full_text += content

                # Handle tool_calls in streaming chat mode.
                _collect_tool_call_deltas(delta, tool_calls_chunks)

        if reasoning_buffer:
            full_text += f"<thinking>\n{reasoning_buffer}\n</thinking>\n"

        stream_sink.on_stream_end()

        # Route tool calls through the same handling path as call_llm_auto_stream.
        if tool_calls_chunks:
            tool_calls = _assemble_tool_calls(tool_calls_chunks)

            if tool_calls:
                dummy_msg = type("obj", (object,), {
                    "content": full_text,
                    "tool_calls": tool_calls,
                })()
                for tc in tool_calls:
                    stream_sink.on_tool_call(tc.function.name, tc.function.arguments[:200])
                # handle_tool_calls executes tools and performs the second LLM call.
                result = await handle_tool_calls(agent, dummy_msg)
                if result:
                    stream_sink.on_content_token(result)
                stream_sink.on_stream_end()
                return result

        return full_text

    except Exception as e:
        # Fallback to non-streaming on streaming-related errors or general failures
        error_text = str(e).lower()
        streaming_markers = [
            "not supported", "not implemented", "streaming",
            "requires an object with __aiter__",
            "stream is not iterable", "doesn't support",
            "not a valid stream",
        ]
        if any(marker in error_text for marker in streaming_markers):
            # Provider doesn't support streaming or other streaming error, fall back
            pass
        else:
            # Other error, re-raise
            raise

    # Fallback: non-streaming with simulated streaming
    # Use existing call_llm as fallback
    response_fallback, _ = await _call_with_persistent_retries(
        agent,
        lambda: client.chat.completions.create(**kwargs),
        "single-turn",
    )

    # Fall back to non-streaming call_llm with retry and tool-call handling.
    return await call_llm(agent, system_prompt)


async def call_llm_auto_stream(
    agent: Any,
    system_prompt: str,
    round_context: str,
    stream_sink: Optional["StreamSink"] = None,
) -> str:
    """Call the LLM in auto-pentest mode with streaming output.

    Args:
        agent: AgentCore instance
        system_prompt: System prompt
        round_context: Round context for auto mode
        stream_sink: Output sink for streaming (None = silent)

    Returns:
        Full response text
    """
    if stream_sink is None:
        stream_sink = _NullSink()

    client = agent._get_client()

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(agent.context.get_messages())
    messages.append({"role": "user", "content": round_context})
    messages = _fit_context_window(agent, messages)
    tools = agent._build_openai_tools()

    kwargs = build_chat_completion_kwargs(agent, messages, tools)

    try:
        # First LLM call with streaming
        stream_sink.on_status("Thinking...")
        response = client.chat.completions.create(**kwargs, stream=True)

        full_text = ""
        reasoning_buffer = ""
        tool_calls_chunks: list[dict] = []

        # Auto-adapt sync/async streams.
        _stream = _ensure_async_iter(response)
        if _stream is None:
            raise ValueError("LLM response is not a valid stream object")
        async for chunk in _stream:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta

                # Handle reasoning_content
                reasoning = getattr(delta, "reasoning_content", None) or ""
                if reasoning:
                    reasoning_buffer += reasoning
                    stream_sink.on_thinking_token(reasoning)

                # Handle content
                content = getattr(delta, "content", None) or ""
                if content:
                    if reasoning_buffer:
                        full_text += f"<thinking>\n{reasoning_buffer}\n</thinking>\n"
                        reasoning_buffer = ""
                    stream_sink.on_content_token(content)
                    full_text += content

                # Handle tool_calls
                _collect_tool_call_deltas(delta, tool_calls_chunks)

        stream_sink.on_stream_end()

        # Flush reasoning to avoid leaking it into the second summary stream.
        if reasoning_buffer:
            full_text += f"<thinking>\n{reasoning_buffer}\n</thinking>\n"
            reasoning_buffer = ""

        # Check if we have tool calls
        choice_dummy = type("obj", (object,), {"message": type("obj", (object,), {
            "content": full_text,
            "tool_calls": None,
        })()})()

        # Reconstruct message for tool call handling
        # We need to check if there are tool calls from the accumulated chunks
        if tool_calls_chunks:
            tool_calls = _assemble_tool_calls(tool_calls_chunks)

            if tool_calls:
                # After streaming aggregation, patch tool_calls back onto the aggregate message.
                # Patch the dummy message with actual tool calls
                choice_dummy.message.tool_calls = tool_calls
                # Execute tool calls
                for tc in tool_calls:
                    stream_sink.on_tool_call(tc.function.name, tc.function.arguments[:200])

                tool_results, skipped_info = await handle_tool_calls_with_results(agent, choice_dummy.message)

                for tr in tool_results:
                    if isinstance(tr, dict) and "content" in tr:
                        content = tr["content"]
                        if len(content) > 200:
                            content = content[:200] + "..."
                        stream_sink.on_tool_result(content)

                # Continue with the messages including tool results
                assistant_msg = {
                    "role": "assistant",
                    "content": full_text,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in tool_calls
                    ],
                }
                messages.append(assistant_msg)

                for tool_result in tool_results:
                    if isinstance(tool_result, dict) and "tool_call_id" in tool_result:
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_result["tool_call_id"],
                            "content": tool_result.get("content", ""),
                        })

                # Second LLM call (streaming) for summary
                kwargs["messages"] = _fit_context_window(agent, messages)
                stream_sink.on_status("Summarizing...")

                try:
                    response2 = client.chat.completions.create(**kwargs, stream=True)
                    full_text = ""

                    _stream2 = _ensure_async_iter(response2)
                    if _stream2 is None:
                        raise ValueError("LLM response is not a valid stream object")
                    async for chunk in _stream2:
                        if chunk.choices and len(chunk.choices) > 0:
                            delta = chunk.choices[0].delta
                            reasoning = getattr(delta, "reasoning_content", None) or ""
                            if reasoning:
                                reasoning_buffer += reasoning
                                stream_sink.on_thinking_token(reasoning)

                            content = getattr(delta, "content", None) or ""
                            if content:
                                if reasoning_buffer:
                                    full_text += f"<thinking>\n{reasoning_buffer}\n</thinking>\n"
                                    reasoning_buffer = ""
                                stream_sink.on_content_token(content)
                                full_text += content

                    if reasoning_buffer:
                        full_text += f"<thinking>\n{reasoning_buffer}\n</thinking>\n"

                    # Context is written by loop_controller; do not duplicate it here.
                    stream_sink.on_stream_end()
                    return full_text

                except Exception as e2:
                    error_text = str(e2).lower()
                    if _is_non_retriable_llm_error(error_text):
                        fallback = _format_tool_results_fallback(tool_results, skipped_info)
                        # Same as above: do not write context here.
                        return fallback
                    return f"[tool results processed] Continued analysis error: {e2}"

        # Context is written by the caller; do not duplicate it here.
        return full_text

    except (NotImplementedError, ValueError, Exception) as e:
        error_text = str(e).lower()
        if not any(
            marker in error_text
            for marker in [
                "not supported", "not implemented", "streaming",
            ]
        ):
            raise

    # Fallback to non-streaming
    return await call_llm_auto(agent, system_prompt, round_context)


# === Stream Output Protocol ===


@runtime_checkable
class StreamSink(Protocol):
    """Streaming output sink abstraction.

    The LLM layer uses this interface to route output to CLI, web, or silent sinks.
    """

    def on_status(self, message: str) -> None:
        """Display a status message such as "Thinking..."."""
        ...

    def on_thinking_token(self, token: str) -> None:
        """Receive a reasoning token, optionally displayed by the sink."""
        ...

    def on_content_token(self, token: str) -> None:
        """Receive a normal content token."""
        ...

    def on_tool_call(self, tool_name: str, args: str) -> None:
        """Display a tool-call notification."""
        ...

    def on_tool_result(self, result_summary: str) -> None:
        """Display a tool-result summary."""
        ...

    def on_stream_end(self) -> None:
        """Handle stream completion, such as newline or cleanup."""
        ...


class _NullSink:
    """No-op sink used when no output sink is provided."""

    def on_status(self, message: str) -> None:
        pass

    def on_thinking_token(self, token: str) -> None:
        pass

    def on_content_token(self, token: str) -> None:
        pass

    def on_tool_call(self, tool_name: str, args: str) -> None:
        pass

    def on_tool_result(self, result_summary: str) -> None:
        pass

    def on_stream_end(self) -> None:
        pass
