from __future__ import annotations

from pathlib import Path
from typing import Optional

import pyto_ui as ui

from core.registry import Registry
from . import theme


def _enum(container_name: str, member: str, legacy_name: str, fallback):
    container = getattr(ui, container_name, None)
    if container is not None and hasattr(container, member):
        return getattr(container, member)
    return getattr(ui, legacy_name, fallback)


SHEET = _enum("PresentationMode", "SHEET", "PRESENTATION_MODE_SHEET", None)


class LauncherProView:
    """Une vue ne fait qu’afficher et renvoyer une action.

    Les sélecteurs de fichiers et l’exécution sont lancés seulement après la
    fermeture de cette vue, afin d’éviter les conflits de présentation iOS.
    """

    def __init__(self) -> None:
        self.registry = Registry.load()
        self.query = ""
        self.filter_kind: Optional[str] = None
        self.rename_mode = False
        self.action: tuple[str, Optional[str]] = ("quit", None)
        self.visible_items = []

        self.view = ui.View()
        self.view.title = "Launcher Pro"
        self.view.background_color = theme.BACKGROUND
        self.view.layout = self.layout

        self.title = self._label("Launcher Pro", 24, True, theme.TEXT)
        self.subtitle = self._label("Touchez une ligne pour lancer", 12, False, theme.MUTED)

        self.search = ui.TextField(placeholder="Rechercher")
        self.search.background_color = theme.SURFACE
        self.search.text_color = theme.TEXT
        self.search.corner_radius = 12
        self.search.did_change = self.on_search

        self.add_script = self._button("＋ Script", self.on_add_script, theme.PRIMARY, theme.TEXT)
        self.add_project = self._button("＋ Projet", self.on_add_project, theme.SURFACE_ALT, theme.PRIMARY)
        self.rename_button = self._button("Renommer", self.on_rename_mode, theme.SURFACE_ALT, theme.PRIMARY)

        self.filter_all = self._button("Tous", self.on_filter_all, theme.PRIMARY, theme.TEXT)
        self.filter_scripts = self._button("Scripts", self.on_filter_scripts, theme.SURFACE_ALT, theme.PRIMARY)
        self.filter_projects = self._button("Projets", self.on_filter_projects, theme.SURFACE_ALT, theme.PRIMARY)

        self.table = ui.TableView()
        self.table.background_color = theme.BACKGROUND

        for control in (
            self.title,
            self.subtitle,
            self.search,
            self.add_script,
            self.add_project,
            self.rename_button,
            self.filter_all,
            self.filter_scripts,
            self.filter_projects,
            self.table,
        ):
            self.view.add_subview(control)

        self.refresh()

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
        margin = 16
        usable = width - margin * 2

        self.title.frame = (margin, 12, usable, 32)
        self.subtitle.frame = (margin, 44, usable, 22)
        self.search.frame = (margin, 76, usable, 42)

        third = (usable - 16) / 3
        self.add_script.frame = (margin, 130, third, 42)
        self.add_project.frame = (margin + third + 8, 130, third, 42)
        self.rename_button.frame = (margin + (third + 8) * 2, 130, third, 42)

        segment = (usable - 12) / 3
        self.filter_all.frame = (margin, 182, segment, 36)
        self.filter_scripts.frame = (margin + segment + 6, 182, segment, 36)
        self.filter_projects.frame = (margin + (segment + 6) * 2, 182, segment, 36)

        table_y = 230
        self.table.frame = (0, table_y, width, max(1, height - table_y))

    def refresh(self) -> None:
        self.registry = Registry.load()
        self.visible_items = self.registry.search(self.query, self.filter_kind)
        cells = []

        if not self.visible_items:
            cell = ui.TableViewCell()
            cell.text_label.text = "Aucun script ou projet"
            cells.append(cell)
        else:
            for item in self.visible_items:
                cell = ui.TableViewCell()
                prefix = "APP" if item.kind == "project" else "PY"
                star = "★ " if item.favorite else ""
                cell.text_label.text = f"{star}{prefix}  {item.name}"
                try:
                    detail = item.entry_script if item.kind == "project" else item.category
                    cell.detail_text_label.text = detail
                except Exception:
                    pass
                cells.append(cell)

        section = ui.TableViewSection("Bibliothèque", cells)
        section.did_select_cell = self.on_select_cell
        self.table.sections = [section]
        try:
            self.table.reload()
        except Exception:
            pass
        self._style_filters()

    def on_select_cell(self, section, index) -> None:
        if not self.visible_items or index < 0 or index >= len(self.visible_items):
            return
        item_id = self.visible_items[index].id
        self.action = ("rename" if self.rename_mode else "run", item_id)
        self.view.close()

    def on_search(self, sender) -> None:
        self.query = (sender.text or "").strip()
        self.refresh()

    def on_add_script(self, sender) -> None:
        self.action = ("add_script", None)
        self.view.close()

    def on_add_project(self, sender) -> None:
        self.action = ("add_project", None)
        self.view.close()

    def on_rename_mode(self, sender) -> None:
        self.rename_mode = not self.rename_mode
        sender.title = "Annuler" if self.rename_mode else "Renommer"
        sender.background_color = theme.PRIMARY if self.rename_mode else theme.SURFACE_ALT
        sender.tint_color = theme.TEXT if self.rename_mode else theme.PRIMARY
        self.subtitle.text = (
            "Touchez la ligne à renommer"
            if self.rename_mode
            else "Touchez une ligne pour lancer"
        )

    def on_filter_all(self, sender) -> None:
        self.filter_kind = None
        self.refresh()

    def on_filter_scripts(self, sender) -> None:
        self.filter_kind = "script"
        self.refresh()

    def on_filter_projects(self, sender) -> None:
        self.filter_kind = "project"
        self.refresh()

    def _style_filters(self) -> None:
        for button, value in (
            (self.filter_all, None),
            (self.filter_scripts, "script"),
            (self.filter_projects, "project"),
        ):
            active = self.filter_kind == value
            button.background_color = theme.PRIMARY if active else theme.SURFACE_ALT
            button.tint_color = theme.TEXT if active else theme.PRIMARY

    def present(self) -> tuple[str, Optional[str]]:
        if SHEET is None:
            ui.show_view(self.view)
        else:
            ui.show_view(self.view, SHEET)
        return self.action


def present_launcher_once() -> tuple[str, Optional[str]]:
    return LauncherProView().present()


def choose_entry_script(root: Path, files: list[Path]) -> Optional[str]:
    """Affiche une liste native scrollable des fichiers .py du projet."""
    state = {"entry": None}
    view = ui.View()
    view.title = "Fichier de lancement"
    view.background_color = theme.BACKGROUND
    table = ui.TableView()
    table.background_color = theme.BACKGROUND

    ordered = sorted(
        files,
        key=lambda p: (
            0 if p.name.lower() in {"main.py", "app.py", "bootstrap.py", "run.py", "launcher.py"} else 1,
            len(p.relative_to(root).parts),
            str(p.relative_to(root)).lower(),
        ),
    )
    cells = []
    for path in ordered:
        cell = ui.TableViewCell()
        cell.text_label.text = str(path.relative_to(root))
        cells.append(cell)

    def selected(section, index) -> None:
        if 0 <= index < len(ordered):
            state["entry"] = str(ordered[index].relative_to(root))
            view.close()

    section = ui.TableViewSection("Choisissez le module à exécuter", cells)
    section.did_select_cell = selected
    table.sections = [section]

    def layout() -> None:
        table.frame = (0, 0, view.width, view.height)

    view.layout = layout
    view.add_subview(table)
    if SHEET is None:
        ui.show_view(view)
    else:
        ui.show_view(view, SHEET)
    return state["entry"]


def prompt_rename(current_name: str) -> Optional[str]:
    alert = ui.Alert(title="Renommer", message="Saisissez le nouveau nom")
    field = ui.TextField(text=current_name)
    alert.add_text_field(field)
    alert.add_action("Annuler")
    alert.add_action("Enregistrer")
    raw = alert.show()
    text = str(raw).strip()
    accepted = raw == 1 or text == "1" or text == "Enregistrer" or text.endswith("Enregistrer")
    if not accepted:
        return None
    value = (field.text or "").strip()
    if not value:
        raise ValueError("Le nom ne peut pas être vide")
    return value


def show_message(title: str, message: str) -> None:
    alert = ui.Alert(title=title, message=message)
    alert.add_action("OK")
    alert.show()
