"""Client minimal de l'API OpenAI Responses."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict, List

from config import API_URL, MAX_OUTPUT_TOKENS, MODEL, OPENAI_API_KEY, SYSTEM_INSTRUCTIONS, TIMEOUT_SECONDS


class OpenAIClientError(Exception):
    pass


def _extract_output_text(data: Dict[str, Any]) -> str:
    direct = data.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()

    parts: List[str] = []
    for item in data.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                text = content.get("text")
                if isinstance(text, str) and text.strip():
                    parts.append(text.strip())
    if parts:
        return "\n\n".join(parts)
    raise OpenAIClientError("Aucun texte exploitable dans la réponse OpenAI.")


class OpenAIClient:
    def __init__(self) -> None:
        if not OPENAI_API_KEY or OPENAI_API_KEY.startswith("sk-votre"):
            raise OpenAIClientError("Clé OpenAI absente. Renseignez config_local.py.")

    def create_response(self, messages: List[Dict[str, str]], enable_web_search: bool = False) -> str:
        payload: Dict[str, Any] = {
            "model": MODEL,
            "instructions": SYSTEM_INSTRUCTIONS,
            "input": messages,
            "max_output_tokens": MAX_OUTPUT_TOKENS,
        }
        if enable_web_search:
            payload["tools"] = [{"type": "web_search"}]

        request = urllib.request.Request(
            API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise OpenAIClientError(f"Erreur OpenAI HTTP {exc.code} : {body}") from exc
        except urllib.error.URLError as exc:
            raise OpenAIClientError(f"Erreur réseau : {exc.reason}") from exc
        except TimeoutError as exc:
            raise OpenAIClientError("Délai d'attente dépassé.") from exc

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise OpenAIClientError("Réponse OpenAI invalide.") from exc
        return _extract_output_text(data)
