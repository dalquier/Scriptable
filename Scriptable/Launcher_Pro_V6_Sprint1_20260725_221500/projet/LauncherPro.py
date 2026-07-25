from __future__ import annotations


def main() -> None:
    try:
        from ui.main_view import present_launcher
    except Exception as exc:
        print("Interface Pyto indisponible, ouverture du mode console.")
        print(f"Détail : {exc}")
        from console_app import main as console_main

        console_main()
        return

    present_launcher()


if __name__ == "__main__":
    main()
