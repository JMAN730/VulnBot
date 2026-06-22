"""VulnClaw configuration schema - Pydantic models for type-safe config."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# LLM provider presets


class LLMProvider(str, Enum):
    """Supported LLM providers with OpenAI-compatible APIs."""

    OPENAI = "openai"
    MINIMAX = "minimax"
    DEEPSEEK = "deepseek"
    ZHIPU = "zhipu"
    MOONSHOT = "moonshot"
    QWEN = "qwen"
    SILICONFLOW = "siliconflow"
    DOUBAO = "doubao"
    BAICHUAN = "baichuan"
    STEPFUN = "stepfun"
    SENSETIME = "sensetime"
    YI = "yi"
    CUSTOM = "custom"


# Provider preset definitions: base_url + default_model + notes
PROVIDER_PRESETS: dict[LLMProvider, dict[str, str]] = {
    LLMProvider.OPENAI: {
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o",
        "label": "OpenAI",
    },
    LLMProvider.MINIMAX: {
        "base_url": "https://api.minimaxi.com/v1",
        "default_model": "MiniMax-M3",
        "label": "MiniMax",
    },
    LLMProvider.DEEPSEEK: {
        "base_url": "https://api.deepseek.com",
        "default_model": "deepseek-v4-pro",
        "label": "DeepSeek",
    },
    LLMProvider.ZHIPU: {
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "default_model": "glm-4.7",
        "label": "Zhipu GLM",
    },
    LLMProvider.MOONSHOT: {
        "base_url": "https://api.moonshot.cn/v1",
        "default_model": "kimi-k2.6",
        "label": "Kimi (Moonshot)",
    },
    LLMProvider.QWEN: {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "default_model": "qwen3-max",
        "label": "Tongyi Qianwen",
    },
    LLMProvider.SILICONFLOW: {
        "base_url": "https://api.siliconflow.cn/v1",
        "default_model": "deepseek-ai/DeepSeek-V4-Flash",
        "label": "SiliconFlow",
    },
    LLMProvider.DOUBAO: {
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "default_model": "Doubao-Seed-2.0-Pro",
        "label": "Doubao (ByteDance)",
    },
    LLMProvider.BAICHUAN: {
        "base_url": "https://api.baichuan-ai.com/v1",
        "default_model": "Baichuan4-Turbo",
        "label": "Baichuan",
    },
    LLMProvider.STEPFUN: {
        "base_url": "https://api.stepfun.com/v1",
        "default_model": "step-3.5-flash",
        "label": "StepFun",
    },
    LLMProvider.SENSETIME: {
        "base_url": "https://api.sensenova.cn/v1",
        "default_model": "SenseNova-6.7-Flash-Lite",
        "label": "SenseTime (SenseNova)",
    },
    LLMProvider.YI: {
        "base_url": "https://api.lingyiwanwu.com/v1",
        "default_model": "yi-lightning",
        "label": "01.AI (Yi)",
    },
    LLMProvider.CUSTOM: {
        "base_url": "",
        "default_model": "",
        "label": "Custom",
    },
}


class LLMConfig(BaseModel):
    """LLM provider configuration."""

    provider: str = Field(
        default="openai",
        description="LLM provider name (openai/minimax/deepseek/zhipu/moonshot/qwen/siliconflow/doubao/baichuan/stepfun/sensetime/yi/custom)",
    )
    api_key: str = Field(default="", description="API key for the chosen provider")
    base_url: str = Field(
        default="https://api.openai.com/v1",
        description="OpenAI-compatible API base URL (auto-filled by provider)",
    )
    model: str = Field(default="gpt-4o", description="Model name to use (auto-filled by provider)")
    max_tokens: int = Field(default=4096, description="Max tokens per response")
    max_context_tokens: int = Field(
        default=128000, description="Max context window tokens before sliding-window truncation"
    )
    temperature: float = Field(default=0.1, description="Sampling temperature")
    reasoning_effort: str = Field(
        default="high", description="Reasoning effort level (OpenAI o-series only)"
    )


class MCPTransportConfig(BaseModel):
    """MCP server transport configuration."""

    type: str = Field(description="Transport type: stdio, sse")
    command: str | None = Field(default=None, description="Command to start the server (stdio)")
    args: list[str] | None = Field(default=None, description="Command arguments")
    url: str | None = Field(default=None, description="Server URL (sse)")
    env: dict[str, str] | None = Field(default=None, description="Environment variables")
    startup_timeout: int = Field(default=30000, description="Startup timeout in ms")
    tool_timeout: int = Field(default=300000, description="Tool call timeout in ms")


class MCPServerConfig(BaseModel):
    """Single MCP server configuration."""

    name: str = Field(description="Server identifier")
    enabled: bool = Field(default=True, description="Whether to auto-start this server")
    priority: int = Field(default=1, description="Priority: 0=critical, 1=normal, 2=optional")
    transport: MCPTransportConfig = Field(description="Transport configuration")
    description: str = Field(default="", description="Human-readable description")


class MCPServersConfig(BaseModel):
    """All MCP servers configuration."""

    servers: dict[str, MCPServerConfig] = Field(default_factory=dict)


class SafetyConfig(BaseModel):
    """Safety / sandbox configuration."""

    enable_python_execute: bool = Field(
        default=True,
        description="Enable the python_execute built-in tool (disable for safer runs)",
    )
    python_execute_restricted: bool = Field(
        default=False,
        description="Restricted mode: block file I/O and network in python_execute",
    )
    python_execute_mode: str = Field(
        default="trusted-local",
        description="Execution mode for python_execute: safe, lab, trusted-local",
    )
    python_execute_max_lines: int = Field(
        default=50,
        description="Max lines of code allowed per python_execute call",
    )
    python_execute_show_warning: bool = Field(
        default=True,
        description="Show a security warning before each python_execute invocation",
    )
    python_execute_max_output_chars: int = Field(
        default=8000,
        description="Max stdout/stderr characters returned from a python_execute call",
    )
    python_execute_audit_enabled: bool = Field(
        default=True,
        description="Write python_execute audit records to the local config directory",
    )
    tool_parallel: bool = Field(
        default=True,
        description="Execute independent tool calls in a single LLM turn concurrently",
    )
    tool_max_concurrent: int = Field(
        default=5,
        description="Max number of tool calls executed concurrently per round (1=serial)",
    )


class SessionConfig(BaseModel):
    """Session / output configuration."""

    output_dir: Path = Field(default=Path("./vulnclaw-output"), description="Output directory")
    auto_save: bool = Field(default=True, description="Auto-save session state")
    report_format: str = Field(
        default="markdown", description="Default report format: markdown, html"
    )
    poc_language: str = Field(default="python", description="Default PoC language: python, bash")
    max_rounds: int = Field(default=15, description="Max autonomous pentest rounds (1-100)")
    show_thinking: bool = Field(
        default=False, description="Show LLM thinking/reasoning output (default: off)"
    )
    # Dead-loop detection
    stale_rounds_threshold: int = Field(
        default=5,
        description="Consecutive rounds without progress before dead-loop warning (1-50)",
    )
    # Persistent pentest configuration
    persistent_rounds_per_cycle: int = Field(
        default=100, description="Rounds per persistent pentest cycle"
    )
    persistent_max_cycles: int = Field(
        default=10, description="Max cycles for persistent pentest (0=unlimited)"
    )
    persistent_auto_report: bool = Field(
        default=True, description="Auto-generate report after each cycle"
    )
    # Language configuration
    language: str = Field(default="en", description="UI language: en")


class VulnClawConfig(BaseModel):
    """Top-level VulnClaw configuration."""

    llm: LLMConfig = Field(default_factory=LLMConfig)
    mcp: MCPServersConfig = Field(default_factory=MCPServersConfig)
    session: SessionConfig = Field(default_factory=SessionConfig)
    safety: SafetyConfig = Field(default_factory=SafetyConfig)

    model_config = ConfigDict(
        env_prefix="VULNCLAW_",
        env_nested_delimiter="__",
    )


# Built-in MCP server definitions

BUILTIN_MCP_SERVERS: dict[str, dict[str, Any]] = {
    "fetch": {
        "name": "fetch",
        "enabled": True,
        "priority": 0,
        "description": "HTTP request tool for API testing & web interaction",
        "transport": {
            "type": "stdio",
            "command": "uvx",
            "args": ["mcp-server-fetch"],
        },
    },
    "memory": {
        "name": "memory",
        "enabled": True,
        "priority": 0,
        "description": "Context memory & session state persistence",
        "transport": {
            "type": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-memory"],
        },
    },
    "chrome-devtools": {
        "name": "chrome-devtools",
        "enabled": False,
        "priority": 0,
        "description": "Browser automation for Web app pentest",
        "transport": {
            "type": "stdio",
            "command": "npx",
            "args": ["-y", "chrome-devtools-mcp@latest"],
        },
    },
    "burp": {
        "name": "burp",
        "enabled": False,
        "priority": 0,
        "description": "Burp Suite proxy integration for HTTP interception",
        "transport": {
            "type": "stdio",
            "command": "java",
            "args": ["-jar", "mcp-proxy.jar", "--sse-url", "http://127.0.0.1:9876"],
        },
    },
}
