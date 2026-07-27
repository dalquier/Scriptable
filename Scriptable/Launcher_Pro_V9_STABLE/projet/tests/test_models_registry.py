"""Tests du modèle et du registre persistant."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from core.models import LauncherItem
from core.registry import Registry, RegistryError


class LauncherItemTests(unittest.TestCase):
    def test_round_trip_preserves_item(self) -> None:
        item = LauncherItem.create_project("Démo", "/tmp/demo", "main.py", "/source")
        self.assertEqual(LauncherItem.from_dict(item.to_dict()), item)

    def test_project_requires_entrypoint(self) -> None:
        with self.assertRaises(ValueError):
            LauncherItem.create_project("Démo", "/tmp/demo", "")


class RegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.path = Path(self.temporary.name) / "nested" / "registry.json"
        self.registry = Registry.load(self.path)
        self.item = LauncherItem.create_script("Démo", "/tmp/demo.py")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_crud_favorite_and_search_are_persistent(self) -> None:
        self.registry.add(self.item)
        self.item.favorite = True
        self.item.name = "Nouveau nom"
        self.registry.update(self.item)
        loaded = Registry.load(self.path)
        self.assertTrue(loaded.require(self.item.id).favorite)
        self.assertEqual(loaded.search("nouveau")[0].id, self.item.id)
        loaded.remove(self.item.id)
        self.assertEqual(Registry.load(self.path).all(), [])

    def test_invalid_json_has_domain_error(self) -> None:
        self.path.write_text("{broken", encoding="utf-8")
        with self.assertRaisesRegex(RegistryError, "JSON illisible"):
            Registry.load(self.path)

    def test_unknown_schema_is_rejected(self) -> None:
        self.path.write_text(json.dumps({"schema_version": 99, "items": []}), encoding="utf-8")
        with self.assertRaisesRegex(RegistryError, "[Vv]ersion"):
            Registry.load(self.path)


if __name__ == "__main__":
    unittest.main()
