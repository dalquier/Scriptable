"""Tests de validation, détection et copie des imports."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.importer import (
    ImporterError,
    detect_entry_point,
    import_project,
    import_script,
    validate_python_file,
)


class ImporterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_invalid_script_is_rejected(self) -> None:
        script = self.root / "broken.py"
        script.write_text("def broken(:", encoding="utf-8")
        with self.assertRaises(ImporterError):
            validate_python_file(script)

    def test_script_is_copied(self) -> None:
        source = self.root / "hello.py"
        source.write_text("print('ok')", encoding="utf-8")
        target = self.root / "scripts"
        with patch("core.importer.SCRIPTS_DIR", target):
            item = import_script(source)
        self.assertEqual(Path(item.local_path).read_text(encoding="utf-8"), "print('ok')")

    def test_project_entrypoint_is_detected_and_project_is_copied(self) -> None:
        project = self.root / "source"
        (project / "src").mkdir(parents=True)
        (project / "src" / "main.py").write_text("print('ok')", encoding="utf-8")
        (project / "src" / "helper.py").write_text("VALUE = 1", encoding="utf-8")
        (project / "__pycache__").mkdir()
        (project / "__pycache__" / "main.pyc").touch()
        entrypoint = detect_entry_point(project)
        with patch("core.importer.PROJECTS_DIR", self.root / "projects"):
            item = import_project(project, entrypoint)
        self.assertEqual(item.entry_script, "src/main.py")
        self.assertTrue((Path(item.local_path) / item.entry_script).is_file())
        self.assertFalse((Path(item.local_path) / "__pycache__").exists())

    def test_ambiguous_project_requires_selection(self) -> None:
        (self.root / "one.py").write_text("pass", encoding="utf-8")
        (self.root / "two.py").write_text("pass", encoding="utf-8")
        with self.assertRaisesRegex(ImporterError, "ambigu"):
            detect_entry_point(self.root)


if __name__ == "__main__":
    unittest.main()
