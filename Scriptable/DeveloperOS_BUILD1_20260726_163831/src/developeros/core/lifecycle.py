"""Lifecycle states and deterministic transition rules."""

from enum import StrEnum

from .errors import LifecycleError


class KernelState(StrEnum):
    """Supported DeveloperOS kernel lifecycle states."""

    CREATED = "CREATED"
    INITIALIZING = "INITIALIZING"
    INITIALIZED = "INITIALIZED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    FAILED = "FAILED"


_ALLOWED_TRANSITIONS: dict[KernelState, frozenset[KernelState]] = {
    KernelState.CREATED: frozenset({KernelState.INITIALIZING, KernelState.STOPPED}),
    KernelState.INITIALIZING: frozenset({KernelState.INITIALIZED, KernelState.FAILED}),
    KernelState.INITIALIZED: frozenset({KernelState.STARTING, KernelState.STOPPING}),
    KernelState.STARTING: frozenset({KernelState.RUNNING, KernelState.FAILED}),
    KernelState.RUNNING: frozenset({KernelState.STOPPING, KernelState.FAILED}),
    KernelState.STOPPING: frozenset({KernelState.STOPPED, KernelState.FAILED}),
    KernelState.STOPPED: frozenset({KernelState.INITIALIZING}),
    KernelState.FAILED: frozenset({KernelState.STOPPING, KernelState.STOPPED}),
}


def ensure_transition(current: KernelState, target: KernelState) -> None:
    """Validate a lifecycle transition or raise :class:`LifecycleError`."""

    if target not in _ALLOWED_TRANSITIONS[current]:
        raise LifecycleError(f"Invalid kernel transition: {current.value} -> {target.value}")
