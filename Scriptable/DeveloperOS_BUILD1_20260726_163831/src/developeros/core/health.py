"""Health checks and aggregate serializable reports."""

from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import IntEnum
from typing import Any


class HealthStatus(IntEnum):
    """Ordered health severity levels."""

    HEALTHY = 0
    WARNING = 1
    DEGRADED = 2
    CRITICAL = 3
    UNKNOWN = 4


@dataclass(frozen=True, slots=True)
class HealthCheckResult:
    """Result returned by one health check."""

    name: str
    status: HealthStatus
    message: str = ""
    details: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""

        payload = asdict(self)
        payload["status"] = self.status.name
        return payload


@dataclass(frozen=True, slots=True)
class HealthReport:
    """Aggregate health report for the kernel."""

    status: HealthStatus
    checks: tuple[HealthCheckResult, ...]
    generated_at: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""

        return {
            "status": self.status.name,
            "generated_at": self.generated_at,
            "checks": [check.to_dict() for check in self.checks],
        }


HealthCheck = Callable[[], HealthCheckResult]


class HealthService:
    """Register and execute named health checks."""

    def __init__(self) -> None:
        self._checks: list[HealthCheck] = []

    def register(self, check: HealthCheck) -> None:
        """Register one health check callable."""

        self._checks.append(check)

    def report(self) -> HealthReport:
        """Execute all checks and aggregate their maximum severity."""

        results: list[HealthCheckResult] = []
        for check in self._checks:
            try:
                results.append(check())
            except Exception as exc:  # noqa: BLE001 - health must contain failures
                results.append(
                    HealthCheckResult(
                        name=getattr(check, "__name__", "unknown"),
                        status=HealthStatus.UNKNOWN,
                        message=f"Health check failed: {exc}",
                    )
                )
        status = max((result.status for result in results), default=HealthStatus.UNKNOWN)
        return HealthReport(
            status=status,
            checks=tuple(results),
            generated_at=datetime.now(UTC).isoformat(),
        )
