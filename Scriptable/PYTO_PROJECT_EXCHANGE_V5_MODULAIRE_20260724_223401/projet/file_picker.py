from __future__ import annotations

from pathlib import Path


def _normalize_selection(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        if not value:
            return None
        value = value[0]
    text = str(value).strip()
    return text or None


def pick_directory(title: str) -> str | None:
    try:
        import pyto_ui as ui
    except ImportError as exc:
        raise RuntimeError("Le module pyto_ui est indisponible. Lancez le projet dans Pyto.") from exc

    function = getattr(ui, "pick_directory", None)
    if callable(function):
        try:
            return _normalize_selection(function(title=title))
        except TypeError:
            return _normalize_selection(function())

    function = getattr(ui, "pick_document", None)
    if callable(function):
        try:
            selected = _normalize_selection(function(types=["public.folder"]))
        except TypeError:
            selected = _normalize_selection(function())
        if selected:
            path = Path(selected)
            return str(path if path.is_dir() else path.parent)

    raise RuntimeError("Aucun sélecteur de dossier compatible n'a été trouvé dans cette version de Pyto.")
