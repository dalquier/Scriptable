"""DeveloperOS Draft v0.1 autonome.

Boucle minimale qui appelle l'API OpenAI, conserve son état et relance
la conversation tant que le modèle répond avec le statut `continue` ou
termine son texte par `En cours`.

Compatible Python 3.10 / Pyto. Aucune dépendance externe.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
STATE_FILE = ROOT / "state.json"
TASK_FILE = ROOT / "task.txt"
LOG_FILE = ROOT / "developeros.log"

API_URL = "https://api.openai.com/v1/responses"
MODEL = os.environ.get("OPENAI_MODEL", "gpt-5.6")
API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
MAX_ITERATIONS = int(os.environ.get("DEVELOPEROS_MAX_ITERATIONS", "25"))
DELAY_SECONDS = float(os.environ.get("DEVELOPEROS_DELAY_SECONDS", "1"))

SYSTEM_PROMPT = """Tu es DeveloperOS Draft v0.1, un agent de développement autonome.
Travaille uniquement sur la tâche fournie. Avance par petites étapes vérifiables.
Réponds exclusivement avec un objet JSON valide contenant :
{
  \"status\": \"continue|done|blocked\",
  \"summary\": \"résumé court\",
  \"next_prompt\": \"instruction précise pour l'itération suivante\"
}
Utilise status=continue lorsqu'une nouvelle itération est nécessaire.
Utilise status=done lorsque la tâche est terminée.
Utilise status=blocked uniquement si une intervention humaine est indispensable.
"""

DEFAULT_TASK = """Construire progressivement DeveloperOS Draft v0.1 dans ce dossier.
Priorités : garder le projet simple, exécutable dans Pyto, sans dépendance externe,
avec état persistant, boucle autonome, reprise après interruption et journalisation.
Commence par analyser l'état actuel et indique l'étape suivante.
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(message: str) -> None:
    line = f"[{now_iso()}] {message}"
    print(line)
    with LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def load_state() -> dict[str, Any]:
    if not STATE_FILE.exists():
        return {
            "version": "0.1.0-draft",
            "status": "ready",
            "iteration": 0,
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "conversation": [],
            "last_summary": "",
            "next_prompt": "",
        }
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"État illisible : {exc}") from exc


def save_state(state: dict[str, Any]) -> None:
    state["updated_at"] = now_iso()
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(STATE_FILE)


def load_task() -> str:
    if TASK_FILE.exists():
        text = TASK_FILE.read_text(encoding="utf-8").strip()
        if text:
            return text
    TASK_FILE.write_text(DEFAULT_TASK, encoding="utf-8")
    return DEFAULT_TASK


def extract_output_text(payload: dict[str, Any]) -> str:
    direct = payload.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()

    chunks: list[str] = []
    for item in payload.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                text = content.get("text")
                if isinstance(text, str) and text.strip():
                    chunks.append(text.strip())
    return "\n".join(chunks).strip()


def call_openai(prompt: str) -> str:
    if not API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY absent. Définis la variable d'environnement avant le lancement."
        )

    body = {
        "model": MODEL,
        "instructions": SYSTEM_PROMPT,
        "input": prompt,
        "max_output_tokens": 1200,
    }
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Erreur OpenAI HTTP {exc.code}: {details}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Connexion OpenAI impossible : {exc.reason}") from exc

    text = extract_output_text(payload)
    if not text:
        raise RuntimeError("Réponse OpenAI vide.")
    return text


def parse_agent_response(text: str) -> dict[str, str]:
    stripped = text.strip()
    try:
        parsed = json.loads(stripped)
        status = str(parsed.get("status", "")).strip().lower()
        if status in {"continue", "done", "blocked"}:
            return {
                "status": status,
                "summary": str(parsed.get("summary", "")).strip(),
                "next_prompt": str(parsed.get("next_prompt", "")).strip(),
            }
    except json.JSONDecodeError:
        pass

    lowered = stripped.lower()
    if lowered.endswith("en cours"):
        return {
            "status": "continue",
            "summary": stripped,
            "next_prompt": "Continue exactement là où tu t'es arrêté.",
        }
    return {"status": "done", "summary": stripped, "next_prompt": ""}


def build_prompt(task: str, state: dict[str, Any]) -> str:
    previous = state.get("last_summary", "")
    next_prompt = state.get("next_prompt", "")
    iteration = int(state.get("iteration", 0)) + 1
    return f"""TÂCHE GLOBALE
{task}

ÉTAT COURANT
- Itération : {iteration}
- Dernier résumé : {previous or 'aucun'}
- Instruction précédente : {next_prompt or 'démarrage'}

Décide et exécute intellectuellement la prochaine petite étape. Retourne le JSON demandé.
"""


def run() -> None:
    state = load_state()
    task = load_task()
    state["status"] = "running"
    save_state(state)

    log(f"DeveloperOS Draft v0.1 démarré avec le modèle {MODEL}.")

    for _ in range(MAX_ITERATIONS):
        prompt = build_prompt(task, state)
        state["iteration"] = int(state.get("iteration", 0)) + 1
        log(f"Itération {state['iteration']}...")

        try:
            raw = call_openai(prompt)
            result = parse_agent_response(raw)
        except Exception as exc:
            state["status"] = "error"
            state["last_error"] = str(exc)
            save_state(state)
            log(f"ERREUR : {exc}")
            return

        state.setdefault("conversation", []).append(
            {
                "iteration": state["iteration"],
                "time": now_iso(),
                "raw": raw,
                "status": result["status"],
                "summary": result["summary"],
            }
        )
        state["last_summary"] = result["summary"]
        state["next_prompt"] = result["next_prompt"]
        state["status"] = result["status"]
        save_state(state)
        log(f"Statut : {result['status']} — {result['summary']}")

        if result["status"] in {"done", "blocked"}:
            return
        time.sleep(DELAY_SECONDS)

    state["status"] = "paused"
    state["last_error"] = "Limite d'itérations atteinte. Relancer le script pour reprendre."
    save_state(state)
    log("Limite d'itérations atteinte ; état sauvegardé.")


if __name__ == "__main__":
    run()
