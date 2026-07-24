"""Client minimal de l'API OpenAI Responses pour AssistantIA Studio."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict, Iterable, List, Optional


class OpenAIClientError(RuntimeError):
    """Erreur lisible renvoyée par le client OpenAI."""


class OpenAIClient:
    """Client HTTP léger, compatible avec Pyto et sans dépendance externe."""

    def __init__(
        self,
        api_key: str,
        model: str,
        api_url: str = "https://api.openai.com/v1/responses",
        timeout_seconds: int = 90,
        max_output_tokens: int = 2000,
    ) -> None:
        self.api_key = api_key.strip()
        self.model = model.strip()
        self.api_url = api_url.strip()
        self.timeout_seconds = int(timeout_seconds)
        self.max_output_tokens = int(max_output_tokens)

    def validate(self) -> None:
        if not self.api_key:
            raise OpenAIClientError("La clé API OpenAI est absente.")
        if not self.model:
            raise OpenAIClientError("Le modèle OpenAI est absent.")

    def create_response(
        self,
        messages: Iterable[Dict[str, str]],
        instructions: str = "",
        enable_web_search: bool = False,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        self.validate()

        payload: Dict[str, Any] = {
            "model": self.model,
            "input": list(messages),
            "max_output_tokens": self.max_output_tokens,
        }
        if instructions.strip():
            payload["instructions"] = instructions.strip()
        if enable_web_search:
            payload["tools"] = [{"type": "web_search_preview"}]
        if metadata:
            payload["metadata"] = metadata

        request = urllib.request.Request(
            self.api_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout_seconds,
            ) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise OpenAIClientError(self._format_http_error(exc.code, detail)) from exc
        except urllib.error.URLError as exc:
            raise OpenAIClientError(
                f"Impossible de joindre l'API OpenAI : {exc.reason}"
            ) from exc
        except TimeoutError as exc:
            raise OpenAIClientError("La requête OpenAI a expiré.") from exc

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise OpenAIClientError("Réponse JSON invalide reçue de l'API OpenAI.") from exc

        if isinstance(data, dict) and data.get("error"):
            error = data.get("error") or {}
            message = error.get("message") or "Erreur OpenAI inconnue."
            raise OpenAIClientError(str(message))
        return data

    def ask(
        self,
        messages: List[Dict[str, str]],
        instructions: str = "",
        enable_web_search: bool = False,
    ) -> str:
        data = self.create_response(
            messages=messages,
            instructions=instructions,
            enable_web_search=enable_web_search,
        )
        text = self.extract_output_text(data)
        if not text:
            raise OpenAIClientError("L'API OpenAI n'a renvoyé aucun texte exploitable.")
        return text

    @staticmethod
    def extract_output_text(response_data: Dict[str, Any]) -> str:
        direct = response_data.get("output_text")
        if isinstance(direct, str) and direct.strip():
            return direct.strip()

        texts: List[str] = []
        for item in response_data.get("output", []):
            if not isinstance(item, dict) or item.get("type") != "message":
                continue
            for content in item.get("content", []):
                if not isinstance(content, dict):
                    continue
                if content.get("type") != "output_text":
                    continue
                text = content.get("text")
                if isinstance(text, str) and text.strip():
                    texts.append(text.strip())
        return "\n\n".join(texts)

    @staticmethod
    def _format_http_error(status_code: int, detail: str) -> str:
        try:
            parsed = json.loads(detail)
            error = parsed.get("error") or {}
            message = error.get("message") or detail
        except (ValueError, TypeError, AttributeError):
            message = detail
        message = str(message).strip() or "Erreur inconnue"
        return f"Erreur OpenAI HTTP {status_code} : {message}"
