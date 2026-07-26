import posixpath
import threading

import pyto_ui as ui

from github_api import GitHubAPIError, GitHubClient
from storage import load_settings, save_settings


class GitHubContentManagerV6:
    def __init__(self):
        self.settings = load_settings()
        self.client = None
        self.opened_path = ""
        self.opened_sha = ""
        self._build_ui()
        self._build_client()

    def _build_ui(self):
        self.view = ui.View()
        self.view.name = "GitHub Content Manager V6"
        self.view.background_color = ui.COLOR_SYSTEM_BACKGROUND

        self.repo = self._field(self.settings["repository"], 12, 12, 235, 36)
        self.branch = self._field(self.settings["branch"], 255, 12, 120, 36)
        self.root_path = self._field(self.settings["root_path"], 12, 54, 180, 36)
        self.token = self._field(self.settings["token"], 198, 54, 177, 36)

        self.path = self._field(self.settings["root_path"], 12, 102, 363, 38)
        self.new_path = self._field("", 12, 146, 363, 38)

        self._button("Lister", self.list_action, 12, 192, 82, 38)
        self._button("Ouvrir", self.open_action, 101, 192, 82, 38)
        self._button("Enregistrer", self.save_action, 190, 192, 96, 38)
        self._button("Réglages", self.settings_action, 293, 192, 82, 38)

        self._button("Nouveau fichier", self.create_file_action, 12, 237, 115, 38)
        self._button("Nouveau dossier", self.create_folder_action, 134, 237, 115, 38)
        self._button("Renommer", self.rename_action, 256, 237, 119, 38)

        self._button("Supprimer", self.delete_action, 12, 282, 115, 38)
        self._button("Parent", self.parent_action, 134, 282, 115, 38)
        self._button("Fermer", self.close_action, 256, 282, 119, 38)

        self.status = ui.Label()
        self.status.text = "Prêt — renseigne le jeton puis enregistre les réglages."
        self.status.frame = (12, 327, 363, 44)
        self.status.number_of_lines = 2
        self.status.text_color = ui.COLOR_SECONDARY_LABEL
        self.view.add_subview(self.status)

        self.editor = ui.TextView()
        self.editor.frame = (12, 376, 363, 430)
        self.editor.text = ""
        self.editor.font = ui.Font("Menlo", 13)
        self.editor.background_color = ui.COLOR_SECONDARY_SYSTEM_BACKGROUND
        self.editor.flex = [ui.FLEXIBLE_WIDTH, ui.FLEXIBLE_HEIGHT]
        self.view.add_subview(self.editor)

    def _field(self, value, x, y, width, height):
        field = ui.TextField()
        field.text = value
        field.frame = (x, y, width, height)
        field.background_color = ui.COLOR_SECONDARY_SYSTEM_BACKGROUND
        self.view.add_subview(field)
        return field

    def _button(self, title, action, x, y, width, height):
        button = ui.Button(title=title)
        button.frame = (x, y, width, height)
        button.action = action
        self.view.add_subview(button)
        return button

    def _build_client(self):
        self.client = GitHubClient(
            self.settings["repository"],
            self.settings["branch"],
            self.settings["token"],
        )

    def run(self):
        mode = getattr(ui, "PRESENTATION_MODE_FULLSCREEN", None)
        if mode is None:
            mode = getattr(ui, "PRESENTATION_MODE_SHEET", None)
        if mode is None:
            ui.show_view(self.view)
        else:
            ui.show_view(self.view, mode)

    def _set_status(self, text):
        self.status.text = text

    def _run(self, operation):
        self._set_status("Traitement en cours…")

        def worker():
            try:
                message = operation()
                self._set_status(message or "Terminé.")
            except (GitHubAPIError, ValueError, KeyError, OSError) as exc:
                self._set_status("Erreur : " + str(exc))
            except Exception as exc:
                self._set_status("Erreur inattendue : " + repr(exc))

        threading.Thread(target=worker, daemon=True).start()

    @staticmethod
    def _clean(path):
        path = (path or "").strip().strip("/")
        if ".." in path.split("/"):
            raise ValueError("Les chemins contenant '..' sont interdits.")
        return path

    def settings_action(self, sender):
        def operation():
            repository = self.repo.text.strip()
            if "/" not in repository:
                raise ValueError("Dépôt attendu : propriétaire/nom")
            self.settings = {
                "repository": repository,
                "branch": self.branch.text.strip() or "main",
                "root_path": self._clean(self.root_path.text),
                "token": self.token.text.strip(),
            }
            save_settings(self.settings)
            self._build_client()
            self.client.get_repo()
            return "Réglages enregistrés et connexion GitHub validée."
        self._run(operation)

    def list_action(self, sender):
        def operation():
            path = self._clean(self.path.text)
            items = self.client.list_path(path)
            lines = []
            for item in items:
                icon = "📁" if item.get("type") == "dir" else "📄"
                size = item.get("size", 0)
                lines.append(f"{icon} {item.get('path', '')}   [{size} o]")
            self.editor.text = "\n".join(lines) if lines else "Dossier vide."
            self.opened_path = ""
            self.opened_sha = ""
            return f"{len(items)} élément(s) dans {path or '/'}"
        self._run(operation)

    def open_action(self, sender):
        def operation():
            path = self._clean(self.path.text)
            if not path:
                raise ValueError("Saisis le chemin d’un fichier.")
            data = self.client.get_file(path)
            self.editor.text = data["content"]
            self.opened_path = data["path"]
            self.opened_sha = data["sha"]
            return "Fichier ouvert : " + data["path"]
        self._run(operation)

    def save_action(self, sender):
        def operation():
            path = self.opened_path or self._clean(self.path.text)
            if not path:
                raise ValueError("Aucun fichier ouvert.")
            sha = self.opened_sha
            if not sha:
                sha = self.client.get_file(path)["sha"]
            result = self.client.put_file(path, self.editor.text or "", "Update " + path, sha)
            self.opened_path = path
            self.opened_sha = result.get("content", {}).get("sha", "") or self.client.get_file(path)["sha"]
            return "Fichier enregistré : " + path
        self._run(operation)

    def create_file_action(self, sender):
        def operation():
            path = self._clean(self.new_path.text)
            if not path:
                raise ValueError("Saisis le nouveau chemin.")
            self.client.put_file(path, self.editor.text or "", "Create " + path)
            self.path.text = path
            return "Fichier créé : " + path
        self._run(operation)

    def create_folder_action(self, sender):
        def operation():
            path = self._clean(self.new_path.text)
            if not path:
                raise ValueError("Saisis le chemin du dossier.")
            self.client.create_folder(path)
            return "Dossier créé : " + path
        self._run(operation)

    def rename_action(self, sender):
        def operation():
            old_path = self._clean(self.path.text)
            new_path = self._clean(self.new_path.text)
            if not old_path or not new_path:
                raise ValueError("Renseigne le chemin actuel et le nouveau chemin.")
            self.client.rename_file(old_path, new_path)
            self.path.text = new_path
            self.opened_path = new_path if self.opened_path == old_path else ""
            self.opened_sha = ""
            return f"Renommé : {old_path} → {new_path}"
        self._run(operation)

    def delete_action(self, sender):
        def operation():
            path = self._clean(self.path.text)
            if not path:
                raise ValueError("Saisis le fichier à supprimer.")
            data = self.client.get_file(path)
            self.client.delete_file(path, data["sha"], "Delete " + path)
            self.opened_path = ""
            self.opened_sha = ""
            self.editor.text = ""
            return "Fichier supprimé : " + path
        self._run(operation)

    def parent_action(self, sender):
        current = self._clean(self.path.text)
        self.path.text = posixpath.dirname(current)
        self.list_action(sender)

    def close_action(self, sender):
        self.view.close()
