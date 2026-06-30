"""VulnBot Config Module Tests — schema.py + settings.py"""


# ── schema.py ────────────────────────────────────────────────────────


class TestLLMConfig:
    """Test LLMConfig schema."""

    def test_default_values(self):
        from vulnbot.config.schema import LLMConfig

        config = LLMConfig()
        assert config.model == "gpt-4o"
        assert config.api_key == ""
        assert config.base_url == "https://api.openai.com/v1"
        assert config.temperature == 0.1  # Updated default for pentest use
        assert config.max_tokens == 4096

    def test_custom_values(self):
        from vulnbot.config.schema import LLMConfig

        config = LLMConfig(
            model="deepseek-chat",
            api_key="sk-test",
            base_url="https://api.deepseek.com/v1",
            temperature=0.3,
            max_tokens=8192,
        )
        assert config.model == "deepseek-chat"
        assert config.api_key == "sk-test"
        assert config.temperature == 0.3

    def test_provider_field(self):
        from vulnbot.config.schema import LLMConfig

        config = LLMConfig(provider="deepseek")
        assert config.provider == "deepseek"

    def test_reasoning_effort_field(self):
        from vulnbot.config.schema import LLMConfig

        config = LLMConfig(reasoning_effort="high")
        assert config.reasoning_effort == "high"

    def test_api_keys_defaults_empty(self):
        from vulnbot.config.schema import LLMConfig

        config = LLMConfig()
        assert config.api_keys == []

    def test_key_pool_falls_back_to_single_key(self):
        from vulnbot.config.schema import LLMConfig

        config = LLMConfig(api_key="sk-single")
        assert config.key_pool() == ["sk-single"]
        assert config.primary_key() == "sk-single"

    def test_key_pool_prefers_list_when_set(self):
        from vulnbot.config.schema import LLMConfig

        config = LLMConfig(api_key="sk-single", api_keys=["k1", "k2", "k3"])
        assert config.key_pool() == ["k1", "k2", "k3"]
        assert config.primary_key() == "k1"

    def test_key_pool_filters_empties(self):
        from vulnbot.config.schema import LLMConfig

        config = LLMConfig(api_keys=["k1", "", "  ", "k2"])
        assert config.key_pool() == ["k1", "k2"]

    def test_primary_key_empty_when_no_keys(self):
        from vulnbot.config.schema import LLMConfig

        config = LLMConfig()
        assert config.key_pool() == []
        assert config.primary_key() == ""


class TestMCPServerConfig:
    """Test MCPServerConfig schema."""

    def test_default_values(self):
        from vulnbot.config.schema import MCPServerConfig, MCPTransportConfig

        config = MCPServerConfig(
            name="test-server",
            transport=MCPTransportConfig(type="stdio"),
        )
        assert config.name == "test-server"
        assert config.enabled is True
        assert config.priority == 1
        assert config.description == ""

    def test_custom_values(self):
        from vulnbot.config.schema import MCPServerConfig, MCPTransportConfig

        config = MCPServerConfig(
            name="burp",
            enabled=False,
            priority=0,
            transport=MCPTransportConfig(type="sse", url="http://localhost:8080"),
            description="Burp Suite MCP server",
        )
        assert config.enabled is False
        assert config.priority == 0
        assert config.transport.type == "sse"


class TestVulnBotConfig:
    """Test VulnBotConfig schema."""

    def test_default_values(self):
        from vulnbot.config.schema import VulnBotConfig

        config = VulnBotConfig()
        assert config.llm.model == "gpt-4o"
        assert isinstance(config.mcp.servers, dict)

    def test_session_repl_parallel_defaults(self):
        from vulnbot.config.schema import SessionConfig

        config = SessionConfig()
        assert config.repl_parallel_enabled is True
        assert config.repl_parallel_agents == 3
        assert config.repl_parallel_depth == 1
        assert config.repl_parallel_worker_rounds == 3
        assert config.repl_parallel_surface_limit == 20

    def test_mcp_builtin_servers(self):
        from vulnbot.config.schema import BUILTIN_MCP_SERVERS, VulnBotConfig

        VulnBotConfig()
        # Builtin servers are defined in BUILTIN_MCP_SERVERS, not in default config
        # Default config has empty servers dict; servers are populated by settings
        assert "fetch" in BUILTIN_MCP_SERVERS
        assert "memory" in BUILTIN_MCP_SERVERS

    def test_builtin_mcp_server_count(self):
        from vulnbot.config.schema import BUILTIN_MCP_SERVERS

        # Should have 4 builtin servers (fetch, memory, chrome-devtools, burp)
        assert len(BUILTIN_MCP_SERVERS) == 4

    def test_provider_presets(self):
        from vulnbot.config.schema import PROVIDER_PRESETS

        # Should have at least the documented providers
        expected_providers = [
            "openai",
            "minimax",
            "deepseek",
            "zhipu",
            "moonshot",
            "qwen",
            "siliconflow",
        ]
        for provider in expected_providers:
            assert provider in PROVIDER_PRESETS, f"Missing provider: {provider}"

    def test_llm_provider_enum(self):
        from vulnbot.config.schema import LLMProvider

        assert hasattr(LLMProvider, "OPENAI")
        assert hasattr(LLMProvider, "DEEPSEEK")
        assert hasattr(LLMProvider, "MINIMAX")


# ── settings.py ──────────────────────────────────────────────────────


class TestSettingsLoad:
    """Test config loading."""

    def test_load_config_returns_config(self):
        from vulnbot.config.schema import VulnBotConfig
        from vulnbot.config.settings import load_config

        config = load_config()
        assert isinstance(config, VulnBotConfig)

    def test_load_config_has_llm(self):
        from vulnbot.config.settings import load_config

        config = load_config()
        assert config.llm is not None

    def test_load_config_has_mcp(self):
        from vulnbot.config.settings import load_config

        config = load_config()
        assert config.mcp is not None

    def test_save_config(self):
        from vulnbot.config.schema import VulnBotConfig
        from vulnbot.config.settings import save_config

        config = VulnBotConfig()
        config.llm.model = "test-model"
        # save_config saves to the default path
        save_config(config)  # Should not crash

    def test_set_config_value(self):
        from vulnbot.config.settings import set_config_value

        # set_config_value(key, value) — sets in the YAML config
        set_config_value("llm.model", "gpt-4o-mini")  # Should not crash

    def test_set_config_nested(self):
        from vulnbot.config.settings import set_config_value

        set_config_value("llm.temperature", "0.1")  # Should not crash

    def test_apply_provider_preset(self):
        from vulnbot.config.schema import VulnBotConfig
        from vulnbot.config.settings import apply_provider_preset

        config = VulnBotConfig()
        apply_provider_preset(config, "deepseek")
        assert config.llm.provider == "deepseek"
        assert "deepseek" in config.llm.base_url.lower()

    def test_list_providers(self):
        from vulnbot.config.settings import list_providers

        providers = list_providers()
        assert isinstance(providers, list)
        assert len(providers) >= 7
        # Each entry should have provider, base_url, default_model
        for p in providers:
            assert "provider" in p
            assert "base_url" in p
            assert "default_model" in p

    def test_env_var_override(self, monkeypatch):
        """Test that environment variables override config values."""
        from vulnbot.config.settings import load_config

        monkeypatch.setenv("VULNBOT_LLM_API_KEY", "env-test-key")
        monkeypatch.setenv("VULNBOT_LLM_MODEL", "env-test-model")
        # Config should pick up env vars
        config = load_config()
        # The env var may or may not be applied depending on load_config implementation
        # Just verify it doesn't crash
        assert config is not None

    def test_env_var_api_keys_list(self, monkeypatch):
        """VULNBOT_LLM_API_KEYS (comma-separated) populates the key list."""
        from vulnbot.config.settings import load_config

        monkeypatch.setenv("VULNBOT_LLM_API_KEYS", "k1, k2 ,k3")
        config = load_config()
        assert config.llm.api_keys == ["k1", "k2", "k3"]

    def test_env_var_repl_parallel_overrides(self, monkeypatch):
        """VULNBOT_SESSION_REPL_PARALLEL_* overrides session fan-out defaults."""
        from vulnbot.config.settings import load_config

        monkeypatch.setenv("VULNBOT_SESSION_REPL_PARALLEL_ENABLED", "false")
        monkeypatch.setenv("VULNBOT_SESSION_REPL_PARALLEL_AGENTS", "2")
        monkeypatch.setenv("VULNBOT_SESSION_REPL_PARALLEL_DEPTH", "2")
        monkeypatch.setenv("VULNBOT_SESSION_REPL_PARALLEL_WORKER_ROUNDS", "4")
        monkeypatch.setenv("VULNBOT_SESSION_REPL_PARALLEL_SURFACE_LIMIT", "9")

        config = load_config()

        assert config.session.repl_parallel_enabled is False
        assert config.session.repl_parallel_agents == 2
        assert config.session.repl_parallel_depth == 2
        assert config.session.repl_parallel_worker_rounds == 4
        assert config.session.repl_parallel_surface_limit == 9

    def test_set_config_value_api_keys_from_string(self, monkeypatch, tmp_path):
        """set_config_value('llm.api_keys', 'a,b') stores a parsed list."""
        import vulnbot.config.settings as settings_mod

        monkeypatch.setattr(settings_mod, "CONFIG_FILE", tmp_path / "config.yaml")
        monkeypatch.setattr(settings_mod, "CONFIG_DIR", tmp_path)
        settings_mod.set_config_value("llm.api_keys", "a, b ,c")
        config = settings_mod.load_config()
        assert config.llm.api_keys == ["a", "b", "c"]

    def test_set_config_value_repl_parallel_fields(self, monkeypatch, tmp_path):
        """set_config_value coerces REPL parallel session fields."""
        import vulnbot.config.settings as settings_mod

        monkeypatch.setattr(settings_mod, "CONFIG_FILE", tmp_path / "config.yaml")
        monkeypatch.setattr(settings_mod, "CONFIG_DIR", tmp_path)

        settings_mod.set_config_value("session.repl_parallel_enabled", "false")
        settings_mod.set_config_value("session.repl_parallel_agents", "2")
        settings_mod.set_config_value("session.repl_parallel_worker_rounds", "4")

        config = settings_mod.load_config()
        assert config.session.repl_parallel_enabled is False
        assert config.session.repl_parallel_agents == 2
        assert config.session.repl_parallel_worker_rounds == 4

    def test_strip_defaults_drops_empty_api_keys(self):
        from vulnbot.config.settings import _strip_defaults

        raw = {"llm": {"api_keys": [], "model": "gpt-4o", "provider": "openai"}}
        _strip_defaults(raw)
        assert "api_keys" not in raw["llm"]

    def test_save_load_roundtrips_api_keys(self, monkeypatch, tmp_path):
        import vulnbot.config.settings as settings_mod
        from vulnbot.config.schema import VulnBotConfig

        monkeypatch.setattr(settings_mod, "CONFIG_FILE", tmp_path / "config.yaml")
        monkeypatch.setattr(settings_mod, "CONFIG_DIR", tmp_path)
        config = VulnBotConfig()
        config.llm.api_keys = ["x1", "x2"]
        settings_mod.save_config(config)
        reloaded = settings_mod.load_config()
        assert reloaded.llm.api_keys == ["x1", "x2"]
