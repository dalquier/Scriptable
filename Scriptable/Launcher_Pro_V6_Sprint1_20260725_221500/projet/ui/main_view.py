from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Dict, List, Optional

import pyto_ui as ui

from core.importer import (
    import_script,
    pick_python_file,
    pick_python_file_from_directory,
)
from core.registry import Registry
from core.runner import run_script
from . import theme


class LauncherProView:
    """Interface native Pyto présentée comme une feuille d’application iOS."""

    def __init__(self) -> None:
        self.registry = Registry.load()
        self.cards: List[Dict[str, object]] = []
        self.query = ""
        self.busy = False
        self.is_presented = False

        self.view = ui.View()
        self.view.title = theme.TITLE
        self.view.background_color = theme.BACKGROUND
        self.view.layout = self.layout

        # Barre d’application
        self.top_bar = ui.View()
        self.top_bar.background_color = theme.CARD
        self.top_bar.corner_radius = 20

        self.logo = self._label("▶︎", 21, True, theme.TEXT)
        self.logo.background_color = theme.PRIMARY
        self.logo.corner_radius = 13
        self.logo.text_alignment = ui.TEXT_ALIGNMENT_CENTER

        self.app_name = self._label("Launcher Pro", 23, True, theme.TEXT)
        self.app_caption = self._label(
            "Bibliothèque de scripts Python",
            12,
            False,
            theme.SECONDARY_TEXT,
        )

        self.quit_button = ui.Button(title="Fermer")
        self.quit_button.action = self.on_quit
        self.quit_button.background_color = theme.CARD_ALT
        self.quit_button.tint_color = theme.DANGER
        self.quit_button.corner_radius = 12

        for child in (self.logo, self.app_name, self.app_caption, self.quit_button):
            self.top_bar.add_subview(child)

        # Panneau de synthèse
        self.summary = ui.View()
        self.summary.background_color = theme.PRIMARY_SOFT
        self.summary.corner_radius = 20

        self.summary_title = self._label(
            "Tes automatisations, au même endroit",
            18,
            True,
            theme.TEXT,
        )
        self.summary_text = self._label(
            "Ajoute un script, organise-le et lance-le en un geste.",
            12,
            False,
            theme.SECONDARY_TEXT,
        )
        self.stat_scripts = self._pill("0", "scripts")
        self.stat_favorites = self._pill("0", "favoris")
        self.stat_runs = self._pill("0", "lancements")

        for child in (
            self.summary_title,
            self.summary_text,
            self.stat_scripts["container"],
            self.stat_favorites["container"],
            self.stat_runs["container"],
        ):
            self.summary.add_subview(child)

        # Actions
        self.search = ui.TextField(placeholder="Rechercher")
        self.search.did_change = self.on_search
        self.search.background_color = theme.CARD
        self.search.text_color = theme.TEXT
        self.search.corner_radius = 14

        self.add_file_button = ui.Button(title="＋ Fichier")
        self.add_file_button.action = self.on_add_file
        self.add_file_button.background_color = theme.PRIMARY
        self.add_file_button.tint_color = theme.TEXT
        self.add_file_button.corner_radius = 14

        self.add_folder_button = ui.Button(title="Dossier")
        self.add_folder_button.action = self.on_add_folder
        self.add_folder_button.background_color = theme.CARD
        self.add_folder_button.tint_color = theme.PRIMARY
        self.add_folder_button.corner_radius = 14

        self.section_title = self._label("Mes scripts", 18, True, theme.TEXT)
        self.status = self._label("Prêt", 12, False, theme.SECONDARY_TEXT)
        self.status.text_alignment = ui.TEXT_ALIGNMENT_RIGHT

        self.scroll = ui.ScrollView()
        self.scroll.background_color = theme.BACKGROUND

        for child in (
            self.top_bar,
            self.summary,
            self.search,
            self.add_file_button,
            self.add_folder_button,
            self.section_title,
            self.status,
            self.scroll,
        ):
            self.view.add_subview(child)

        self.refresh()

    @staticmethod
    def _label(text: str, size: float, bold: bool, color):
        label = ui.Label(text=text)
        label.text_color = color
        selected_font = theme.font(size, bold)
        if selected_font is not None:
            label.font = selected_font
        return label

    def _pill(self, value: str, caption: str) -> Dict[str, object]:
        container = ui.View()
        container.background_color = theme.CARD
        container.corner_radius = 12
        value_label = self._label(value, 16, True, theme.TEXT)
        caption_label = self._label(caption, 10, False, theme.SECONDARY_TEXT)
        value_label.text_alignment = ui.TEXT_ALIGNMENT_CENTER
        caption_label.text_alignment = ui.TEXT_ALIGNMENT_CENTER
        container.add_subview(value_label)
        container.add_subview(caption_label)
        return {"container": container, "value": value_label, "caption": caption_label}

    def layout(self) -> None:
        width = self.view.width
        height = self.view.height
        margin = 16
        usable = max(300, width - 2 * margin)

        self.top_bar.frame = (margin, 14, usable, 82)
        self.logo.frame = (14, 17, 48, 48)
        self.app_name.frame = (76, 13, usable - 168, 31)
        self.app_caption.frame = (76, 42, usable - 168, 24)
        self.quit_button.frame = (usable - 84, 20, 70, 40)

        self.summary.frame = (margin, 108, usable, 132)
        self.summary_title.frame = (16, 13, usable - 32, 28)
        self.summary_text.frame = (16, 40, usable - 32, 23)
        gap = 8
        pill_width = (usable - 32 - 2 * gap) / 3
        for index, pill in enumerate(
            (self.stat_scripts, self.stat_favorites, self.stat_runs)
        ):
            x = 16 + index * (pill_width + gap)
            pill["container"].frame = (x, 75, pill_width, 44)
            pill["value"].frame = (0, 3, pill_width, 21)
            pill["caption"].frame = (0, 22, pill_width, 17)

        action_y = 252
        self.search.frame = (margin, action_y, usable, 44)
        half = (usable - 10) / 2
        self.add_file_button.frame = (margin, action_y + 54, half, 46)
        self.add_folder_button.frame = (margin + half + 10, action_y + 54, half, 46)

        self.section_title.frame = (margin, action_y + 114, usable * 0.55, 26)
        self.status.frame = (margin + usable * 0.42, action_y + 116, usable * 0.58, 22)

        scroll_y = action_y + 148
        self.scroll.frame = (0, scroll_y, width, max(1, height - scroll_y - 10))
        self.layout_cards()

    def layout_cards(self) -> None:
        y = 6
        width = max(290, self.scroll.width - 32)
        for card in self.cards:
            card["container"].frame = (16, y, width, 96)
            card["icon"].frame = (14, 18, 42, 42)
            card["name"].frame = (68, 12, width - 210, 27)
            card["category"].frame = (68, 39, width - 210, 20)
            card["meta"].frame = (16, 69, width - 166, 18)
            card["favorite"].frame = (width - 138, 24, 36, 46)
            card["delete"].frame = (width - 98, 24, 36, 46)
            card["run"].frame = (width - 56, 22, 44, 48)
            y += 106
        self.scroll.content_size = (self.scroll.width, max(self.scroll.height + 1, y + 8))

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
        entries = self.registry.search(self.query)

        favorites = sum(1 for item in self.registry.scripts if item.favorite)
        runs = sum(item.run_count for item in self.registry.scripts)
        self.stat_scripts["value"].text = str(len(self.registry.scripts))
        self.stat_favorites["value"].text = str(favorites)
        self.stat_runs["value"].text = str(runs)

        if not entries:
            self._add_empty_card()
        else:
            for entry in entries:
                self._add_script_card(entry)
        self.layout_cards()

    def _base_card(self):
        container = ui.View()
        container.background_color = theme.CARD
        container.corner_radius = 18
        return container

    def _add_empty_card(self) -> None:
        container = self._base_card()
        icon = self._label("＋", 24, True, theme.PRIMARY)
        icon.text_alignment = ui.TEXT_ALIGNMENT_CENTER
        icon.background_color = theme.PRIMARY_SOFT
        icon.corner_radius = 12
        name = self._label(
            "Aucun script" if not self.query else "Aucun résultat",
            17,
            True,
            theme.TEXT,
        )
        category = self._label(
            "Ajoute un fichier ou sélectionne un dossier"
            if not self.query
            else "Essaie avec un autre terme",
            12,
            False,
            theme.SECONDARY_TEXT,
        )
        meta = self._label("", 11, False, theme.SECONDARY_TEXT)
        favorite = ui.Button(title="")
        delete = ui.Button(title="")
        run = ui.Button(title="")
        for child in (icon, name, category, meta, favorite, delete, run):
            container.add_subview(child)
        self.scroll.add_subview(container)
        self.cards.append({
            "container": container,
            "icon": icon,
            "name": name,
            "category": category,
            "meta": meta,
            "favorite": favorite,
            "delete": delete,
            "run": run,
        })

    def _add_script_card(self, entry) -> None:
        container = self._base_card()
        icon = self._label(">_", 18, True, theme.PRIMARY)
        icon.background_color = theme.PRIMARY_SOFT
        icon.corner_radius = 12
        icon.text_alignment = ui.TEXT_ALIGNMENT_CENTER

        name = self._label(entry.name, 17, True, theme.TEXT)
        category = self._label(entry.category or "Général", 12, False, theme.SECONDARY_TEXT)
        meta = self._label(self._status_text(entry), 11, False, theme.SECONDARY_TEXT)

        favorite = ui.Button(title="★" if entry.favorite else "☆")
        favorite.tint_color = theme.SUCCESS if entry.favorite else theme.SECONDARY_TEXT
        favorite.action = lambda sender, sid=entry.id: self.toggle_favorite(sid)

        delete = ui.Button(title="×")
        delete.tint_color = theme.DANGER
        delete.action = lambda sender, sid=entry.id: self.delete_entry(sid)

        run = ui.Button(title="▶︎")
        run.background_color = theme.PRIMARY
        run.tint_color = theme.TEXT
        run.corner_radius = 13
        run.action = lambda sender, sid=entry.id: self.launch(sid)

        for child in (icon, name, category, meta, favorite, delete, run):
            container.add_subview(child)
        self.scroll.add_subview(container)
        self.cards.append({
            "container": container,
            "icon": icon,
            "name": name,
            "category": category,
            "meta": meta,
            "favorite": favorite,
            "delete": delete,
            "run": run,
        })

    @staticmethod
    def _status_text(entry) -> str:
        if entry.last_status == "success":
            duration = f" · {entry.last_duration:.2f}s" if entry.last_duration is not None else ""
            return f"✓ Réussi{duration} · {entry.run_count} lancement(s)"
        if entry.last_status == "error":
            return f"⚠ Erreur · {entry.run_count} lancement(s)"
        return "Jamais lancé"

    def on_search(self, sender) -> None:
        self.query = (sender.text or "").strip()
        self.refresh()

    def on_add_file(self, sender) -> None:
        self._open_picker("file")

    def on_add_folder(self, sender) -> None:
        self._open_picker("folder")

    def _open_picker(self, mode: str) -> None:
        if self.busy:
            return
        self.busy = True
        self.status.text = "Ouverture de Fichiers…"

        try:
            self._close_view(confirm=False)
            time.sleep(0.25)
            if mode == "file":
                selected = pick_python_file()
            else:
                files = pick_python_file_from_directory()
                selected = self._choose_file(files)
                if selected is None:
                    raise RuntimeError("Sélection annulée")
        except Exception as exc:
            self.busy = False
            self.present()
            self.status.text = "Sélection annulée"
            self._alert("Import impossible", str(exc))
            return

        self.present()
        self.busy = False
        self._finish_import(str(selected))

    def _choose_file(self, files: List[Path]) -> Optional[Path]:
        if len(files) == 1:
            return files[0]
        alert = ui.Alert(
            title="Choisir un script",
            message=f"{len(files)} fichiers Python détectés",
        )
        alert.add_action("Annuler")
        visible = files[:12]
        for path in visible:
            alert.add_action(path.name)
        choice = alert.show()
        if choice <= 0 or choice > len(visible):
            return None
        return visible[choice - 1]

    def _finish_import(self, selected: str) -> None:
        default_name = Path(selected).stem
        alert = ui.Alert(title="Ajouter le script", message=Path(selected).name)
        name_field = ui.TextField(text=default_name)
        category_field = ui.TextField(text="Général")
        alert.add_text_field(name_field)
        alert.add_text_field(category_field)
        alert.add_action("Annuler")
        alert.add_action("Ajouter")
        if alert.show() != 1:
            self.status.text = "Ajout annulé"
            return

        name = (name_field.text or default_name).strip()
        category = (category_field.text or "Général").strip() or "Général"
        try:
            import_script(selected, name=name, category=category, registry=self.registry)
            self.query = ""
            self.search.text = ""
            self.status.text = f"{name} ajouté"
            self.refresh()
        except Exception as exc:
            self.status.text = "Import impossible"
            self._alert("Import impossible", str(exc))

    def toggle_favorite(self, script_id: str) -> None:
        registry = Registry.load()
        entry = registry.require(script_id)
        entry.favorite = not entry.favorite
        registry.save()
        self.status.text = "Favori mis à jour"
        self.refresh()

    def delete_entry(self, script_id: str) -> None:
        registry = Registry.load()
        entry = registry.require(script_id)
        alert = ui.Alert(title="Supprimer ?", message=f"Retirer « {entry.name} » du lanceur ?")
        alert.add_action("Annuler")
        try:
            alert.add_destructive_action("Supprimer")
        except Exception:
            alert.add_action("Supprimer")
        if alert.show() != 1:
            return
        registry.remove(script_id)
        self.status.text = f"{entry.name} supprimé"
        self.refresh()

    def launch(self, script_id: str) -> None:
        if self.busy:
            return
        self.busy = True
        registry = Registry.load()
        entry = registry.require(script_id)
        self.status.text = f"Lancement de {entry.name}…"

        def worker() -> None:
            result = run_script(entry)
            registry.save()

            def finish() -> None:
                self.busy = False
                self.refresh()
                if result.success:
                    self.status.text = f"Terminé en {result.duration:.2f}s"
                    if result.output.strip():
                        self._alert(f"Sortie — {entry.name}", result.output[-1800:])
                else:
                    self.status.text = f"Erreur dans {entry.name}"
                    self._alert("Erreur d’exécution", (result.error or "Erreur inconnue")[-1800:])

            self._on_main_thread(finish)

        threading.Thread(target=worker, daemon=True).start()

    def on_quit(self, sender) -> None:
        if self.busy:
            self._alert("Action en cours", "Attends la fin de l’opération avant de fermer.")
            return
        self._close_view(confirm=True)

    def _close_view(self, confirm: bool = False) -> None:
        if confirm:
            alert = ui.Alert(title="Fermer Launcher Pro ?", message="Tes scripts restent enregistrés.")
            alert.add_action("Annuler")
            alert.add_action("Fermer")
            if alert.show() != 1:
                return
        for name in ("close", "dismiss"):
            method = getattr(self.view, name, None)
            if callable(method):
                method()
                self.is_presented = False
                return
        closer = getattr(ui, "close_view", None)
        if callable(closer):
            closer(self.view)
        self.is_presented = False

    @staticmethod
    def _on_main_thread(callback) -> None:
        runner = getattr(ui, "run_on_main_thread", None)
        if callable(runner):
            runner(callback)
        else:
            callback()

    @staticmethod
    def _alert(title: str, message: str) -> None:
        alert = ui.Alert(title=title, message=message)
        alert.add_action("OK")
        alert.show()

    def present(self) -> None:
        if self.is_presented:
            return
        self.is_presented = True
        sheet = getattr(ui, "PRESENTATION_MODE_SHEET", None)
        if sheet is not None:
            ui.show_view(self.view, sheet)
            return
        form_sheet = getattr(ui, "PRESENTATION_MODE_FORM_SHEET", None)
        if form_sheet is not None:
            ui.show_view(self.view, form_sheet)
            return
        ui.show_view(self.view)


def present_launcher() -> None:
    LauncherProView().present()
