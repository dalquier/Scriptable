"""Client sans dépendance pour l'API OpenAI Responses."""

from __future__ import annotations

import json
import socket
import urllib.error
import urllib.request
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urlparse

import config


class OpenAIClientError(Exception):
    """Erreur sûre à présenter à l'utilisateur (jamais de secret)."""


def _extract_output_text(data: Dict[str, Any]) -> str:
    direct = data.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()
    parts = []  # type: List[str]
    output = data.get("output", [])
    if not isinstance(output, list):
        output = []
    for item in output:
        if not isinstance(item, dict) or item.get("type") != "message":
            continue
        content_items = item.get("content", [])
        if not isinstance(content_items, list):
            continue
        for content in content_items:
            if not isinstance(content, dict):
                continue
            text = content.get("text")
            if content.get("type") == "output_text" and isinstance(text, str) and text.strip():
                parts.append(text.strip())
    if parts:
        return "\n\n".join(parts)
    raise OpenAIClientError("La réponse OpenAI ne contient aucun texte exploitable.")


def _extract_sources(data: Dict[str, Any]) -> List[Dict[str, str]]:
    """Normalise les citations URL; tolère les réponses qui n'en ont aucune."""
    sources = []  # type: List[Dict[str, str]]
    seen = set()
    for item in data.get("output", []) if isinstance(data.get("output"), list) else []:
        if not isinstance(item, dict):
            continue
        for content in item.get("content", []) if isinstance(item.get("content"), list) else []:
            if not isinstance(content, dict):
                continue
            for annotation in content.get("annotations", []) if isinstance(content.get("annotations"), list) else []:
                if not isinstance(annotation, dict):
                    continue
                citation = annotation.get("url_citation", annotation)
                url = citation.get("url") if isinstance(citation, dict) else None
                if not isinstance(url, str) or not url.startswith(("http://", "https://")) or url in seen:
                    continue
                seen.add(url)
                sources.append({
                    "title": str(citation.get("title") or url),
                    "domain": urlparse(url).netloc,
                    "url": url,
                })
    return sources


def parse_response(raw: bytes) -> Dict[str, Any]:
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise OpenAIClientError("La réponse OpenAI n'est pas un JSON valide.") from exc
    if not isinstance(data, dict):
        raise OpenAIClientError("La réponse OpenAI a un format inattendu.")
    return {"text": _extract_output_text(data), "sources": _extract_sources(data), "metadata": {"id": data.get("id"), "status": data.get("status")}}


class OpenAIClient:
    def __init__(self, api_key: Optional[str] = None, opener: Optional[Callable[..., Any]] = None) -> None:
        self.api_key = config.OPENAI_API_KEY if api_key is None else api_key
        self._opener = opener or urllib.request.urlopen
        if not self.api_key or self.api_key in ("sk-...", "VOTRE_CLE_ICI"):
            raise OpenAIClientError("Clé OpenAI absente. Créez projet/config_local.py.")

    @staticmethod
    def build_payload(messages: List[Dict[str, str]], enable_web_search: bool = False) -> Dict[str, Any]:
        payload = {
            "model": config.MODEL,
            "instructions": config.SYSTEM_INSTRUCTIONS,
            "input": [{"role": m["role"], "content": m["content"]} for m in messages],
            "max_output_tokens": config.MAX_OUTPUT_TOKENS,
        }  # type: Dict[str, Any]
        if enable_web_search:
            payload["tools"] = [{"type": "web_search"}]
        return payload

    def create_response(self, messages: List[Dict[str, str]], enable_web_search: bool = False) -> Dict[str, Any]:
        payload = self.build_payload(messages, enable_web_search)
        request = urllib.request.Request(
            config.API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": "Bearer " + self.api_key, "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with self._opener(request, timeout=config.TIMEOUT_SECONDS) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            # Ne pas recopier le corps: il peut contenir des données sensibles.
            messages_by_status = {401: "Clé API refusée.", 403: "Accès au modèle refusé.", 404: "Modèle ou endpoint introuvable.", 429: "Quota ou limite de débit atteint."}
            detail = messages_by_status.get(exc.code, "La requête OpenAI a échoué.")
            raise OpenAIClientError("Erreur OpenAI HTTP {0} — {1}".format(exc.code, detail)) from exc
        except (socket.timeout, TimeoutError) as exc:
            raise OpenAIClientError("Délai d'attente OpenAI dépassé; vous pouvez réessayer.") from exc
        except urllib.error.URLError as exc:
            reason = "connexion indisponible"
            if isinstance(exc.reason, socket.timeout):
                raise OpenAIClientError("Délai d'attente OpenAI dépassé; vous pouvez réessayer.") from exc
            raise OpenAIClientError("Erreur réseau ({0}); vérifiez votre connexion.".format(reason)) from exc
        except OSError as exc:
            raise OpenAIClientError("Erreur réseau; vérifiez votre connexion.") from exc
        return parse_response(raw)
