"""Client minimal pour l'API OpenAI Responses, sans dépendance externe."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


class OpenAIClientError(RuntimeError):
    pass


class OpenAIClient:
    API_URL = "https://api.openai.com/v1/responses"

    def __init__(self, api_key: str, model: str, timeout_seconds: int = 180) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds

    def create_response(
        self,
        user_input: str,
        instructions: str,
        previous_response_id: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model,
            "instructions": instructions,
            "input": user_input,
            "max_output_tokens": 12000,
        }
        if previous_response_id:
            payload["previous_response_id"] = previous_response_id

        request = urllib.request.Request(
            self.API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise OpenAIClientError(f"Erreur OpenAI HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise OpenAIClientError(f"Erreur réseau OpenAI: {exc.reason}") from exc
        except json.JSONDecodeError as exc:
            raise OpenAIClientError("Réponse OpenAI non JSON.") from exc


def extract_output_text(response_data: dict[str, Any]) -> str:
    direct = response_data.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()

    chunks: list[str] = []
    for item in response_data.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                text = content.get("text")
                if isinstance(text, str):
                    chunks.append(text)
    text = "\n".join(chunks).strip()
    if not text:
        raise OpenAIClientError("Aucun texte exploitable dans la réponse OpenAI.")
    return text
