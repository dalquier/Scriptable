from __future__ import annotations

import ast
import shutil
from pathlib import Path
from typing import Optional

from .logger import log
from .models import ScriptEntry
from .paths import SCRIPTS_DIR, ensure_directories
from .registry import Registry
from .settings import load_settings


def validate_python_file(path: str | Path) -> Path:
    source = Path(path).expanduser().resolve()
    if not source.exists() or not source.is_file():
        raise FileNotFoundError(f"Fichier introuvable : {source}")
    if source.suffix.lower() != ".py":
        raise ValueError("Le fichier sélectionné doit avoir l'extension .py")
    text = source.read_text(encoding="utf-8-sig", errors="strict")
    ast.parse(text, filename=str(source))
    return source


def import_script(
    path: str | Path,
    name: Optional[str] = None,
    category: Optional[str] = None,
    registry: Optional[Registry] = None,
) -> ScriptEntry:
    ensure_directories()
    source = validate_python_file(path)
    settings = load_settings()
    entry_name = (name or source.stem).strip()
    if not entry_name:
        raise ValueError("Le nom du script ne peut pas être vide")

    entry = ScriptEntry.create(
        entry_name,
        "",
        str(source) if settings.get("keep_source_path", True) else "",
    )
    entry.category = (
        category or settings.get("default_category", "Général")
    ).strip() or "Général"

    target = SCRIPTS_DIR / f"{entry.id}_{source.name}"
    shutil.copy2(source, target)
    entry.local_path = str(target)

    active_registry = registry or Registry.load()
    try:
        active_registry.add(entry)
    except Exception:
        target.unlink(missing_ok=True)
        raise

    log(f"Script importé : {entry.name} depuis {source}")
    return entry


def pick_python_file() -> str:
    """Sélectionne un script Python avec l'API officielle de Pyto.

    La sélection directe filtre explicitement l'extension ``py``. Si le
    fournisseur iOS refuse ce type de fichier, l'appelant peut utiliser
    ``pick_python_file_from_directory`` comme solution de secours.
    """
    try:
        import file_system  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Le sélecteur iOS nécessite Pyto et son module file_system"
        ) from exc

    importer = getattr(file_system, "import_file", None)
    if not callable(importer):
        raise RuntimeError("Cette version de Pyto ne fournit pas file_system.import_file")

    attempts = (
        {"multiple_selection": False, "file_extension": "py"},
        {"multiple_selection": False, "type_identifier": "public.python-script"},
        {"multiple_selection": False, "type_identifier": "public.source-code"},
        {"multiple_selection": False},
    )
    last_error: Optional[Exception] = None

    for kwargs in attempts:
        try:
            result = importer(**kwargs)
            if isinstance(result, (list, tuple)):
                result = result[0] if result else None
            if result:
                return str(validate_python_file(result))
        except Exception as exc:
            last_error = exc

    if last_error:
        raise RuntimeError(f"Sélection impossible : {last_error}") from last_error
    raise RuntimeError("Aucun fichier Python n'a été sélectionné")


def list_python_files(directory: str | Path, recursive: bool = True) -> list[Path]:
    root = Path(directory).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise NotADirectoryError(f"Dossier introuvable : {root}")
    pattern = "**/*.py" if recursive else "*.py"
    return sorted(
        (path for path in root.glob(pattern) if path.is_file()),
        key=lambda path: (path.name.lower(), str(path).lower()),
    )


def pick_python_file_from_directory() -> list[Path]:
    """Ouvre le sélecteur de dossier et renvoie les scripts détectés."""
    try:
        import file_system  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Le sélecteur iOS nécessite Pyto et son module file_system"
        ) from exc

    picker = getattr(file_system, "pick_directory", None)
    if not callable(picker):
        raise RuntimeError("Cette version de Pyto ne permet pas de choisir un dossier")

    directory = picker()
    files = list_python_files(directory, recursive=True)
    if not files:
        raise FileNotFoundError("Aucun fichier .py trouvé dans le dossier sélectionné")
    return files
