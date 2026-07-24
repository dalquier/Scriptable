from __future__ import annotations

import json
import socket
import urllib.error
import urllib.request

from tcc_budy.providers.base import ResponseProvider
from tcc_budy.support.errors import ProviderError


class OpenAIProvider(ResponseProvider):
    def __init__(self, settings):
        self.settings = settings

    @property
    def name(self) -> str:
        return "openai"

    def respond(self, messages) -> str:
        payload = {
            "model": self.settings.model,
            "instructions": self.settings.system_instructions,
            "input": [
                {
                    "role": item["role"],
                    "content": [{"type": "input_text", "text": item["content"]}],
                }
                for item in messages
            ],
            "max_output_tokens": self.settings.max_output_tokens,
            "store": self.settings.store_remote_responses,
        }
        request = urllib.request.Request(
            self.settings.api_url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.settings.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.settings.timeout_seconds) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise ProviderError(self._http_error(exc.code, detail)) from exc
        except (urllib.error.URLError, socket.timeout, TimeoutError) as exc:
            raise ProviderError("Impossible de joindre OpenAI ou délai dépassé.") from exc
        except json.JSONDecodeError as exc:
            raise ProviderError("Réponse OpenAI invalide.") from exc

        text = self._extract_text(data)
        if not text:
            raise ProviderError("OpenAI n'a renvoyé aucun texte exploitable.")
        return text

    @staticmethod
    def _extract_text(data):
        direct = data.get("output_text")
        if isinstance(direct, str) and direct.strip():
            return direct.strip()
        texts = []
        for item in data.get("output", []):
            if not isinstance(item, dict) or item.get("type") != "message":
                continue
            for content in item.get("content", []):
                if isinstance(content, dict) and content.get("type") == "output_text":
                    value = content.get("text")
                    if isinstance(value, str) and value.strip():
                        texts.append(value.strip())
        return "\n\n".join(texts)

    @staticmethod
    def _http_error(code, detail):
        try:
            parsed = json.loads(detail)
            message = (parsed.get("error") or {}).get("message") or detail
        except Exception:
            message = detail
        return f"Erreur OpenAI HTTP {code}: {str(message).strip()}"
