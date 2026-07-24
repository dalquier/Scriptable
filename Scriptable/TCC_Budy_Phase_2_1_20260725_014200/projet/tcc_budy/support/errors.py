class TCCBudyError(Exception):
    """Erreur de base du projet."""


class NotFoundError(TCCBudyError):
    pass


class ValidationError(TCCBudyError):
    pass


class ProviderError(TCCBudyError):
    pass


class ConfigurationError(TCCBudyError):
    pass
