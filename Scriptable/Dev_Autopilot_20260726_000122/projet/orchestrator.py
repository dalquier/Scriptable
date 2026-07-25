"""Boucle autonome : OpenAI -> fichiers GitHub -> Continue jusqu'à complétude."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from config import Settings
from github_store import GitHubStore, WriteResult
from openai_client import OpenAIClient, extract_output_text


DEVELOPER_INSTRUCTIONS = """
Tu es un agent de développement logiciel autonome.

Tu dois répondre UNIQUEMENT avec un objet JSON valide, sans Markdown, sans texte avant ou après.
Le schéma attendu est exactement :
{
  "status": "in_progress" | "complete" | "blocked",
  "summary": "résumé bref de ce qui a été réalisé pendant cette itération",
  "files": [
    {
      "path": "chemin/relatif/du/fichier",
      "content": "contenu UTF-8 COMPLET du fichier"
    }
  ],
  "next_action": "prochaine action précise ou raison du blocage"
}

Règles impératives :
- Fournis toujours des fichiers complets, jamais des extraits ni des patches.
- N'utilise jamais de chemin absolu, de '..' ou de chemin sortant de la racine du projet.
- Ne fournis aucun secret réel.
- Le statut doit rester "in_progress" tant que la phase demandée n'est pas entièrement terminée.
- Utilise "complete" uniquement lorsque tous les livrables de la phase sont créés et cohérents.
- Utilise "blocked" uniquement si une information ou une action humaine est indispensable.
- Limite chaque itération à un lot raisonnable de fichiers cohérents.
""".strip()


@dataclass
class RunState:
    previous_response_id: str | None = None
    iteration: int = 0
    status: str = "in_progress"

    @classmethod
    def load(cls, path: Path) -> "RunState":
        if not path.exists():
            return cls()
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            previous_response_id=data.get("previous_response_id"),
            iteration=int(data.get("iteration", 0)),
            status=str(data.get("status", "in_progress")),
        )

    def save(self, path: Path) -> None:
        path.write_text(
            json.dumps(
                {
                    "previous_response_id": self.previous_response_id,
                    "iteration": self.iteration,
                    "status": self.status,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )


def _safe_relative_path(raw_path: str) -> str:
    normalized = raw_path.replace("\\", "/").strip().strip("/")
    if not normalized or normalized.startswith(".") or ".." in normalized.split("/"):
        raise ValueError(f"Chemin de fichier refusé : {raw_path!r}")
    return normalized


def _parse_model_payload(text: str) -> dict[str, Any]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Le modèle n'a pas renvoyé le JSON strict attendu. Réponse reçue :\n" + text[:1000]
        ) from exc

    status = payload.get("status")
    if status not in {"in_progress", "complete", "blocked"}:
        raise RuntimeError(f"Statut invalide renvoyé par le modèle : {status!r}")
    files = payload.get("files", [])
    if not isinstance(files, list):
        raise RuntimeError("Le champ 'files' doit être une liste.")
    return payload


class DevAutopilot:
    def __init__(self, settings: Settings, workdir: Path) -> None:
        self.settings = settings
        self.workdir = workdir
        self.state_path = workdir / "state.json"
        self.handoff_path = workdir / "handoff.md"
        self.openai = OpenAIClient(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            timeout_seconds=settings.timeout_seconds,
        )
        self.github = GitHubStore(
            token=settings.github_token,
            repository=settings.github_repository,
            branch=settings.github_branch,
        )

    def run(self) -> str:
        if not self.handoff_path.exists():
            raise RuntimeError(
                f"Fichier manquant : {self.handoff_path}. Copiez handoff.example.md vers handoff.md."
            )

        mission = self.handoff_path.read_text(encoding="utf-8").strip()
        if not mission:
            raise RuntimeError("handoff.md est vide.")

        state = RunState.load(self.state_path)
        user_input = mission if not state.previous_response_id else "Continue"

        while state.iteration < self.settings.max_iterations:
            state.iteration += 1
            print(f"\n=== Itération {state.iteration}/{self.settings.max_iterations} ===")

            response = self.openai.create_response(
                user_input=user_input,
                instructions=DEVELOPER_INSTRUCTIONS,
                previous_response_id=state.previous_response_id,
            )
            response_id = response.get("id")
            if not isinstance(response_id, str) or not response_id:
                raise RuntimeError("La réponse OpenAI ne contient pas d'identifiant.")

            payload = _parse_model_payload(extract_output_text(response))
            results: list[WriteResult] = []
            for file_data in payload.get("files", []):
                if not isinstance(file_data, dict):
                    raise RuntimeError("Entrée de fichier invalide.")
                rel_path = _safe_relative_path(str(file_data.get("path", "")))
                content = file_data.get("content")
                if not isinstance(content, str):
                    raise RuntimeError(f"Contenu non textuel pour {rel_path}.")
                target = f"{self.settings.target_root}/{rel_path}"
                result = self.github.upsert_text(
                    repo_path=target,
                    content=content,
                    message=f"feat: génération automatique itération {state.iteration}",
                )
                results.append(result)
                print(f"{result.action}: {result.path} ({result.commit_sha[:12]})")

            state.previous_response_id = response_id
            state.status = str(payload["status"])
            state.save(self.state_path)

            summary = str(payload.get("summary", "")).strip()
            next_action = str(payload.get("next_action", "")).strip()
            print(f"Statut : {state.status}")
            if summary:
                print(f"Résumé : {summary}")
            if next_action:
                print(f"Suite : {next_action}")

            if state.status == "complete":
                return "Projet terminé"
            if state.status == "blocked":
                return "Projet bloqué"

            user_input = "Continue"

        state.status = "blocked"
        state.save(self.state_path)
        return "Arrêt : nombre maximal d'itérations atteint"
