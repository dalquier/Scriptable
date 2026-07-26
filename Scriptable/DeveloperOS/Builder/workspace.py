import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List


class WorkspaceError(Exception):
    pass


class Workspace:
    def __init__(self, project_root: Path, builder_root: Path) -> None:
        self.project_root = project_root.resolve()
        self.builder_root = builder_root.resolve()
        self.backup_root = self.builder_root / "backups"

    def _resolve_safe(self, relative_path: str) -> Path:
        candidate = (self.project_root / relative_path).resolve()
        try:
            candidate.relative_to(self.project_root)
        except ValueError as exc:
            raise WorkspaceError(f"Chemin interdit: {relative_path}") from exc
        if candidate == self.builder_root or self.builder_root in candidate.parents:
            raise WorkspaceError("Le Builder ne peut pas se réécrire lui-même en v0.1")
        return candidate

    def read_text(self, relative_path: str) -> str:
        path = self._resolve_safe(relative_path)
        return path.read_text(encoding="utf-8")

    def collect_context(self, paths: Iterable[str], max_chars: int = 40000) -> str:
        chunks: List[str] = []
        used = 0
        for relative_path in paths:
            try:
                content = self.read_text(relative_path)
            except (OSError, UnicodeDecodeError, WorkspaceError):
                continue
            block = f"\n--- FILE: {relative_path} ---\n{content}\n"
            if used + len(block) > max_chars:
                break
            chunks.append(block)
            used += len(block)
        return "".join(chunks)

    def apply_changes(self, changes: Iterable[Dict[str, str]], backup: bool = True) -> List[str]:
        written: List[str] = []
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        for change in changes:
            relative_path = str(change.get("path", "")).strip()
            content = change.get("content")
            if not relative_path or not isinstance(content, str):
                raise WorkspaceError("Modification invalide")
            path = self._resolve_safe(relative_path)
            if backup and path.exists():
                destination = self.backup_root / stamp / relative_path
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, destination)
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(path.suffix + ".tmp")
            tmp.write_text(content, encoding="utf-8")
            tmp.replace(path)
            written.append(relative_path)
        return written
