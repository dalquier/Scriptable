import hashlib
import json
from pathlib import Path
from typing import Dict, Iterable, List


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_excluded(relative: Path, excluded: Iterable[str]) -> bool:
    text = relative.as_posix()
    return any(text == item or text.startswith(item.rstrip("/") + "/") for item in excluded)


def build_index(
    root: Path,
    include_extensions: Iterable[str],
    exclude_directories: Iterable[str],
) -> Dict[str, object]:
    extensions = {ext.lower() for ext in include_extensions}
    files: List[Dict[str, object]] = []

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if _is_excluded(relative, exclude_directories):
            continue
        if path.suffix.lower() not in extensions:
            continue
        try:
            size = path.stat().st_size
            digest = _sha256(path)
        except OSError:
            continue
        files.append(
            {
                "path": relative.as_posix(),
                "size": size,
                "sha256": digest,
            }
        )

    return {
        "root": str(root),
        "file_count": len(files),
        "files": files,
    }


def save_index(path: Path, index: Dict[str, object]) -> None:
    path.write_text(
        json.dumps(index, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
