from __future__ import annotations

from core.url_scheme import item_id_from_argv, run_by_id


def main() -> None:
    item_id = item_id_from_argv()
    if not item_id:
        raise SystemExit("Identifiant Launcher Pro manquant")

    item, result = run_by_id(item_id)
    if result.output:
        print(result.output, end="")
    if not result.success:
        raise RuntimeError(result.error or f"Échec de {item.name}")


if __name__ == "__main__":
    main()
