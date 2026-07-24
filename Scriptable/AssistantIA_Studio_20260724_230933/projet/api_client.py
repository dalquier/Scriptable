"""Client OpenAI Responses compatible avec Pyto."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict, Iterable, List, Optional


class OpenAIClientError(RuntimeError):
    """Erreur lisible renvoyée par le client OpenAI."""


class OpenAIClient:
    def __init__(
        self,
        api_key: str,
        model: str,
        api_url: str,
        timeout_seconds: int,
        max_output_tokens: int,
    ) -> None:
        self.api_key = api_key.strip()
        self.model = model.strip()
        self.api_url = api_url.strip()
        self.timeout_seconds = int(timeout_seconds)
        self.max_output_tokens = int(max_output_tokens)

    def ask(
        self,
        messages: Iterable[Dict[str, str]],
        instructions: str,
        enable_web_search: bool = False,
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        if not self.api_key:
            raise OpenAIClientError("La clé API OpenAI est absente.")
        if not self.model:
            raise OpenAIClientError("Le modèle OpenAI est absent.")

        payload: Dict[str, Any] = {
            "model": self.model,
            "input": list(messages),
            "instructions": instructions,
            "max_output_tokens": self.max_output_tokens,
        }
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
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
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
            message = (parsed.get("error") or {}).get("message") or detail
        except (ValueError, TypeError, AttributeError):
            message = detail
        return f"Erreur OpenAI HTTP {status_code} : {str(message).strip()}"
