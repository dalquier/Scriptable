from __future__ import annotations

import threading
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
    """Interface native Pyto, pensée comme une application iPhone."""

    def __init__(self) -> None:
        self.registry = Registry.load()
        self.cards: List[Dict[str, object]] = []
        self.query = ""
        self.busy = False

        self.view = ui.View()
        self.view.title = theme.TITLE
        self.view.background_color = theme.BACKGROUND
        self.view.layout = self.layout

        # En-tête principal
        self.hero = ui.View()
        self.hero.background_color = theme.CARD
        self.hero.corner_radius = 24

        self.app_icon = self._label("▶︎", 25, True, theme.TEXT)
        self.app_icon.background_color = theme.PRIMARY
        self.app_icon.corner_radius = 15
        self.app_icon.text_alignment = ui.TEXT_ALIGNMENT_CENTER

        self.title = self._label(theme.TITLE, 28, True, theme.TEXT)
        self.subtitle = self._label(
            "Lance tes automatisations en un geste",
            14,
            False,
            theme.SECONDARY_TEXT,
        )

        self.quit_button = ui.Button(title="Quitter")
        self.quit_button.action = self.on_quit
        self.quit_button.background_color = theme.CARD_ALT
        self.quit_button.tint_color = theme.DANGER
        self.quit_button.corner_radius = 13

        for item in (self.app_icon, self.title, self.subtitle, self.quit_button):
            self.hero.add_subview(item)

        # Statistiques
        self.stats_bar = ui.View()
        self.stats_bar.background_color = theme.CARD
        self.stats_bar.corner_radius = 18
        self.stat_scripts = self._stat_block("0", "Scripts")
        self.stat_favorites = self._stat_block("0", "Favoris")
        self.stat_runs = self._stat_block("0", "Lancements")
        for block in (self.stat_scripts, self.stat_favorites, self.stat_runs):
            self.stats_bar.add_subview(block["container"])

        # Recherche et actions
        self.search = ui.TextField(placeholder="Rechercher un script ou une catégorie")
        self.search.did_change = self.on_search
        self.search.background_color = theme.CARD
        self.search.text_color = theme.TEXT
        self.search.corner_radius = 15

        self.add_button = ui.Button(title="＋ Ajouter un script")
        self.add_button.action = self.on_add
        self.add_button.background_color = theme.PRIMARY
        self.add_button.tint_color = theme.TEXT
        self.add_button.corner_radius = 15

        self.section_title = self._label("Mes scripts", 20, True, theme.TEXT)
        self.status = self._label("Prêt", 13, False, theme.SECONDARY_TEXT)

        self.scroll = ui.ScrollView()
        self.scroll.background_color = theme.BACKGROUND

        for control in (
            self.hero,
            self.stats_bar,
            self.search,
            self.add_button,
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
        selected_font = theme.font(size, bold)
        if selected_font is not None:
            label.font = selected_font
        return label

    def _stat_block(self, value: str, caption: str) -> Dict[str, object]:
        container = ui.View()
        value_label = self._label(value, 21, True, theme.TEXT)
        value_label.text_alignment = ui.TEXT_ALIGNMENT_CENTER
        caption_label = self._label(caption, 11, False, theme.SECONDARY_TEXT)
        caption_label.text_alignment = ui.TEXT_ALIGNMENT_CENTER
        container.add_subview(value_label)
        container.add_subview(caption_label)
        return {"container": container, "value": value_label, "caption": caption_label}

    def layout(self) -> None:
        width = self.view.width
        height = self.view.height
        margin = 16
        usable = max(280, width - margin * 2)

        self.hero.frame = (margin, 16, usable, 104)
        self.app_icon.frame = (16, 22, 54, 54)
        self.title.frame = (84, 17, usable - 178, 36)
        self.subtitle.frame = (84, 51, usable - 178, 38)
        self.quit_button.frame = (usable - 90, 30, 76, 42)

        self.stats_bar.frame = (margin, 132, usable, 76)
        third = usable / 3
        for index, block in enumerate(
            (self.stat_scripts, self.stat_favorites, self.stat_runs)
        ):
            block["container"].frame = (third * index, 0, third, 76)
            block["value"].frame = (0, 11, third, 30)
            block["caption"].frame = (0, 41, third, 22)

        self.search.frame = (margin, 220, usable, 46)
        self.add_button.frame = (margin, 278, usable, 48)
        self.section_title.frame = (margin, 342, usable * 0.55, 28)
        self.status.frame = (margin + usable * 0.45, 344, usable * 0.55, 24)
        self.status.text_alignment = ui.TEXT_ALIGNMENT_RIGHT

        scroll_y = 382
        self.scroll.frame = (0, scroll_y, width, max(1, height - scroll_y))
        self.layout_cards()

    def layout_cards(self) -> None:
        y = 8
        width = max(280, self.scroll.width - 32)
        for card in self.cards:
            container = card["container"]
            container.frame = (16, y, width, 112)
            card["icon"].frame = (15, 18, 46, 46)
            card["name"].frame = (74, 14, width - 220, 28)
            card["category"].frame = (74, 42, width - 220, 22)
            card["meta"].frame = (16, 80, width - 178, 21)
            card["favorite"].frame = (width - 148, 28, 38, 50)
            card["delete"].frame = (width - 106, 28, 38, 50)
            card["run"].frame = (width - 60, 27, 48, 52)
            y += 124
        self.scroll.content_size = (
            self.scroll.width,
            max(self.scroll.height + 1, y + 12),
        )

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
            self._show_empty_state()
        else:
            for entry in entries:
                self._add_card(entry)

        self.layout_cards()

    def _show_empty_state(self) -> None:
        container = ui.View()
        container.background_color = theme.CARD
        container.corner_radius = 22
        icon = self._label("⌘", 32, True, theme.PRIMARY)
        icon.text_alignment = ui.TEXT_ALIGNMENT_CENTER
        name = self._label(
            "Aucun script" if not self.query else "Aucun résultat",
            19,
            True,
            theme.TEXT,
        )
        category = self._label(
            "Ajoute ton premier fichier Python avec le bouton ci-dessus"
            if not self.query
            else "Modifie les termes de ta recherche",
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
        self.cards.append(
            {
                "container": container,
                "icon": icon,
                "name": name,
                "category": category,
                "meta": meta,
                "favorite": favorite,
                "delete": delete,
                "run": run,
            }
        )

    def _add_card(self, entry) -> None:
        container = ui.View()
        container.background_color = theme.CARD
        container.corner_radius = 22

        icon = self._label(self._icon_for(entry), 22, True, theme.PRIMARY)
        icon.background_color = theme.PRIMARY_SOFT
        icon.corner_radius = 13
        icon.text_alignment = ui.TEXT_ALIGNMENT_CENTER

        name = self._label(entry.name, 18, True, theme.TEXT)
        category = self._label(
            entry.category or "Général", 13, False, theme.SECONDARY_TEXT
        )
        meta = self._label(
            self._status_text(entry), 12, False, theme.SECONDARY_TEXT
        )

        favorite = ui.Button(title="★" if entry.favorite else "☆")
        favorite.tint_color = (
            theme.SUCCESS if entry.favorite else theme.SECONDARY_TEXT
        )
        favorite.action = (
            lambda sender, script_id=entry.id: self.toggle_favorite(script_id)
        )

        delete = ui.Button(title="×")
        delete.tint_color = theme.DANGER
        delete.action = lambda sender, script_id=entry.id: self.delete_entry(script_id)

        run = ui.Button(title="▶︎")
        run.background_color = theme.PRIMARY
        run.tint_color = theme.TEXT
        run.corner_radius = 15
        run.action = lambda sender, script_id=entry.id: self.launch(script_id)

        for sub in (icon, name, category, meta, favorite, delete, run):
            container.add_subview(sub)
        self.scroll.add_subview(container)
        self.cards.append(
            {
                "container": container,
                "icon": icon,
                "name": name,
                "category": category,
                "meta": meta,
                "favorite": favorite,
                "delete": delete,
                "run": run,
            }
        )

    @staticmethod
    def _icon_for(entry) -> str:
        mapping = {
            "terminal": ">_",
            "hammer": "⚒",
            "gear": "⚙︎",
            "wand": "✦",
            "folder": "▣",
        }
        return mapping.get((entry.icon or "terminal").lower(), ">_")

    @staticmethod
    def _status_text(entry) -> str:
        if entry.last_status == "success":
            duration = (
                f" · {entry.last_duration:.2f}s"
                if entry.last_duration is not None
                else ""
            )
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
        alert = ui.Alert(
            title="Ajouter un script",
            message="Choisis la méthode la plus adaptée à l'emplacement du fichier.",
        )
        alert.add_action("Annuler")
        alert.add_action("Choisir un fichier .py")
        alert.add_action("Choisir un dossier")
        choice = alert.show()
        if choice == 1:
            self._import_direct_file()
        elif choice == 2:
            self._import_from_directory()

    def _import_direct_file(self) -> None:
        self.status.text = "Ouverture de Fichiers…"
        try:
            selected = pick_python_file()
            self._finish_import(selected)
        except Exception as exc:
            self.status.text = "Sélection impossible"
            self._alert(
                "Fichier non sélectionnable",
                f"{exc}\n\nUtilise « Choisir un dossier » : Launcher Pro détectera les fichiers .py présents.",
            )

    def _import_from_directory(self) -> None:
        self.status.text = "Sélection du dossier…"
        try:
            files = pick_python_file_from_directory()
            selected = self._choose_file_from_list(files)
            if selected is not None:
                self._finish_import(str(selected))
            else:
                self.status.text = "Ajout annulé"
        except Exception as exc:
            self.status.text = "Dossier inutilisable"
            self._alert("Import impossible", str(exc))

    def _choose_file_from_list(self, files: List[Path]) -> Optional[Path]:
        visible = files[:20]
        alert = ui.Alert(
            title="Scripts détectés",
            message=(
                f"{len(files)} fichier(s) .py trouvé(s)."
                + (" Les 20 premiers sont affichés." if len(files) > 20 else "")
            ),
        )
        alert.add_action("Annuler")
        for path in visible:
            alert.add_action(path.name)
        choice = alert.show()
        if choice <= 0 or choice > len(visible):
            return None
        return visible[choice - 1]

    def _finish_import(self, selected: str) -> None:
        default_name = Path(selected).stem
        values = self._prompt_import(default_name)
        if values is None:
            self.status.text = "Ajout annulé"
            return
        name, category = values
        try:
            import_script(
                selected,
                name=name,
                category=category,
                registry=self.registry,
            )
            self.query = ""
            self.search.text = ""
            self.status.text = f"{name} ajouté"
            self.refresh()
        except Exception as exc:
            self.status.text = "Import impossible"
            self._alert("Import impossible", str(exc))

    def _prompt_import(self, default_name: str):
        alert = ui.Alert(
            title="Nouveau raccourci",
            message="Donne un nom clair et une catégorie au script.",
        )
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
        alert = ui.Alert(
            title="Supprimer le script ?",
            message=f"« {entry.name} » sera retiré de Launcher Pro.",
        )
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
                    self._alert(
                        f"Erreur — {entry.name}",
                        (result.error or "Erreur inconnue")[-1800:],
                    )

            self._on_main_thread(finish)

        threading.Thread(target=worker, daemon=True).start()

    def on_quit(self, sender=None) -> None:
        if self.busy:
            self._alert(
                "Exécution en cours",
                "Attends la fin du script avant de fermer Launcher Pro.",
            )
            return
        alert = ui.Alert(
            title="Quitter Launcher Pro ?",
            message="Les scripts et réglages sont déjà enregistrés.",
        )
        alert.add_action("Annuler")
        alert.add_action("Quitter")
        if alert.show() != 1:
            return
        self._close_view()

    def _close_view(self) -> None:
        candidates = [self.view]
        current = self.view
        for _ in range(8):
            current = getattr(current, "superview", None)
            if current is None:
                break
            candidates.append(current)
        for candidate in reversed(candidates):
            closer = getattr(candidate, "close", None)
            if callable(closer):
                try:
                    closer()
                    return
                except Exception:
                    pass
        self.status.text = "Utilise la flèche retour de Pyto pour fermer"

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
