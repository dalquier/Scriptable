from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from ppx_config import (
    EXCLUDED_DIR_NAMES,
    EXCLUDED_FILE_NAMES,
    FILE_BEGIN,
    FILE_END,
    FORMAT_VERSION,
    INDEX_FILENAME,
    MAX_FRAGMENT_CHARACTERS,
    PART_PREFIX,
    PART_SUFFIX,
    TARGET_PART_CHARACTERS,
    TEXT_EXTENSIONS,
)
from ppx_utils import encode_base64, json_dumps, read_bytes, sha256_bytes, sha256_text, split_text


class ExportError(Exception):
    pass


def _iter_project_files(root: Path):
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in EXCLUDED_DIR_NAMES for part in relative.parts[:-1]):
            continue
        if path.name in EXCLUDED_FILE_NAMES:
            continue
        yield path, relative.as_posix()


def _encode_file(path: Path):
    raw = read_bytes(path)
    suffix = path.suffix.lower()
    if suffix in TEXT_EXTENSIONS or path.name == ".gitignore":
        try:
            return "utf-8", raw.decode("utf-8"), raw
        except UnicodeDecodeError:
            pass
    return "base64", encode_base64(raw), raw


def _fragment_block(path: str, encoding: str, file_sha: str, chunk_index: int, chunk_count: int, payload: str) -> str:
    header = {
        "path": path,
        "encoding": encoding,
        "sha256": file_sha,
        "chunk_index": chunk_index,
        "chunk_count": chunk_count,
    }
    return (
        f"{FILE_BEGIN}\n"
        f"{json_dumps(header)}\n"
        f"PYTO_CONTENT_BEGIN\n"
        f"{payload}\n"
        f"PYTO_CONTENT_END\n"
        f"{FILE_END}\n"
    )


def export_project(project_folder: str, destination_folder: str) -> dict:
    root = Path(project_folder).expanduser().resolve()
    destination = Path(destination_folder).expanduser().resolve()
    if not root.is_dir():
        raise ExportError("Le dossier projet sélectionné n'existe pas.")
    if destination == root or root in destination.parents:
        raise ExportError("Le dossier de sortie ne doit pas être situé dans le projet exporté.")

    project_name = root.name or "Projet_Pyto"
    output = destination / f"{project_name}__PYTO_EXCHANGE_V5"
    output.mkdir(parents=True, exist_ok=True)

    files = []
    blocks = []
    for path, relative in _iter_project_files(root):
        encoding, encoded, raw = _encode_file(path)
        fragments = split_text(encoded, MAX_FRAGMENT_CHARACTERS)
        file_sha = sha256_bytes(raw)
        files.append({
            "path": relative,
            "encoding": encoding,
            "size_bytes": len(raw),
            "sha256": file_sha,
            "chunk_count": len(fragments),
        })
        for index, payload in enumerate(fragments, start=1):
            blocks.append(_fragment_block(relative, encoding, file_sha, index, len(fragments), payload))

    if not files:
        raise ExportError("Aucun fichier exportable n'a été trouvé.")

    parts = []
    current = []
    current_size = 0
    for block in blocks:
        if current and current_size + len(block) > TARGET_PART_CHARACTERS:
            parts.append("\n".join(current))
            current = []
            current_size = 0
        current.append(block)
        current_size += len(block)
    if current:
        parts.append("\n".join(current))

    part_entries = []
    for number, body in enumerate(parts, start=1):
        filename = f"{PART_PREFIX}{number:03d}{PART_SUFFIX}"
        document = (
            f"<!-- PYTO_PROJECT_EXCHANGE:{FORMAT_VERSION} -->\n"
            f"# Partie {number:03d}/{len(parts):03d}\n\n"
            f"{body}"
        )
        (output / filename).write_text(document, encoding="utf-8")
        part_entries.append({
            "filename": filename,
            "sha256": sha256_text(document),
            "character_count": len(document),
        })

    project_hash_source = "\n".join(f"{entry['path']}:{entry['sha256']}" for entry in files)
    index = {
        "protocol": "PYTO_PROJECT_EXCHANGE",
        "version": FORMAT_VERSION,
        "project_name": project_name,
        "project_uuid": str(uuid4()),
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "mode": "FULL",
        "part_count": len(parts),
        "file_count": len(files),
        "fragment_count": len(blocks),
        "project_sha256": sha256_text(project_hash_source),
        "parts": part_entries,
        "files": files,
    }
    index_text = (
        f"<!-- PYTO_PROJECT_EXCHANGE:{FORMAT_VERSION} -->\n"
        f"# Index canonique\n\n"
        f"```json\n{json_dumps(index)}\n```\n"
    )
    (output / INDEX_FILENAME).write_text(index_text, encoding="utf-8")

    return {
        "output_folder": str(output),
        "project_name": project_name,
        "file_count": len(files),
        "fragment_count": len(blocks),
        "part_count": len(parts),
    }
