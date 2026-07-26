"""Couche de compatibilité Pyto pour GitHub Content Manager V5.

Cette classe corrige les différences entre l'API pyto_ui de Pyto et l'API
Pythonista utilisée par erreur dans la première livraison.
"""

import threading

import pyto_ui as ui

from ui_app import GitHubContentManagerApp as _BaseApp


class GitHubContentManagerApp(_BaseApp):
    """Version du lanceur adaptée à l'API native de Pyto."""

    def run(self):
        self.root = ui.View()
        self.root.name = "GitHub Content Manager V5"
        self.root.background_color = ui.COLOR_SYSTEM_BACKGROUND

        # Pyto n'accepte pas frame= dans le constructeur de WebView.
        self.web = ui.WebView()
        self.web.frame = (0, 0, self.root.width, self.root.height)
        self.web.flex = [ui.FLEXIBLE_WIDTH, ui.FLEXIBLE_HEIGHT]
        self.web.delegate = self
        self.web.load_html(self._html())
        self.root.add_subview(self.web)

        # Le chargement GitHub démarre une fois la vue affichée.
        threading.Timer(0.8, self.refresh).start()

        # Pyto utilise ui.show_view(...) et non View.present(...).
        mode = getattr(
            ui,
            "PRESENTATION_MODE_FULLSCREEN",
            getattr(
                ui,
                "PRESENTATION_MODE_FULL_SCREEN",
                getattr(ui, "PRESENTATION_MODE_SHEET", None),
            ),
        )
        if mode is None:
            ui.show_view(self.root)
        else:
            ui.show_view(self.root, mode)

    @staticmethod
    def _html():
        # HTML reste défini dans ui_app.py ; cet import différé évite sa copie.
        from ui_app import HTML

        return HTML
