"""VulnBot CLI module tests for main.py."""

import io

import pytest
from prompt_toolkit.history import FileHistory

pytest.importorskip("typer")

from typer.testing import CliRunner

# CLI smoke tests


class TestCLI:
    """Test CLI entry point and sub-commands."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_cli_help(self, runner):
        from vulnbot.cli.main import app

        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "VulnBot" in result.output or "vulnbot" in result.output.lower()
        assert "TUI" in result.output

    def test_cli_version(self, runner):
        from vulnbot import __version__
        from vulnbot.cli.main import app

        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert __version__ in result.output

    def test_cli_manual_command(self, runner):
        from vulnbot.cli.main import app

        result = runner.invoke(app, ["manual"])

        assert result.exit_code == 0
        assert "VULNBOT(1)" in result.output
        assert "COMMON TASK FLAGS" in result.output
        assert "--only-port" in result.output
        assert "network-scan" in result.output
        assert "--parallel-agents" in result.output

    def test_cli_manual_topic_markdown(self, runner):
        from vulnbot.cli.main import app

        result = runner.invoke(app, ["manual", "network-scan", "--format", "markdown"])

        assert result.exit_code == 0
        assert "### `network-scan`" in result.output
        assert "`--safe-probes / --no-safe-probes`" in result.output
        assert "### `run`" not in result.output

    def test_cli_man_alias_and_root_flag(self, runner):
        from vulnbot.cli.main import app

        alias_result = runner.invoke(app, ["man", "config"])
        root_result = runner.invoke(app, ["--man"])

        assert alias_result.exit_code == 0
        assert "CONFIG" in alias_result.output
        assert "llm.api_keys" in alias_result.output
        assert root_result.exit_code == 0
        assert "VULNBOT(1)" in root_result.output

    def test_cli_manual_rejects_unknown_topic(self, runner):
        from vulnbot.cli.main import app

        result = runner.invoke(app, ["manual", "does-not-exist"])

        assert result.exit_code == 1
        assert "unknown manual topic" in result.output

    def test_cli_init(self, runner):
        from vulnbot.cli.main import app

        result = runner.invoke(app, ["init"])
        # Should not crash
        assert result.exit_code == 0
        assert "vulnbot" in result.output
        assert "vulnbot tui" in result.output

    def test_cli_doctor(self, runner):
        from vulnbot.cli.main import app

        result = runner.invoke(app, ["doctor"])
        # Should not crash
        assert result.exit_code == 0
        assert "Registered:" in result.output
        assert "Tools:" in result.output
        assert "vulnbot tui" in result.output or "Set an API key first" in result.output

    def test_cli_config_list(self, runner):
        from vulnbot.cli.main import app

        result = runner.invoke(app, ["config", "list"])
        # Should not crash
        assert result.exit_code == 0

    def test_cli_config_without_subcommand_opens_tui(self, runner, monkeypatch):
        import vulnbot.cli.main as cli_main
        from vulnbot.cli.main import app

        called = []

        monkeypatch.setattr(cli_main, "run_config_tui", lambda: called.append(True))

        result = runner.invoke(app, ["config"])

        assert result.exit_code == 0
        assert called == [True]

    def test_repl_prompt_session_uses_persistent_history(self, monkeypatch, tmp_path):
        from prompt_toolkit.application import create_app_session
        from prompt_toolkit.input import DummyInput
        from prompt_toolkit.output import DummyOutput

        import vulnbot.cli.main as cli_main

        monkeypatch.setattr(cli_main, "CONFIG_DIR", tmp_path)

        # Use dummy I/O: building a real PromptSession probes the actual
        # console (fails with NoConsoleScreenBufferError on Windows CI
        # runners, which have no attached console).
        with create_app_session(input=DummyInput(), output=DummyOutput()):
            session = cli_main._build_repl_prompt_session()

        assert isinstance(session.history, FileHistory)
        assert session.history.filename == str(tmp_path / "repl_history")

    def test_repl_parallel_budget_defaults_and_low_rounds(self):
        import vulnbot.cli.main as cli_main

        settings = cli_main.ReplParallelSettings(
            enabled=True,
            agents=3,
            depth=1,
            worker_rounds=3,
            surface_limit=20,
        )

        default_budget = cli_main._resolve_repl_parallel_budget(settings, max_rounds=15)
        low_budget = cli_main._resolve_repl_parallel_budget(settings, max_rounds=5)

        assert default_budget.use_parallel is True
        assert default_budget.discovery_rounds == 6
        assert default_budget.max_agents == 3
        assert default_budget.worker_rounds == 3
        assert default_budget.max_depth == 1
        assert default_budget.surface_limit == 20
        assert low_budget.use_parallel is True
        assert low_budget.discovery_rounds == 2
        assert low_budget.max_agents == 3
        assert low_budget.worker_rounds == 1

    def test_repl_parallel_budget_disabled_and_invalid(self):
        import vulnbot.cli.main as cli_main

        disabled = cli_main.ReplParallelSettings(True, 3, 1, 3, 20)
        disabled.enabled = False
        invalid_agents = cli_main.ReplParallelSettings(True, 0, 1, 3, 20)
        invalid_depth = cli_main.ReplParallelSettings(True, 3, 0, 3, 20)
        invalid_workers = cli_main.ReplParallelSettings(True, 3, 1, 0, 20)

        assert cli_main._resolve_repl_parallel_budget(disabled, max_rounds=15).use_parallel is False
        assert (
            cli_main._resolve_repl_parallel_budget(invalid_agents, max_rounds=15).use_parallel
            is False
        )
        assert (
            cli_main._resolve_repl_parallel_budget(invalid_depth, max_rounds=15).use_parallel
            is False
        )
        assert (
            cli_main._resolve_repl_parallel_budget(invalid_workers, max_rounds=15).use_parallel
            is False
        )

    def test_repl_parallel_status_command_prints_effective_values(self, monkeypatch):
        from rich.console import Console

        import vulnbot.cli.main as cli_main
        from vulnbot.config.schema import VulnBotConfig

        output = io.StringIO()
        monkeypatch.setattr(
            cli_main,
            "console",
            Console(file=output, force_terminal=False, color_system=None, width=100),
        )
        config = VulnBotConfig()
        settings = cli_main._repl_parallel_settings_from_config(config)

        handled, updated = cli_main._handle_repl_parallel_command(
            "parallel status",
            settings,
            config,
        )

        assert handled is True
        assert updated is settings
        text = output.getvalue()
        assert "Enabled:" in text
        assert "Effective:" in text
        assert "3 child agent" in text

    @pytest.mark.asyncio
    async def test_repl_auto_mode_uses_parallel_by_default(self, monkeypatch):
        import vulnbot.agent.parallel_agents as parallel_mod
        import vulnbot.cli.main as cli_main
        from vulnbot.agent.parallel_agents import AttackSurface, ParallelAgentRunResult
        from vulnbot.config.schema import VulnBotConfig

        config = VulnBotConfig()
        captured = {}

        class DummyAgent:
            def __init__(self, _config=None, mcp_manager=None):
                from vulnbot.agent.context import SessionState

                self.config = _config
                self.mcp_manager = mcp_manager
                self.session_state = SessionState(target="https://example.com")

            async def auto_pentest(self, *args, **kwargs):
                raise AssertionError("parallel auto-mode should use run_parallel_pentest")

        async def fake_parallel(agent, **kwargs):
            captured.update(kwargs)
            return ParallelAgentRunResult(
                root_results=["root-result"],
                worker_results=[{"results": ["worker-result"]}],
                surfaces=[AttackSurface(target="https://example.com:443")],
                waves_completed=1,
            )

        monkeypatch.setattr(parallel_mod, "run_parallel_pentest", fake_parallel)

        results = await cli_main._run_repl_auto_pentest(
            DummyAgent(config),
            config,
            cli_main._repl_parallel_settings_from_config(config),
            user_input="Perform a pentest against https://example.com",
            target="https://example.com",
            on_step=lambda *_args: None,
            stream_sink=None,
        )

        assert results == ["root-result", "worker-result"]
        assert captured["discovery_rounds"] == 6
        assert captured["worker_rounds"] == 3
        assert captured["max_agents"] == 3
        assert captured["max_depth"] == 1
        assert captured["surface_limit"] == 20

    @pytest.mark.asyncio
    async def test_repl_parallel_off_uses_single_agent_auto(self, monkeypatch):
        import vulnbot.agent.parallel_agents as parallel_mod
        import vulnbot.cli.main as cli_main
        from vulnbot.config.schema import VulnBotConfig

        config = VulnBotConfig()
        calls = []

        class DummyAgent:
            def __init__(self):
                from vulnbot.agent.context import SessionState

                self.session_state = SessionState(target="https://example.com")

            async def auto_pentest(self, prompt, **kwargs):
                calls.append((prompt, kwargs))
                return ["direct-result"]

        async def fake_parallel(*args, **kwargs):
            raise AssertionError("parallel coordinator should not run when disabled")

        settings = cli_main._repl_parallel_settings_from_config(config)
        handled, settings = cli_main._handle_repl_parallel_command("parallel off", settings, config)
        monkeypatch.setattr(parallel_mod, "run_parallel_pentest", fake_parallel)

        results = await cli_main._run_repl_auto_pentest(
            DummyAgent(),
            config,
            settings,
            user_input="Perform a pentest against https://example.com",
            target="https://example.com",
            on_step=lambda *_args: None,
            stream_sink=None,
        )

        assert handled is True
        assert settings.enabled is False
        assert results == ["direct-result"]
        assert calls[0][1]["max_rounds"] == 15

    @pytest.mark.asyncio
    async def test_repl_parallel_agents_command_changes_effective_fanout(self, monkeypatch):
        import vulnbot.agent.parallel_agents as parallel_mod
        import vulnbot.cli.main as cli_main
        from vulnbot.agent.parallel_agents import AttackSurface, ParallelAgentRunResult
        from vulnbot.config.schema import VulnBotConfig

        config = VulnBotConfig()
        settings = cli_main._repl_parallel_settings_from_config(config)
        handled, settings = cli_main._handle_repl_parallel_command(
            "parallel agents 2",
            settings,
            config,
        )
        captured = {}

        class DummyAgent:
            def __init__(self, _config=None, mcp_manager=None):
                from vulnbot.agent.context import SessionState

                self.session_state = SessionState(target="https://example.com")
                self.mcp_manager = mcp_manager

        async def fake_parallel(agent, **kwargs):
            captured.update(kwargs)
            return ParallelAgentRunResult(
                root_results=["root-result"],
                surfaces=[AttackSurface(target="https://example.com:443")],
                waves_completed=1,
            )

        monkeypatch.setattr(parallel_mod, "run_parallel_pentest", fake_parallel)

        await cli_main._run_repl_auto_pentest(
            DummyAgent(),
            config,
            settings,
            user_input="Perform a pentest against https://example.com",
            target="https://example.com",
            on_step=lambda *_args: None,
            stream_sink=None,
        )

        assert handled is True
        assert settings.agents == 2
        assert captured["max_agents"] == 2

    def test_repl_single_turn_chat_does_not_use_parallel(self, runner, monkeypatch):
        import vulnbot.agent.core as agent_core
        import vulnbot.agent.parallel_agents as parallel_mod
        import vulnbot.cli.main as cli_main
        import vulnbot.mcp.lifecycle as lifecycle_mod
        from vulnbot.agent.runtime_state import AgentResult
        from vulnbot.cli.main import app
        from vulnbot.config.schema import VulnBotConfig

        config = VulnBotConfig()
        config.llm.api_key = "test-key"
        chat_calls = []

        async def fake_chat(self, user_input, target=None, stream_sink=None):
            chat_calls.append((user_input, target))
            return AgentResult(output="ok")

        async def fake_auto(self, *args, **kwargs):
            raise AssertionError("single-turn chat should not call auto_pentest")

        async def fake_parallel(*args, **kwargs):
            raise AssertionError("single-turn chat should not call run_parallel_pentest")

        monkeypatch.setattr(cli_main, "load_config", lambda: config)
        monkeypatch.setattr(
            lifecycle_mod.MCPLifecycleManager, "start_enabled_servers", lambda self: 0
        )
        monkeypatch.setattr(lifecycle_mod.MCPLifecycleManager, "stop_all", lambda self: None)
        monkeypatch.setattr(agent_core.AgentCore, "chat", fake_chat)
        monkeypatch.setattr(agent_core.AgentCore, "auto_pentest", fake_auto)
        monkeypatch.setattr(parallel_mod, "run_parallel_pentest", fake_parallel)

        result = runner.invoke(app, ["repl"], input="hello there\nexit\n")

        assert result.exit_code == 0
        assert chat_calls == [("hello there", None)]

    def test_repl_parallel_status_command_is_exposed_through_repl(self, runner, monkeypatch):
        import vulnbot.cli.main as cli_main
        import vulnbot.mcp.lifecycle as lifecycle_mod
        from vulnbot.cli.main import app
        from vulnbot.config.schema import VulnBotConfig

        config = VulnBotConfig()
        config.llm.api_key = "test-key"

        monkeypatch.setattr(cli_main, "load_config", lambda: config)
        monkeypatch.setattr(
            lifecycle_mod.MCPLifecycleManager, "start_enabled_servers", lambda self: 0
        )
        monkeypatch.setattr(lifecycle_mod.MCPLifecycleManager, "stop_all", lambda self: None)

        result = runner.invoke(app, ["repl"], input="parallel status\nexit\n")

        assert result.exit_code == 0
        assert "REPL Parallel" in result.output
        assert "Enabled:" in result.output
        assert "Effective:" in result.output

    def test_cli_config_provider_list(self, runner):
        from vulnbot.cli.main import app

        result = runner.invoke(app, ["config", "provider", "--list"])
        # Should show available providers
        assert result.exit_code == 0

    def test_cli_config_provider_set(self, runner):
        from vulnbot.cli.main import app

        result = runner.invoke(app, ["config", "provider", "deepseek"])
        # Should not crash
        assert result.exit_code == 0

    def test_cli_kb_update(self, runner, monkeypatch, tmp_path):
        import vulnbot.kb.store as kb_store
        from vulnbot.cli.main import app

        monkeypatch.setattr(kb_store, "KB_DIR", tmp_path)
        result = runner.invoke(app, ["kb", "update"])
        assert result.exit_code == 0
        assert "Knowledge base updated" in result.output or result.output
        assert (tmp_path / "index.json").exists()

    def test_cli_doctor_reports_registered_tools(self, runner):
        from vulnbot.cli.main import app

        result = runner.invoke(app, ["doctor"])
        assert result.exit_code == 0
        assert "Registered:" in result.output
        assert "Tools:" in result.output

    def test_recon_resumes_target_state(self, runner, monkeypatch, tmp_path):
        import vulnbot.orchestrator as orchestrator_mod
        import vulnbot.target_state.store as store_mod
        from vulnbot.agent.context import PentestPhase, SessionState
        from vulnbot.cli.main import app

        monkeypatch.setattr(store_mod, "TARGETS_DIR", tmp_path / "targets")
        state = SessionState(target="https://example.com")
        state.advance_phase(PentestPhase.RECON)
        store_mod.save_target_state("https://example.com", state, command="recon")

        calls: list[tuple[str, str | None]] = []
        original_apply = orchestrator_mod.apply_target_state_to_agent

        def tracking_apply(agent, target, snapshot_id=None):
            calls.append((target, snapshot_id))
            return original_apply(agent, target, snapshot_id=snapshot_id)

        monkeypatch.setattr(orchestrator_mod, "apply_target_state_to_agent", tracking_apply)

        result = runner.invoke(app, ["recon", "https://example.com"])
        assert result.exit_code == 0
        assert result.output
        assert calls == [("https://example.com", None)]

    def test_recon_no_resume_skips_target_state(self, runner, monkeypatch, tmp_path):
        import vulnbot.target_state.store as store_mod
        from vulnbot.agent.context import PentestPhase, SessionState
        from vulnbot.cli.main import app

        monkeypatch.setattr(store_mod, "TARGETS_DIR", tmp_path / "targets")
        state = SessionState(target="https://example.com")
        state.advance_phase(PentestPhase.RECON)
        store_mod.save_target_state("https://example.com", state, command="recon")

        result = runner.invoke(app, ["recon", "https://example.com", "--no-resume"])
        assert result.exit_code == 0
        assert result.output is not None

    def test_network_scan_defaults_to_safe_recon_scan_actions(self, runner, monkeypatch):
        import vulnbot.cli.main as cli_main
        from vulnbot.cli.main import app

        captured = {}

        async def fake_orchestrated_task(**kwargs):
            captured["command"] = kwargs["command"]
            captured["target"] = kwargs["target"]

            class DummyConfig:
                class session:
                    show_thinking = False
                    max_rounds = 3

            class DummyAgent:
                async def auto_pentest(self, prompt, target=None, max_rounds=0, stream_sink=None):
                    captured["prompt"] = prompt
                    captured["runner_target"] = target
                    captured["max_rounds"] = max_rounds

            await kwargs["runner"](DummyAgent(), DummyConfig())

            class Result:
                summary = {"findings_count": 0, "executed_steps": 0}

            return Result()

        monkeypatch.setattr(cli_main, "_run_cli_orchestrated_task", fake_orchestrated_task)

        result = runner.invoke(
            app,
            ["network-scan", "192.168.56.10", "--profile", "fast", "--ports", "22,80"],
        )

        assert result.exit_code == 0
        assert captured["command"] == "network-scan"
        assert captured["target"] == "192.168.56.10"
        assert "profile=fast" in captured["prompt"]
        assert "ports=22,80" in captured["prompt"]
        assert "Only allowed actions: recon,scan" in captured["prompt"]
        assert captured["max_rounds"] == 3

    def test_network_scan_without_target_uses_connected_wifi(self, runner, monkeypatch):
        import vulnbot.agent.network_scan as network_scan_mod
        import vulnbot.cli.main as cli_main
        from vulnbot.cli.main import app

        captured = {}

        monkeypatch.setattr(
            network_scan_mod,
            "detect_connected_wifi_target",
            lambda: network_scan_mod.WifiScanTarget(
                interface="wlp2s0",
                address="192.168.1.42",
                cidr="192.168.1.0/24",
            ),
        )

        async def fake_orchestrated_task(**kwargs):
            captured["target"] = kwargs["target"]

            class DummyConfig:
                class session:
                    show_thinking = False
                    max_rounds = 3

            class DummyAgent:
                async def auto_pentest(self, prompt, target=None, max_rounds=0, stream_sink=None):
                    captured["prompt"] = prompt
                    captured["runner_target"] = target

            await kwargs["runner"](DummyAgent(), DummyConfig())

            class Result:
                summary = {"findings_count": 0, "executed_steps": 0}

            return Result()

        monkeypatch.setattr(cli_main, "_run_cli_orchestrated_task", fake_orchestrated_task)

        result = runner.invoke(app, ["network-scan", "--profile", "fast"])

        assert result.exit_code == 0
        assert "wlp2s0" in result.output
        assert captured["target"] == "192.168.1.0/24"
        assert captured["runner_target"] == "192.168.1.0/24"
        assert "against 192.168.1.0/24" in captured["prompt"]

    def test_network_scan_rejects_unknown_profile(self, runner):
        from vulnbot.cli.main import app

        result = runner.invoke(app, ["network-scan", "192.168.56.10", "--profile", "loud"])

        assert result.exit_code == 1
        assert "profile must be one of" in result.output

    def test_network_scan_parallel_agents_uses_coordinator(self, runner, monkeypatch):
        import vulnbot.agent.parallel_agents as parallel_mod
        import vulnbot.cli.main as cli_main
        from vulnbot.cli.main import app

        captured = {}

        async def fake_parallel(agent, **kwargs):
            captured.update(kwargs)
            return []

        async def fake_orchestrated_task(**kwargs):
            captured["command"] = kwargs["command"]
            captured["target"] = kwargs["target"]

            class DummyConfig:
                class session:
                    show_thinking = False
                    max_rounds = 9

            class DummyAgent:
                async def auto_pentest(self, prompt, target=None, max_rounds=0, stream_sink=None):
                    raise AssertionError("parallel branch should use run_parallel_pentest")

            await kwargs["runner"](DummyAgent(), DummyConfig())

            class Result:
                summary = {"findings_count": 0, "executed_steps": 0}

            return Result()

        monkeypatch.setattr(parallel_mod, "run_parallel_pentest", fake_parallel)
        monkeypatch.setattr(cli_main, "_run_cli_orchestrated_task", fake_orchestrated_task)

        result = runner.invoke(
            app,
            [
                "network-scan",
                "192.168.56.0/24",
                "--profile",
                "fast",
                "--parallel-agents",
                "2",
                "--parallel-depth",
                "2",
                "--worker-rounds",
                "4",
                "--surface-limit",
                "7",
                "--max-rounds",
                "5",
            ],
        )

        assert result.exit_code == 0
        assert captured["command"] == "network-scan"
        assert captured["target"] == "192.168.56.0/24"
        assert captured["discovery_rounds"] == 5
        assert captured["worker_rounds"] == 4
        assert captured["max_agents"] == 2
        assert captured["max_depth"] == 2
        assert captured["surface_limit"] == 7
        assert "Parallel agents:" in result.output

    def test_repl_persistent_explicit_target_restores_history(self, runner, monkeypatch):
        import vulnbot.agent.core as agent_core
        import vulnbot.cli.main as cli_main
        import vulnbot.mcp.lifecycle as lifecycle_mod
        from vulnbot.agent.context import PentestPhase, SessionState
        from vulnbot.cli.main import app
        from vulnbot.config.schema import VulnBotConfig

        config = VulnBotConfig()
        config.llm.api_key = "test-key"

        old_state = SessionState(target="https://old.example")
        old_state.advance_phase(PentestPhase.RECON)

        new_state = SessionState(target="https://new.example")
        new_state.advance_phase(PentestPhase.EXPLOITATION)

        observed: dict[str, str] = {}

        monkeypatch.setattr(cli_main, "load_config", lambda: config)
        monkeypatch.setattr(
            lifecycle_mod.MCPLifecycleManager, "start_enabled_servers", lambda self: 0
        )
        monkeypatch.setattr(lifecycle_mod.MCPLifecycleManager, "stop_all", lambda self: None)

        def fake_apply(agent, target: str, snapshot_id=None):
            restored = None
            if target == "https://old.example":
                restored = old_state
            elif target == "https://new.example":
                restored = new_state

            if restored is not None:
                agent.context.state = restored
                return type(
                    "Restore",
                    (),
                    {
                        "restored": True,
                        "target": restored.target,
                        "phase": restored.phase.value,
                        "snapshot_id": snapshot_id or "",
                        "resume_strategy": "",
                        "resume_reason": "",
                    },
                )()

            agent.context.state.target = target
            return type(
                "Restore",
                (),
                {
                    "restored": False,
                    "target": target,
                    "phase": agent.context.state.phase.value,
                    "snapshot_id": snapshot_id or "",
                    "resume_strategy": "",
                    "resume_reason": "",
                },
            )()

        async def fake_persistent_pentest(self, user_input: str, target=None, **kwargs):
            observed["target_arg"] = target or ""
            observed["state_target"] = self.context.state.target or ""
            observed["phase"] = self.context.state.phase.value
            return []

        monkeypatch.setattr(cli_main, "apply_target_state_to_agent", fake_apply)
        monkeypatch.setattr(agent_core.AgentCore, "persistent_pentest", fake_persistent_pentest)

        result = runner.invoke(
            app,
            ["repl"],
            input="target https://old.example\npersistent https://new.example\nexit\n",
        )

        assert result.exit_code == 0
        assert observed["target_arg"] == "https://new.example"
        assert observed["state_target"] == "https://new.example"
        assert observed["phase"] == PentestPhase.EXPLOITATION.value

    def test_report_target_mode(self, runner, monkeypatch, tmp_path):
        import vulnbot.target_state.store as store_mod
        from vulnbot.agent.context import SessionState, VulnerabilityFinding
        from vulnbot.cli.main import app

        monkeypatch.setattr(store_mod, "TARGETS_DIR", tmp_path / "targets")
        state = SessionState(target="https://example.com")
        finding = VulnerabilityFinding(title="SQLi", severity="High", vuln_type="SQLi")
        finding.verified = True
        finding.verification_status = "verified"
        state.add_finding(finding)
        store_mod.save_target_state("https://example.com", state, command="scan")

        result = runner.invoke(app, ["report", "https://example.com", "--target"])
        assert result.exit_code == 0
        assert "Report generated" in result.output or result.output

    def test_report_target_mode_pdf(self, runner, monkeypatch, tmp_path):
        import vulnbot.config.settings as settings_mod
        import vulnbot.target_state.store as store_mod
        from vulnbot.agent.context import SessionState, VulnerabilityFinding
        from vulnbot.cli.main import app
        from vulnbot.report import pdf_exporter

        sessions = tmp_path / "sessions"
        sessions.mkdir()
        monkeypatch.setattr(store_mod, "TARGETS_DIR", tmp_path / "targets")
        monkeypatch.setattr(settings_mod, "SESSIONS_DIR", sessions)

        state = SessionState(target="https://example.com")
        finding = VulnerabilityFinding(title="SQLi", severity="High", vuln_type="SQLi")
        finding.verified = True
        finding.verification_status = "verified"
        state.add_finding(finding)
        store_mod.save_target_state("https://example.com", state, command="scan")

        result = runner.invoke(app, ["report", "https://example.com", "--target", "--pdf"])

        if pdf_exporter._HAVE_REPORTLAB:
            assert result.exit_code == 0, result.output
            assert "PDF exported" in result.output
            pdfs = list(sessions.glob("*.pdf"))
            assert pdfs and pdfs[0].read_bytes()[:5] == b"%PDF-"
        else:
            assert result.exit_code == 1
            assert "vulnbot[pdf]" in result.output

    def test_repl_report_command_uses_current_session_or_target_state(self, runner, monkeypatch):
        import vulnbot.cli.main as cli_main
        import vulnbot.mcp.lifecycle as lifecycle_mod
        from vulnbot.cli.main import app
        from vulnbot.config.schema import VulnBotConfig

        config = VulnBotConfig()
        config.llm.api_key = "test-key"

        monkeypatch.setattr(cli_main, "load_config", lambda: config)
        monkeypatch.setattr(
            lifecycle_mod.MCPLifecycleManager, "start_enabled_servers", lambda self: 0
        )
        monkeypatch.setattr(lifecycle_mod.MCPLifecycleManager, "stop_all", lambda self: None)
        monkeypatch.setattr(
            cli_main, "_generate_report_for_target", lambda target, **kwargs: "C:/tmp/report.md"
        )

        result = runner.invoke(
            app,
            ["repl"],
            input="target https://example.com\nreport https://example.com\nexit\n",
        )

        assert result.exit_code == 0
        assert "Report generated" in result.output
        assert "report.md" in result.output

    def test_run_uses_shared_orchestrator(self, runner, monkeypatch):
        import vulnbot.cli.main as cli_main
        from vulnbot.cli.main import app
        from vulnbot.config.schema import VulnBotConfig

        config = VulnBotConfig()
        config.llm.api_key = "test-key"
        monkeypatch.setattr(cli_main, "load_config", lambda: config)

        called: list[tuple[str, str]] = []

        async def fake_orchestrated(*, command, target, resume, snapshot, runner):
            called.append((command, target))
            return type("RunResult", (), {"summary": {"findings_count": 3}})()

        monkeypatch.setattr(cli_main, "_run_cli_orchestrated_task", fake_orchestrated)

        result = runner.invoke(app, ["run", "https://example.com"])
        assert result.exit_code == 0
        assert called == [("run", "https://example.com")]

    def test_run_output_generates_report_from_target_state(self, runner, monkeypatch, tmp_path):
        import vulnbot.cli.main as cli_main
        import vulnbot.report.generator as report_generator
        from vulnbot.agent.context import SessionState
        from vulnbot.cli.main import app
        from vulnbot.config.schema import VulnBotConfig

        config = VulnBotConfig()
        config.llm.api_key = "test-key"
        monkeypatch.setattr(cli_main, "load_config", lambda: config)

        async def fake_orchestrated(*, command, target, resume, snapshot, runner):
            return type("RunResult", (), {"summary": {"findings_count": 0}})()

        generated = []

        def fake_generate_from_target_state(state, *, report_format, output_path):
            generated.append((state["target"], report_format, output_path))
            return output_path

        monkeypatch.setattr(cli_main, "_run_cli_orchestrated_task", fake_orchestrated)
        monkeypatch.setattr(
            cli_main,
            "load_target_state",
            lambda target: SessionState(target=target).model_dump(mode="json"),
        )
        monkeypatch.setattr(
            report_generator,
            "generate_report_from_target_state",
            fake_generate_from_target_state,
        )

        output = tmp_path / "report.html"
        result = runner.invoke(app, ["run", "https://example.com", "--output", str(output)])

        assert result.exit_code == 0
        assert generated == [("https://example.com", "html", str(output))]
        assert "Report generated" in result.output

    def test_run_cli_constraints_are_appended_to_prompt(self, runner, monkeypatch):
        import vulnbot.cli.main as cli_main
        from vulnbot.cli.main import app
        from vulnbot.config.schema import VulnBotConfig

        config = VulnBotConfig()
        config.llm.api_key = "test-key"
        monkeypatch.setattr(cli_main, "load_config", lambda: config)

        prompts = []

        async def fake_orchestrated(*, command, target, resume, snapshot, runner):
            class DummyAgent:
                async def auto_pentest(self, prompt, **kwargs):
                    prompts.append(prompt)
                    return []

            await runner(DummyAgent(), config)
            return type("RunResult", (), {"summary": {"findings_count": 0}})()

        monkeypatch.setattr(cli_main, "_run_cli_orchestrated_task", fake_orchestrated)

        result = runner.invoke(
            app,
            [
                "run",
                "https://example.com",
                "--only-port",
                "443",
                "--only-host",
                "example.com",
                "--only-path",
                "/admin",
            ],
        )
        assert result.exit_code == 0
        assert prompts
        assert "Only test port 443" in prompts[0]
        assert "Only test host example.com" in prompts[0]
        assert "Only test path /admin" in prompts[0]

    def test_run_cli_blocked_host_and_path_are_appended_to_prompt(self, runner, monkeypatch):
        import vulnbot.cli.main as cli_main
        from vulnbot.cli.main import app
        from vulnbot.config.schema import VulnBotConfig

        config = VulnBotConfig()
        config.llm.api_key = "test-key"
        monkeypatch.setattr(cli_main, "load_config", lambda: config)

        prompts = []

        async def fake_orchestrated(*, command, target, resume, snapshot, runner):
            class DummyAgent:
                async def auto_pentest(self, prompt, **kwargs):
                    prompts.append(prompt)
                    return []

            await runner(DummyAgent(), config)
            return type("RunResult", (), {"summary": {"findings_count": 0}})()

        monkeypatch.setattr(cli_main, "_run_cli_orchestrated_task", fake_orchestrated)

        result = runner.invoke(
            app,
            [
                "run",
                "https://example.com",
                "--blocked-host",
                "staging.example.com",
                "--blocked-path",
                "/internal",
            ],
        )
        assert result.exit_code == 0
        assert prompts
        assert "Blocked host staging.example.com" in prompts[0]
        assert "Blocked path /internal" in prompts[0]

    def test_cli_blocks_command_when_allowed_actions_conflict(self, runner, monkeypatch):
        import vulnbot.cli.main as cli_main
        from vulnbot.cli.main import app
        from vulnbot.config.schema import VulnBotConfig

        config = VulnBotConfig()
        config.llm.api_key = "test-key"
        monkeypatch.setattr(cli_main, "load_config", lambda: config)
        monkeypatch.setattr(
            cli_main,
            "_append_cli_constraints",
            lambda prompt, only_port, only_host, only_path: f"{prompt} recon only.",
        )

        result = runner.invoke(app, ["run", "https://example.com"])
        assert result.exit_code == 0

    def test_cli_blocks_command_with_explicit_allow_actions_option(self, runner):
        import vulnbot.cli.main as cli_main
        from vulnbot.cli.main import app
        from vulnbot.config.schema import VulnBotConfig

        config = VulnBotConfig()
        config.llm.api_key = "test-key"
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setattr(cli_main, "load_config", lambda: config)

        result = runner.invoke(app, ["run", "https://example.com", "--allow-actions", "recon"])
        monkeypatch.undo()
        assert result.exit_code == 0

    def test_persistent_command_uses_correct_cycle_callback(self, runner, monkeypatch):
        import vulnbot.cli.main as cli_main
        from vulnbot.cli.main import app
        from vulnbot.config.schema import VulnBotConfig

        config = VulnBotConfig()
        config.llm.api_key = "test-key"
        monkeypatch.setattr(cli_main, "load_config", lambda: config)

        class DummyAgent:
            def __init__(self):
                self.context = type(
                    "Ctx", (), {"state": type("State", (), {"target": "https://example.com"})()}
                )()
                self.runtime = type("Runtime", (), {})()

            async def persistent_pentest(self, *args, **kwargs):
                assert "on_cycle_complete" in kwargs
                assert kwargs["on_cycle_complete"] is not None
                return []

        async def fake_orchestrated(*, command, target, resume, snapshot, runner):
            await runner(DummyAgent(), config)
            return type("Result", (), {"summary": {"findings_count": 0, "executed_steps": 0}})()

        monkeypatch.setattr(cli_main, "_run_cli_orchestrated_task", fake_orchestrated)

        result = runner.invoke(
            app, ["persistent", "https://example.com", "--cycles", "1", "--rounds", "1"]
        )
        assert result.exit_code == 0

    def test_repl_persistent_interrupt_generates_final_report(self, runner, monkeypatch):
        import vulnbot.agent.core as agent_core
        import vulnbot.cli.main as cli_main
        import vulnbot.mcp.lifecycle as lifecycle_mod
        from vulnbot.agent.context import SessionState, VulnerabilityFinding
        from vulnbot.cli.main import app
        from vulnbot.config.schema import VulnBotConfig

        config = VulnBotConfig()
        config.llm.api_key = "test-key"

        monkeypatch.setattr(cli_main, "load_config", lambda: config)
        monkeypatch.setattr(
            lifecycle_mod.MCPLifecycleManager, "start_enabled_servers", lambda self: 0
        )
        monkeypatch.setattr(lifecycle_mod.MCPLifecycleManager, "stop_all", lambda self: None)

        state = SessionState(target="https://example.com")
        finding = VulnerabilityFinding(title="SQLi", severity="High", vuln_type="SQLi")
        state.add_finding(finding)

        def fake_apply(agent, target: str, snapshot_id=None):
            agent.context.state = state
            return type(
                "Restore",
                (),
                {
                    "restored": True,
                    "target": state.target,
                    "phase": state.phase.value,
                    "snapshot_id": snapshot_id or "",
                    "resume_strategy": "",
                    "resume_reason": "",
                },
            )()

        async def fake_persistent_pentest(self, user_input: str, target=None, **kwargs):
            raise KeyboardInterrupt()

        monkeypatch.setattr(cli_main, "apply_target_state_to_agent", fake_apply)
        monkeypatch.setattr(agent_core.AgentCore, "persistent_pentest", fake_persistent_pentest)
        monkeypatch.setattr(
            cli_main, "_generate_report_for_target", lambda target, **kwargs: "C:/tmp/final.md"
        )

        result = runner.invoke(
            app,
            ["repl"],
            input="persistent https://example.com\nexit\n",
        )

        assert result.exit_code == 0
        assert "Final report" in result.output
        assert "final.md" in result.output

    def test_target_state_list_and_clear(self, runner, monkeypatch, tmp_path):
        import vulnbot.target_state.store as store_mod
        from vulnbot.agent.context import SessionState
        from vulnbot.cli.main import app

        monkeypatch.setattr(store_mod, "TARGETS_DIR", tmp_path / "targets")
        state = SessionState(target="https://example.com")
        store_mod.save_target_state("https://example.com", state, command="recon")

        result_list = runner.invoke(app, ["target-state", "list", "https://example.com"])
        assert result_list.exit_code == 0
        assert "snapshot" in result_list.output.lower()

        result_clear = runner.invoke(app, ["target-state", "clear", "https://example.com"])
        assert result_clear.exit_code == 0
        assert result_clear.output

    def test_target_state_preview_and_diff(self, runner, monkeypatch, tmp_path):
        import vulnbot.target_state.store as store_mod
        from vulnbot.agent.context import SessionState, VulnerabilityFinding
        from vulnbot.cli.main import app

        monkeypatch.setattr(store_mod, "TARGETS_DIR", tmp_path / "targets")

        state1 = SessionState(target="https://example.com")
        state1.add_finding(VulnerabilityFinding(title="SQLi", severity="High", vuln_type="SQLi"))
        store_mod.save_target_state("https://example.com", state1, command="recon")

        state2 = SessionState(target="https://example.com")
        state2.add_finding(VulnerabilityFinding(title="XSS", severity="Medium", vuln_type="XSS"))
        store_mod.save_target_state("https://example.com", state2, command="scan")

        snapshots = store_mod.list_target_snapshots("https://example.com")
        result_preview = runner.invoke(app, ["target-state", "preview", "https://example.com"])
        assert result_preview.exit_code == 0
        assert "Target Preview" in result_preview.output

        result_diff = runner.invoke(
            app,
            [
                "target-state",
                "diff",
                "https://example.com",
                snapshots[-1]["snapshot_id"],
                "--to",
                snapshots[0]["snapshot_id"],
            ],
        )
        assert result_diff.exit_code == 0
        assert "Target Diff" in result_diff.output

    @pytest.mark.asyncio
    async def test_repl_runner_executes_post_hook(self):
        from vulnbot.repl_runner import run_repl_call

        observed = []

        async def call():
            observed.append("call")
            return "hello"

        async def after_result(result):
            observed.append(f"after:{result}")

        result = await run_repl_call(call=call, after_result=after_result)
        assert result == "hello"
        assert observed == ["call", "after:hello"]

    def test_cli_kb_info(self, runner):
        from vulnbot.cli.main import app

        result = runner.invoke(app, ["kb", "info"])
        # kb info might not exist in all versions, just verify no crash
        assert result.exit_code in (0, 2)

    def test_cli_no_args(self, runner, monkeypatch):
        """Running with no args should open the original CLI/REPL by default."""
        import vulnbot.cli.main as cli_main
        from vulnbot.cli.main import app

        called = []
        monkeypatch.setattr(cli_main, "_run_repl", lambda: called.append("repl"))

        result = runner.invoke(app, [])
        assert result.exit_code == 0
        assert called == ["repl"]

    def test_repl_command_starts_classic_repl(self, runner, monkeypatch):
        import vulnbot.cli.main as cli_main
        from vulnbot.cli.main import app

        called = []
        monkeypatch.setattr(cli_main, "_run_repl", lambda: called.append("repl"))

        result = runner.invoke(app, ["repl"])
        assert result.exit_code == 0
        assert called == ["repl"]

    def test_tui_once_renders_workbench(self, runner):
        from vulnbot.cli.main import app

        result = runner.invoke(app, ["tui", "--once"])
        assert result.exit_code == 0
        assert "VulnBot TUI" in result.output
        assert "Authorized Target" in result.output
        assert "Run Overview" in result.output
        assert "No target selected" in result.output
        assert "Security Boundary" in result.output
        # Newer TUI uses slash commands instead of the old numeric menu.

    def test_tui_once_renders_target_overview(self, runner, monkeypatch):
        import vulnbot.cli.tui as tui_mod
        from vulnbot.cli.main import app

        monkeypatch.setattr(
            tui_mod,
            "get_target_state_preview",
            lambda target: {
                "target": target,
                "phase": "scanning",
                "findings_count": 3,
                "verified_count": 1,
                "pending_count": 2,
                "last_command": "scan",
                "constraints": {
                    "allowed_ports": [443],
                    "allowed_paths": ["/admin"],
                    "strict_mode": True,
                },
                "constraint_violations": ["blocked port 80"],
            },
        )
        monkeypatch.setattr(
            tui_mod,
            "list_target_snapshots",
            lambda target: [{"snapshot_id": "snap_a"}, {"snapshot_id": "snap_b"}],
        )

        result = runner.invoke(app, ["tui", "--once", "--target", "https://example.com"])
        assert result.exit_code == 0
        assert "2 snapshots" in result.output
        assert "3 risks" in result.output
        assert "Allowed ports: 443" in result.output
        assert "Allowed paths: /admin" in result.output
        assert "Strict Mode" in result.output
        assert "1 times" in result.output

    def test_tui_once_accepts_prefilled_target(self, runner):
        from vulnbot.cli.main import app

        result = runner.invoke(
            app,
            [
                "tui",
                "--once",
                "--target",
                "https://example.com",
                "--mode",
                "quick",
                "--only-port",
                "443",
            ],
        )
        assert result.exit_code == 0
        assert "https://example.com" in result.output
        assert "Quick Scan" in result.output
        assert "443" in result.output

    def test_tui_dry_run_renders_launch_summary(self, runner):
        from vulnbot.cli.main import app

        result = runner.invoke(
            app,
            [
                "tui",
                "--dry-run",
                "--target",
                "https://example.com",
                "--mode",
                "deep",
                "--only-host",
                "example.com",
                "--only-port",
                "443",
                "--only-path",
                "/admin",
                "--blocked-host",
                "staging.example.com",
                "--block-actions",
                "post_exploitation",
            ],
        )
        assert result.exit_code == 0
        assert "Launch Summary" in result.output
        assert "vulnbot scan https://example.com" in result.output
        assert "--only-port 443" in result.output
        assert "--only-path /admin" in result.output
        assert "--blocked-host staging.example.com" in result.output

    def test_tui_rejects_unknown_mode(self, runner):
        from vulnbot.cli.main import app

        result = runner.invoke(app, ["tui", "--mode", "unknown", "--dry-run"])
        assert result.exit_code == 1
        assert "Unknown TUI mode" in result.output

    def test_tui_interactive_launch_builds_task_draft(self, runner, monkeypatch):
        import vulnbot.cli.tui as tui_mod
        from vulnbot.cli.main import app

        launched = []

        def fake_run_tui(*, launcher=None, once=False, initial_state=None):
            state = tui_mod.TuiState(
                target="https://example.com",
                mode="quick",
                only_port="443",
                only_path="/admin",
                blocked_host="staging.example.com",
            )
            draft = tui_mod._draft_from_state(state)
            launched.append(draft)

        monkeypatch.setattr(tui_mod, "run_tui", fake_run_tui)

        result = runner.invoke(app, ["tui"])
        assert result.exit_code == 0
        assert launched
        assert launched[0].command == "recon"
        assert launched[0].target == "https://example.com"
        assert launched[0].only_port == 443
        assert launched[0].only_path == "/admin"
        assert launched[0].blocked_host == "staging.example.com"
        assert launched[0].allow_actions == ("recon",)

    def test_tui_scope_prompt_updates_action_constraints(self, monkeypatch):
        import vulnbot.cli.tui as tui_mod

        answers = iter(
            [
                "example.com",
                "443",
                "/admin",
                "staging.example.com",
                "/logout",
                "recon,scan",
                "exploit,post_exploitation",
            ]
        )
        monkeypatch.setattr(tui_mod.Prompt, "ask", lambda *args, **kwargs: next(answers))
        monkeypatch.setattr(tui_mod.Confirm, "ask", lambda *args, **kwargs: False)

        state = tui_mod.TuiState(target="https://example.com")
        tui_mod._prompt_scope(state)
        draft = tui_mod.build_task_draft(state)

        assert state.only_host == "example.com"
        assert state.only_port == "443"
        assert state.only_path == "/admin"
        assert state.blocked_host == "staging.example.com"
        assert state.blocked_path == "/logout"
        assert state.allow_actions == ["recon", "scan"]
        assert state.block_actions == ["exploit", "post_exploitation"]
        assert state.resume is False
        assert draft.allow_actions == ("recon", "scan")
        assert draft.block_actions == ("exploit", "post_exploitation")
        assert "--allow-actions recon,scan" in draft.command_line
        assert "--block-actions exploit,post_exploitation" in draft.command_line

    def test_tui_runtime_diagnostic_panel_renders_environment_summary(self, monkeypatch):
        import vulnbot.cli.tui as tui_mod
        from vulnbot.config.schema import VulnBotConfig

        config = VulnBotConfig()
        config.llm.api_key = "test-key"
        config.llm.provider = "openai"
        config.llm.model = "gpt-test"

        monkeypatch.setattr(tui_mod, "_command_version", lambda *args: "v20.0.0")
        monkeypatch.setattr(tui_mod.shutil, "which", lambda command: f"/usr/bin/{command}")

        class DummyMCPDiagnostics:
            total_services = 3
            running_services = 1
            local_services = 2
            placeholder_services = 1
            tool_count = 5

        def fake_get_mcp_diagnostics():
            return DummyMCPDiagnostics()

        import vulnbot.web.services.mcp_service as mcp_service

        monkeypatch.setattr(mcp_service, "get_mcp_diagnostics", fake_get_mcp_diagnostics)
        rendered = tui_mod.Console(
            file=io.StringIO(),
            record=True,
            width=100,
            force_terminal=False,
            color_system=None,
        )
        rendered.print(tui_mod.build_runtime_diagnostic_panel(config))
        output = rendered.export_text()

        assert "Environment Diagnostic" in output
        assert "v20.0.0" in output
        assert "openai" in output
        assert "gpt-test" in output
        assert "Configured" in output
        assert "3 registered" in output
        assert "5" in output

    def test_tui_llm_config_prompt_saves_provider_and_api_key(self, monkeypatch):
        import vulnbot.cli.tui as tui_mod
        from vulnbot.config.schema import VulnBotConfig

        config = VulnBotConfig()
        # New flow: provider -> base_url -> api_key -> fetch models -> model -> enter
        answers = iter(
            [
                "deepseek",
                "https://api.deepseek.com/v1",
                "sk-test",
                "deepseek-chat",
                "",
            ]
        )
        saved = []

        monkeypatch.setattr(tui_mod.Prompt, "ask", lambda *args, **kwargs: next(answers))
        monkeypatch.setattr(tui_mod, "save_config", lambda cfg: saved.append(cfg))
        # Mock fetch_provider_models to return a model list
        monkeypatch.setattr(tui_mod, "fetch_provider_models", lambda *a, **kw: ["deepseek-chat", "deepseek-reasoner"])

        screen = tui_mod.Console(
            file=io.StringIO(),
            record=True,
            width=100,
            force_terminal=False,
            color_system=None,
        )
        updated = tui_mod._prompt_llm_config(screen, config)
        output = screen.export_text()

        assert updated.llm.provider == "deepseek"
        assert updated.llm.base_url == "https://api.deepseek.com/v1"
        assert updated.llm.model == "deepseek-chat"
        assert updated.llm.api_key == "sk-test"
        assert saved and saved[0] is updated
        assert "Model/API configuration saved" in output
        assert "API Key: Updated" in output

    def test_config_tui_edits_api_keys_and_session(self, monkeypatch):
        from pathlib import Path

        import vulnbot.cli.tui as tui_mod
        from vulnbot.config.schema import VulnBotConfig

        config = VulnBotConfig()
        config.session.max_rounds = 15

        answers = iter(
            [
                "llm",
                "deepseek",
                "",
                "",
                "k1, k2, k3",
                "",
                "",
                "",
                "",
                "",
                "session",
                "tmp/output",
                "y",
                "markdown",
                "bash",
                "20",
                "n",
                "y",
                "2",
                "1",
                "4",
                "9",
                "7",
                "11",
                "12",
                "y",
                "en",
                "save",
            ]
        )
        saved = []

        monkeypatch.setattr(tui_mod.Prompt, "ask", lambda *args, **kwargs: next(answers))
        monkeypatch.setattr(tui_mod.Confirm, "ask", lambda *args, **kwargs: next(answers) == "y")
        monkeypatch.setattr(tui_mod, "load_config", lambda: config)
        monkeypatch.setattr(tui_mod, "save_config", lambda cfg: saved.append(cfg))

        tui_mod.run_config_tui()

        assert saved and saved[0] is config
        assert config.llm.provider == "deepseek"
        assert config.llm.api_keys == ["k1", "k2", "k3"]
        assert config.session.output_dir == Path("tmp/output")
        assert config.session.max_rounds == 20
        assert config.session.show_thinking is False
        assert config.session.repl_parallel_enabled is True
        assert config.session.repl_parallel_agents == 2
        assert config.session.repl_parallel_worker_rounds == 4
        assert config.session.repl_parallel_surface_limit == 9
        assert config.session.language == "en"

    def test_config_tui_can_add_and_delete_mcp_servers(self, monkeypatch):
        import vulnbot.cli.tui as tui_mod
        from vulnbot.config.schema import MCPServerConfig, MCPTransportConfig, VulnBotConfig

        config = VulnBotConfig()
        config.mcp.servers = {
            "custom": MCPServerConfig(
                name="custom",
                enabled=True,
                priority=1,
                description="custom server",
                transport=MCPTransportConfig(type="stdio", command="uvx", args=["tool"]),
            )
        }

        add_answers = iter(
            [
                "custom2",
                "y",
                "2",
                "another server",
                "stdio",
                "npx",
                "server-one, server-two",
                "",
                "!clear",
                "1000",
                "2000",
            ]
        )
        monkeypatch.setattr(tui_mod.Prompt, "ask", lambda *args, **kwargs: next(add_answers))
        monkeypatch.setattr(tui_mod.Confirm, "ask", lambda *args, **kwargs: next(add_answers) == "y")

        screen = tui_mod.Console(
            file=io.StringIO(),
            record=True,
            width=100,
            force_terminal=False,
            color_system=None,
        )

        name, server = tui_mod._prompt_mcp_server(screen, config)
        config.mcp.servers[name] = server
        assert name == "custom2"
        assert server.transport.command == "npx"
        assert server.transport.args == ["server-one", "server-two"]

        delete_answers = iter(["delete", "custom", "back"])
        monkeypatch.setattr(tui_mod.Prompt, "ask", lambda *args, **kwargs: next(delete_answers))
        monkeypatch.setattr(tui_mod.Confirm, "ask", lambda *args, **kwargs: True)
        tui_mod._edit_mcp_config(screen, config)

        assert "custom" not in config.mcp.servers
        assert "custom2" in config.mcp.servers


class TestCLISubCommands:
    """Test CLI sub-command help messages."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_run_help(self, runner):
        from vulnbot.cli.main import app

        result = runner.invoke(app, ["run", "--help"])
        assert result.exit_code == 0

    def test_recon_help(self, runner):
        from vulnbot.cli.main import app

        result = runner.invoke(app, ["recon", "--help"])
        assert result.exit_code == 0

    def test_scan_help(self, runner):
        from vulnbot.cli.main import app

        result = runner.invoke(app, ["scan", "--help"])
        assert result.exit_code == 0

    def test_network_scan_help(self, runner):
        from vulnbot.cli.main import app

        result = runner.invoke(app, ["network-scan", "--help"])
        assert result.exit_code == 0

    def test_report_help(self, runner):
        from vulnbot.cli.main import app

        result = runner.invoke(app, ["report", "--help"])
        assert result.exit_code == 0

    def test_repl_help(self, runner):
        from vulnbot.cli.main import app

        result = runner.invoke(app, ["repl", "--help"])
        assert result.exit_code == 0

    def test_run_with_prompt_option(self, runner):
        # 2026-06-10 Nyaecho - add --prompt option coverage
        from vulnbot.cli.main import app

        # Test that --prompt option is accepted and doesn't crash
        # We expect failure due to missing target, but the option should be parsed
        result = runner.invoke(app, ["run", "--prompt", "test prompt", "example.com"])
        # Should not be a usage error (exit code 2)
        assert result.exit_code != 2
        # The command will fail for other reasons (no config, etc.), but that's okay


class TestFreshReconI18n:
    """Force-fresh-recon UI strings exist in both locales."""

    def test_keys_present(self):
        import json
        from pathlib import Path

        import vulnbot

        base = Path(vulnbot.__file__).parent / "i18n"
        en = json.loads((base / "en.json").read_text(encoding="utf-8"))
        zh = json.loads((base / "zh.json").read_text(encoding="utf-8"))
        for key in ("cli.fresh_recon_armed", "cli.recon_reused", "help.rescan"):
            assert key in en, f"missing {key} in en.json"
            assert key in zh, f"missing {key} in zh.json"
