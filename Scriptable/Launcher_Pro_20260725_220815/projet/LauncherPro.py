from __future__ import annotations

import os
import threading
import pyto_ui as ui

from launcher_core import ScriptEntry
from launcher_picker import import_python_file
from launcher_runner import run_entry
from launcher_storage import load_registry, save_registry
from launcher_theme import BG, CARD, DANGER, MUTED, PRIMARY, SUCCESS, TEXT, TITLE, SUBTITLE


class LauncherApp:
    def __init__(self):
        self.registry = load_registry()
        self.view = ui.View()
        self.view.background_color = BG
        self.view.title = TITLE
        self.view.layout = self.layout
        self.search = ui.TextField(placeholder="Rechercher un script")
        self.search.did_change = self.on_search
        self.add_button = ui.Button(title="＋ Ajouter")
        self.add_button.background_color = PRIMARY
        self.add_button.tint_color = TEXT
        self.add_button.action = self.on_add
        self.header = ui.Label(text=TITLE)
        self.header.text_color = TEXT
        self.header.font = ui.Font.bold_system_font_of_size(28)
        self.subtitle = ui.Label(text=SUBTITLE)
        self.subtitle.text_color = MUTED
        self.status = ui.Label(text="Prêt")
        self.status.text_color = MUTED
        self.scroll = ui.ScrollView()
        for control in (self.header, self.subtitle, self.search, self.add_button, self.status, self.scroll):
            self.view.add_subview(control)
        self.cards = []
        self.refresh()

    def layout(self):
        w, h = self.view.width, self.view.height
        self.header.frame = (20, 20, w - 40, 36)
        self.subtitle.frame = (20, 56, w - 40, 24)
        self.search.frame = (20, 92, w - 150, 42)
        self.add_button.frame = (w - 120, 92, 100, 42)
        self.status.frame = (20, 140, w - 40, 24)
        self.scroll.frame = (0, 170, w, h - 170)
        self.layout_cards()

    def layout_cards(self):
        y = 10
        width = max(280, self.scroll.width - 32)
        for card in self.cards:
            card["container"].frame = (16, y, width, 86)
            card["name"].frame = (16, 10, width - 165, 28)
            card["meta"].frame = (16, 42, width - 165, 24)
            card["favorite"].frame = (width - 142, 18, 38, 44)
            card["delete"].frame = (width - 98, 18, 38, 44)
            card["run"].frame = (width - 54, 18, 42, 44)
            y += 98
        self.scroll.content_size = (self.scroll.width, max(self.scroll.height + 1, y))

    def clear_cards(self):
        for card in self.cards:
            card["container"].remove_from_superview()
        self.cards = []

    def refresh(self, query=""):
        self.clear_cards()
        q = query.strip().lower()
        items = [x for x in self.registry.scripts if not q or q in x.name.lower()]
        items.sort(key=lambda x: (not x.favorite, x.name.lower()))
        for entry in items:
            container = ui.View()
            container.background_color = CARD
            container.corner_radius = 16
            name = ui.Label(text=entry.name)
            name.text_color = TEXT
            name.font = ui.Font.bold_system_font_of_size(18)
            meta_text = f"{entry.run_count} lancement(s)"
            if entry.last_status == "success":
                meta_text += " · réussi"
            elif entry.last_status == "error":
                meta_text += " · erreur"
            meta = ui.Label(text=meta_text)
            meta.text_color = MUTED
            favorite = ui.Button(title="★" if entry.favorite else "☆")
            favorite.tint_color = SUCCESS
            favorite.action = lambda sender, e=entry: self.toggle_favorite(e)
            delete = ui.Button(title="×")
            delete.tint_color = DANGER
            delete.action = lambda sender, e=entry: self.delete_entry(e)
            run = ui.Button(title="▶︎")
            run.background_color = PRIMARY
            run.tint_color = TEXT
            run.corner_radius = 12
            run.action = lambda sender, e=entry: self.launch(e)
            for sub in (name, meta, favorite, delete, run):
                container.add_subview(sub)
            self.scroll.add_subview(container)
            self.cards.append({"container": container, "name": name, "meta": meta, "favorite": favorite, "delete": delete, "run": run})
        self.status.text = f"{len(items)} script(s)"
        self.layout_cards()

    def on_search(self, sender):
        self.refresh(sender.text or "")

    def on_add(self, sender):
        self.status.text = "Ouverture du sélecteur iOS…"
        try:
            source, local = import_python_file()
            default_name = os.path.splitext(os.path.basename(source))[0]
            alert = ui.Alert(title="Nom du script", message="Donne un nom à ce raccourci")
            field = ui.TextField(text=default_name)
            alert.add_text_field(field)
            alert.add_action("Annuler")
            alert.add_action("Enregistrer")
            choice = alert.show()
            if choice != 1:
                try:
                    os.remove(local)
                except OSError:
                    pass
                self.status.text = "Ajout annulé"
                return
            name = (field.text or default_name).strip()
            self.registry.scripts.append(ScriptEntry.create(name, local, source))
            save_registry(self.registry)
            self.refresh(self.search.text or "")
        except Exception as exc:
            self.show_error("Import impossible", str(exc))

    def toggle_favorite(self, entry):
        entry.favorite = not entry.favorite
        save_registry(self.registry)
        self.refresh(self.search.text or "")

    def delete_entry(self, entry):
        alert = ui.Alert(title="Supprimer ?", message=f"Retirer « {entry.name} » du lanceur ?")
        alert.add_action("Annuler")
        alert.add_destructive_action("Supprimer")
        if alert.show() != 1:
            return
        self.registry.scripts = [x for x in self.registry.scripts if x.id != entry.id]
        try:
            os.remove(entry.local_path)
        except OSError:
            pass
        save_registry(self.registry)
        self.refresh(self.search.text or "")

    def launch(self, entry):
        self.status.text = f"Lancement de {entry.name}…"
        def worker():
            ok, message = run_entry(entry)
            save_registry(self.registry)
            def finish():
                self.refresh(self.search.text or "")
                self.status.text = message if ok else f"Erreur dans {entry.name}"
                if not ok:
                    self.show_error(f"Erreur — {entry.name}", message[-1800:])
            ui.run_on_main_thread(finish)
        threading.Thread(target=worker, daemon=True).start()

    def show_error(self, title, message):
        alert = ui.Alert(title=title, message=message)
        alert.add_action("OK")
        alert.show()

    def present(self):
        ui.show_view(self.view, ui.PRESENTATION_MODE_FULLSCREEN)


if __name__ == "__main__":
    LauncherApp().present()
