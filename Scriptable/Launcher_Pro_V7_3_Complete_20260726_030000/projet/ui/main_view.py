from __future__ import annotations

from pathlib import Path
from typing import Optional

import pyto_ui as ui

from core.importer import add_project, import_script, list_python_files, pick_directory, pick_file
from core.registry import Registry
from core.url_scheme import build_open_url, build_run_url, copy_text, run_by_id
from . import theme


def _enum(container_name: str, member: str, legacy_name: str, fallback):
    container = getattr(ui, container_name, None)
    if container is not None and hasattr(container, member):
        return getattr(container, member)
    return getattr(ui, legacy_name, fallback)


ALIGN_CENTER = _enum("TextAlignment", "CENTER", "TEXT_ALIGNMENT_CENTER", 1)
SHEET = _enum("PresentationMode", "SHEET", "PRESENTATION_MODE_SHEET", None)


class LauncherProView:
    PAGE_SIZE = 4

    def __init__(self) -> None:
        self.registry = Registry.load()
        self.query = ""
        self.filter_kind: Optional[str] = None
        self.page = 0
        self.pending_run_id: Optional[str] = None
        self.current_item_id: Optional[str] = None

        self.view = ui.View()
        self.view.title = "Launcher Pro"
        self.view.background_color = theme.BACKGROUND
        self.view.layout = self.layout

        self.title = self._label("Launcher Pro", 24, True, theme.TEXT)
        self.subtitle = self._label("Scripts et projets Pyto", 12, False, theme.MUTED)
        self.url_button = self._button("URL", self.copy_launcher_url, theme.SURFACE_ALT, theme.PRIMARY)
        self.search = ui.TextField(placeholder="Rechercher")
        self.search.background_color = theme.SURFACE
        self.search.text_color = theme.TEXT
        self.search.corner_radius = 12
        self.search.did_change = self.on_search

        self.add_script = self._button("＋ Script", self.on_add_script, theme.PRIMARY, theme.TEXT)
        self.add_project = self._button("＋ Projet", self.on_add_project, theme.SURFACE_ALT, theme.PRIMARY)
        self.filter_all = self._button("Tous", self.on_filter_all, theme.SURFACE_ALT, theme.PRIMARY)
        self.filter_scripts = self._button("Scripts", self.on_filter_scripts, theme.SURFACE_ALT, theme.PRIMARY)
        self.filter_projects = self._button("Projets", self.on_filter_projects, theme.SURFACE_ALT, theme.PRIMARY)
        self.previous = self._button("‹", self.previous_page, theme.SURFACE_ALT, theme.PRIMARY)
        self.next = self._button("›", self.next_page, theme.SURFACE_ALT, theme.PRIMARY)
        self.page_label = self._label("1 / 1", 12, False, theme.MUTED)
        self.page_label.text_alignment = ALIGN_CENTER

        self.item_buttons = [self._button("", self.on_item_pressed, theme.CARD, theme.TEXT) for _ in range(self.PAGE_SIZE)]
        self.visible_ids: list[Optional[str]] = [None] * self.PAGE_SIZE

        for control in (
            self.title, self.subtitle, self.url_button, self.search, self.add_script,
            self.add_project, self.filter_all, self.filter_scripts, self.filter_projects,
            *self.item_buttons, self.previous, self.page_label, self.next,
        ):
            self.view.add_subview(control)

        self.refresh_library()

    @staticmethod
    def _label(text: str, size: float, bold: bool, color):
        label = ui.Label(text=text)
        label.text_color = color
        selected = theme.font(size, bold)
        if selected is not None:
            label.font = selected
        return label

    @staticmethod
    def _button(title: str, action, background, tint):
        button = ui.Button(title=title)
        button.action = action
        button.background_color = background
        button.tint_color = tint
        button.corner_radius = 12
        return button

    def layout(self) -> None:
        width, height = self.view.width, self.view.height
        margin = 18
        usable = width - margin * 2
        self.title.frame = (margin, 16, usable - 80, 32)
        self.subtitle.frame = (margin, 48, usable - 80, 22)
        self.url_button.frame = (width - margin - 62, 24, 62, 40)
        self.search.frame = (margin, 84, usable, 44)
        half = (usable - 10) / 2
        self.add_script.frame = (margin, 140, half, 44)
        self.add_project.frame = (margin + half + 10, 140, half, 44)
        segment = (usable - 12) / 3
        self.filter_all.frame = (margin, 196, segment, 38)
        self.filter_scripts.frame = (margin + segment + 6, 196, segment, 38)
        self.filter_projects.frame = (margin + (segment + 6) * 2, 196, segment, 38)

        y = 250
        button_height = 64
        gap = 10
        for button in self.item_buttons:
            button.frame = (margin, y, usable, button_height)
            y += button_height + gap
        self.previous.frame = (margin, y + 4, 52, 38)
        self.page_label.frame = (margin + 62, y + 4, usable - 124, 38)
        self.next.frame = (width - margin - 52, y + 4, 52, 38)

    def refresh_library(self) -> None:
        self.registry = Registry.load()
        items = self.registry.search(self.query, self.filter_kind)
        page_count = max(1, (len(items) + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
        self.page = max(0, min(self.page, page_count - 1))
        start = self.page * self.PAGE_SIZE
        page_items = items[start:start + self.PAGE_SIZE]
        self.page_label.text = f"{self.page + 1} / {page_count}"
        self.visible_ids = [None] * self.PAGE_SIZE

        for index, button in enumerate(self.item_buttons):
            if index < len(page_items):
                item = page_items[index]
                kind = "APP" if item.kind == "project" else "PY"
                star = "★ " if item.favorite else ""
                button.title = f"{star}{kind}  {item.name}"
                button.hidden = False
                self.visible_ids[index] = item.id
            else:
                button.title = ""
                button.hidden = True
        self._style_filters()

    def on_item_pressed(self, sender) -> None:
        try:
            index = self.item_buttons.index(sender)
        except ValueError:
            return
        item_id = self.visible_ids[index]
        if item_id:
            self.show_detail(item_id)

    def show_detail(self, item_id: str) -> None:
        registry = Registry.load()
        item = registry.require(item_id)
        self.current_item_id = item_id
        alert = ui.Alert(title=item.name, message="Modifier ou lancer cet élément")
        name_field = ui.TextField(text=item.name)
        category_field = ui.TextField(text=item.category)
        alert.add_text_field(name_field)
        alert.add_text_field(category_field)
        entry_field = None
        if item.kind == "project":
            entry_field = ui.TextField(text=item.entry_script)
            alert.add_text_field(entry_field)
        actions = ["Annuler", "Enregistrer", "Lancer", "Favori", "Copier URL", "Supprimer"]
        for action in actions:
            alert.add_action(action)
        choice = str(alert.show())

        def selected(title: str, index: int) -> bool:
            return choice == title or choice.endswith(title) or choice == str(index)

        if selected("Enregistrer", 1):
            new_name = (name_field.text or "").strip()
            if not new_name:
                self._alert("Nom invalide", "Le nom ne peut pas être vide.")
                return
            item.name = new_name
            item.category = (category_field.text or "Général").strip() or "Général"
            if entry_field is not None:
                candidate = (entry_field.text or "").strip()
                target = Path(item.project_root) / candidate
                if not target.exists() or target.suffix.lower() != ".py":
                    self._alert("Point d’entrée invalide", "Le fichier indiqué n’existe pas.")
                    return
                item.entry_script = candidate
            registry.update(item)
            self.refresh_library()
        elif selected("Lancer", 2):
            self.pending_run_id = item_id
            try:
                self.view.close()
            except Exception:
                pass
        elif selected("Favori", 3):
            item.favorite = not item.favorite
            registry.update(item)
            self.refresh_library()
        elif selected("Copier URL", 4):
            url = build_run_url(item_id)
            self._alert("URL", "URL copiée." if copy_text(url) else url)
        elif selected("Supprimer", 5):
            registry.remove(item_id)
            self.refresh_library()

    def on_search(self, sender) -> None:
        self.query = (sender.text or "").strip()
        self.page = 0
        self.refresh_library()

    def on_filter_all(self, sender) -> None:
        self.filter_kind = None
        self.page = 0
        self.refresh_library()

    def on_filter_scripts(self, sender) -> None:
        self.filter_kind = "script"
        self.page = 0
        self.refresh_library()

    def on_filter_projects(self, sender) -> None:
        self.filter_kind = "project"
        self.page = 0
        self.refresh_library()

    def _style_filters(self) -> None:
        for button, value in ((self.filter_all, None), (self.filter_scripts, "script"), (self.filter_projects, "project")):
            active = self.filter_kind == value
            button.background_color = theme.PRIMARY if active else theme.SURFACE_ALT
            button.tint_color = theme.TEXT if active else theme.PRIMARY

    def previous_page(self, sender) -> None:
        if self.page > 0:
            self.page -= 1
            self.refresh_library()

    def next_page(self, sender) -> None:
        self.page += 1
        self.refresh_library()

    def on_add_script(self, sender) -> None:
        try:
            path = pick_file()
            item = import_script(path, registry=Registry.load())
        except Exception as exc:
            self._alert("Script non ajouté", str(exc))
            return
        self.show_detail(item.id)

    def on_add_project(self, sender) -> None:
        try:
            root = pick_directory()
            files = list_python_files(root, recursive=True)
            if not files:
                raise ValueError("Aucun fichier .py trouvé dans ce dossier.")
            entry = self._default_entry(Path(root), files)
            item = add_project(root, entry, registry=Registry.load())
        except Exception as exc:
            self._alert("Projet non ajouté", str(exc))
            return
        self.show_detail(item.id)

    @staticmethod
    def _default_entry(root: Path, files) -> str:
        preferred = ("main.py", "bootstrap.py", "app.py", "run.py", "launcher.py")
        ordered = sorted(files, key=lambda p: (preferred.index(p.name.lower()) if p.name.lower() in preferred else 99, len(p.relative_to(root).parts), p.name.lower()))
        return str(ordered[0].relative_to(root))

    def copy_launcher_url(self, sender) -> None:
        url = build_open_url()
        self._alert("URL", "URL copiée." if copy_text(url) else url)

    @staticmethod
    def _alert(title: str, message: str) -> None:
        alert = ui.Alert(title=title, message=message)
        alert.add_action("OK")
        alert.show()

    def present(self):
        if SHEET is None:
            ui.show_view(self.view)
        else:
            ui.show_view(self.view, SHEET)
        return self.pending_run_id


def present_launcher() -> None:
    controller = LauncherProView()
    item_id = controller.present()
    if item_id:
        item, result = run_by_id(item_id)
        if result.output:
            print(result.output, end="")
        if not result.success:
            raise RuntimeError(result.error or f"Échec de {item.name}")
