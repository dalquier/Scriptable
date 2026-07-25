from __future__ import annotations

import json
import socket
import urllib.error
import urllib.request

from tcc_budy.providers.base import ResponseProvider
from tcc_budy.support.errors import ProviderError


class OpenAIProvider(ResponseProvider):
    """Provider OpenAI basé sur l'API Responses."""

    def __init__(self, settings):
        self.settings = settings

    @property
    def name(self) -> str:
        return "openai"

    def respond(self, messages) -> str:
        # Le champ content est volontairement transmis sous forme de chaîne.
        # Cela évite d'envoyer input_text pour les messages assistant : dans
        # l'API Responses, un ancien message assistant doit être représenté
        # comme une sortie, pas comme une nouvelle entrée utilisateur.
        input_messages = []
        for item in messages:
            role = item.get("role")
            content = str(item.get("content") or "").strip()
            if role not in ("user", "assistant") or not content:
                continue
            input_messages.append({"role": role, "content": content})

        if not input_messages:
            raise ProviderError("Aucun message valide à envoyer à OpenAI.")

        payload = {
            "model": self.settings.model,
            "instructions": self.settings.system_instructions,
            "input": input_messages,
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
            with urllib.request.urlopen(
                request, timeout=self.settings.timeout_seconds
            ) as response:
                raw = response.read().decode("utf-8")
                data = json.loads(raw)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise ProviderError(self._http_error(exc.code, detail)) from exc
        except (urllib.error.URLError, socket.timeout, TimeoutError) as exc:
            raise ProviderError(
                "Impossible de joindre OpenAI ou délai de réponse dépassé."
            ) from exc
        except json.JSONDecodeError as exc:
            raise ProviderError("La réponse reçue d'OpenAI n'est pas un JSON valide.") from exc

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
                if not isinstance(content, dict):
                    continue
                if content.get("type") != "output_text":
                    continue
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
