import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict


class OpenAIClientError(Exception):
    pass


def _extract_output_text(data: Dict[str, Any]) -> str:
    direct = data.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()
    texts = []
    for item in data.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                text = content.get("text")
                if isinstance(text, str) and text.strip():
                    texts.append(text.strip())
    return "\n".join(texts).strip()


class OpenAIClient:
    def __init__(self, api_url: str, model: str, max_output_tokens: int) -> None:
        self.api_url = api_url
        self.model = model
        self.max_output_tokens = max_output_tokens
        self.api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not self.api_key:
            raise OpenAIClientError("OPENAI_API_KEY manquante")

    def ask(self, instructions: str, prompt: str) -> str:
        payload = {
            "model": self.model,
            "instructions": instructions,
            "input": prompt,
            "max_output_tokens": self.max_output_tokens,
        }
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
            with urllib.request.urlopen(request, timeout=120) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise OpenAIClientError(f"Erreur OpenAI {exc.code}: {detail}") from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise OpenAIClientError(f"Appel OpenAI impossible: {exc}") from exc
        text = _extract_output_text(data)
        if not text:
            raise OpenAIClientError("Réponse OpenAI vide")
        return text
