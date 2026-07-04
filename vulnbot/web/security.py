"""Web UI security helpers (SEC-3)."""

from __future__ import annotations

import os
import secrets
from typing import Any, Callable

WEB_AUTH_COOKIE = "vulnbot_web_token"
WEB_AUTH_HEADER = "X-VulnBot-Token"
MUTATING_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})


def resolve_web_auth_token(explicit: str | None = None) -> str:
    """Return the configured token or generate one for localhost-only use."""
    token = (explicit or os.environ.get("VULNBOT_WEB_AUTH_TOKEN", "")).strip()
    if token:
        return token
    return secrets.token_urlsafe(32)


def require_remote_web_auth_token(allow_remote: bool, explicit: str | None = None) -> str:
    """Remote binds must set VULNBOT_WEB_AUTH_TOKEN explicitly."""
    token = (explicit or os.environ.get("VULNBOT_WEB_AUTH_TOKEN", "")).strip()
    if allow_remote and not token:
        raise RuntimeError(
            "Refusing to start the Web UI on a non-local address without "
            "VULNBOT_WEB_AUTH_TOKEN. Set a strong token in the environment first."
        )
    return token or secrets.token_urlsafe(32)


def trusted_hosts_for(bind_host: str, port: int, *, allow_remote: bool) -> list[str]:
    """Hosts allowed by TrustedHostMiddleware for the current bind mode."""
    if allow_remote and bind_host in {"0.0.0.0", "::"}:
        return ["*"]
    hosts = ["localhost", "127.0.0.1", "[::1]", bind_host]
    if bind_host in {"127.0.0.1", "localhost", "::1"}:
        hosts.extend(
            [
                f"127.0.0.1:{port}",
                f"localhost:{port}",
                f"[::1]:{port}",
            ]
        )
    return list(dict.fromkeys(host for host in hosts if host))


def _request_token(request: Any) -> str:
    auth_header = str(getattr(request.headers, "get", lambda *_: "")("authorization", "")).strip()
    if auth_header.lower().startswith("bearer "):
        return auth_header[7:].strip()
    header_token = str(getattr(request.headers, "get", lambda *_: "")(WEB_AUTH_HEADER, "")).strip()
    if header_token:
        return header_token
    return str(getattr(request, "cookies", {}).get(WEB_AUTH_COOKIE, "")).strip()


def _is_public_api_path(path: str) -> bool:
    return path in {"/api/health"}


def install_web_security_middleware(
    app: Any,
    *,
    auth_token: str,
    bind_host: str,
    port: int,
    allow_remote: bool,
) -> None:
    """Add TrustedHost pinning and token auth for mutating /api routes."""
    from starlette.middleware.trustedhost import TrustedHostMiddleware
    from starlette.requests import Request
    from starlette.responses import JSONResponse, Response

    allowed_hosts = trusted_hosts_for(bind_host, port, allow_remote=allow_remote)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

    @app.middleware("http")
    async def web_auth_middleware(request: Request, call_next: Callable) -> Response:
        path = request.url.path
        if path.startswith("/api/") and request.method in MUTATING_METHODS and not _is_public_api_path(
            path
        ):
            if _request_token(request) != auth_token:
                return JSONResponse(
                    status_code=401,
                    content={
                        "detail": "Missing or invalid Web UI auth token.",
                        "code": "web_auth_required",
                    },
                )

        response = await call_next(request)

        if WEB_AUTH_COOKIE not in request.cookies and path in {"/", "/index.html"}:
            response.set_cookie(
                WEB_AUTH_COOKIE,
                auth_token,
                httponly=True,
                samesite="strict",
                secure=allow_remote and bind_host not in {"127.0.0.1", "localhost", "::1"},
            )
        return response
