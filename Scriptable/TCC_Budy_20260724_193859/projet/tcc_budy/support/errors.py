class TCCBudyError(Exception):
    """Base error for the application."""


class StartupError(TCCBudyError):
    pass


class StorageError(TCCBudyError):
    pass


class NotFoundError(TCCBudyError):
    pass


class ValidationError(TCCBudyError):
    pass


class ProviderError(TCCBudyError):
    pass
