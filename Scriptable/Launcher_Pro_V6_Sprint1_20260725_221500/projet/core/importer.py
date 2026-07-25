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
    text = source.read_text(encoding="utf-8", errors="strict")
    ast.parse(text, filename=str(source))
    return source


def import_script(path: str | Path, name: Optional[str] = None, category: Optional[str] = None, registry: Optional[Registry] = None) -> ScriptEntry:
    ensure_directories()
    source = validate_python_file(path)
    settings = load_settings()
    entry_name = (name or source.stem).strip()
    if not entry_name:
        raise ValueError("Le nom du script ne peut pas être vide")
    entry = ScriptEntry.create(entry_name, "", str(source) if settings.get("keep_source_path", True) else "")
    entry.category = (category or settings.get("default_category", "Général")).strip() or "Général"
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
    try:
        import file_system  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Le sélecteur iOS nécessite Pyto et son module file_system") from exc

    candidates = ("pick_document", "import_file", "pick_file")
    last_error: Optional[Exception] = None
    for name in candidates:
        picker = getattr(file_system, name, None)
        if picker is None:
            continue
        try:
            result = picker()
            if isinstance(result, (list, tuple)):
                result = result[0] if result else None
            if result:
                return str(result)
        except Exception as exc:
            last_error = exc
    if last_error:
        raise RuntimeError(f"Sélection impossible : {last_error}") from last_error
    raise RuntimeError("Aucune fonction de sélection compatible n'a été trouvée dans cette version de Pyto")
