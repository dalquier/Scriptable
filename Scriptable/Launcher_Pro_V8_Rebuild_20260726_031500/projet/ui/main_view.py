from __future__ import annotations

from pathlib import Path
from typing import Optional

import pyto_ui as ui

from core.importer import add_project, import_script, list_python_files, pick_directory, pick_file
from core.registry import Registry
from core.service import rename_item, run_by_id
from . import theme


def _enum(container_name: str, member: str, legacy_name: str, fallback):
    container = getattr(ui, container_name, None)
    if container is not None and hasattr(container, member):
        return getattr(container, member)
    return getattr(ui, legacy_name, fallback)


ALIGN_CENTER = _enum("TextAlignment", "CENTER", "TEXT_ALIGNMENT_CENTER", 1)
SHEET = _enum("PresentationMode", "SHEET", "PRESENTATION_MODE_SHEET", None)


class LauncherProView:
    def __init__(self) -> None:
        self.registry = Registry.load()
        self.query = ""
        self.filter_kind: Optional[str] = None
        self.pending_run_id: Optional[str] = None
        self.cards = []
        self.callbacks = []

        self.view = ui.View()
        self.view.title = "Launcher Pro"
        self.view.background_color = theme.BACKGROUND
        self.view.layout = self.layout

        self.title = self._label("Launcher Pro", 24, True, theme.TEXT)
        self.subtitle = self._label("Toucher pour lancer · appui long pour renommer", 12, False, theme.MUTED)
        self.search = ui.TextField(placeholder="Rechercher")
        self.search.background_color = theme.SURFACE
        self.search.text_color = theme.TEXT
        self.search.corner_radius = 12
        self.search.did_change = self.on_search

        self.add_script = self._button("＋ Script", self.on_add_script, theme.PRIMARY, theme.TEXT)
        self.add_project = self._button("＋ Projet", self.on_add_project, theme.SURFACE_ALT, theme.PRIMARY)
        self.filter_all = self._button("Tous", self.on_filter_all, theme.PRIMARY, theme.TEXT)
        self.filter_scripts = self._button("Scripts", self.on_filter_scripts, theme.SURFACE_ALT, theme.PRIMARY)
        self.filter_projects = self._button("Projets", self.on_filter_projects, theme.SURFACE_ALT, theme.PRIMARY)

        self.scroll = ui.ScrollView()
        self.scroll.background_color = theme.BACKGROUND
        self.scroll_host = getattr(self.scroll, "content_view", self.scroll)

        for control in (
            self.title, self.subtitle, self.search, self.add_script, self.add_project,
            self.filter_all, self.filter_scripts, self.filter_projects, self.scroll,
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
        self.title.frame = (margin, 14, usable, 32)
        self.subtitle.frame = (margin, 47, usable, 22)
        self.search.frame = (margin, 82, usable, 44)
        half = (usable - 10) / 2
        self.add_script.frame = (margin, 138, half, 44)
        self.add_project.frame = (margin + half + 10, 138, half, 44)
        segment = (usable - 12) / 3
        self.filter_all.frame = (margin, 194, segment, 38)
        self.filter_scripts.frame = (margin + segment + 6, 194, segment, 38)
        self.filter_projects.frame = (margin + (segment + 6) * 2, 194, segment, 38)
        scroll_y = 244
        self.scroll.frame = (0, scroll_y, width, max(1, height - scroll_y))
        self.layout_cards()

    def clear_cards(self) -> None:
        for card in self.cards:
            try:
                card["container"].remove_from_superview()
            except Exception:
                pass
        self.cards = []
        self.callbacks = []

    def refresh(self) -> None:
        self.registry = Registry.load()
        self.clear_cards()
        items = self.registry.search(self.query, self.filter_kind)
        for item in items:
            self._add_card(item)
        if not items:
            self._add_empty_card()
        self._style_filters()
        self.layout_cards()

    def _add_empty_card(self) -> None:
        container = ui.View()
        container.background_color = theme.CARD
        container.corner_radius = 16
        label = self._label("Aucun script ou projet", 16, True, theme.TEXT)
        detail = self._label("Ajoute un script autonome ou un projet Pyto.", 12, False, theme.MUTED)
        container.add_subview(label)
        container.add_subview(detail)
        self.scroll_host.add_subview(container)
        self.cards.append({"container": container, "label": label, "detail": detail, "button": None, "menu": None})

    def _add_card(self, item) -> None:
        container = ui.View()
        container.background_color = theme.CARD
        container.corner_radius = 16
        kind = "APP" if item.kind == "project" else "PY"
        badge = self._label(kind, 13, True, theme.PRIMARY)
        badge.background_color = theme.PRIMARY_SOFT
        badge.corner_radius = 10
        badge.text_alignment = ALIGN_CENTER
        title = self._label(item.name, 17, True, theme.TEXT)
        detail_text = item.entry_script if item.kind == "project" else item.category
        detail = self._label(("Projet · " if item.kind == "project" else "Script · ") + detail_text, 11, False, theme.MUTED)
        status = self._label(self._status_text(item), 11, False, theme.MUTED)
        run_callback = self._make_run_callback(item.id)
        menu_callback = self._make_menu_callback(item.id)
        self.callbacks.extend((run_callback, menu_callback))
        run_button = self._button("Lancer", run_callback, theme.PRIMARY, theme.TEXT)
        menu_button = self._button("•••", menu_callback, theme.SURFACE_ALT, theme.PRIMARY)
        for sub in (badge, title, detail, status, run_button, menu_button):
            container.add_subview(sub)
        self.scroll_host.add_subview(container)
        self.cards.append({
            "container": container, "badge": badge, "title": title, "detail": detail,
            "status": status, "button": run_button, "menu": menu_button,
        })

    def _make_run_callback(self, item_id: str):
        def callback(sender) -> None:
            self.pending_run_id = item_id
            try:
                self.view.close()
            except Exception:
                pass
        return callback

    def _make_menu_callback(self, item_id: str):
        def callback(sender) -> None:
            self.rename_dialog(item_id)
        return callback

    def rename_dialog(self, item_id: str) -> None:
        item = Registry.load().require(item_id)
        alert = ui.Alert(title="Renommer", message="Nouveau nom")
        field = ui.TextField(text=item.name)
        alert.add_text_field(field)
        alert.add_action("Annuler")
        alert.add_action("Enregistrer")
        choice = str(alert.show())
        if choice in {"1", "Enregistrer"} or choice.endswith("Enregistrer"):
            try:
                rename_item(item_id, field.text or "")
                self.refresh()
            except Exception as exc:
                self._alert("Renommage impossible", str(exc))

    @staticmethod
    def _status_text(item) -> str:
        if item.last_status == "success":
            duration = f" · {item.last_duration:.2f}s" if item.last_duration is not None else ""
            return f"Réussi{duration} · {item.run_count} lancement(s)"
        if item.last_status == "error":
            return f"Dernière exécution en erreur · {item.run_count} lancement(s)"
        return "Jamais lancé"

    def layout_cards(self) -> None:
        y = 8
        width = max(300, self.scroll.width - 28)
        for card in self.cards:
            container = card["container"]
            if card.get("button") is None:
                container.frame = (14, y, width, 92)
                card["label"].frame = (16, 16, width - 32, 28)
                card["detail"].frame = (16, 46, width - 32, 24)
                y += 104
                continue
            container.frame = (14, y, width, 98)
            card["badge"].frame = (12, 20, 48, 48)
            card["title"].frame = (72, 10, width - 220, 28)
            card["detail"].frame = (72, 38, width - 220, 20)
            card["status"].frame = (72, 60, width - 220, 20)
            card["menu"].frame = (width - 136, 27, 48, 44)
            card["button"].frame = (width - 82, 23, 68, 52)
            y += 110
        height = max(self.scroll.height + 1, y + 8)
        self.scroll.content_size = (self.scroll.width, height)
        try:
            self.scroll_host.frame = (0, 0, self.scroll.width, height)
        except Exception:
            pass

    def on_search(self, sender) -> None:
        self.query = (sender.text or "").strip()
        self.refresh()

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
        for button, value in ((self.filter_all, None), (self.filter_scripts, "script"), (self.filter_projects, "project")):
            active = self.filter_kind == value
            button.background_color = theme.PRIMARY if active else theme.SURFACE_ALT
            button.tint_color = theme.TEXT if active else theme.PRIMARY

    def on_add_script(self, sender) -> None:
        try:
            path = pick_file()
            import_script(path, registry=Registry.load())
            self.refresh()
        except Exception as exc:
            self._alert("Script non ajouté", str(exc))

    def on_add_project(self, sender) -> None:
        try:
            root = Path(pick_directory())
            files = list_python_files(root)
            if not files:
                raise ValueError("Aucun fichier .py trouvé dans ce dossier")
            entry = self.choose_entry(root, files)
            if entry is None:
                return
            add_project(root, entry, registry=Registry.load())
            self.refresh()
        except Exception as exc:
            self._alert("Projet non ajouté", str(exc))

    def choose_entry(self, root: Path, files: list[Path]) -> Optional[str]:
        alert = ui.Alert(title="Fichier de lancement", message="Choisis le module à exécuter")
        actions = ["Annuler"]
        shown = files[:20]
        alert.add_action("Annuler")
        for path in shown:
            relative = str(path.relative_to(root))
            actions.append(relative)
            alert.add_action(relative)
        choice = str(alert.show())
        if choice in {"0", "Annuler"} or choice.endswith("Annuler"):
            return None
        for index, title in enumerate(actions[1:], start=1):
            if choice == str(index) or choice == title or choice.endswith(title):
                return title
        return None

    @staticmethod
    def _alert(title: str, message: str) -> None:
        alert = ui.Alert(title=title, message=message)
        alert.add_action("OK")
        alert.show()

    def present(self) -> Optional[str]:
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
