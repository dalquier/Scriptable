import os
import sys
import tempfile
import unittest
from pathlib import Path

from launcher_pro.controller import LibraryController
from launcher_pro.registry import ItemKind, LibraryItem, LibraryRegistry
from launcher_pro.runner import PythonRunner


class ControllerRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.controller = LibraryController(LibraryRegistry(self.root / "library.json"))

    def tearDown(self):
        self.temp.cleanup()

    def test_search_favorites_and_sort(self):
        alpha = self.root / "alpha.py"
        beta = self.root / "beta.py"
        alpha.touch(); beta.touch()
        first = self.controller.registry.add(LibraryItem.create("Alpha", ItemKind.SCRIPT, alpha, alpha))
        self.controller.registry.add(LibraryItem.create("Beta", ItemKind.SCRIPT, beta, beta))
        self.controller.toggle_favorite(first.id)
        self.assertEqual([item.name for item in self.controller.items()], ["Alpha", "Beta"])
        self.assertEqual([item.name for item in self.controller.items("bet")], ["Beta"])
        self.assertEqual([item.name for item in self.controller.items(favorites_only=True)], ["Alpha"])

    def test_runner_executes_and_restores_process_state(self):
        marker = self.root / "marker.txt"
        script = self.root / "main.py"
        script.write_text("from pathlib import Path\nPath('marker.txt').write_text('ok')\n", encoding="utf-8")
        item = LibraryItem.create("Demo", ItemKind.PROJECT, self.root, script)
        cwd, argv, path = os.getcwd(), sys.argv[:], sys.path[:]
        self.assertTrue(PythonRunner().run(item).succeeded)
        self.assertEqual(marker.read_text(), "ok")
        self.assertEqual((os.getcwd(), sys.argv, sys.path), (cwd, argv, path))

    def test_runner_reports_traceback(self):
        script = self.root / "bad.py"
        script.write_text("raise RuntimeError('boom')", encoding="utf-8")
        result = PythonRunner().run(LibraryItem.create("Bad", ItemKind.SCRIPT, script, script))
        self.assertFalse(result.succeeded)
        self.assertIn("RuntimeError: boom", result.error)


if __name__ == "__main__":
    unittest.main()


class RunnerConcurrencyTests(unittest.TestCase):
    def test_concurrent_run_is_rejected(self):
        import threading

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            started = threading.Event()
            release = threading.Event()
            script = root / "wait.py"
            script.write_text(
                "import builtins\nbuiltins._runner_started.set()\nbuiltins._runner_release.wait(2)\n",
                encoding="utf-8",
            )
            item = LibraryItem.create("Wait", ItemKind.SCRIPT, script, script)
            import builtins
            builtins._runner_started, builtins._runner_release = started, release
            runner = PythonRunner()
            worker = threading.Thread(target=runner.run, args=(item,))
            worker.start()
            self.assertTrue(started.wait(1))
            result = runner.run(item)
            release.set()
            worker.join(2)
            del builtins._runner_started, builtins._runner_release
            self.assertFalse(result.succeeded)
            self.assertIn("déjà en cours", result.error)
