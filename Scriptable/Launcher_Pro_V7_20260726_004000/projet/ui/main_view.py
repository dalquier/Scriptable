from __future__ import annotations

import threading
from pathlib import Path
from typing import Dict, List, Optional

import pyto_ui as ui

from core.history import append_history
from core.importer import add_project, import_script, list_python_files, pick_directory, pick_file
from core.registry import Registry
from core.runner import run_item
from core.url_scheme import build_open_url, build_run_url, copy_text
from . import theme


def _enum(container_name: str, member: str, legacy_name: str, fallback):
    container = getattr(ui, container_name, None)
    if container is not None and hasattr(container, member):
        return getattr(container, member)
    return getattr(ui, legacy_name, fallback)


ALIGN_CENTER = _enum("TextAlignment", "CENTER", "TEXT_ALIGNMENT_CENTER", 1)
ALIGN_RIGHT = _enum("TextAlignment", "RIGHT", "TEXT_ALIGNMENT_RIGHT", 2)
SHEET = _enum("PresentationMode", "SHEET", "PRESENTATION_MODE_SHEET", None)


def _choice_index(value, titles: List[str]) -> int:
    """Normalise le résultat de ``Alert.show()`` selon la version de Pyto."""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    text = str(value).strip()
    for index, title in enumerate(titles):
        if text == title or text.endswith(title):
            return index
    try:
        return int(text)
    except (TypeError, ValueError):
        return -1


class LauncherProView:
    def __init__(self) -> None:
        self.registry = Registry.load()
        self.cards: List[Dict[str, object]] = []
        self.query = ""
        self.filter_kind: Optional[str] = None
        self.busy = False
        self._card_callbacks = []

        self.view = ui.View()
        self.view.title = "Launcher Pro"
        self.view.background_color = theme.BACKGROUND
        self.view.layout = self.layout

        self.topbar = ui.View()
        self.topbar.background_color = theme.SURFACE
        self.topbar.corner_radius = 20
        self.logo = self._label("▶", 18, True, theme.TEXT)
        self.logo.background_color = theme.PRIMARY
        self.logo.corner_radius = 11
        self.logo.text_alignment = ALIGN_CENTER
        self.title = self._label("Launcher Pro", 22, True, theme.TEXT)
        self.subtitle = self._label("Scripts et projets Pyto", 12, False, theme.MUTED)
        self.link_button = self._button("URL", self.copy_launcher_url, theme.SURFACE_ALT, theme.PRIMARY)
        for sub in (self.logo, self.title, self.subtitle, self.link_button):
            self.topbar.add_subview(sub)

        self.metrics = ui.View()
        self.metrics.background_color = theme.PRIMARY_SOFT
        self.metrics.corner_radius = 14
        self.metric_items = self._label("0 élément", 12, True, theme.TEXT)
        self.metric_favorites = self._label("0 favori", 11, False, theme.MUTED)
        self.metric_runs = self._label("0 lancement", 11, False, theme.MUTED)
        for sub in (self.metric_items, self.metric_favorites, self.metric_runs):
            self.metrics.add_subview(sub)

        self.search = ui.TextField(placeholder="Rechercher")
        self.search.background_color = theme.SURFACE
        self.search.text_color = theme.TEXT
        self.search.corner_radius = 13
        self.search.did_change = self.on_search

        self.add_script_button = self._button("＋ Script", self.on_add_script, theme.PRIMARY, theme.TEXT)
        self.add_project_button = self._button("＋ Projet", self.on_add_project, theme.SURFACE_ALT, theme.PRIMARY)

        self.filter_bar = ui.View()
        self.filter_bar.background_color = theme.SURFACE
        self.filter_bar.corner_radius = 13
        self.filter_all = self._button("Tous", lambda sender: self.set_filter(None), theme.SURFACE, theme.MUTED)
        self.filter_scripts = self._button("Scripts", lambda sender: self.set_filter("script"), theme.SURFACE, theme.MUTED)
        self.filter_projects = self._button("Projets", lambda sender: self.set_filter("project"), theme.SURFACE, theme.MUTED)
        for button in (self.filter_all, self.filter_scripts, self.filter_projects):
            button.corner_radius = 10
            self.filter_bar.add_subview(button)

        self.section_title = self._label("Bibliothèque", 18, True, theme.TEXT)
        self.status = self._label("Prêt", 11, False, theme.MUTED)
        self.status.text_alignment = ALIGN_RIGHT

        self.scroll = ui.ScrollView()
        self.scroll.background_color = theme.BACKGROUND
        self.scroll_host = getattr(self.scroll, "content_view", self.scroll)

        for control in (
            self.topbar, self.metrics, self.search, self.add_script_button,
            self.add_project_button, self.filter_bar, self.section_title,
            self.status, self.scroll,
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
        button.corner_radius = 13
        return button

    def layout(self) -> None:
        width, height = self.view.width, self.view.height
        margin = 14
        usable = max(300, width - margin * 2)
        self.topbar.frame = (margin, 12, usable, 72)
        self.logo.frame = (12, 13, 46, 46)
        self.title.frame = (70, 10, usable - 142, 29)
        self.subtitle.frame = (70, 38, usable - 142, 21)
        self.link_button.frame = (usable - 66, 17, 54, 38)

        self.metrics.frame = (margin, 94, usable, 42)
        self.metric_items.frame = (12, 6, usable * 0.37, 30)
        self.metric_favorites.frame = (usable * 0.40, 6, usable * 0.27, 30)
        self.metric_runs.frame = (usable * 0.68, 6, usable * 0.29, 30)

        self.search.frame = (margin, 146, usable, 42)
        half = (usable - 8) / 2
        self.add_script_button.frame = (margin, 198, half, 42)
        self.add_project_button.frame = (margin + half + 8, 198, half, 42)

        self.filter_bar.frame = (margin, 250, usable, 39)
        segment = (usable - 8) / 3
        self.filter_all.frame = (4, 4, segment - 4, 31)
        self.filter_scripts.frame = (segment + 2, 4, segment - 4, 31)
        self.filter_projects.frame = (segment * 2, 4, segment - 4, 31)

        self.section_title.frame = (margin, 298, usable * 0.55, 26)
        self.status.frame = (margin + usable * 0.42, 300, usable * 0.58, 22)
        scroll_y = 329
        self.scroll.frame = (0, scroll_y, width, max(1, height - scroll_y))
        self.layout_cards()

    def layout_cards(self) -> None:
        y = 6
        width = max(300, self.scroll.width - 28)
        for card in self.cards:
            card["container"].frame = (14, y, width, 92)
            card["badge"].frame = (12, 16, 48, 48)
            card["name"].frame = (72, 10, width - 240, 26)
            card["detail"].frame = (72, 36, width - 240, 19)
            card["meta"].frame = (72, 57, width - 240, 19)
            card["edit"].frame = (width - 160, 25, 72, 40)
            card["run"].frame = (width - 82, 21, 68, 48)
            y += 101
        height = max(self.scroll.height + 1, y + 8)
        self.scroll.content_size = (self.scroll.width, height)
        try:
            self.scroll_host.frame = (0, 0, self.scroll.width, height)
        except Exception:
            pass

    def clear_cards(self) -> None:
        for card in self.cards:
            try:
                card["container"].remove_from_superview()
            except Exception:
                pass
        self.cards = []
        self._card_callbacks = []

    def refresh(self) -> None:
        self.registry = Registry.load()
        self.clear_cards()
        items = self.registry.search(self.query, self.filter_kind)
        favorites = sum(1 for item in self.registry.items if item.favorite)
        runs = sum(item.run_count for item in self.registry.items)
        total = len(self.registry.items)
        self.metric_items.text = f"{total} élément{'s' if total != 1 else ''}"
        self.metric_favorites.text = f"{favorites} favori{'s' if favorites != 1 else ''}"
        self.metric_runs.text = f"{runs} lancement{'s' if runs != 1 else ''}"
        self._style_filters()
        if not items:
            self._empty_state()
        else:
            for item in items:
                self._add_card(item)
        self.layout_cards()

    def _style_filters(self) -> None:
        for button, value in ((self.filter_all, None), (self.filter_scripts, "script"), (self.filter_projects, "project")):
            active = value == self.filter_kind
            button.background_color = theme.PRIMARY if active else theme.SURFACE
            button.tint_color = theme.TEXT if active else theme.MUTED

    def _empty_state(self) -> None:
        container = ui.View()
        container.background_color = theme.CARD
        container.corner_radius = 18
        badge = self._label("＋", 24, True, theme.PRIMARY)
        badge.text_alignment = ALIGN_CENTER
        name = self._label("Aucun élément", 17, True, theme.TEXT)
        detail = self._label("Ajoute un script autonome ou un projet Pyto.", 12, False, theme.MUTED)
        meta = self._label("", 11, False, theme.MUTED)
        edit, run = ui.Button(title=""), ui.Button(title="")
        for sub in (badge, name, detail, meta, edit, run):
            container.add_subview(sub)
        self.scroll_host.add_subview(container)
        self.cards.append({"container": container, "badge": badge, "name": name, "detail": detail, "meta": meta, "edit": edit, "run": run})

    def _add_card(self, item) -> None:
        container = ui.View()
        container.background_color = theme.CARD
        container.corner_radius = 18
        badge = self._label("APP" if item.kind == "project" else "PY", 14, True, theme.PRIMARY)
        badge.background_color = theme.PRIMARY_SOFT
        badge.corner_radius = 12
        badge.text_alignment = ALIGN_CENTER
        name = self._label(item.name, 17, True, theme.TEXT)
        detail_text = item.entry_script if item.kind == "project" else item.category
        detail = self._label(("Projet · " if item.kind == "project" else "Script · ") + detail_text, 11, False, theme.MUTED)
        meta = self._label(self._status_text(item), 11, False, theme.MUTED)
        edit_callback = self._make_edit_callback(item.id)
        run_callback = self._make_run_callback(item.id)
        self._card_callbacks.extend((edit_callback, run_callback))
        edit = self._button("Modifier", edit_callback, theme.SURFACE_ALT, theme.PRIMARY)
        run = self._button("Lancer", run_callback, theme.PRIMARY, theme.TEXT)
        for sub in (badge, name, detail, meta, edit, run):
            container.add_subview(sub)
        self.scroll_host.add_subview(container)
        self.cards.append({"container": container, "badge": badge, "name": name, "detail": detail, "meta": meta, "edit": edit, "run": run})

    def _make_edit_callback(self, item_id: str):
        def callback(sender) -> None:
            self.status.text = "Ouverture des réglages…"
            self.edit_item(item_id)
        return callback

    def _make_run_callback(self, item_id: str):
        def callback(sender) -> None:
            self.launch(item_id)
        return callback

    @staticmethod
    def _status_text(item) -> str:
        star = "★ " if item.favorite else ""
        if item.last_status == "success":
            duration = f" · {item.last_duration:.2f}s" if item.last_duration is not None else ""
            return f"{star}Réussi{duration} · {item.run_count}×"
        if item.last_status == "error":
            return f"{star}Dernière exécution en erreur · {item.run_count}×"
        return f"{star}Jamais lancé"

    def on_search(self, sender) -> None:
        self.query = (sender.text or "").strip()
        self.refresh()

    def set_filter(self, kind: Optional[str]) -> None:
        self.filter_kind = kind
        self.refresh()

    def on_add_script(self, sender) -> None:
        if self.busy:
            return
        self.busy = True
        self.status.text = "Ouverture de Fichiers…"
        try:
            selected = pick_file()
        except Exception as exc:
            self.busy = False
            self.status.text = "Sélection impossible"
            self._alert("Script non ajouté", str(exc))
            return
        self.status.text = "Copie du script…"

        def worker() -> None:
            try:
                item, error = import_script(selected, registry=Registry.load()), None
            except Exception as exc:
                item, error = None, str(exc)
            self._on_main_thread(lambda: self._finish_import(item, error))
        threading.Thread(target=worker, daemon=True).start()

    def on_add_project(self, sender) -> None:
        if self.busy:
            return
        self.busy = True
        self.status.text = "Ouverture de Fichiers…"
        try:
            root = pick_directory()
            files = list_python_files(root, recursive=True)
            selected = self._choose_entry_script(root, files)
            if selected is None:
                self.busy = False
                self.status.text = "Ajout annulé"
                return
        except Exception as exc:
            self.busy = False
            self.status.text = "Sélection impossible"
            self._alert("Projet non ajouté", str(exc))
            return
        self.status.text = "Copie du projet…"

        def worker() -> None:
            try:
                item, error = add_project(root, selected, registry=Registry.load()), None
            except Exception as exc:
                item, error = None, str(exc)
            self._on_main_thread(lambda: self._finish_import(item, error))
        threading.Thread(target=worker, daemon=True).start()

    def _finish_import(self, item, error: Optional[str]) -> None:
        self.busy = False
        if error:
            self.status.text = "Ajout impossible"
            self._alert("Élément non ajouté", error)
            return
        self.status.text = f"{item.name} ajouté"
        self.refresh()
        self.edit_item(item.id)

    def _choose_entry_script(self, root: str, files: List[Path]) -> Optional[str]:
        if not files:
            self._alert("Projet invalide", "Aucun fichier .py trouvé.")
            return None
        root_path = Path(root)
        preferred = ["main.py", "bootstrap.py", "app.py", "run.py", "launcher.py"]
        ordered = sorted(files, key=lambda p: (preferred.index(p.name.lower()) if p.name.lower() in preferred else 99, len(p.relative_to(root_path).parts), p.name.lower()))
        shown = ordered[:18]
        titles = ["Annuler"] + [str(path.relative_to(root_path)) for path in shown]
        alert = ui.Alert(title="Point d’entrée", message="Choisis le script à lancer")
        for title in titles:
            alert.add_action(title)
        choice = _choice_index(alert.show(), titles)
        if choice <= 0 or choice >= len(titles):
            return None
        return titles[choice]

    def edit_item(self, item_id: str) -> None:
        registry = Registry.load()
        item = registry.require(item_id)
        alert = ui.Alert(title="Modifier", message="Nom, catégorie et configuration")
        name_field = ui.TextField(text=item.name)
        category_field = ui.TextField(text=item.category)
        alert.add_text_field(name_field)
        alert.add_text_field(category_field)
        entry_field = None
        if item.kind == "project":
            entry_field = ui.TextField(text=item.entry_script)
            alert.add_text_field(entry_field)
        favorite_title = "Favori" if not item.favorite else "Retirer favori"
        titles = ["Annuler", "Enregistrer", "Copier URL", favorite_title, "Supprimer"]
        for title in titles[:-1]:
            alert.add_action(title)
        try:
            alert.add_destructive_action("Supprimer")
        except Exception:
            alert.add_action("Supprimer")
        choice = _choice_index(alert.show(), titles)
        if choice == 1:
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
            self.status.text = "Modifications enregistrées"
            self.refresh()
        elif choice == 2:
            url = build_run_url(item.id)
            self._alert("URL de lancement", "URL copiée dans le presse-papiers." if copy_text(url) else url)
        elif choice == 3:
            item.favorite = not item.favorite
            registry.update(item)
            self.refresh()
        elif choice == 4:
            registry.remove(item_id)
            self.status.text = f"{item.name} supprimé"
            self.refresh()

    def copy_launcher_url(self, sender) -> None:
        url = build_open_url()
        self._alert("URL Launcher Pro", "URL copiée dans le presse-papiers." if copy_text(url) else url)

    def launch(self, item_id: str) -> None:
        """Ferme Launcher Pro puis exécute l’élément sur le thread principal.

        L’exécution directe est nécessaire pour les projets qui présentent une
        interface ``pyto_ui``. Une URL Pyto ouverte depuis Pyto peut être ignorée
        par iOS, et un thread secondaire ne peut pas présenter une UI fiable.
        """
        if self.busy:
            return
        self.busy = True
        registry = Registry.load()
        try:
            item = registry.require(item_id)
        except Exception as exc:
            self.busy = False
            self._alert("Lancement impossible", str(exc))
            return

        self.status.text = f"Lancement de {item.name}…"
        try:
            self.view.close()
        except Exception:
            pass

        try:
            result = run_item(item)
            append_history(item, result)
            registry.update(item)
        except BaseException as exc:
            self.busy = False
            self._alert("Lancement impossible", str(exc))
            return

        self.busy = False
        if not result.success:
            self._alert("Erreur d’exécution", (result.error or "Erreur inconnue")[-2200:])
        elif result.output.strip():
            print(result.output, end="")

    @staticmethod
    def _on_main_thread(callback) -> None:
        runner = getattr(ui, "run_on_main_thread", None)
        runner(callback) if callable(runner) else callback()

    @staticmethod
    def _alert(title: str, message: str) -> None:
        alert = ui.Alert(title=title, message=message)
        alert.add_action("OK")
        alert.show()

    def present(self) -> None:
        ui.show_view(self.view, SHEET) if SHEET is not None else ui.show_view(self.view)


def present_launcher() -> None:
    LauncherProView().present()
