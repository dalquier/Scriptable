"""DeveloperOS exception hierarchy."""


class DeveloperOSError(Exception):
    """Base class for all expected DeveloperOS errors."""


class ConfigurationError(DeveloperOSError):
    """Raised when configuration cannot be loaded or validated."""


class ContainerError(DeveloperOSError):
    """Base class for service container errors."""


class DuplicateServiceError(ContainerError):
    """Raised when an existing service is registered without replacement permission."""


class ServiceNotFoundError(ContainerError):
    """Raised when a requested service is absent."""


class LifecycleError(DeveloperOSError):
    """Raised for invalid lifecycle transitions."""


class KernelCriticalError(DeveloperOSError):
    """Raised when a critical kernel operation fails."""
