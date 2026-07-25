from __future__ import annotations

import threading
from pathlib import Path
from typing import Dict, List, Optional

import pyto_ui as ui

from core.history import append_history
from core.importer import add_project, import_script, list_python_files, pick_directory, pick_file
from core.registry import Registry
from core.runner import run_item
from . import theme


class LauncherProView:
    def __init__(self) -> None:
        self.registry = Registry.load()
        self.cards: List[Dict[str, object]] = []
        self.query = ""
        self.filter_kind: Optional[str] = None
        self.busy = False

        self.view = ui.View()
        self.view.title = "Launcher Pro V7"
        self.view.background_color = theme.BACKGROUND
        self.view.layout = self.layout

        self.header = ui.View()
        self.header.background_color = theme.SURFACE
        self.header.corner_radius = 24
        self.app_icon = self._label("▶", 24, True, theme.TEXT)
        self.app_icon.background_color = theme.PRIMARY
        self.app_icon.corner_radius = 14
        self.app_icon.text_alignment = ui.TEXT_ALIGNMENT_CENTER
        self.title = self._label("Launcher Pro", 28, True, theme.TEXT)
        self.subtitle = self._label("Scripts autonomes et projets Pyto", 14, False, theme.MUTED)
        self.close_button = ui.Button(title="Fermer")
        self.close_button.background_color = theme.SURFACE_ALT
        self.close_button.tint_color = theme.DANGER
        self.close_button.corner_radius = 13
        self.close_button.action = self.on_close
        for sub in (self.app_icon, self.title, self.subtitle, self.close_button):
            self.header.add_subview(sub)

        self.summary = ui.View()
        self.summary.background_color = theme.PRIMARY_SOFT
        self.summary.corner_radius = 22
        self.summary_title = self._label("Ta bibliothèque d’automatisations", 21, True, theme.TEXT)
        self.summary_text = self._label("Lance un fichier unique ou un projet complet avec ses modules.", 13, False, theme.MUTED)
        self.stat_scripts = self._stat("0", "Scripts")
        self.stat_projects = self._stat("0", "Projets")
        self.stat_runs = self._stat("0", "Lancements")
        for sub in (
            self.summary_title,
            self.summary_text,
            self.stat_scripts["container"],
            self.stat_projects["container"],
            self.stat_runs["container"],
        ):
            self.summary.add_subview(sub)

        self.search = ui.TextField(placeholder="Rechercher")
        self.search.background_color = theme.SURFACE
        self.search.text_color = theme.TEXT
        self.search.corner_radius = 14
        self.search.did_change = self.on_search

        self.add_script_button = ui.Button(title="＋ Script")
        self.add_script_button.background_color = theme.PRIMARY
        self.add_script_button.tint_color = theme.TEXT
        self.add_script_button.corner_radius = 14
        self.add_script_button.action = self.on_add_script

        self.add_project_button = ui.Button(title="＋ Projet")
        self.add_project_button.background_color = theme.SURFACE_ALT
        self.add_project_button.tint_color = theme.PRIMARY
        self.add_project_button.corner_radius = 14
        self.add_project_button.action = self.on_add_project

        self.filter_all = ui.Button(title="Tous")
        self.filter_scripts = ui.Button(title="Scripts")
        self.filter_projects = ui.Button(title="Projets")
        for button in (self.filter_all, self.filter_scripts, self.filter_projects):
            button.background_color = theme.SURFACE
            button.tint_color = theme.MUTED
            button.corner_radius = 12
        self.filter_all.action = lambda sender: self.set_filter(None)
        self.filter_scripts.action = lambda sender: self.set_filter("script")
        self.filter_projects.action = lambda sender: self.set_filter("project")

        self.section_title = self._label("Bibliothèque", 20, True, theme.TEXT)
        self.status = self._label("Prêt", 12, False, theme.MUTED)
        self.status.text_alignment = ui.TEXT_ALIGNMENT_RIGHT
        self.scroll = ui.ScrollView()
        self.scroll.background_color = theme.BACKGROUND

        for control in (
            self.header,
            self.summary,
            self.search,
            self.add_script_button,
            self.add_project_button,
            self.filter_all,
            self.filter_scripts,
            self.filter_projects,
            self.section_title,
            self.status,
            self.scroll,
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

    def _stat(self, value: str, caption: str):
        container = ui.View()
        value_label = self._label(value, 22, True, theme.TEXT)
        caption_label = self._label(caption, 11, False, theme.MUTED)
        value_label.text_alignment = ui.TEXT_ALIGNMENT_CENTER
        caption_label.text_alignment = ui.TEXT_ALIGNMENT_CENTER
        container.add_subview(value_label)
        container.add_subview(caption_label)
        return {"container": container, "value": value_label, "caption": caption_label}

    def layout(self) -> None:
        width, height = self.view.width, self.view.height
        margin = 16
        usable = max(300, width - margin * 2)
        self.header.frame = (margin, 14, usable, 102)
        self.app_icon.frame = (16, 22, 54, 54)
        self.title.frame = (84, 16, usable - 184, 34)
        self.subtitle.frame = (84, 49, usable - 184, 36)
        self.close_button.frame = (usable - 92, 29, 78, 42)
        self.summary.frame = (margin, 128, usable, 150)
        self.summary_title.frame = (18, 16, usable - 36, 30)
        self.summary_text.frame = (18, 46, usable - 36, 36)
        third = usable / 3
        for index, stat in enumerate((self.stat_scripts, self.stat_projects, self.stat_runs)):
            stat["container"].frame = (third * index, 86, third, 58)
            stat["value"].frame = (0, 0, third, 30)
            stat["caption"].frame = (0, 29, third, 22)
        self.search.frame = (margin, 292, usable, 46)
        self.add_script_button.frame = (margin, 350, (usable - 12) / 2, 48)
        self.add_project_button.frame = (margin + (usable - 12) / 2 + 12, 350, (usable - 12) / 2, 48)
        filter_width = (usable - 16) / 3
        self.filter_all.frame = (margin, 410, filter_width, 38)
        self.filter_scripts.frame = (margin + filter_width + 8, 410, filter_width, 38)
        self.filter_projects.frame = (margin + (filter_width + 8) * 2, 410, filter_width, 38)
        self.section_title.frame = (margin, 462, usable * 0.6, 28)
        self.status.frame = (margin + usable * 0.4, 464, usable * 0.6, 24)
        scroll_y = 500
        self.scroll.frame = (0, scroll_y, width, max(1, height - scroll_y))
        self.layout_cards()

    def layout_cards(self) -> None:
        y = 8
        width = max(300, self.scroll.width - 32)
        for card in self.cards:
            card["container"].frame = (16, y, width, 126)
            card["badge"].frame = (15, 17, 56, 56)
            card["name"].frame = (84, 13, width - 234, 28)
            card["kind"].frame = (84, 42, width - 234, 22)
            card["meta"].frame = (16, 92, width - 192, 22)
            card["edit"].frame = (width - 174, 29, 44, 48)
            card["favorite"].frame = (width - 126, 29, 40, 48)
            card["run"].frame = (width - 74, 24, 60, 58)
            y += 138
        self.scroll.content_size = (self.scroll.width, max(self.scroll.height + 1, y + 10))

    def clear_cards(self) -> None:
        for card in self.cards:
            try:
                card["container"].remove_from_superview()
            except Exception:
                pass
        self.cards = []

    def refresh(self) -> None:
        self.registry = Registry.load()
        self.clear_cards()
        scripts = sum(1 for item in self.registry.items if item.kind == "script")
        projects = sum(1 for item in self.registry.items if item.kind == "project")
        runs = sum(item.run_count for item in self.registry.items)
        self.stat_scripts["value"].text = str(scripts)
        self.stat_projects["value"].text = str(projects)
        self.stat_runs["value"].text = str(runs)
        self._style_filters()
        items = self.registry.search(self.query, self.filter_kind)
        if not items:
            self._empty_state()
        else:
            for item in items:
                self._add_card(item)
        self.layout_cards()

    def _style_filters(self) -> None:
        for button, value in (
            (self.filter_all, None),
            (self.filter_scripts, "script"),
            (self.filter_projects, "project"),
        ):
            active = value == self.filter_kind
            button.background_color = theme.PRIMARY if active else theme.SURFACE
            button.tint_color = theme.TEXT if active else theme.MUTED

    def _empty_state(self) -> None:
        container = ui.View()
        container.background_color = theme.CARD
        container.corner_radius = 20
        badge = self._label("＋", 28, True, theme.PRIMARY)
        badge.text_alignment = ui.TEXT_ALIGNMENT_CENTER
        name = self._label("Aucun élément", 19, True, theme.TEXT)
        kind = self._label("Ajoute un script autonome ou un projet Pyto.", 13, False, theme.MUTED)
        meta = self._label("", 12, False, theme.MUTED)
        edit, favorite, run = ui.Button(title=""), ui.Button(title=""), ui.Button(title="")
        for sub in (badge, name, kind, meta, edit, favorite, run):
            container.add_subview(sub)
        self.scroll.add_subview(container)
        self.cards.append({"container": container, "badge": badge, "name": name, "kind": kind, "meta": meta, "edit": edit, "favorite": favorite, "run": run})

    def _add_card(self, item) -> None:
        container = ui.View()
        container.background_color = theme.CARD
        container.corner_radius = 20
        badge = self._label("APP" if item.kind == "project" else "PY", 16, True, theme.PRIMARY)
        badge.background_color = theme.PRIMARY_SOFT
        badge.corner_radius = 13
        badge.text_alignment = ui.TEXT_ALIGNMENT_CENTER
        name = self._label(item.name, 18, True, theme.TEXT)
        kind_text = f"Projet · {item.entry_script}" if item.kind == "project" else f"Script autonome · {item.category}"
        kind = self._label(kind_text, 12, False, theme.MUTED)
        meta = self._label(self._status_text(item), 12, False, theme.MUTED)
        edit = ui.Button(title="•••")
        edit.tint_color = theme.MUTED
        edit.action = lambda sender, item_id=item.id: self.edit_item(item_id)
        favorite = ui.Button(title="★" if item.favorite else "☆")
        favorite.tint_color = theme.SUCCESS if item.favorite else theme.MUTED
        favorite.action = lambda sender, item_id=item.id: self.toggle_favorite(item_id)
        run = ui.Button(title="▶")
        run.background_color = theme.PRIMARY
        run.tint_color = theme.TEXT
        run.corner_radius = 16
        run.action = lambda sender, item_id=item.id: self.launch(item_id)
        for sub in (badge, name, kind, meta, edit, favorite, run):
            container.add_subview(sub)
        self.scroll.add_subview(container)
        self.cards.append({"container": container, "badge": badge, "name": name, "kind": kind, "meta": meta, "edit": edit, "favorite": favorite, "run": run})

    @staticmethod
    def _status_text(item) -> str:
        if item.last_status == "success":
            duration = f" · {item.last_duration:.2f}s" if item.last_duration is not None else ""
            return f"✓ Réussi{duration} · {item.run_count} lancement(s)"
        if item.last_status == "error":
            return f"⚠ Erreur · {item.run_count} lancement(s)"
        return "Jamais lancé"

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
            path = pick_file()
            self.status.text = "Copie et enregistrement…"
            item = import_script(path, registry=Registry.load())
        except Exception as exc:
            self.status.text = "Import impossible"
            self._alert("Import impossible", str(exc))
            self.busy = False
            return
        self.busy = False
        self.status.text = f"{item.name} ajouté"
        self.refresh()
        self.edit_item(item.id)

    def on_add_project(self, sender) -> None:
        if self.busy:
            return
        self.busy = True
        self.status.text = "Choisis le dossier du projet…"
        try:
            root = pick_directory()
            files = list_python_files(root, recursive=True)
            selected = self._choose_entry_script(root, files)
            if selected is None:
                self.status.text = "Ajout annulé"
                self.busy = False
                return
            self.status.text = "Copie et enregistrement du projet…"
            item = add_project(root, selected, registry=Registry.load())
        except Exception as exc:
            self.status.text = "Projet non ajouté"
            self._alert("Projet non ajouté", str(exc))
            self.busy = False
            return
        self.busy = False
        self.status.text = f"{item.name} ajouté"
        self.refresh()
        self.edit_item(item.id)

    def _choose_entry_script(self, root: str, files: List[Path]) -> Optional[str]:
        if not files:
            self._alert("Projet invalide", "Aucun fichier .py trouvé dans ce dossier.")
            return None
        root_path = Path(root)
        preferred = ["main.py", "bootstrap.py", "app.py", "run.py", "launcher.py"]
        ordered = sorted(
            files,
            key=lambda p: (
                preferred.index(p.name.lower()) if p.name.lower() in preferred else 99,
                len(p.relative_to(root_path).parts),
                p.name.lower(),
            ),
        )
        alert = ui.Alert(title="Script de démarrage", message="Choisis le point d’entrée du projet")
        alert.add_action("Annuler")
        shown = ordered[:12]
        for path in shown:
            alert.add_action(str(path.relative_to(root_path)))
        choice = alert.show()
        if choice <= 0:
            return None
        index = choice - 1
        if index >= len(shown):
            return None
        return str(shown[index].relative_to(root_path))

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
        alert.add_action("Annuler")
        alert.add_action("Enregistrer")
        try:
            alert.add_destructive_action("Supprimer")
        except Exception:
            alert.add_action("Supprimer")
        choice = alert.show()
        if choice == 1:
            item.name = (name_field.text or item.name).strip() or item.name
            item.category = (category_field.text or "Général").strip() or "Général"
            if entry_field is not None:
                candidate = (entry_field.text or item.entry_script).strip()
                target = Path(item.project_root) / candidate
                if not target.exists() or target.suffix.lower() != ".py":
                    self._alert("Point d’entrée invalide", "Le fichier indiqué n’existe pas ou n’est pas un .py")
                    return
                item.entry_script = candidate
            registry.update(item)
            self.status.text = "Modifications enregistrées"
            self.refresh()
        elif choice == 2:
            registry.remove(item_id)
            self.status.text = f"{item.name} supprimé"
            self.refresh()

    def toggle_favorite(self, item_id: str) -> None:
        registry = Registry.load()
        item = registry.require(item_id)
        item.favorite = not item.favorite
        registry.update(item)
        self.refresh()

    def launch(self, item_id: str) -> None:
        if self.busy:
            return
        self.busy = True
        registry = Registry.load()
        item = registry.require(item_id)
        self.status.text = f"Lancement de {item.name}…"

        def worker():
            result = run_item(item)
            append_history(item, result)
            registry.update(item)

            def finish():
                self.busy = False
                self.refresh()
                if result.success:
                    self.status.text = f"{item.name} terminé en {result.duration:.2f}s"
                    if result.output.strip():
                        self._alert(f"Sortie — {item.name}", result.output[-1800:])
                else:
                    self.status.text = f"Erreur dans {item.name}"
                    self._alert("Erreur d’exécution", (result.error or "Erreur inconnue")[-2200:])

            self._on_main_thread(finish)

        threading.Thread(target=worker, daemon=True).start()

    def on_close(self, sender) -> None:
        if self.busy:
            self._alert("Opération en cours", "Attends la fin de l’opération avant de fermer.")
            return
        self.view.close()

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
        mode = getattr(ui, "PRESENTATION_MODE_SHEET", None)
        if mode is None:
            mode = getattr(ui, "PRESENTATION_MODE_FORM_SHEET", None)
        if mode is None:
            ui.show_view(self.view)
        else:
            ui.show_view(self.view, mode)


def present_launcher() -> None:
    LauncherProView().present()
