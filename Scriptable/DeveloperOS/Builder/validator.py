import ast
from pathlib import Path
from typing import Iterable, List, Tuple


def validate_python_files(root: Path, paths: Iterable[str]) -> List[Tuple[str, str]]:
    errors: List[Tuple[str, str]] = []
    for relative_path in paths:
        if not relative_path.endswith(".py"):
            continue
        path = root / relative_path
        try:
            source = path.read_text(encoding="utf-8")
            ast.parse(source, filename=str(path))
        except (OSError, UnicodeDecodeError, SyntaxError) as exc:
            errors.append((relative_path, str(exc)))
    return errors
