import base64
import hashlib
import json
import os
from pathlib import Path


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def read_bytes(path: Path) -> bytes:
    with path.open("rb") as handle:
        return handle.read()


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        handle.write(data)


def is_safe_relative_path(value: str) -> bool:
    if not value or os.path.isabs(value):
        return False
    normalized = value.replace("\\", "/")
    parts = [part for part in normalized.split("/") if part]
    return bool(parts) and all(part not in {".", ".."} for part in parts)


def safe_join(root: Path, relative: str) -> Path:
    if not is_safe_relative_path(relative):
        raise ValueError(f"Chemin non sûr : {relative}")
    candidate = (root / relative).resolve()
    root_resolved = root.resolve()
    if root_resolved != candidate and root_resolved not in candidate.parents:
        raise ValueError(f"Chemin hors racine : {relative}")
    return candidate


def json_dumps(data) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False)


def encode_base64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def decode_base64(text: str) -> bytes:
    return base64.b64decode(text.encode("ascii"), validate=True)


def split_text(text: str, limit: int) -> list[str]:
    if limit <= 0:
        raise ValueError("La limite doit être positive.")
    if not text:
        return [""]
    return [text[index:index + limit] for index in range(0, len(text), limit)]
