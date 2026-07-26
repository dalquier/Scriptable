from __future__ import annotations

from .history import append_history
from .registry import Registry
from .runner import run_item


def run_by_id(item_id: str):
    registry = Registry.load()
    item = registry.require(item_id)
    result = run_item(item)
    registry.update(item)
    append_history(item, result)
    return item, result


def rename_item(item_id: str, new_name: str):
    registry = Registry.load()
    item = registry.require(item_id)
    name = new_name.strip()
    if not name:
        raise ValueError("Le nom ne peut pas être vide")
    item.name = name
    registry.update(item)
    return item
