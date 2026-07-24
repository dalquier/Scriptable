from tcc_budy.providers.openai_provider import OpenAIProvider
from tcc_budy.providers.simulator import SimulatorProvider


def build_provider(settings):
    if settings.provider == "openai":
        return OpenAIProvider(settings)
    return SimulatorProvider()
