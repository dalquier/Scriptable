"""Minimal DeveloperOS kernel and lifecycle orchestration."""

from __future__ import annotations

import logging
from collections.abc import Callable

from .configuration import Settings
from .container import ServiceContainer
from .errors import KernelCriticalError
from .health import HealthCheckResult, HealthService, HealthStatus
from .lifecycle import KernelState, ensure_transition

Hook = Callable[[], None]


class Kernel:
    """Deterministic, restartable BUILD-1 kernel with no business logic."""

    def __init__(
        self,
        settings: Settings,
        container: ServiceContainer,
        health: HealthService,
        *,
        on_initialize: Hook | None = None,
        on_start: Hook | None = None,
        on_stop: Hook | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.settings = settings
        self.container = container
        self.health = health
        self.state = KernelState.CREATED
        self._on_initialize = on_initialize
        self._on_start = on_start
        self._on_stop = on_stop
        self._logger = logger or logging.getLogger("developeros.kernel")

    def initialize(self) -> None:
        """Initialize services once; repeated calls in initialized/running states are no-ops."""

        if self.state in {KernelState.INITIALIZED, KernelState.STARTING, KernelState.RUNNING}:
            return
        self._transition(KernelState.INITIALIZING)
        try:
            if self._on_initialize:
                self._on_initialize()
            self._transition(KernelState.INITIALIZED)
        except Exception as exc:  # noqa: BLE001 - convert to kernel boundary error
            self._fail("Kernel initialization failed", exc)

    def start(self) -> None:
        """Initialize when needed and transition the kernel to RUNNING."""

        if self.state is KernelState.RUNNING:
            return
        if self.state in {KernelState.CREATED, KernelState.STOPPED}:
            self.initialize()
        self._transition(KernelState.STARTING)
        try:
            if self._on_start:
                self._on_start()
            self._transition(KernelState.RUNNING)
        except Exception as exc:  # noqa: BLE001 - convert to kernel boundary error
            self._fail("Kernel start failed", exc)

    def stop(self) -> None:
        """Stop the kernel and dispose services; repeated calls are safe."""

        if self.state is KernelState.STOPPED:
            return
        if self.state is KernelState.CREATED:
            self._transition(KernelState.STOPPED)
            return
        self._transition(KernelState.STOPPING)
        try:
            if self._on_stop:
                self._on_stop()
            self.container.dispose()
            self._transition(KernelState.STOPPED)
        except Exception as exc:  # noqa: BLE001 - convert to kernel boundary error
            self._fail("Kernel stop failed", exc)

    def _transition(self, target: KernelState) -> None:
        ensure_transition(self.state, target)
        previous = self.state
        self.state = target
        self._logger.info(
            "kernel_state_changed",
            extra={"context": {"from": previous.value, "to": target.value}},
        )

    def _fail(self, message: str, cause: Exception) -> None:
        if self.state is not KernelState.FAILED:
            ensure_transition(self.state, KernelState.FAILED)
            self.state = KernelState.FAILED
        self._logger.critical(message, exc_info=cause)
        raise KernelCriticalError(f"{message}: {cause}") from cause


def kernel_health_check(kernel: Kernel) -> HealthCheckResult:
    """Return a basic health result for the current kernel lifecycle state."""

    if kernel.state is KernelState.RUNNING:
        return HealthCheckResult("kernel", HealthStatus.HEALTHY, "Kernel is running")
    if kernel.state is KernelState.FAILED:
        return HealthCheckResult("kernel", HealthStatus.CRITICAL, "Kernel has failed")
    return HealthCheckResult(
        "kernel", HealthStatus.WARNING, f"Kernel state is {kernel.state.value}"
    )
