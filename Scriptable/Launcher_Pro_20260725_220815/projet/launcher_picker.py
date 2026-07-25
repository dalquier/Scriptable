from __future__ import annotations

import os
import shutil
import uuid
from launcher_storage import SCRIPTS_DIR, ensure_layout


def _pick_with_pyto() -> str | None:
    import file_system
    candidates = ("pick_document", "import_file", "pick_file")
    last_error = None
    for name in candidates:
        fn = getattr(file_system, name, None)
        if not callable(fn):
            continue
        try:
            result = fn()
            if isinstance(result, (list, tuple)):
                result = result[0] if result else None
            if result:
                return os.fspath(result)
        except TypeError as exc:
            last_error = exc
            try:
                result = fn(["public.python-script", "public.text"])
                if isinstance(result, (list, tuple)):
                    result = result[0] if result else None
                if result:
                    return os.fspath(result)
            except Exception as nested:
                last_error = nested
        except Exception as exc:
            last_error = exc
    if last_error:
        raise RuntimeError(f"Sélecteur Pyto indisponible : {last_error}")
    raise RuntimeError("Aucune fonction de sélection de fichier reconnue dans cette version de Pyto.")


def import_python_file() -> tuple[str, str]:
    ensure_layout()
    source = _pick_with_pyto()
    if not source:
        raise RuntimeError("Sélection annulée")
    if not source.lower().endswith(".py"):
        raise ValueError("Le fichier sélectionné doit avoir l’extension .py")
    if not os.path.isfile(source):
        raise FileNotFoundError(source)
    stem = os.path.splitext(os.path.basename(source))[0]
    destination = os.path.join(SCRIPTS_DIR, f"{stem}_{uuid.uuid4().hex[:8]}.py")
    shutil.copy2(source, destination)
    return source, destination
