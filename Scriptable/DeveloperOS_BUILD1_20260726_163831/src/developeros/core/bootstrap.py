"""Bootstrap the BUILD-1 kernel and its foundational services."""

from pathlib import Path
from typing import Any, Mapping

from .configuration import Settings, load_settings
from .container import ServiceContainer
from .health import HealthService
from .kernel import Kernel, kernel_health_check
from .logging import configure_logging


def bootstrap(
    config_path: str | Path | None = None,
    *,
    env: Mapping[str, str] | None = None,
    overrides: Mapping[str, Any] | None = None,
) -> Kernel:
    """Create a configured, initialized DeveloperOS kernel."""

    settings: Settings = load_settings(config_path, env=env, overrides=overrides)
    logger = configure_logging(settings.log_level)
    container = ServiceContainer()
    health = HealthService()
    container.register_instance("settings", settings)
    container.register_instance("logger", logger)
    container.register_instance("health", health)
    kernel = Kernel(settings, container, health, logger=logger)
    container.register_instance("kernel", kernel)
    if settings.health_enabled:
        health.register(lambda: kernel_health_check(kernel))
    kernel.initialize()
    return kernel
