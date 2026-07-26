"""Entrypoint detection without any UI dependency."""

import ast
from pathlib import Path
from typing import Iterable, List


class ImportValidationError(ValueError):
    """Raised when an imported path cannot be launched."""


class EntrypointDetector:
    PRIORITY = ("__main__.py", "main.py", "app.py", "run.py", "launcher.py")
    IGNORED_PARTS = {".git", ".venv", "venv", "__pycache__", "site-packages", "tests"}

    def detect_script(self, path: Path) -> Path:
        path = Path(path).expanduser()
        if not path.is_file() or path.suffix.lower() != ".py":
            raise ImportValidationError("Sélectionnez un fichier Python .py valide.")
        self._validate_python(path)
        return path.resolve()

    def detect_project(self, path: Path) -> Path:
        root = Path(path).expanduser()
        if not root.is_dir():
            raise ImportValidationError("Sélectionnez un dossier de projet valide.")
        for name in self.PRIORITY:
            candidate = root / name
            if candidate.is_file():
                self._validate_python(candidate)
                return candidate.resolve()
        candidates = list(self._python_files(root))
        for name in self.PRIORITY:
            named = [candidate for candidate in candidates if candidate.name == name]
            if named:
                selected = sorted(named, key=lambda item: (len(item.relative_to(root).parts), str(item)))[0]
                self._validate_python(selected)
                return selected.resolve()
        guarded = [candidate for candidate in candidates if self._has_main_guard(candidate)]
        if guarded:
            selected = sorted(guarded, key=lambda item: (len(item.relative_to(root).parts), str(item)))[0]
            self._validate_python(selected)
            return selected.resolve()
        if len(candidates) == 1:
            self._validate_python(candidates[0])
            return candidates[0].resolve()
        raise ImportValidationError(
            "Aucun point d'entrée détecté. Ajoutez __main__.py, main.py, app.py, run.py "
            "ou un bloc if __name__ == '__main__'."
        )

    def _python_files(self, root: Path) -> Iterable[Path]:
        for candidate in root.rglob("*.py"):
            relative = candidate.relative_to(root)
            if not any(part in self.IGNORED_PARTS or part.startswith(".") for part in relative.parts):
                yield candidate

    @staticmethod
    def _validate_python(path: Path) -> None:
        try:
            ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        except (OSError, UnicodeError) as exc:
            raise ImportValidationError("Impossible de lire le point d'entrée : {}".format(exc)) from exc
        except SyntaxError as exc:
            raise ImportValidationError("Syntaxe Python invalide à la ligne {} : {}".format(exc.lineno, exc.msg)) from exc

    @staticmethod
    def _has_main_guard(path: Path) -> bool:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        except (OSError, UnicodeError, SyntaxError):
            return False
        for node in ast.walk(tree):
            if not isinstance(node, ast.If) or not isinstance(node.test, ast.Compare):
                continue
            test = node.test
            if (isinstance(test.left, ast.Name) and test.left.id == "__name__" and
                    len(test.ops) == 1 and isinstance(test.ops[0], ast.Eq) and
                    len(test.comparators) == 1 and isinstance(test.comparators[0], ast.Constant) and
                    test.comparators[0].value == "__main__"):
                return True
        return False
