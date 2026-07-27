"""Point d'entrée console du cœur Launcher Pro V9 — Sprint 1.

L'interface Pyto définitive sera ajoutée au Sprint 2. Cette commande permet dès
maintenant de vérifier le registre et d'afficher la bibliothèque persistante.
"""

from __future__ import annotations

from controller import Action, LauncherController
from core.paths import ensure_directories


def main() -> int:
    """Initialise les dossiers puis affiche les éléments enregistrés."""
    ensure_directories()
    result = LauncherController().dispatch(Action.LIST)
    if not result.success:
        print(result.error)
        return 1
    print("Launcher Pro V9 — Sprint 1")
    if not result.value:
        print("Bibliothèque vide.")
        return 0
    for item in result.value:
        marker = "★" if item.favorite else " "
        print(f"{marker} {item.name} [{item.kind}] — {item.id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
