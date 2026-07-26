import json
from typing import Any, Dict, List


SYSTEM_INSTRUCTIONS = """Tu es le moteur de planification de DeveloperOS Builder.
Tu travailles exclusivement sur le projet DeveloperOS existant.
Tu dois proposer une seule itération petite, cohérente, testable et réversible.
Réponds uniquement avec un objet JSON valide, sans Markdown.
Schéma attendu:
{
  "status": "continue|done|blocked",
  "goal": "objectif bref",
  "summary": "raison du choix",
  "changes": [
    {"path": "chemin/relatif", "content": "contenu complet du fichier"}
  ]
}
N'utilise jamais de chemin absolu, jamais '..', jamais de suppression.
Ne modifie pas le dossier Builder.
"""


def choose_context_paths(index: Dict[str, Any], limit: int = 12) -> List[str]:
    files = index.get("files", [])
    preferred = [
        "README.md",
        "main.py",
        "executor.py",
        "planner.py",
        "state.py",
        "config.py",
        "task.txt",
    ]
    available = {item.get("path") for item in files if isinstance(item, dict)}
    selected = [path for path in preferred if path in available]
    for item in files:
        path = item.get("path") if isinstance(item, dict) else None
        if not isinstance(path, str) or path in selected or path.startswith("Builder/"):
            continue
        selected.append(path)
        if len(selected) >= limit:
            break
    return selected


def build_prompt(state: Dict[str, Any], index: Dict[str, Any], context: str) -> str:
    return (
        "Mission générale: poursuivre la construction de DeveloperOS jusqu'à une version finale robuste.\n\n"
        "État courant:\n"
        + json.dumps(state, ensure_ascii=False, indent=2)
        + "\n\nIndex du projet:\n"
        + json.dumps(index, ensure_ascii=False, indent=2)
        + "\n\nExtraits des fichiers existants:\n"
        + context
        + "\n\nChoisis la prochaine amélioration utile, limitée à quelques fichiers. "
          "Préserve la compatibilité Python 3.10 et Pyto."
    )
