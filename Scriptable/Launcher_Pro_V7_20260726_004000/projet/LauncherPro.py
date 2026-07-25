from __future__ import annotations


def main() -> None:
    try:
        from ui.main_view import present_launcher
    except Exception as exc:
        print("Impossible de charger l’interface Launcher Pro V7.")
        print(exc)
        return
    present_launcher()


if __name__ == "__main__":
    main()
