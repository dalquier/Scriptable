from __future__ import annotations

from core.backup import create_registry_backup, restore_latest_backup
from core.importer import import_script, pick_python_file
from core.registry import Registry
from core.runner import run_script


def print_scripts(registry: Registry) -> None:
    items = registry.search()
    if not items:
        print("Aucun script enregistré.")
        return
    for index, entry in enumerate(items, start=1):
        favorite = "★" if entry.favorite else " "
        print(f"{index}. {favorite} {entry.name} [{entry.category}] — {entry.run_count} lancement(s)")


def choose_entry(registry: Registry):
    items = registry.search()
    if not items:
        print("Aucun script disponible.")
        return None
    print_scripts(registry)
    try:
        index = int(input("Numéro du script : ").strip()) - 1
        return items[index]
    except (ValueError, IndexError):
        print("Sélection invalide.")
        return None


def main() -> None:
    registry = Registry.load()
    while True:
        print("\n=== LAUNCHER PRO V6 — MODE CONSOLE ===")
        print("1. Lister les scripts")
        print("2. Importer un script")
        print("3. Lancer un script")
        print("4. Basculer le favori")
        print("5. Supprimer un script")
        print("6. Sauvegarder le registre")
        print("7. Restaurer la dernière sauvegarde")
        print("0. Quitter")
        choice = input("> ").strip()

        if choice == "0":
            break
        if choice == "1":
            print_scripts(registry)
        elif choice == "2":
            try:
                path = pick_python_file()
                name = input("Nom du script (vide = nom du fichier) : ").strip() or None
                category = input("Catégorie (vide = Général) : ").strip() or None
                entry = import_script(path, name=name, category=category, registry=registry)
                print(f"Import réussi : {entry.name}")
            except Exception as exc:
                print(f"Import impossible : {exc}")
        elif choice == "3":
            entry = choose_entry(registry)
            if entry:
                result = run_script(entry)
                registry.save()
                print(result.output, end="")
                print("Succès" if result.success else f"Erreur :\n{result.error}")
        elif choice == "4":
            entry = choose_entry(registry)
            if entry:
                entry.favorite = not entry.favorite
                registry.save()
                print("Favori mis à jour.")
        elif choice == "5":
            entry = choose_entry(registry)
            if entry and input(f"Supprimer {entry.name} ? (oui/non) : ").strip().lower() == "oui":
                registry.remove(entry.id)
                print("Script supprimé.")
        elif choice == "6":
            backup = create_registry_backup()
            print(f"Sauvegarde créée : {backup}" if backup else "Aucun registre à sauvegarder.")
        elif choice == "7":
            backup = restore_latest_backup()
            if backup:
                registry = Registry.load()
                print(f"Registre restauré depuis {backup.name}")
            else:
                print("Aucune sauvegarde disponible.")
        else:
            print("Commande inconnue.")


if __name__ == "__main__":
    main()
