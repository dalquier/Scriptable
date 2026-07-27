"""Tests du journal métier."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from core.history import HistoryJournal


class HistoryJournalTests(unittest.TestCase):
    def test_append_and_limited_read(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            journal = HistoryJournal(Path(directory) / "history.jsonl")
            journal.append("import", item_id="one", detail="Démo")
            journal.append("run", success=False, item_id="one", detail="boom")
            events = journal.read(limit=1)
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0].action, "run")
            self.assertFalse(events[0].success)

    def test_incomplete_lines_are_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "history.jsonl"
            path.write_text('{"broken"\n', encoding="utf-8")
            self.assertEqual(HistoryJournal(path).read(), [])


if __name__ == "__main__":
    unittest.main()
