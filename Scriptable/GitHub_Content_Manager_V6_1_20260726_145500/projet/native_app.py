import posixpath
import threading

import pyto_ui as ui

from config import APP_NAME, DISPLAY_MODE
from github_api import GitHubAPIError, GitHubClient
from storage import load_settings, save_settings


class GitHubContentManagerV61:
    def __init__(self):
        self.settings = load_settings()
        self.client = None
        self.current_path = self.settings.get("root_path", "").strip("/")
        self.current_items = []
        self.current_file_sha = ""
        self._build_client()
        self._build_ui()

    def _build_client(self):
        self.client = GitHubClient(
            self.settings.get("repository", ""),
            self.settings.get("branch", "main"),
            self.settings.get("token", ""),
        )

    def _build_ui(self):
        self.view = ui.View()
        self.view.name = APP_NAME
        self.view.background_color = ui.COLOR_SYSTEM_BACKGROUND

        self.repo_field = self._field("Dépôt propriétaire/nom", self.settings.get("repository", ""))
        self.branch_field = self._field("Branche", self.settings.get("branch", "main"))
        self.root_field = self._field("Dossier racine", self.settings.get("root_path", "Scriptable"))
        self.token_field = self._field("Jeton GitHub facultatif en lecture", self.settings.get("token", ""), secure=True)

        self.save_settings_button = self._button("Enregistrer les réglages", self.save_settings_action)
        self.refresh_button = self._button("Actualiser", self.refresh_action)
        self.up_button = self._button("Dossier parent", self.go_up_action)

        self.path_field = self._field("Chemin du fichier sélectionné", "")
        self.new_path_field = self._field("Nouveau chemin / nouveau fichier", "")

        self.open_button = self._button("Ouvrir", self.open_file_action)
        self.create_button = self._button("Créer fichier", self.create_file_action)
        self.folder_button = self._button("Créer dossier", self.create_folder_action)
        self.rename_button = self._button("Renommer / déplacer", self.rename_action)
        self.delete_button = self._button("Supprimer", self.delete_action)
        self.save_file_button = self._button("Enregistrer le fichier", self.save_file_action)

        self.status_label = ui.Label()
        self.status_label.text = "Prêt"
        self.status_label.number_of_lines = 0
        self.status_label.text_color = ui.COLOR_SECONDARY_LABEL

        self.list_view = ui.TableView()
        self.list_view.data_source = self
        self.list_view.delegate = self

        self.editor = ui.TextView()
        self.editor.font = ui.Font.system_font_of_size(14)
        self.editor.hidden = True

        controls = [
            self.repo_field,
            self.branch_field,
            self.root_field,
            self.token_field,
            self.save_settings_button,
            self.refresh_button,
            self.up_button,
            self.path_field,
            self.new_path_field,
            self.open_button,
            self.create_button,
            self.folder_button,
            self.rename_button,
            self.delete_button,
            self.save_file_button,
            self.status_label,
            self.list_view,
            self.editor,
        ]
        for control in controls:
            self.view.add_subview(control)

        self.view.layout = self.layout

    def _field(self, placeholder, value, secure=False):
        field = ui.TextField()
        field.placeholder = placeholder
        field.text = value
        field.secure_text_entry = secure
        field.border_style = ui.TEXT_FIELD_BORDER_STYLE_ROUNDED_RECT
        return field

    def _button(self, title, action):
        button = ui.Button()
        button.title = title
        button.action = action
        return button

    def layout(self, sender=None):
        width = self.view.width
        margin = 12
        gap = 8
        y = 12
        full = width - 2 * margin
        field_h = 38
        button_h = 36

        for field in (self.repo_field, self.branch_field, self.root_field, self.token_field):
            field.frame = (margin, y, full, field_h)
            y += field_h + gap

        self.save_settings_button.frame = (margin, y, full, button_h)
        y += button_h + gap

        half = (full - gap) / 2
        self.refresh_button.frame = (margin, y, half, button_h)
        self.up_button.frame = (margin + half + gap, y, half, button_h)
        y += button_h + gap

        self.path_field.frame = (margin, y, full, field_h)
        y += field_h + gap
        self.new_path_field.frame = (margin, y, full, field_h)
        y += field_h + gap

        buttons = [self.open_button, self.create_button, self.folder_button, self.rename_button, self.delete_button, self.save_file_button]
        button_width = (full - gap) / 2
        for index, button in enumerate(buttons):
            row = index // 2
            column = index % 2
            button.frame = (margin + column * (button_width + gap), y + row * (button_h + gap), button_width, button_h)
        y += 3 * (button_h + gap)

        self.status_label.frame = (margin, y, full, 44)
        y += 48

        available = max(180, self.view.height - y - margin)
        if self.editor.hidden:
            self.list_view.frame = (margin, y, full, available)
            self.editor.frame = (margin, y, full, available)
        else:
            self.list_view.frame = (margin, y, full, available)
            self.editor.frame = (margin, y, full, available)

    def run(self):
        mode = getattr(ui, "PRESENTATION_MODE_SHEET", None)
        if mode is None:
            mode = getattr(ui, "PRESENTATION_MODE_FORM_SHEET", None)
        if mode is None:
            mode = DISPLAY_MODE
        ui.show_view(self.view, mode)
        threading.Timer(0.4, self.refresh).start()

    def save_settings_action(self, sender):
        try:
            repository = (self.repo_field.text or "").strip()
            branch = (self.branch_field.text or "main").strip() or "main"
            root_path = (self.root_field.text or "").strip().strip("/")
            token = (self.token_field.text or "").strip()

            if "/" not in repository:
                raise ValueError("Le dépôt doit être au format propriétaire/nom.")

            new_settings = {
                "repository": repository,
                "branch": branch,
                "root_path": root_path,
                "token": token,
            }
            save_settings(new_settings)
            self.settings = new_settings
            self.current_path = root_path
            self._build_client()
            self._set_status("Réglages enregistrés localement.")
            self.refresh()
        except Exception as exc:
            self._set_status("Erreur réglages : {}".format(exc))

    def refresh_action(self, sender):
        self.refresh()

    def go_up_action(self, sender):
        root = self.settings.get("root_path", "").strip("/")
        if self.current_path == root:
            self._set_status("Déjà au dossier racine.")
            return
        parent = posixpath.dirname(self.current_path)
        if root and not (parent == root or parent.startswith(root + "/")):
            parent = root
        self.current_path = parent
        self.refresh()

    def refresh(self):
        self._background(self._refresh_worker)

    def _refresh_worker(self):
        items = self.client.list_path(self.current_path)
        self.current_items = sorted(items, key=lambda item: (item.get("type") != "dir", item.get("name", "").lower()))
        self._main(self._reload_table)
        self._set_status("{} · {} / {}".format(self.settings["repository"], self.settings["branch"], self.current_path))

    def open_file_action(self, sender):
        path = (self.path_field.text or "").strip().strip("/")
        if not path:
            self._set_status("Sélectionne ou saisis un chemin de fichier.")
            return
        self._background(lambda: self._open_file_worker(path))

    def _open_file_worker(self, path):
        data = self.client.get_file(path)
        self.current_file_sha = data["sha"]
        self._main(lambda: self._show_editor(data["path"], data["content"]))
        self._set_status("Fichier ouvert : " + data["path"])

    def create_file_action(self, sender):
        path = self._target_new_path()
        if path:
            self._background(lambda: self._create_file_worker(path))

    def _create_file_worker(self, path):
        self.client.put_file(path, "", "Create {}".format(path))
        self._set_status("Fichier créé : " + path)
        self.refresh()

    def create_folder_action(self, sender):
        path = self._target_new_path()
        if path:
            self._background(lambda: self._create_folder_worker(path))

    def _create_folder_worker(self, path):
        self.client.create_folder(path)
        self._set_status("Dossier créé : " + path)
        self.refresh()

    def rename_action(self, sender):
        old_path = (self.path_field.text or "").strip().strip("/")
        new_path = (self.new_path_field.text or "").strip().strip("/")
        if not old_path or not new_path:
            self._set_status("Indique l'ancien et le nouveau chemin.")
            return
        self._background(lambda: self._rename_worker(old_path, new_path))

    def _rename_worker(self, old_path, new_path):
        self.client.rename_file(old_path, new_path)
        self._set_status("Renommé : {} → {}".format(old_path, new_path))
        self.refresh()

    def delete_action(self, sender):
        path = (self.path_field.text or "").strip().strip("/")
        if not path:
            self._set_status("Indique un fichier à supprimer.")
            return
        self._background(lambda: self._delete_worker(path))

    def _delete_worker(self, path):
        data = self.client.get_file(path)
        self.client.delete_file(path, data["sha"], "Delete {}".format(path))
        self._set_status("Supprimé : " + path)
        self.refresh()

    def save_file_action(self, sender):
        path = (self.path_field.text or "").strip().strip("/")
        if not path or not self.current_file_sha:
            self._set_status("Ouvre d'abord un fichier.")
            return
        content = self.editor.text or ""
        self._background(lambda: self._save_file_worker(path, content))

    def _save_file_worker(self, path, content):
        result = self.client.put_file(path, content, "Update {}".format(path), self.current_file_sha)
        try:
            self.current_file_sha = result["content"]["sha"]
        except Exception:
            pass
        self._set_status("Fichier enregistré : " + path)

    def _target_new_path(self):
        value = (self.new_path_field.text or "").strip().strip("/")
        if not value:
            self._set_status("Indique un nouveau chemin.")
            return ""
        if ".." in value.split("/"):
            self._set_status("Chemin invalide.")
            return ""
        if "/" not in value and self.current_path:
            return posixpath.join(self.current_path, value)
        return value

    def _show_editor(self, path, content):
        self.path_field.text = path
        self.editor.text = content
        self.editor.hidden = False
        self.list_view.hidden = True
        self.layout()

    def _show_list(self):
        self.editor.hidden = True
        self.list_view.hidden = False
        self.layout()

    def _reload_table(self):
        self._show_list()
        self.list_view.reload()

    def tableview_number_of_rows(self, tableview, section):
        return len(self.current_items)

    def tableview_cell_for_row(self, tableview, section, row):
        item = self.current_items[row]
        cell = ui.TableViewCell()
        prefix = "📁 " if item.get("type") == "dir" else "📄 "
        cell.text_label.text = prefix + item.get("name", "")
        return cell

    def tableview_did_select(self, tableview, section, row):
        item = self.current_items[row]
        path = item.get("path", "")
        self.path_field.text = path
        if item.get("type") == "dir":
            self.current_path = path
            self.refresh()
        else:
            self._background(lambda: self._open_file_worker(path))

    def _background(self, function):
        threading.Thread(target=self._safe_call, args=(function,), daemon=True).start()

    def _safe_call(self, function):
        try:
            function()
        except (GitHubAPIError, ValueError, KeyError) as exc:
            self._set_status(str(exc))
        except Exception as exc:
            self._set_status("Erreur inattendue : {}".format(exc))

    def _set_status(self, text):
        self._main(lambda: setattr(self.status_label, "text", text))

    def _main(self, function):
        try:
            ui.run_on_main_thread(function)
        except AttributeError:
            function()
