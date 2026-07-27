from __future__ import annotations

import json
from pathlib import Path

import pytest

from developeros.__main__ import main
from developeros.core import api
from developeros.core.bootstrap import bootstrap
from developeros.core.configuration import Settings, load_settings
from developeros.core.container import ServiceContainer
from developeros.core.diagnostics import collect_diagnostics
from developeros.core.errors import (
    ConfigurationError,
    DuplicateServiceError,
    KernelCriticalError,
    LifecycleError,
    ServiceNotFoundError,
)
from developeros.core.health import HealthCheckResult, HealthService, HealthStatus
from developeros.core.kernel import Kernel
from developeros.core.lifecycle import KernelState, ensure_transition
from developeros.core.logging import JsonFormatter, configure_logging


def test_imports_and_public_api() -> None:
    assert api.__version__ == "0.1.0"
    assert api.KernelState.CREATED.value == "CREATED"


def test_bootstrap_initializes_services() -> None:
    kernel = bootstrap(env={})
    assert kernel.state is KernelState.INITIALIZED
    assert kernel.container.resolve("kernel") is kernel
    assert kernel.container.resolve("settings") == kernel.settings


def test_kernel_transitions_start_and_stop() -> None:
    kernel = bootstrap(env={})
    kernel.start()
    assert kernel.state is KernelState.RUNNING
    kernel.start()
    kernel.stop()
    assert kernel.state is KernelState.STOPPED
    kernel.stop()
    assert kernel.state is KernelState.STOPPED


def test_created_kernel_can_stop() -> None:
    kernel = Kernel(Settings(), ServiceContainer(), HealthService())
    kernel.stop()
    assert kernel.state is KernelState.STOPPED


def test_invalid_transition() -> None:
    with pytest.raises(LifecycleError):
        ensure_transition(KernelState.CREATED, KernelState.RUNNING)


def test_start_failure_marks_failed() -> None:
    def explode() -> None:
        raise RuntimeError("boom")

    kernel = Kernel(Settings(), ServiceContainer(), HealthService(), on_start=explode)
    with pytest.raises(KernelCriticalError, match="boom"):
        kernel.start()
    assert kernel.state is KernelState.FAILED
    kernel.stop()
    assert kernel.state is KernelState.STOPPED


def test_initialize_failure_marks_failed() -> None:
    kernel = Kernel(
        Settings(),
        ServiceContainer(),
        HealthService(),
        on_initialize=lambda: (_ for _ in ()).throw(RuntimeError("init")),
    )
    with pytest.raises(KernelCriticalError, match="init"):
        kernel.initialize()


def test_container_resolution_duplicates_and_disposal() -> None:
    container = ServiceContainer()
    closed: list[str] = []

    class Resource:
        def close(self) -> None:
            closed.append("closed")

    container.register_instance("value", 42)
    container.register_factory("resource", lambda _: Resource())
    assert container.contains("value")
    assert container.resolve("value") == 42
    assert container.resolve("resource") is container.resolve("resource")
    with pytest.raises(DuplicateServiceError):
        container.register_instance("value", 99)
    container.register_instance("value", 99, replace=True)
    assert container.resolve("value") == 99
    with pytest.raises(ServiceNotFoundError):
        container.resolve("missing")
    container.dispose()
    container.dispose()
    assert closed == ["closed"]
    with pytest.raises(ServiceNotFoundError):
        container.resolve("value")


def test_configuration_priority_and_validation(tmp_path: Path) -> None:
    path = tmp_path / "settings.toml"
    path.write_text(
        '[developeros]\napp_name="File"\nenvironment="production"\nlog_level="warning"\n',
        encoding="utf-8",
    )
    settings = load_settings(
        path,
        env={"DEVELOPEROS_APP_NAME": "Environment", "DEVELOPEROS_HEALTH_ENABLED": "false"},
        overrides={"app_name": "Override", "environment": "test"},
    )
    assert settings.app_name == "Override"
    assert settings.environment == "test"
    assert settings.log_level == "WARNING"
    assert settings.health_enabled is False

    with pytest.raises(ConfigurationError):
        load_settings(env={}, overrides={"environment": "invalid"})
    with pytest.raises(ConfigurationError):
        load_settings(env={}, overrides={"health_enabled": "maybe"})
    with pytest.raises(ConfigurationError):
        load_settings(env={}, overrides={"unknown": 1})
    with pytest.raises(ConfigurationError):
        load_settings(env={}, overrides={"app_name": ""})


def test_invalid_toml(tmp_path: Path) -> None:
    path = tmp_path / "bad.toml"
    path.write_text("[", encoding="utf-8")
    with pytest.raises(ConfigurationError):
        load_settings(path, env={})


def test_health_aggregation_and_serialization() -> None:
    service = HealthService()
    service.register(lambda: HealthCheckResult("ok", HealthStatus.HEALTHY))
    service.register(lambda: HealthCheckResult("warn", HealthStatus.DEGRADED, details={"x": 1}))
    service.register(lambda: (_ for _ in ()).throw(RuntimeError("unknown")))
    report = service.report()
    payload = report.to_dict()
    assert report.status is HealthStatus.UNKNOWN
    assert payload["status"] == "UNKNOWN"
    assert len(payload["checks"]) == 3
    json.dumps(payload)


def test_empty_health_is_unknown() -> None:
    assert HealthService().report().status is HealthStatus.UNKNOWN


def test_diagnostics_are_safe_and_serializable() -> None:
    payload = collect_diagnostics().to_dict()
    assert payload["developeros_version"] == "0.1.0"
    assert "python_version" in payload
    assert "environment" not in payload
    json.dumps(payload)


def test_cli_health_diagnostics_and_version(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["health"]) == 0
    assert '"status": "HEALTHY"' in capsys.readouterr().out
    assert main(["diagnostics"]) == 0
    assert '"developeros_version": "0.1.0"' in capsys.readouterr().out
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0


def test_json_logging() -> None:
    logger = configure_logging("debug")
    assert logger.level > 0
    formatter = JsonFormatter()
    import logging

    record = logging.LogRecord("x", logging.INFO, __file__, 1, "hello", (), None)
    record.context = {"answer": 42}  # type: ignore[attr-defined]
    payload = json.loads(formatter.format(record))
    assert payload["message"] == "hello"
    assert payload["context"]["answer"] == 42
