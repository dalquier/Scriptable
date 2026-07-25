from __future__ import annotations

from core.url_scheme import item_id_from_argv, run_by_id


def main() -> None:
    item_id = item_id_from_argv()
    if item_id:
        item, result = run_by_id(item_id)
        if result.output:
            print(result.output, end="")
        if not result.success:
            raise RuntimeError(result.error or f"Échec de {item.name}")
        return

    try:
        from ui.main_view import present_launcher
    except Exception as exc:
        print("Impossible de charger l’interface Launcher Pro V7.")
        print(exc)
        return
    present_launcher()


if __name__ == "__main__":
    main()
