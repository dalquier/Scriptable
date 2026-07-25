from __future__ import annotations

import json
import os
import tempfile
from launcher_core import Registry

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SCRIPTS_DIR = os.path.join(DATA_DIR, "scripts")
REGISTRY_PATH = os.path.join(DATA_DIR, "registry.json")


def ensure_layout() -> None:
    os.makedirs(SCRIPTS_DIR, exist_ok=True)
    if not os.path.exists(REGISTRY_PATH):
        save_registry(Registry())


def load_registry() -> Registry:
    ensure_layout()
    try:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as handle:
            return Registry.from_dict(json.load(handle))
    except Exception:
        backup = REGISTRY_PATH + ".corrupt"
        try:
            os.replace(REGISTRY_PATH, backup)
        except OSError:
            pass
        registry = Registry()
        save_registry(registry)
        return registry


def save_registry(registry: Registry) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix="registry_", suffix=".json", dir=DATA_DIR)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(registry.to_dict(), handle, ensure_ascii=False, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, REGISTRY_PATH)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
