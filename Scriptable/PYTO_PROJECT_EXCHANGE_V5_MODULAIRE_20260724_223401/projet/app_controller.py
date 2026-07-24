from __future__ import annotations

from exporter import export_project
from file_picker import pick_directory
from importer import import_exchange
from prompts import MIGRATION_PROMPT, PROMPT_V5


class AppController:
    def __init__(self, ui_adapter):
        self.ui = ui_adapter

    def export_action(self, sender=None):
        try:
            project = pick_directory("Choisir le dossier projet")
            if not project:
                self.ui.set_status("Export annulé.")
                return
            destination = pick_directory("Choisir le dossier de destination")
            if not destination:
                self.ui.set_status("Export annulé.")
                return
            self.ui.set_status("Export en cours…")
            result = export_project(project, destination)
            self.ui.show_message(
                "Export terminé",
                f"Dossier : {result['output_folder']}\n"
                f"Fichiers : {result['file_count']}\n"
                f"Fragments : {result['fragment_count']}\n"
                f"Parties : {result['part_count']}",
            )
            self.ui.set_status("Export terminé.")
        except Exception as exc:
            self.ui.show_error("Erreur d'export", str(exc))
            self.ui.set_status("Échec de l'export.")

    def import_action(self, sender=None):
        try:
            exchange = pick_directory("Choisir le dossier PYTO_EXCHANGE")
            if not exchange:
                self.ui.set_status("Import annulé.")
                return
            destination = pick_directory("Choisir le dossier de destination")
            if not destination:
                self.ui.set_status("Import annulé.")
                return
            self.ui.set_status("Import en cours…")
            result = import_exchange(exchange, destination)
            self.ui.show_message(
                "Import terminé",
                f"Dossier : {result['output_folder']}\n"
                f"Fichiers reconstruits : {result['file_count']}\n"
                f"Parties lues : {result['part_count']}",
            )
            self.ui.set_status("Import terminé.")
        except Exception as exc:
            self.ui.show_error("Erreur d'import", str(exc))
            self.ui.set_status("Échec de l'import.")

    def copy_prompt_action(self, sender=None):
        try:
            self.ui.copy_text(PROMPT_V5)
            self.ui.set_status("Prompt V5 copié.")
        except Exception as exc:
            self.ui.show_error("Erreur de copie", str(exc))

    def copy_migration_action(self, sender=None):
        try:
            self.ui.copy_text(MIGRATION_PROMPT)
            self.ui.set_status("Prompt de migration copié.")
        except Exception as exc:
            self.ui.show_error("Erreur de copie", str(exc))
