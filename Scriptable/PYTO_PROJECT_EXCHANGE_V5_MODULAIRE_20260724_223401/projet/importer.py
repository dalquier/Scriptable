from __future__ import annotations

import json
import re
from pathlib import Path

from config import FILE_BEGIN, FILE_END, INDEX_FILENAME, PART_PREFIX, PART_SUFFIX
from utils import decode_base64, safe_join, sha256_bytes, write_bytes


class ImportErrorExchange(Exception):
    pass


def _extract_json_code_block(text: str) -> dict:
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if not match:
        raise ImportErrorExchange("Le bloc JSON de 00_INDEX.md est introuvable.")
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise ImportErrorExchange(f"Index JSON invalide : {exc}") from exc


def _parse_blocks(text: str) -> list[dict]:
    pattern = re.compile(
        rf"{re.escape(FILE_BEGIN)}\s*\n"
        r"(\{.*?\})\s*\n"
        r"PYTO_CONTENT_BEGIN\s*\n"
        r"(.*?)\n"
        r"PYTO_CONTENT_END\s*\n"
        rf"{re.escape(FILE_END)}",
        flags=re.DOTALL,
    )
    blocks = []
    for metadata_text, payload in pattern.findall(text):
        try:
            metadata = json.loads(metadata_text)
        except json.JSONDecodeError as exc:
            raise ImportErrorExchange(f"Métadonnées de fragment invalides : {exc}") from exc
        metadata["payload"] = payload
        blocks.append(metadata)
    return blocks


def import_exchange(exchange_folder: str, destination_folder: str) -> dict:
    source = Path(exchange_folder).expanduser().resolve()
    destination = Path(destination_folder).expanduser().resolve()
    index_path = source / INDEX_FILENAME
    if not index_path.is_file():
        raise ImportErrorExchange("00_INDEX.md est absent du lot sélectionné.")

    index = _extract_json_code_block(index_path.read_text(encoding="utf-8"))
    part_count = index.get("part_count")
    project_name = index.get("project_name") or "Projet_Importe"
    if not isinstance(part_count, int) or part_count < 1:
        raise ImportErrorExchange("Le champ part_count est invalide.")

    fragments_by_path: dict[str, list[dict]] = {}
    for number in range(1, part_count + 1):
        filename = f"{PART_PREFIX}{number:03d}{PART_SUFFIX}"
        part_path = source / filename
        if not part_path.is_file():
            raise ImportErrorExchange(f"Partie attendue absente : {filename}")
        for block in _parse_blocks(part_path.read_text(encoding="utf-8")):
            path = block.get("path")
            if not isinstance(path, str):
                raise ImportErrorExchange(f"Fragment sans chemin valide dans {filename}.")
            fragments_by_path.setdefault(path, []).append(block)

    output = destination / f"{project_name}__IMPORTE_V5"
    if output.exists():
        suffix = 2
        while (destination / f"{project_name}__IMPORTE_V5_{suffix}").exists():
            suffix += 1
        output = destination / f"{project_name}__IMPORTE_V5_{suffix}"
    output.mkdir(parents=True, exist_ok=False)

    reconstructed = 0
    try:
        for file_entry in index.get("files", []):
            relative = file_entry.get("path")
            expected_count = file_entry.get("chunk_count")
            encoding = file_entry.get("encoding")
            expected_sha = file_entry.get("sha256")
            chunks = fragments_by_path.get(relative, [])
            chunks.sort(key=lambda item: item.get("chunk_index", 0))
            if not isinstance(expected_count, int) or len(chunks) != expected_count:
                raise ImportErrorExchange(f"Fragments incomplets pour {relative}.")
            for position, chunk in enumerate(chunks, start=1):
                if chunk.get("chunk_index") != position or chunk.get("chunk_count") != expected_count:
                    raise ImportErrorExchange(f"Ordre de fragments invalide pour {relative}.")
            merged = "".join(chunk["payload"] for chunk in chunks)
            if encoding == "utf-8":
                raw = merged.encode("utf-8")
            elif encoding == "base64":
                raw = decode_base64(merged)
            else:
                raise ImportErrorExchange(f"Encodage inconnu pour {relative} : {encoding}")
            if expected_sha and sha256_bytes(raw) != expected_sha:
                raise ImportErrorExchange(f"Empreinte SHA-256 invalide pour {relative}.")
            target = safe_join(output, relative)
            write_bytes(target, raw)
            reconstructed += 1
    except Exception:
        for path in sorted(output.rglob("*"), reverse=True):
            if path.is_file() or path.is_symlink():
                path.unlink(missing_ok=True)
            elif path.is_dir():
                path.rmdir()
        output.rmdir()
        raise

    return {
        "output_folder": str(output),
        "project_name": project_name,
        "file_count": reconstructed,
        "part_count": part_count,
    }
