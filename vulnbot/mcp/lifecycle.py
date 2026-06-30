"""VulnBot MCP Lifecycle Manager - start/stop MCP servers and manage their lifetime."""

from __future__ import annotations

import asyncio
import subprocess
import time
from contextlib import suppress
from typing import Any
from urllib.parse import urlparse

from vulnbot.agent.builtin_tools import infer_port_from_url
from vulnbot.agent.constraint_policy import host_matches_allowed_scope
from vulnbot.config.schema import MCPServerConfig, VulnBotConfig
from vulnbot.mcp.registry import HealthStatus, MCPRegistry

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:  # pragma: no cover - optional runtime dependency
    ClientSession = None
    StdioServerParameters = None
    stdio_client = None


class MCPLifecycleManager:
    """Manages the lifecycle of MCP servers: start, stop, health check.

    For MVP, we use subprocess-based MCP communication.
    In later versions, this will use the Python MCP SDK for proper protocol handling.
    """

    # Auto-restart policy.
    MAX_RESTART_ATTEMPTS = 3
    RESTART_BACKOFF_BASE = 1.0  # seconds; attempt N waits BASE * 2**(N-1)

    # Graceful stop policy.
    TERMINATE_GRACE_SECONDS = 5.0

    # Health-score thresholds on the recent success-rate window.
    HEALTHY_RATE = 0.9
    DEGRADED_RATE = 0.5

    def __init__(self, config: VulnBotConfig) -> None:
        self.config = config
        self.registry = MCPRegistry()
        self._processes: dict[str, subprocess.Popen] = {}
        self._mcp_clients: dict[str, Any] = {}  # Server attach capability cache
        self._loop: asyncio.AbstractEventLoop | None = None
        self._task_constraints: Any = None

    async def __aenter__(self) -> MCPLifecycleManager:
        self.start_enabled_servers()
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        await self.astop_all()

    def set_task_constraints(self, constraints: Any) -> None:
        """Attach current task constraints for tool-level enforcement."""
        self._task_constraints = constraints

    def _check_fetch_constraints(self, arguments: dict[str, Any]) -> dict[str, Any] | None:
        constraints = self._task_constraints
        if constraints is None or constraints.is_empty():
            return None

        url = str(arguments.get("url", "") or "").strip()
        if not url:
            return None

        try:
            parsed = urlparse(url)
        except Exception:
            parsed = None
        host = parsed.hostname.lower() if parsed and parsed.hostname else ""
        path = parsed.path.rstrip("/") if parsed and parsed.path else ""

        port = infer_port_from_url(url)
        if port is None:
            port = None

        if (
            constraints.allowed_hosts
            and host
            and not host_matches_allowed_scope(host, constraints.allowed_hosts)
        ):
            allowed_hosts = ", ".join(constraints.allowed_hosts)
            return self._tool_result(
                ok=False,
                server="fetch",
                tool="fetch",
                execution_mode="local",
                error_type="constraint_violation",
                message=f"Host {host} is outside allowed scope [{allowed_hosts}] for url {url}",
                suggestion="Adjust the task scope or send the request to an allowed host.",
            )

        if host and host in constraints.blocked_hosts:
            return self._tool_result(
                ok=False,
                server="fetch",
                tool="fetch",
                execution_mode="local",
                error_type="constraint_violation",
                message=f"Host {host} is blocked by task constraints for url {url}",
                suggestion="Remove the blocked host from the request or adjust constraints.",
            )

        if constraints.allowed_paths and path and path not in constraints.allowed_paths:
            allowed_paths = ", ".join(constraints.allowed_paths)
            return self._tool_result(
                ok=False,
                server="fetch",
                tool="fetch",
                execution_mode="local",
                error_type="constraint_violation",
                message=f"Path {path} is outside allowed scope [{allowed_paths}] for url {url}",
                suggestion="Adjust the task scope or send the request to an allowed path.",
            )

        if path and path in constraints.blocked_paths:
            return self._tool_result(
                ok=False,
                server="fetch",
                tool="fetch",
                execution_mode="local",
                error_type="constraint_violation",
                message=f"Path {path} is blocked by task constraints for url {url}",
                suggestion="Remove the blocked path from the request or adjust constraints.",
            )

        if port is not None and constraints.allowed_ports and port not in constraints.allowed_ports:
            allowed = ", ".join(str(p) for p in constraints.allowed_ports)
            return self._tool_result(
                ok=False,
                server="fetch",
                tool="fetch",
                execution_mode="local",
                error_type="constraint_violation",
                message=f"Port {port} is outside allowed scope [{allowed}] for url {url}",
                suggestion="Adjust the task scope or send the request to an allowed port.",
            )

        if port is not None and port in constraints.blocked_ports:
            return self._tool_result(
                ok=False,
                server="fetch",
                tool="fetch",
                execution_mode="local",
                error_type="constraint_violation",
                message=f"Port {port} is blocked by task constraints for url {url}",
                suggestion="Remove the blocked port from the request or adjust constraints.",
            )

        return None

    def _tool_result(
        self,
        *,
        ok: bool,
        server: str,
        tool: str,
        execution_mode: str,
        content: Any = None,
        structured_content: dict[str, Any] | None = None,
        error_type: str | None = None,
        message: str = "",
        suggestion: str = "",
    ) -> dict[str, Any]:
        return {
            "ok": ok,
            "server": server,
            "tool": tool,
            "execution_mode": execution_mode,
            "content": content,
            "structured_content": structured_content,
            "error_type": error_type,
            "message": message,
            "suggestion": suggestion,
        }

    def start_enabled_servers(self) -> int:
        """Start all enabled MCP servers.

        Returns the number of servers successfully started.
        """
        with suppress(RuntimeError):
            self._loop = asyncio.get_running_loop()
        started = 0
        for name, server_config in self.config.mcp.servers.items():
            if server_config.enabled:
                self.registry.register_server(name)
                try:
                    if self._start_server(name, server_config):
                        started += 1
                except Exception as e:
                    self.registry.set_server_error(name, str(e), error_type="startup_error")
        return started

    def _start_server(self, name: str, config: MCPServerConfig) -> bool:
        """Start a single MCP server.

        Current execution modes:
        - fetch/memory: local implementation (usable now, no external MCP process)
        - stdio/sse others: attempt attach, then degrade to placeholder if unavailable
        """
        transport = config.transport

        if name in {"fetch", "memory"}:
            self.registry.set_server_running(name, running=False)
            self.registry.set_server_execution_mode(name, "local")
            self.registry.set_server_health(name, "healthy")
            self.registry.set_server_attach_result(name, attempted=False, succeeded=True)
            self._register_known_tools(name)
            return True

        if transport.type == "stdio":
            self.registry.set_server_health(name, HealthStatus.STARTING.value)
            attached = self._try_attach_stdio_client(name, config)
            self.registry.set_server_attach_result(name, attempted=True, succeeded=attached)
            self.registry.set_server_running(name, running=attached)
            self.registry.set_server_execution_mode(name, "sdk" if attached else "placeholder")
            self.registry.set_server_health(
                name,
                HealthStatus.HEALTHY.value if attached else HealthStatus.DEGRADED.value,
            )
            if not attached:
                self._register_known_tools(name)
            return True

        if transport.type == "sse":
            attached = self._try_attach_sse_client(name, config)
            self.registry.set_server_attach_result(name, attempted=True, succeeded=attached)
            self.registry.set_server_running(name, running=attached)
            self.registry.set_server_execution_mode(name, "sse" if attached else "placeholder")
            self.registry.set_server_health(name, "healthy" if attached else "degraded")
            self._register_known_tools(name)
            return True

        self.registry.set_server_health(name, "unavailable")
        return False

    def _try_attach_stdio_client(self, name: str, config: MCPServerConfig) -> bool:
        """Attempt a real stdio MCP attach when SDK primitives are available."""
        transport = config.transport
        probe_overridden = "_probe_stdio_server" in self.__dict__
        if (
            not probe_overridden
            and (ClientSession is None or StdioServerParameters is None or stdio_client is None)
        ):
            self.registry.set_server_error(
                name, "MCP Python SDK is not installed", error_type="sdk_unavailable"
            )
            return False

        if not transport.command:
            self.registry.set_server_error(
                name, "stdio transport is missing command", error_type="config_error"
            )
            return False

        if not probe_overridden and self._is_deferred_package_command(transport):
            self.registry.set_server_error(
                name,
                "stdio probe skipped for package-manager command; install the MCP server "
                "locally or provide a running server config before attaching",
                error_type="attach_failed",
            )
            return False

        ok, details, tools = self._probe_stdio_server(config)
        if not ok:
            self.registry.set_server_error(
                name, details or "stdio attach probe failed", error_type="attach_failed"
            )
            return False

        self._mcp_clients[name] = {"kind": "stdio-probe", "config": config}
        if tools:
            self._register_runtime_tools(name, tools)
        return True

    def _is_deferred_package_command(self, transport: Any) -> bool:
        """Avoid letting health probes trigger package-manager installs/downloads."""
        command = (transport.command or "").lower()
        args = [str(arg).lower() for arg in (transport.args or [])]

        if command in {"npx", "pnpx", "bunx"}:
            return True

        if command == "yarn" and args and args[0] in {"dlx", "exec"}:
            return True

        return command == "npm" and any(arg in {"exec", "x"} for arg in args)

    def _try_attach_sse_client(self, name: str, config: MCPServerConfig) -> bool:
        """Attempt a minimal SSE reachability/config validation before fallback."""
        from urllib.parse import urlparse

        url = config.transport.url or ""
        if not url:
            self.registry.set_server_error(
                name, "sse transport is missing url", error_type="config_error"
            )
            return False

        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            self.registry.set_server_error(
                name, f"invalid SSE url: {url}", error_type="config_error"
            )
            return False

        return False

    def _probe_stdio_server(
        self, config: MCPServerConfig
    ) -> tuple[bool, str, list[dict[str, Any]]]:
        """Run a one-shot stdio MCP probe to validate the server can initialize."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            return False, "stdio probe skipped because an event loop is already running", []

        timeout_s = self._startup_timeout_seconds(config)
        try:
            return asyncio.run(
                asyncio.wait_for(self._async_probe_stdio_server(config), timeout=timeout_s)
            )
        except asyncio.TimeoutError:
            return False, f"stdio attach timed out after {timeout_s:.0f}s", []
        except RuntimeError as exc:
            return False, str(exc), []
        except Exception as exc:  # pragma: no cover - defensive
            return False, str(exc), []

    @staticmethod
    def _startup_timeout_seconds(config: MCPServerConfig) -> float:
        """Resolve the startup timeout (config is in ms) to seconds, defaulting to 30s."""
        raw = getattr(config.transport, "startup_timeout", None)
        if not raw or raw <= 0:
            return 30.0
        return float(raw) / 1000.0

    async def _async_probe_stdio_server(
        self, config: MCPServerConfig
    ) -> tuple[bool, str, list[dict[str, Any]]]:
        transport = config.transport
        server = StdioServerParameters(
            command=transport.command or "",
            args=transport.args or [],
            env=transport.env,
        )

        try:
            async with stdio_client(server) as (read_stream, write_stream):
                session = ClientSession(read_stream, write_stream)
                await session.initialize()
                tools = await session.list_tools()
                tool_defs = self._normalize_mcp_tools(getattr(tools, "tools", []) or [])
                return True, f"initialized with {len(tool_defs)} tools", tool_defs
        except Exception as exc:
            return False, str(exc), []

    def _normalize_mcp_tools(self, tools: list[Any]) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for tool in tools:
            name = getattr(tool, "name", None)
            if not name:
                continue
            normalized.append(
                {
                    "name": name,
                    "description": getattr(tool, "description", "") or "",
                    "inputSchema": getattr(tool, "inputSchema", None)
                    or getattr(tool, "input_schema", None)
                    or {"type": "object", "properties": {}},
                }
            )
        return normalized

    def _render_mcp_call_result(self, result: Any) -> tuple[str, dict[str, Any] | None, bool]:
        """Normalize an MCP CallToolResult into readable text plus structured data."""
        if result is None:
            return "", None, False

        structured = getattr(result, "structuredContent", None)
        is_error = bool(getattr(result, "isError", False))
        content_items = getattr(result, "content", None)

        if not content_items:
            return (
                str(structured or result),
                structured if isinstance(structured, dict) else None,
                is_error,
            )

        parts: list[str] = []
        for item in content_items:
            item_type = getattr(item, "type", "")
            if item_type == "text":
                text = getattr(item, "text", "")
                if text:
                    parts.append(str(text))
                continue
            if item_type == "image":
                mime = getattr(item, "mimeType", "") or getattr(item, "mime_type", "")
                parts.append(f"[image:{mime or 'unknown'}]")
                continue
            if item_type == "resource_link":
                uri = getattr(item, "uri", "")
                name = getattr(item, "name", "") or uri
                parts.append(f"[resource:{name}]")
                continue
            parts.append(str(item))

        rendered = "\n".join(part for part in parts if part).strip()
        if not rendered and structured is not None:
            rendered = str(structured)
        return rendered, structured if isinstance(structured, dict) else None, is_error

    def _register_runtime_tools(self, server_name: str, tools: list[dict[str, Any]]) -> None:
        """Replace static known tools with tools discovered from the live MCP server."""
        self.registry.clear_server_tools(server_name)
        for tool in tools:
            self.registry.register_tool(server_name, tool)

    async def _call_stdio_server(
        self, server_name: str, tool_name: str, arguments: dict[str, Any]
    ) -> Any:
        """Run a one-shot stdio MCP call using the Python SDK."""
        client_meta = self._mcp_clients.get(server_name)
        config = None
        if isinstance(client_meta, dict):
            config = client_meta.get("config")
        if config is None:
            config = self.config.mcp.servers.get(server_name)
        if config is None:
            raise RuntimeError(f"missing MCP config for server {server_name}")

        transport = config.transport
        server = StdioServerParameters(
            command=transport.command or "",
            args=transport.args or [],
            env=transport.env,
        )

        async with stdio_client(server) as (read_stream, write_stream):
            session = ClientSession(read_stream, write_stream)
            await session.initialize()
            result = await session.call_tool(tool_name, arguments=arguments)
            return result

    async def _get_or_create_persistent_stdio_session(self, server_name: str) -> Any:
        """Create and cache a persistent stdio-backed MCP session for the current loop."""
        client_meta = self._mcp_clients.get(server_name)
        current_loop = asyncio.get_running_loop()

        if isinstance(client_meta, dict) and client_meta.get("kind") == "persistent-stdio":
            if client_meta.get("loop") is current_loop and client_meta.get("session") is not None:
                return client_meta["session"]

        config = None
        if isinstance(client_meta, dict):
            config = client_meta.get("config")
        if config is None:
            config = self.config.mcp.servers.get(server_name)
        if config is None:
            raise RuntimeError(f"missing MCP config for server {server_name}")

        transport = config.transport
        server = StdioServerParameters(
            command=transport.command or "",
            args=transport.args or [],
            env=transport.env,
        )

        cm = stdio_client(server)
        read_stream, write_stream = await cm.__aenter__()
        session = ClientSession(read_stream, write_stream)
        await session.initialize()

        self._mcp_clients[server_name] = {
            "kind": "persistent-stdio",
            "config": config,
            "loop": current_loop,
            "session": session,
            "context_manager": cm,
        }
        return session

    def _is_process_alive(self, server_name: str) -> bool:
        """Return True if the server's tracked subprocess (if any) is still running.

        Servers without a tracked OS process (local fetch/memory, persistent stdio
        sessions whose process is owned by the SDK context manager) are treated as
        alive; their failures surface through call errors instead.
        """
        proc = self._processes.get(server_name)
        if proc is None:
            return True
        return proc.poll() is None

    async def _restart_server(self, server_name: str) -> bool:
        """Restart a crashed server with exponential backoff (max 3 attempts).

        Returns True if the server was brought back to a running/attached state.
        """
        config = self.config.mcp.servers.get(server_name)
        if config is None:
            self.registry.set_server_error(
                server_name, "missing config for restart", error_type="config_error"
            )
            self.registry.set_server_health(server_name, HealthStatus.UNAVAILABLE.value)
            return False

        # Tear down any stale session/process before re-attaching.
        await self._teardown_server(server_name)

        for attempt in range(1, self.MAX_RESTART_ATTEMPTS + 1):
            if attempt > 1:
                backoff = self.RESTART_BACKOFF_BASE * (2 ** (attempt - 2))
                await asyncio.sleep(backoff)

            self.registry.record_restart(server_name)
            self.registry.set_server_health(server_name, HealthStatus.STARTING.value)
            try:
                started = self._start_server(server_name, config)
            except Exception as exc:
                self.registry.set_server_error(
                    server_name, str(exc), error_type="restart_error"
                )
                continue

            if started and self._is_server_back_up(server_name):
                return True

        self.registry.set_server_health(server_name, HealthStatus.UNAVAILABLE.value)
        return False

    def _is_server_back_up(self, server_name: str) -> bool:
        """A server is back up if it is attached/running, or runs in local mode.

        Local servers (fetch/memory) are never marked ``running`` because they
        have no backing process, so a healthy local execution mode counts as up.
        """
        state = self.registry.get_all_servers().get(server_name)
        if state is None:
            return False
        if state.running:
            return True
        return (
            state.execution_mode == "local"
            and state.health_status == HealthStatus.HEALTHY.value
        )

    async def _teardown_server(self, server_name: str) -> None:
        """Close any cached session and kill any tracked process for a server."""
        client_meta = self._mcp_clients.pop(server_name, None)
        if isinstance(client_meta, dict) and client_meta.get("kind") == "persistent-stdio":
            cm = client_meta.get("context_manager")
            if cm is not None:
                with suppress(Exception):
                    await cm.__aexit__(None, None, None)

        proc = self._processes.pop(server_name, None)
        if proc is not None:
            await self._terminate_process(proc)

    async def health_check(self, server_name: str) -> HealthStatus:
        """Evaluate and update a server's health from its recent success rate.

        >90% success -> healthy, 50-90% -> degraded, <50% -> unavailable.
        Servers with no recorded calls keep their current lifecycle status
        (starting/healthy/degraded) rather than being forced to a verdict.
        """
        state = self.registry.get_all_servers().get(server_name)
        if state is None:
            return HealthStatus.UNKNOWN

        # A dead subprocess is unavailable regardless of past success.
        if not self._is_process_alive(server_name):
            self.registry.set_server_health(server_name, HealthStatus.UNAVAILABLE.value)
            return HealthStatus.UNAVAILABLE

        rate = self.registry.recent_success_rate(server_name)
        if rate is None:
            try:
                return HealthStatus(state.health_status)
            except ValueError:
                return HealthStatus.UNKNOWN

        if rate > self.HEALTHY_RATE:
            status = HealthStatus.HEALTHY
        elif rate >= self.DEGRADED_RATE:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.UNAVAILABLE

        self.registry.set_server_health(server_name, status.value)
        return status

    def _register_known_tools(self, server_name: str) -> None:
        """Register known tools for a server based on its type.

        This is a temporary approach for MVP. In production, tools will be
        discovered dynamically via the MCP protocol.
        """
        KNOWN_TOOLS: dict[str, list[dict]] = {
            "fetch": [
                {
                    "name": "fetch",
                    "description": "Fetch a URL and return the content",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "description": "URL to fetch"},
                            "method": {
                                "type": "string",
                                "description": "HTTP method",
                                "default": "GET",
                            },
                            "headers": {"type": "object", "description": "HTTP headers"},
                            "body": {"type": "string", "description": "Request body"},
                        },
                        "required": ["url"],
                    },
                },
            ],
            "memory": [
                {
                    "name": "save",
                    "description": "Save information to persistent memory",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "key": {"type": "string", "description": "Memory key"},
                            "value": {"type": "string", "description": "Memory value"},
                        },
                        "required": ["key", "value"],
                    },
                },
                {
                    "name": "retrieve",
                    "description": "Retrieve information from persistent memory",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "key": {"type": "string", "description": "Memory key to retrieve"},
                        },
                        "required": ["key"],
                    },
                },
            ],
            "chrome-devtools": [
                {
                    "name": "new_page",
                    "description": "Open a new browser page",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "description": "URL to navigate to"},
                        },
                    },
                },
                {
                    "name": "navigate",
                    "description": "Navigate to a URL in the current page",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "description": "URL to navigate to"},
                        },
                        "required": ["url"],
                    },
                },
                {
                    "name": "screenshot",
                    "description": "Take a screenshot of the current page",
                    "inputSchema": {"type": "object", "properties": {}},
                },
                {
                    "name": "evaluate_js",
                    "description": "Evaluate JavaScript in the browser",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "JS expression to evaluate",
                            },
                        },
                        "required": ["expression"],
                    },
                },
            ],
            "burp": [
                {
                    "name": "send_http1_request",
                    "description": "Send an HTTP/1 request through Burp proxy",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "method": {"type": "string", "description": "HTTP method"},
                            "url": {"type": "string", "description": "Target URL"},
                            "headers": {"type": "object", "description": "Request headers"},
                            "body": {"type": "string", "description": "Request body"},
                        },
                        "required": ["method", "url"],
                    },
                },
                {
                    "name": "get_proxy_history",
                    "description": "Get proxy history from Burp",
                    "inputSchema": {"type": "object", "properties": {}},
                },
            ],
        }

        tools = KNOWN_TOOLS.get(server_name, [])
        for tool in tools:
            self.registry.register_tool(server_name, tool)

    def _graceful_terminate(self, proc: subprocess.Popen) -> None:
        """Synchronously stop a process: terminate, wait, then kill if still alive.

        On Windows there is no SIGTERM; subprocess.terminate() maps to
        TerminateProcess, so we use it directly rather than os.kill(SIGTERM).
        """
        if proc.poll() is not None:
            return
        try:
            proc.terminate()
        except Exception:
            pass
        try:
            proc.wait(timeout=self.TERMINATE_GRACE_SECONDS)
            return
        except Exception:
            pass
        try:
            proc.kill()
            proc.wait(timeout=self.TERMINATE_GRACE_SECONDS)
        except Exception:
            pass

    async def _terminate_process(self, proc: subprocess.Popen) -> None:
        """Async wrapper: terminate, wait up to grace, then kill - without blocking the loop."""
        if proc.poll() is not None:
            return
        try:
            proc.terminate()
        except Exception:
            pass

        deadline = time.monotonic() + self.TERMINATE_GRACE_SECONDS
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                return
            await asyncio.sleep(0.05)

        with suppress(Exception):
            proc.kill()

    def stop_server(self, name: str) -> None:
        """Stop a single MCP server (synchronous; safe to call without a running loop)."""
        self.registry.set_server_health(name, HealthStatus.STOPPING.value)
        client_meta = self._mcp_clients.pop(name, None)
        if isinstance(client_meta, dict) and client_meta.get("kind") == "persistent-stdio":
            cm = client_meta.get("context_manager")
            loop = client_meta.get("loop")
            if cm is not None and loop is not None and not loop.is_closed():
                try:
                    future = asyncio.run_coroutine_threadsafe(cm.__aexit__(None, None, None), loop)
                    future.result(timeout=5)
                except Exception:
                    pass

        proc = self._processes.pop(name, None)
        if proc is not None:
            self._graceful_terminate(proc)

        self.registry.set_server_running(name, running=False)
        self.registry.set_server_health(name, HealthStatus.UNKNOWN.value)

    async def astop_server(self, name: str) -> None:
        """Stop a single MCP server from within an event loop."""
        self.registry.set_server_health(name, HealthStatus.STOPPING.value)
        await self._teardown_server(name)
        self.registry.set_server_running(name, running=False)
        self.registry.set_server_health(name, HealthStatus.UNKNOWN.value)

    def stop_all(self) -> None:
        """Stop all running MCP servers (synchronous)."""
        names = set(self._processes.keys()) | set(self.registry.get_running_servers())
        for name in names:
            self.stop_server(name)

        for name in self.registry.get_running_servers():
            self.registry.set_server_running(name, running=False)

    async def astop_all(self) -> None:
        """Stop all running MCP servers in parallel from within an event loop."""
        names = set(self._processes.keys()) | set(self.registry.get_running_servers())
        if names:
            await asyncio.gather(
                *(self.astop_server(name) for name in names), return_exceptions=True
            )

        for name in self.registry.get_running_servers():
            self.registry.set_server_running(name, running=False)

    def running_count(self) -> int:
        """Number of currently running servers."""
        return len(self.registry.get_running_servers())

    def list_available_tools(self) -> list[str]:
        """List all available tool names."""
        return [
            schema.name
            for schema in [
                self.registry.get_tool_schema(n)
                for n in [
                    t for server_tools in self.registry._server_tools.values() for t in server_tools
                ]
            ]
            if schema is not None
        ]

    def get_tool_schemas(self) -> list[dict[str, Any]]:
        """Get all tool schemas for LLM function calling."""
        return self.registry.get_all_tool_schemas()

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Call an MCP tool by name.

        fetch/memory currently run via local implementations.
        Other servers expose structured unsupported/service-unavailable results.
        """

        server_name = self.registry.get_server_for_tool(tool_name)
        if not server_name:
            raise ValueError(f"Unknown tool: {tool_name}")

        # Liveness gate: if a tracked subprocess died, attempt a bounded restart
        # before dispatching the call.
        if server_name in self._processes and not self._is_process_alive(server_name):
            await self._restart_server(server_name)

        server_state = self.registry.get_all_servers().get(server_name)
        mode = server_state.execution_mode if server_state else "unknown"

        call_started = time.monotonic()
        try:
            return await self._dispatch_call_tool(server_name, tool_name, arguments, mode)
        finally:
            latency_ms = (time.monotonic() - call_started) * 1000.0
            self.registry.set_last_call_latency(server_name, latency_ms)

    async def _dispatch_call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: dict[str, Any],
        mode: str,
    ) -> Any:
        try:
            if server_name == "fetch" and tool_name == "fetch":
                violation = self._check_fetch_constraints(arguments)
                if violation is not None:
                    self.registry.record_tool_call(server_name, success=False)
                    return violation
                content = await self._call_fetch(arguments)
                self.registry.record_tool_call(server_name, success=True)
                self.registry.set_server_health(server_name, "healthy")
                return self._tool_result(
                    ok=True,
                    server=server_name,
                    tool=tool_name,
                    execution_mode=mode,
                    content=content,
                    structured_content=None,
                )
            if server_name == "memory":
                content = await self._call_memory(tool_name, arguments)
                self.registry.record_tool_call(server_name, success=True)
                self.registry.set_server_health(server_name, "healthy")
                return self._tool_result(
                    ok=True,
                    server=server_name,
                    tool=tool_name,
                    execution_mode=mode,
                    content=content,
                    structured_content=None,
                )
            if server_name == "chrome-devtools":
                try:
                    content, structured = await self._call_chrome(tool_name, arguments)
                    self.registry.record_tool_call(server_name, success=True)
                    self.registry.set_server_health(server_name, "healthy")
                    return self._tool_result(
                        ok=True,
                        server=server_name,
                        tool=tool_name,
                        execution_mode=mode,
                        content=content,
                        structured_content=structured,
                    )
                except Exception as exc:
                    message = str(exc)
                    self.registry.record_tool_call(server_name, success=False)
                    self.registry.set_server_error(
                        server_name, message, error_type="service_unavailable"
                    )
                    return self._tool_result(
                        ok=False,
                        server=server_name,
                        tool=tool_name,
                        execution_mode=mode,
                        error_type="service_unavailable",
                        message=message,
                        suggestion="Start the chrome-devtools MCP service or switch to a browser-capable local setup.",
                    )
            if server_name == "burp":
                try:
                    content, structured = await self._call_burp(tool_name, arguments)
                    self.registry.record_tool_call(server_name, success=True)
                    self.registry.set_server_health(server_name, "healthy")
                    return self._tool_result(
                        ok=True,
                        server=server_name,
                        tool=tool_name,
                        execution_mode=mode,
                        content=content,
                        structured_content=structured,
                    )
                except Exception as exc:
                    message = str(exc)
                    self.registry.record_tool_call(server_name, success=False)
                    self.registry.set_server_error(
                        server_name, message, error_type="service_unavailable"
                    )
                    return self._tool_result(
                        ok=False,
                        server=server_name,
                        tool=tool_name,
                        execution_mode=mode,
                        error_type="service_unavailable",
                        message=message,
                        suggestion="Start the Burp MCP service and verify the proxy integration is ready.",
                    )

            message = (
                f"MCP tool '{tool_name}' is registered in {mode} mode but is not executable yet."
            )
            suggestion = (
                "Use a local alternative, or enable a runnable MCP backend for this service."
            )
            self.registry.record_tool_call(server_name, success=False)
            self.registry.set_server_error(server_name, message, error_type="unsupported_mode")
            return self._tool_result(
                ok=False,
                server=server_name,
                tool=tool_name,
                execution_mode=mode,
                error_type="unsupported_mode",
                message=message,
                suggestion=suggestion,
            )
        except Exception as exc:
            self.registry.record_tool_call(server_name, success=False)
            self.registry.set_server_error(server_name, str(exc), error_type="execution_failed")
            return self._tool_result(
                ok=False,
                server=server_name,
                tool=tool_name,
                execution_mode=mode,
                error_type="execution_failed",
                message=str(exc),
                suggestion="Inspect the MCP service health and tool arguments, then retry.",
            )

    async def _call_fetch(self, args: dict) -> str:
        """Execute a fetch request using httpx."""
        try:
            import httpx

            url = args.get("url", "")
            method = args.get("method", "GET").upper()
            headers = args.get("headers", {})
            body = args.get("body")

            async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    content=body,
                )

            result = f"Status: {response.status_code}\n"
            result += f"Headers: {dict(response.headers)}\n"
            result += f"Body (first 2000 chars): {response.text[:2000]}"
            return result

        except ImportError:
            return "[!] httpx is not installed; cannot execute fetch request"
        except Exception as e:
            return f"[!] fetch request failed: {e}"

    async def _call_memory(self, tool_name: str, args: dict) -> str:
        """Execute a memory tool call (local implementation)."""
        from vulnbot.agent.memory import MemoryStore

        store = MemoryStore()

        if tool_name == "save":
            store.save(args.get("key", ""), args.get("value", ""))
            return f"[+] Saved: {args.get('key', '')}"
        elif tool_name == "retrieve":
            value = store.retrieve(args.get("key", ""))
            return str(value) if value else "[-] Not found"
        return "[!] Unknown memory tool"

    async def _call_chrome(self, tool_name: str, args: dict) -> tuple[str, dict[str, Any] | None]:
        """Execute a Chrome DevTools tool call."""
        session = await self._get_or_create_persistent_stdio_session("chrome-devtools")
        result = await session.call_tool(tool_name, arguments=args)
        rendered, _, is_error = self._render_mcp_call_result(result)
        if is_error:
            raise RuntimeError(rendered or "chrome-devtools call returned an error")
        _, structured, _ = self._render_mcp_call_result(result)
        return rendered, structured

    async def _call_burp(self, tool_name: str, args: dict) -> tuple[str, dict[str, Any] | None]:
        """Execute a Burp Suite tool call."""
        session = await self._get_or_create_persistent_stdio_session("burp")
        result = await session.call_tool(tool_name, arguments=args)
        rendered, _, is_error = self._render_mcp_call_result(result)
        if is_error:
            raise RuntimeError(rendered or "burp call returned an error")
        _, structured, _ = self._render_mcp_call_result(result)
        return rendered, structured
