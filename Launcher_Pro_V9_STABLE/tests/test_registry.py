import tempfile
import unittest
from pathlib import Path

from launcher_pro.registry import ItemKind, LibraryItem, LibraryRegistry, RegistryError


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.registry = LibraryRegistry(Path(self.temp.name) / "library.json")
        script = Path(self.temp.name) / "hello.py"
        script.touch()
        self.item = LibraryItem.create("Hello", ItemKind.SCRIPT, script, script)

    def tearDown(self):
        self.temp.cleanup()

    def test_lifecycle_is_persistent(self):
        self.registry.add(self.item)
        self.assertEqual(self.registry.all()[0].name, "Hello")
        self.assertTrue(self.registry.toggle_favorite(self.item.id).favorite)
        self.assertEqual(self.registry.rename(self.item.id, "World").name, "World")
        self.registry.remove(self.item.id)
        self.assertEqual(self.registry.all(), [])

    def test_duplicate_entrypoint_is_rejected(self):
        self.registry.add(self.item)
        duplicate = LibraryItem.create("Copy", ItemKind.SCRIPT, Path(self.item.source_path), Path(self.item.entrypoint))
        with self.assertRaises(RegistryError):
            self.registry.add(duplicate)


if __name__ == "__main__":
    unittest.main()
