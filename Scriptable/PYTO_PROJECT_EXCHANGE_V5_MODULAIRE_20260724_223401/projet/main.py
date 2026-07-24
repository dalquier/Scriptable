from __future__ import annotations

from time import sleep

from ui_app import MainUI


# Référence globale indispensable sous Pyto : elle empêche l'interface,
# son contrôleur et les callbacks des boutons d'être libérés après main().
APP = None


def main():
    global APP

    APP = MainUI()
    APP.present()

    # pyto_ui.show_view() rend la main immédiatement. Le script doit donc
    # rester actif tant que la feuille est affichée, sinon les actions des
    # boutons ne sont plus exécutées et la console revient à l'invite >>>.
    sleep(0.25)
    native_view = getattr(APP.view, "__py_view__", None)

    try:
        while native_view is not None and bool(getattr(native_view, "isPresented", False)):
            sleep(0.20)
    except KeyboardInterrupt:
        # Permet d'arrêter proprement le script depuis Pyto.
        pass


if __name__ == "__main__":
    main()
