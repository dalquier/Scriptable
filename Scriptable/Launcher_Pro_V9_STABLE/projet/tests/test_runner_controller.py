"""Tests du moteur, du service et du contrôleur central."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from controller import Action, LauncherController
from core.history import HistoryJournal
from core.library_service import LibraryService
from core.models import LauncherItem
from core.registry import Registry
from core.runner import execute_item


class RunnerTests(unittest.TestCase):
    def test_script_restores_complete_python_environment(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = root / "run.py"
            script.write_text("import pathlib\npathlib.Path('done').write_text('ok')", encoding="utf-8")
            item = LauncherItem.create_script("Run", str(script))
            old_cwd = Path.cwd()
            old_path = list(sys.path)
            old_argv = list(sys.argv)
            old_main = sys.modules.get("__main__")
            result = execute_item(item)
            self.assertTrue(result.success)
            self.assertEqual((root / "done").read_text(encoding="utf-8"), "ok")
            self.assertEqual(Path.cwd(), old_cwd)
            self.assertEqual(sys.path, old_path)
            self.assertEqual(sys.argv, old_argv)
            self.assertIs(sys.modules.get("__main__"), old_main)

    def test_project_uses_project_as_working_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project / "helper.py").write_text("VALUE = 'project'", encoding="utf-8")
            (project / "main.py").write_text(
                "from helper import VALUE\nfrom pathlib import Path\nPath('result').write_text(VALUE)",
                encoding="utf-8",
            )
            item = LauncherItem.create_project("Project", str(project), "main.py")
            self.assertTrue(execute_item(item).success)
            self.assertEqual((project / "result").read_text(encoding="utf-8"), "project")


class ServiceControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.service = LibraryService(
            Registry.load(self.root / "registry.json"),
            HistoryJournal(self.root / "history.jsonl"),
        )
        self.controller = LauncherController(self.service)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_complete_script_lifecycle_through_controller(self) -> None:
        source = self.root / "source.py"
        source.write_text("print('ok')", encoding="utf-8")
        with patch("core.importer.SCRIPTS_DIR", self.root / "scripts"):
            imported = self.controller.dispatch(Action.IMPORT_SCRIPT, {"path": source})
        self.assertTrue(imported.success, imported.error)
        item = imported.value
        self.assertTrue(self.controller.dispatch("favorite", {"id": item.id, "favorite": True}).success)
        self.assertTrue(self.controller.dispatch("rename", {"id": item.id, "name": "Renamed"}).success)
        listed = self.controller.dispatch("list", {"query": "renamed"})
        self.assertEqual(listed.value[0].id, item.id)
        self.assertTrue(self.controller.dispatch("delete", {"id": item.id}).success)
        self.assertEqual(self.service.registry.all(), [])
        self.assertEqual(
            [event.action for event in self.service.recent_history()],
            ["import_script", "favorite", "rename", "delete"],
        )

    def test_invalid_intention_returns_controlled_error(self) -> None:
        result = self.controller.dispatch("unknown")
        self.assertFalse(result.success)
        self.assertIn("ValueError", result.error or "")


if __name__ == "__main__":
    unittest.main()
