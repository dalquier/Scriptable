from types import SimpleNamespace

import pytest

from shared.ai.config import AISettings
from shared.ai.gateway import AIGateway, AIRequest, ModelRouter, TaskProfile


@pytest.fixture
def settings() -> AISettings:
    return AISettings(
        api_key="test-key",
        economy_model="gpt-5.6-luna",
        balanced_model="gpt-5.6-terra",
        reasoning_model="gpt-5.6-sol",
        coding_model="gpt-5.6-sol",
        embedding_model="text-embedding-3-small",
        economy_reasoning="none",
        balanced_reasoning="low",
        reasoning_reasoning="medium",
        coding_reasoning="high",
        web_enabled=True,
        request_timeout_seconds=30.0,
        max_retries=1,
    )


def test_router_prefers_coding_for_code_request() -> None:
    router = ModelRouter()
    assert router.choose_profile("Corrige ce bug Python") is TaskProfile.CODING


def test_explicit_profile_overrides_heuristics() -> None:
    router = ModelRouter()
    assert (
        router.choose_profile("Corrige ce code", TaskProfile.ECONOMY)
        is TaskProfile.ECONOMY
    )


def test_gateway_adds_web_search_sources_and_reasoning(settings: AISettings) -> None:
    class Connector:
        name = "github"

        def search(self, query: str, *, limit: int = 8):
            return [{"path": "README.md", "excerpt": "Project documentation"}]

    class Responses:
        def __init__(self) -> None:
            self.payload = None

        def create(self, **payload):
            self.payload = payload
            return SimpleNamespace(output_text="Réponse", id="resp-test")

    responses = Responses()
    client = SimpleNamespace(responses=responses)
    gateway = AIGateway(settings=settings, connectors=[Connector()], client=client)

    result = gateway.respond(AIRequest(prompt="Analyse l’architecture"))

    assert result.text == "Réponse"
    assert result.web_enabled is True
    assert result.profile is TaskProfile.REASONING
    assert result.model == "gpt-5.6-sol"
    assert result.reasoning_effort == "medium"
    assert result.sources[0]["connector"] == "github"
    assert responses.payload["tools"] == [{"type": "web_search"}]
    assert responses.payload["reasoning"] == {"effort": "medium"}
    assert "README.md" in responses.payload["input"]


def test_gateway_can_disable_web_per_request(settings: AISettings) -> None:
    class Responses:
        def __init__(self) -> None:
            self.payload = None

        def create(self, **payload):
            self.payload = payload
            return SimpleNamespace(output_text="OK", id=None)

    responses = Responses()
    gateway = AIGateway(
        settings=settings,
        client=SimpleNamespace(responses=responses),
    )

    result = gateway.respond(
        AIRequest(prompt="Reformate ce texte", use_web=False, search_files=False)
    )

    assert result.web_enabled is False
    assert result.profile is TaskProfile.ECONOMY
    assert result.model == "gpt-5.6-luna"
    assert result.reasoning_effort == "none"
    assert "tools" not in responses.payload
