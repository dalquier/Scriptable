from __future__ import annotations

import pyto_ui as ui

from app_controller import AppController
from ppx_config import APP_TITLE


def _system_color(name: str, legacy_name: str):
    palette = getattr(ui, "SystemColors", None)
    if palette is not None and hasattr(palette, name):
        return getattr(palette, name)
    return getattr(ui, legacy_name)


def _sheet_presentation_mode():
    modes = getattr(ui, "PresentationMode", None)
    if modes is not None and hasattr(modes, "SHEET"):
        return modes.SHEET
    return getattr(ui, "PRESENTATION_MODE_SHEET")


class MainUI:
    def __init__(self):
        self.view = ui.View()
        self.view.background_color = _system_color("SYSTEM_BACKGROUND", "COLOR_SYSTEM_BACKGROUND")
        self.view.title = APP_TITLE

        # Les références sont conservées pendant toute la durée de la vue.
        self._callbacks = []
        self.controller = AppController(self)

        self._build()
        self._bind_actions()

    def _build(self):
        title = ui.Label()
        title.text = APP_TITLE
        title.font = ui.Font.bold_system_font_of_size(24)
        title.text_alignment = ui.TEXT_ALIGNMENT_CENTER
        title.number_of_lines = 2
        title.frame = (20, 30, 360, 70)
        self.view.add_subview(title)

        subtitle = ui.Label()
        subtitle.text = "Exporter et réimporter un projet Pyto au format Markdown multipartie."
        subtitle.font = ui.Font.system_font_of_size(15)
        subtitle.text_alignment = ui.TEXT_ALIGNMENT_CENTER
        subtitle.number_of_lines = 3
        subtitle.frame = (25, 95, 350, 70)
        self.view.add_subview(subtitle)

        self.export_button = self._make_button("Exporter un projet", 180)
        self.import_button = self._make_button("Importer un lot", 240)
        self.prompt_button = self._make_button("Copier le prompt V5", 300)
        self.migration_button = self._make_button("Copier le prompt de migration", 360)

        self.status_label = ui.Label()
        self.status_label.text = "Prêt."
        self.status_label.font = ui.Font.system_font_of_size(14)
        self.status_label.text_alignment = ui.TEXT_ALIGNMENT_CENTER
        self.status_label.number_of_lines = 3
        self.status_label.frame = (25, 430, 350, 80)
        self.view.add_subview(self.status_label)

        self.view.frame = (0, 0, 400, 540)

    def _make_button(self, title: str, y: float):
        button = ui.Button()
        button.title = title
        button.frame = (35, y, 330, 48)
        button.corner_radius = 12
        button.background_color = _system_color("SYSTEM_BLUE", "COLOR_SYSTEM_BLUE")
        button.tint_color = _system_color("WHITE", "COLOR_WHITE")
        self.view.add_subview(button)
        return button

    def _bind_actions(self):
        bindings = [
            (self.export_button, self.controller.export_action),
            (self.import_button, self.controller.import_action),
            (self.prompt_button, self.controller.copy_prompt_action),
            (self.migration_button, self.controller.copy_migration_action),
        ]

        for button, callback in bindings:
            self._callbacks.append(callback)
            button.action = callback

    def set_status(self, text: str):
        self.status_label.text = text

    def show_message(self, title: str, message: str):
        alert = ui.Alert(title=title, message=message)
        alert.add_action("OK")
        alert.show()

    def show_error(self, title: str, message: str):
        alert = ui.Alert(title=title, message=message)
        alert.add_action("OK")
        alert.show()

    def copy_text(self, text: str):
        ui.Pasteboard.string = text

    def present(self):
        ui.show_view(self.view, _sheet_presentation_mode())
