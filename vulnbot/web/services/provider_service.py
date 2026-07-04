"""Provider preset + model-listing service for the Web UI backend.

Powers the Settings page dropdowns: the static list of provider presets
(provider / base URL) and a live "list models" call that reuses the saved
API key server-side (the key is never sent to the browser).
"""

from __future__ import annotations

from vulnbot.config.schema import PROVIDER_PRESETS, LLMProvider
from vulnbot.config.settings import (
    fetch_provider_models,
    load_config,
    uses_verified_provider_transport,
)
from vulnbot.web.schemas import (
    ProviderModelsRequest,
    ProviderModelsResponse,
    ProviderPresetView,
    ProvidersView,
)


def get_provider_presets() -> ProvidersView:
    """Return the built-in provider presets for the Settings dropdowns."""
    providers = [
        ProviderPresetView(
            id=provider.value,
            label=str(preset.get("label", provider.value)),
            base_url=str(preset.get("base_url", "")),
            default_model=str(preset.get("default_model", "")),
        )
        for provider, preset in PROVIDER_PRESETS.items()
    ]
    return ProvidersView(providers=providers)


def _resolve_base_url(request: ProviderModelsRequest, config_base_url: str) -> str:
    """Pick the base URL to query: request override > provider preset > config."""
    explicit = (request.base_url or "").strip()
    if explicit:
        return explicit
    if request.provider:
        try:
            preset = PROVIDER_PRESETS.get(LLMProvider(request.provider.lower()))
        except ValueError:
            preset = None
        if preset and preset.get("base_url"):
            return str(preset["base_url"])
    return config_base_url.strip()


def _is_allowed_base_url(base_url: str, config_base_url: str) -> bool:
    """Only send the saved API key to hosts the operator already trusts.

    SEC-2: without this check, any caller of this endpoint (including a
    cross-origin request the operator's browser sends without their
    knowledge, since the web API has no CSRF/auth protection) could name an
    arbitrary ``base_url`` and have the server-side API key sent to it. We
    only honor a request base_url if it's a known provider preset or the
    base_url already saved in config -- an unsaved custom URL must be saved
    first (establishing intent) before it can be queried with the real key.
    """
    if not uses_verified_provider_transport(base_url):
        return False
    candidate = base_url.strip()
    if not candidate:
        return False
    if candidate == config_base_url.strip():
        return True
    return any(candidate == preset.get("base_url") for preset in PROVIDER_PRESETS.values())


def fetch_models(request: ProviderModelsRequest) -> ProviderModelsResponse:
    """List models for a provider/base URL using the saved API key.

    The key is read from the saved config (never accepted from the browser).
    Returns an empty list with a hint when no key is configured.
    """
    config = load_config()
    base_url = _resolve_base_url(request, config.llm.base_url)
    api_key = config.llm.primary_key()

    if not api_key:
        return ProviderModelsResponse(
            base_url=base_url,
            models=[],
            has_api_key=False,
            detail="No API key configured. Save your API key first, then refresh.",
        )

    if not uses_verified_provider_transport(base_url):
        return ProviderModelsResponse(
            base_url=base_url,
            models=[],
            has_api_key=True,
            detail="Provider model listing requires HTTPS, except for loopback HTTP URLs.",
        )

    if not _is_allowed_base_url(base_url, config.llm.base_url):
        return ProviderModelsResponse(
            base_url=base_url,
            models=[],
            has_api_key=True,
            detail="Save this base URL before listing its models.",
        )

    models = fetch_provider_models(base_url, api_key)
    detail = "" if models else "The provider returned no models (check the base URL / key)."
    return ProviderModelsResponse(
        base_url=base_url,
        models=models,
        has_api_key=True,
        detail=detail,
    )
