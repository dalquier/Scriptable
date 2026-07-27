"""Shared OpenAI gateway for every App-perso project.

The gateway centralizes model selection, reasoning effort, web access, retries and
storage connectors. Business code must not instantiate the OpenAI client directly.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable, Protocol, Sequence

from openai import OpenAI

from .config import AIConfigurationError, AISettings, load_ai_settings


class TaskProfile(str, Enum):
    ECONOMY = "economy"
    BALANCED = "balanced"
    REASONING = "reasoning"
    CODING = "coding"


class SourceConnector(Protocol):
    """Contract implemented by GitHub, Drive, Replit and storage adapters."""

    @property
    def name(self) -> str: ...

    def search(self, query: str, *, limit: int = 8) -> Sequence[dict[str, Any]]: ...


@dataclass(frozen=True)
class AIRequest:
    prompt: str
    profile: TaskProfile | None = None
    use_web: bool | None = None
    search_files: bool = True
    max_source_results: int = 8


@dataclass(frozen=True)
class AIResult:
    text: str
    model: str
    profile: TaskProfile
    reasoning_effort: str
    web_enabled: bool
    sources: tuple[dict[str, Any], ...]
    response_id: str | None


class ModelRouter:
    """Selects the cheapest configured model and effort suitable for the task."""

    _CODING_MARKERS = (
        "code", "python", "javascript", "typescript", "bug", "refactor",
        "test", "github", "api", "classe", "fonction", "script",
    )
    _REASONING_MARKERS = (
        "architecture", "stratégie", "analyse complexe", "arbitrage",
        "risque", "diagnostic", "compare", "décision", "raisonnement",
    )
    _ECONOMY_MARKERS = (
        "classe", "extrais", "reformate", "traduis", "résume brièvement",
        "catégorise", "titre", "corrige la forme",
    )

    def choose_profile(self, prompt: str, explicit: TaskProfile | None = None) -> TaskProfile:
        if explicit is not None:
            return explicit

        normalized = prompt.casefold()
        if any(marker in normalized for marker in self._CODING_MARKERS):
            return TaskProfile.CODING
        if any(marker in normalized for marker in self._REASONING_MARKERS):
            return TaskProfile.REASONING
        if any(marker in normalized for marker in self._ECONOMY_MARKERS):
            return TaskProfile.ECONOMY
        return TaskProfile.BALANCED

    @staticmethod
    def model_for(profile: TaskProfile, settings: AISettings) -> str:
        mapping = {
            TaskProfile.ECONOMY: settings.economy_model,
            TaskProfile.BALANCED: settings.balanced_model,
            TaskProfile.REASONING: settings.reasoning_model,
            TaskProfile.CODING: settings.coding_model,
        }
        model = mapping[profile].strip()
        if not model:
            raise AIConfigurationError(
                f"No model configured for profile '{profile.value}'. "
                f"Set OPENAI_MODEL_{profile.value.upper()}."
            )
        return model

    @staticmethod
    def reasoning_for(profile: TaskProfile, settings: AISettings) -> str:
        return {
            TaskProfile.ECONOMY: settings.economy_reasoning,
            TaskProfile.BALANCED: settings.balanced_reasoning,
            TaskProfile.REASONING: settings.reasoning_reasoning,
            TaskProfile.CODING: settings.coding_reasoning,
        }[profile]


class AIGateway:
    """Single application-facing entry point for OpenAI and source retrieval."""

    def __init__(
        self,
        *,
        settings: AISettings | None = None,
        connectors: Iterable[SourceConnector] = (),
        client: OpenAI | None = None,
        router: ModelRouter | None = None,
    ) -> None:
        self.settings = settings or load_ai_settings()
        self.connectors = tuple(connectors)
        self.client = client or OpenAI(
            api_key=self.settings.api_key,
            timeout=self.settings.request_timeout_seconds,
            max_retries=self.settings.max_retries,
        )
        self.router = router or ModelRouter()

    def _retrieve_sources(self, request: AIRequest) -> tuple[dict[str, Any], ...]:
        if not request.search_files:
            return ()

        gathered: list[dict[str, Any]] = []
        for connector in self.connectors:
            try:
                results = connector.search(
                    request.prompt,
                    limit=request.max_source_results,
                )
            except Exception as exc:  # One connector must not disable all AI access.
                gathered.append(
                    {
                        "connector": connector.name,
                        "status": "error",
                        "error": str(exc),
                    }
                )
                continue

            for item in results:
                gathered.append({"connector": connector.name, **dict(item)})

        return tuple(gathered[: request.max_source_results])

    @staticmethod
    def _build_input(prompt: str, sources: Sequence[dict[str, Any]]) -> str:
        if not sources:
            return prompt

        source_text = "\n".join(
            f"[{index}] {source}" for index, source in enumerate(sources, start=1)
        )
        return (
            f"USER REQUEST:\n{prompt}\n\n"
            "RETRIEVED SOURCES:\n"
            f"{source_text}\n\n"
            "Use only relevant sources. State uncertainty and identify the sources used."
        )

    def respond(self, request: AIRequest) -> AIResult:
        profile = self.router.choose_profile(request.prompt, request.profile)
        model = self.router.model_for(profile, self.settings)
        reasoning_effort = self.router.reasoning_for(profile, self.settings)
        sources = self._retrieve_sources(request)

        use_web = self.settings.web_enabled if request.use_web is None else request.use_web
        tools: list[dict[str, str]] = []
        if use_web:
            tools.append({"type": "web_search"})

        payload: dict[str, Any] = {
            "model": model,
            "input": self._build_input(request.prompt, sources),
            "reasoning": {"effort": reasoning_effort},
        }
        if tools:
            payload["tools"] = tools

        response = self.client.responses.create(**payload)
        return AIResult(
            text=response.output_text,
            model=model,
            profile=profile,
            reasoning_effort=reasoning_effort,
            web_enabled=use_web,
            sources=sources,
            response_id=getattr(response, "id", None),
        )
