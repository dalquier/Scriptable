from __future__ import annotations

from pathlib import Path

from core.importer import add_project, import_script, list_python_files, pick_directory, pick_file
from core.registry import Registry
from core.service import rename_item, run_by_id
from ui.main_view import (
    choose_entry_script,
    present_launcher_once,
    prompt_rename,
    show_message,
)


def main() -> None:
    """Boucle principale.

    Chaque action système est exécutée après la fermeture de Launcher Pro.
    Cela évite de présenter le sélecteur Fichiers ou un script au-dessus d’une
    autre feuille modale, comportement bloqué par iOS sur certaines versions.
    """
    while True:
        action, item_id = present_launcher_once()

        if action == "quit":
            return

        try:
            if action == "add_script":
                selected = pick_file()
                import_script(selected, registry=Registry.load())

            elif action == "add_project":
                root = Path(pick_directory())
                files = list_python_files(root)
                if not files:
                    raise ValueError("Aucun fichier .py trouvé dans ce dossier")
                entry = choose_entry_script(root, files)
                if entry:
                    add_project(root, entry, registry=Registry.load())

            elif action == "rename" and item_id:
                registry = Registry.load()
                item = registry.require(item_id)
                new_name = prompt_rename(item.name)
                if new_name is not None:
                    rename_item(item_id, new_name)

            elif action == "run" and item_id:
                item, result = run_by_id(item_id)
                if result.output:
                    print(result.output, end="")
                if not result.success:
                    show_message(
                        f"Erreur — {item.name}",
                        (result.error or "Erreur inconnue")[-3000:],
                    )

        except Exception as exc:
            show_message("Launcher Pro", str(exc))


if __name__ == "__main__":
    main()
