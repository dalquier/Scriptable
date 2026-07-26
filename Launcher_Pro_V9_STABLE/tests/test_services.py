import tempfile
import unittest
from pathlib import Path

from launcher_pro.registry import ItemKind
from launcher_pro.services import EntrypointDetector, ImportService, ImportValidationError


class ImportServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.service = ImportService()

    def tearDown(self):
        self.temp.cleanup()

    def test_import_script(self):
        script = self.root / "hello.py"
        script.write_text("print('hello')", encoding="utf-8")
        item = self.service.script(script)
        self.assertEqual(item.kind, ItemKind.SCRIPT)
        self.assertEqual(Path(item.entrypoint), script)

    def test_project_prefers_named_entrypoint(self):
        (self.root / "other.py").write_text("pass", encoding="utf-8")
        main = self.root / "main.py"
        main.write_text("pass", encoding="utf-8")
        self.assertEqual(self.service.project(self.root).entrypoint, str(main))

    def test_project_finds_main_guard(self):
        package = self.root / "src"
        package.mkdir()
        app = package / "cli.py"
        app.write_text("if __name__ == '__main__':\n    print('ok')\n", encoding="utf-8")
        self.assertEqual(EntrypointDetector().detect_project(self.root), app)

    def test_ambiguous_project_is_rejected(self):
        (self.root / "a.py").write_text("pass", encoding="utf-8")
        (self.root / "b.py").write_text("pass", encoding="utf-8")
        with self.assertRaises(ImportValidationError):
            self.service.project(self.root)


if __name__ == "__main__":
    unittest.main()


class ManagedImportTests(unittest.TestCase):
    def test_script_is_copied_to_managed_storage(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.py"
            source.write_text("print('durable')", encoding="utf-8")
            item = ImportService(storage_root=root / "managed").script(source)
            source.unlink()
            self.assertEqual(Path(item.entrypoint).read_text(encoding="utf-8"), "print('durable')")

    def test_project_is_copied_and_junk_is_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "demo"
            project.mkdir()
            (project / "main.py").write_text("pass", encoding="utf-8")
            (project / "__pycache__").mkdir()
            (project / "__pycache__" / "main.pyc").touch()
            item = ImportService(storage_root=root / "managed").project(project)
            self.assertTrue(Path(item.entrypoint).is_file())
            self.assertFalse((Path(item.source_path) / "__pycache__").exists())


class ImportValidationTests(unittest.TestCase):
    def test_invalid_python_is_rejected_before_registration(self):
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "broken.py"
            script.write_text("def broken(:\n", encoding="utf-8")
            with self.assertRaisesRegex(ImportValidationError, "Syntaxe Python invalide"):
                ImportService().script(script)

    def test_utf8_bom_script_is_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "bom.py"
            script.write_bytes(b"\xef\xbb\xbfprint('ok')\n")
            self.assertEqual(Path(ImportService().script(script).entrypoint), script)


class NestedEntrypointTests(unittest.TestCase):
    def test_nested_src_main_is_detected_among_multiple_modules(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "src"
            source.mkdir()
            main = source / "main.py"
            main.write_text("print('main')", encoding="utf-8")
            (source / "helpers.py").write_text("VALUE = 1", encoding="utf-8")
            self.assertEqual(EntrypointDetector().detect_project(root), main)
