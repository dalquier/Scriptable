"""Small dependency container for kernel-level services."""

from collections.abc import Callable
from typing import Any

from .errors import DuplicateServiceError, ServiceNotFoundError

ServiceFactory = Callable[["ServiceContainer"], Any]


class ServiceContainer:
    """Register, resolve and dispose singleton instances and lazy factories."""

    def __init__(self) -> None:
        self._instances: dict[str, Any] = {}
        self._factories: dict[str, ServiceFactory] = {}
        self._disposed = False

    def register_instance(self, name: str, instance: Any, *, replace: bool = False) -> None:
        """Register an already-created service instance."""

        self._ensure_available()
        self._check_duplicate(name, replace)
        if replace:
            self._instances.pop(name, None)
            self._factories.pop(name, None)
        self._instances[name] = instance

    def register_factory(self, name: str, factory: ServiceFactory, *, replace: bool = False) -> None:
        """Register a lazy singleton factory receiving this container."""

        self._ensure_available()
        self._check_duplicate(name, replace)
        if replace:
            self._instances.pop(name, None)
            self._factories.pop(name, None)
        self._factories[name] = factory

    def resolve(self, name: str) -> Any:
        """Resolve a service or raise :class:`ServiceNotFoundError`."""

        self._ensure_available()
        if name in self._instances:
            return self._instances[name]
        factory = self._factories.get(name)
        if factory is None:
            raise ServiceNotFoundError(f"Service is not registered: {name}")
        instance = factory(self)
        self._instances[name] = instance
        return instance

    def contains(self, name: str) -> bool:
        """Return whether a service name is registered."""

        return name in self._instances or name in self._factories

    def dispose(self) -> None:
        """Dispose resolved services in reverse registration order, then clear the container."""

        if self._disposed:
            return
        for service in reversed(tuple(self._instances.values())):
            closer = getattr(service, "close", None)
            if callable(closer):
                closer()
            else:
                disposer = getattr(service, "dispose", None)
                if callable(disposer):
                    disposer()
        self._instances.clear()
        self._factories.clear()
        self._disposed = True

    def _check_duplicate(self, name: str, replace: bool) -> None:
        if self.contains(name) and not replace:
            raise DuplicateServiceError(f"Service is already registered: {name}")

    def _ensure_available(self) -> None:
        if self._disposed:
            raise ServiceNotFoundError("Service container has been disposed")
