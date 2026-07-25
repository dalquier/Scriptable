from __future__ import annotations


def main() -> None:
    print("=== TEST LAUNCHER PRO V6 — SPRINT 2 ===")
    import pyto_ui  # noqa: F401
    from core.registry import Registry
    from ui.main_view import LauncherProView

    registry = Registry.load()
    app = LauncherProView()
    assert app.registry is not None
    assert len(app.registry.scripts) == len(registry.scripts)
    assert app.view is not None
    assert app.scroll is not None
    print("Import pyto_ui : OK")
    print("Chargement du registre : OK")
    print("Construction de la vue : OK")
    print("Nombre de scripts :", len(registry.scripts))
    print("=== SPRINT 2 — INTERFACE CONSTRUITE ===")
    print("Lance maintenant LauncherPro.py pour le test visuel.")


if __name__ == "__main__":
    main()
