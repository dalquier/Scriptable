import tempfile
import unittest
from pathlib import Path

from tcc_budy.application.conversation_service import ConversationService
from tcc_budy.providers.openai_provider import OpenAIProvider
from tcc_budy.providers.simulator import SimulatorProvider
from tcc_budy.storage.conversation_repository import ConversationRepository
from tcc_budy.storage.database import Database
from tcc_budy.storage.migrations import MigrationRunner
from tcc_budy.support.config import Settings


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(__file__).resolve().parents[1]
        db = Database(Path(self.temp.name) / "test.sqlite3")
        MigrationRunner(db, root / "migrations").apply_all()
        self.repository = ConversationRepository(db)
        self.service = ConversationService(self.repository, SimulatorProvider(0), 12)

    def tearDown(self):
        self.temp.cleanup()

    def test_create_send_reload_delete(self):
        conversation = self.service.create_conversation()
        result = self.service.send_message(conversation["id"], "Bonjour", "request-1")
        self.assertIsNotNone(result["assistant_message"])
        self.assertEqual(len(self.service.load_conversation(conversation["id"])["messages"]), 2)
        self.service.delete_conversation(conversation["id"])
        self.assertEqual(self.service.list_conversations(), [])

    def test_request_id_is_idempotent(self):
        conversation = self.service.create_conversation()
        self.service.send_message(conversation["id"], "Bonjour", "same-id")
        second = self.service.send_message(conversation["id"], "Bonjour", "same-id")
        self.assertTrue(second["duplicate_request"])
        self.assertEqual(len(self.service.load_conversation(conversation["id"])["messages"]), 2)

    def test_provider_failure_keeps_user_message(self):
        conversation = self.service.create_conversation()
        result = self.service.send_message(conversation["id"], "/erreur", "error-id")
        self.assertTrue(result["provider_error"])
        self.assertEqual(len(self.service.load_conversation(conversation["id"])["messages"]), 1)

    def test_openai_extract_output_text(self):
        settings = Settings("openai", "test-model", "https://example.test", 30, 500, 12, False, "Instructions", "secret-test")
        provider = OpenAIProvider(settings)
        payload = {"output": [{"type": "message", "content": [{"type": "output_text", "text": "Réponse"}]}]}
        self.assertEqual(provider._extract_text(payload), "Réponse")

    def test_native_close_strategy_is_present(self):
        source = (Path(__file__).resolve().parents[1] / "tcc_budy" / "ui" / "webview.py").read_text(encoding="utf-8")
        self.assertIn("sender.superview.superview.close()", source)


if __name__ == "__main__":
    unittest.main()
