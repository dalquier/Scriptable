from __future__ import annotations

import os
import threading
from pathlib import Path
from typing import Dict, List

import pyto_ui as ui

from core.importer import import_script, pick_python_file
from core.registry import Registry
from core.runner import run_script
from . import theme


class LauncherProView:
    """Interface native Pyto du Sprint 2.

    La classe ne contient pas de logique de stockage ou d'exécution : elle appelle
    exclusivement les services du dossier core/ validés pendant le Sprint 1.
    """

    def __init__(self) -> None:
        self.registry = Registry.load()
        self.cards: List[Dict[str, object]] = []
        self.query = ""
        self.busy = False

        self.view = ui.View()
        self.view.title = theme.TITLE
        self.view.background_color = theme.BACKGROUND
        self.view.layout = self.layout

        self.title = self._label(theme.TITLE, 31, True, theme.TEXT)
        self.subtitle = self._label(theme.SUBTITLE, 15, False, theme.SECONDARY_TEXT)

        self.search = ui.TextField(placeholder="Rechercher un script ou une catégorie")
        self.search.did_change = self.on_search
        self.search.background_color = theme.CARD
        self.search.text_color = theme.TEXT
        self.search.corner_radius = 14

        self.add_button = ui.Button(title="＋ Ajouter")
        self.add_button.action = self.on_add
        self.add_button.background_color = theme.PRIMARY
        self.add_button.tint_color = theme.TEXT
        self.add_button.corner_radius = 14

        self.stats = self._label("", 13, False, theme.SECONDARY_TEXT)
        self.status = self._label("Prêt", 13, False, theme.SECONDARY_TEXT)

        self.scroll = ui.ScrollView()
        self.scroll.background_color = theme.BACKGROUND

        for control in (
            self.title,
            self.subtitle,
            self.search,
            self.add_button,
            self.stats,
            self.status,
            self.scroll,
        ):
            self.view.add_subview(control)

        self.refresh()

    @staticmethod
    def _label(text: str, size: float, bold: bool, color):
        label = ui.Label(text=text)
        label.text_color = color
        selected_font = theme.font(size, bold)
        if selected_font is not None:
            label.font = selected_font
        return label

    def layout(self) -> None:
        width = self.view.width
        height = self.view.height
        margin = 18
        top = 20

        self.title.frame = (margin, top, width - margin * 2, 40)
        self.subtitle.frame = (margin, top + 40, width - margin * 2, 24)

        search_width = max(140, width - margin * 2 - 112)
        self.search.frame = (margin, top + 78, search_width, 44)
        self.add_button.frame = (margin + search_width + 10, top + 78, 102, 44)

        self.stats.frame = (margin, top + 132, width - margin * 2, 20)
        self.status.frame = (margin, top + 154, width - margin * 2, 20)
        scroll_y = top + 182
        self.scroll.frame = (0, scroll_y, width, max(1, height - scroll_y))
        self.layout_cards()

    def layout_cards(self) -> None:
        y = 8
        width = max(280, self.scroll.width - 32)
        for card in self.cards:
            container = card["container"]
            container.frame = (16, y, width, 104)
            card["icon"].frame = (14, 18, 42, 42)
            card["name"].frame = (68, 13, width - 208, 27)
            card["category"].frame = (68, 40, width - 208, 21)
            card["meta"].frame = (16, 73, width - 176, 20)
            card["favorite"].frame = (width - 146, 26, 38, 48)
            card["delete"].frame = (width - 104, 26, 38, 48)
            card["run"].frame = (width - 60, 24, 48, 52)
            y += 116
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
        favorite_count = sum(1 for item in self.registry.scripts if item.favorite)
        total_runs = sum(item.run_count for item in self.registry.scripts)
        self.stats.text = (
            f"{len(self.registry.scripts)} script(s) · "
            f"{favorite_count} favori(s) · {total_runs} lancement(s)"
        )

        if not entries:
            self._show_empty_state()
        else:
            for entry in entries:
                self._add_card(entry)

        self.layout_cards()

    def _show_empty_state(self) -> None:
        container = ui.View()
        container.background_color = theme.CARD
        container.corner_radius = 20
        icon = self._label("⌘", 30, True, theme.PRIMARY)
        name = self._label(
            "Aucun script" if not self.query else "Aucun résultat",
            19,
            True,
            theme.TEXT,
        )
        category = self._label(
            "Touche ＋ Ajouter pour importer ton premier fichier .py"
            if not self.query else "Essaie une autre recherche",
            13,
            False,
            theme.SECONDARY_TEXT,
        )
        meta = self._label("", 12, False, theme.SECONDARY_TEXT)
        favorite = ui.Button(title="")
        delete = ui.Button(title="")
        run = ui.Button(title="")
        for sub in (icon, name, category, meta, favorite, delete, run):
            container.add_subview(sub)
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

    def _add_card(self, entry) -> None:
        container = ui.View()
        container.background_color = theme.CARD
        container.corner_radius = 20

        icon = self._label(self._icon_for(entry), 23, True, theme.PRIMARY)
        icon.background_color = theme.PRIMARY_SOFT
        icon.corner_radius = 12
        icon.text_alignment = ui.TEXT_ALIGNMENT_CENTER

        name = self._label(entry.name, 18, True, theme.TEXT)
        category = self._label(entry.category or "Général", 13, False, theme.SECONDARY_TEXT)

        status_text = self._status_text(entry)
        meta = self._label(status_text, 12, False, theme.SECONDARY_TEXT)

        favorite = ui.Button(title="★" if entry.favorite else "☆")
        favorite.tint_color = theme.SUCCESS if entry.favorite else theme.SECONDARY_TEXT
        favorite.action = lambda sender, script_id=entry.id: self.toggle_favorite(script_id)

        delete = ui.Button(title="×")
        delete.tint_color = theme.DANGER
        delete.action = lambda sender, script_id=entry.id: self.delete_entry(script_id)

        run = ui.Button(title="▶︎")
        run.background_color = theme.PRIMARY
        run.tint_color = theme.TEXT
        run.corner_radius = 14
        run.action = lambda sender, script_id=entry.id: self.launch(script_id)

        for sub in (icon, name, category, meta, favorite, delete, run):
            container.add_subview(sub)
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
    def _icon_for(entry) -> str:
        icon = (entry.icon or "terminal").lower()
        mapping = {
            "terminal": ">_",
            "hammer": "⚒",
            "gear": "⚙︎",
            "wand": "✦",
            "folder": "▣",
        }
        return mapping.get(icon, ">_")

    @staticmethod
    def _status_text(entry) -> str:
        if entry.last_status == "success":
            duration = f" · {entry.last_duration:.2f}s" if entry.last_duration is not None else ""
            return f"✓ Réussi{duration} · {entry.run_count} lancement(s)"
        if entry.last_status == "error":
            return f"⚠ Dernière exécution en erreur · {entry.run_count} lancement(s)"
        return "Jamais lancé"

    def on_search(self, sender) -> None:
        self.query = (sender.text or "").strip()
        self.refresh()

    def on_add(self, sender) -> None:
        if self.busy:
            return
        self.status.text = "Ouverture du sélecteur iOS…"
        try:
            selected = pick_python_file()
            default_name = Path(selected).stem
            values = self._prompt_import(default_name)
            if values is None:
                self.status.text = "Ajout annulé"
                return
            name, category = values
            import_script(selected, name=name, category=category, registry=self.registry)
            self.status.text = f"{name} ajouté"
            self.query = ""
            self.search.text = ""
            self.refresh()
        except Exception as exc:
            self.status.text = "Import impossible"
            self._alert("Import impossible", str(exc))

    def _prompt_import(self, default_name: str):
        alert = ui.Alert(title="Nouveau raccourci", message="Personnalise le script importé")
        name_field = ui.TextField(text=default_name)
        category_field = ui.TextField(text="Général")
        alert.add_text_field(name_field)
        alert.add_text_field(category_field)
        alert.add_action("Annuler")
        alert.add_action("Enregistrer")
        if alert.show() != 1:
            return None
        name = (name_field.text or default_name).strip()
        category = (category_field.text or "Général").strip() or "Général"
        if not name:
            raise ValueError("Le nom du script ne peut pas être vide")
        return name, category

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
        alert = ui.Alert(title="Supprimer le script ?", message=f"« {entry.name} » sera retiré du lanceur.")
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
                    self.status.text = f"{entry.name} terminé en {result.duration:.2f}s"
                    if result.output.strip():
                        self._alert(f"Sortie — {entry.name}", result.output[-1800:])
                else:
                    self.status.text = f"Erreur dans {entry.name}"
                    self._alert(f"Erreur — {entry.name}", (result.error or "Erreur inconnue")[-1800:])

            self._on_main_thread(finish)

        threading.Thread(target=worker, daemon=True).start()

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
        mode = getattr(ui, "PRESENTATION_MODE_FULLSCREEN", None)
        if mode is None:
            ui.show_view(self.view)
        else:
            ui.show_view(self.view, mode)


def present_launcher() -> None:
    LauncherProView().present()
