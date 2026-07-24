import tempfile
import unittest
from pathlib import Path

from tcc_budy.application.conversation_service import ConversationService
from tcc_budy.providers.simulator import SimulatorProvider
from tcc_budy.storage.conversation_repository import ConversationRepository
from tcc_budy.storage.database import Database
from tcc_budy.storage.migrations import MigrationRunner


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(__file__).resolve().parents[1]
        database = Database(Path(self.temp.name) / "test.sqlite3")
        MigrationRunner(database, root / "migrations").apply_all()
        self.repository = ConversationRepository(database)
        self.service = ConversationService(
            self.repository, SimulatorProvider(delay_seconds=0)
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_create_send_reload_delete(self):
        conversation = self.service.create_conversation()
        result = self.service.send_message(
            conversation["id"], "Une situation difficile", "request-1"
        )
        self.assertIsNotNone(result["assistant_message"])
        loaded = self.service.load_conversation(conversation["id"])
        self.assertEqual(len(loaded["messages"]), 2)
        self.service.delete_conversation(conversation["id"])
        self.assertEqual(self.service.list_conversations(), [])

    def test_request_id_is_idempotent(self):
        conversation = self.service.create_conversation()
        first = self.service.send_message(conversation["id"], "Bonjour", "same-id")
        second = self.service.send_message(conversation["id"], "Bonjour", "same-id")
        self.assertFalse(first.get("duplicate_request", False))
        self.assertTrue(second["duplicate_request"])
        loaded = self.service.load_conversation(conversation["id"])
        self.assertEqual(len(loaded["messages"]), 2)

    def test_provider_failure_keeps_user_message(self):
        conversation = self.service.create_conversation()
        result = self.service.send_message(conversation["id"], "/erreur", "error-id")
        self.assertTrue(result["provider_error"])
        self.assertIsNone(result["assistant_message"])
        loaded = self.service.load_conversation(conversation["id"])
        self.assertEqual(len(loaded["messages"]), 1)
        self.assertEqual(loaded["messages"][0]["role"], "user")

    def test_retry_does_not_duplicate_user_message(self):
        conversation = self.service.create_conversation()
        result = self.service.send_message(conversation["id"], "/erreur", "retry-id")
        retry = self.service.retry_response(
            conversation["id"], result["user_message"]["id"]
        )
        self.assertTrue(retry["provider_error"])
        loaded = self.service.load_conversation(conversation["id"])
        self.assertEqual(len(loaded["messages"]), 1)


if __name__ == "__main__":
    unittest.main()
