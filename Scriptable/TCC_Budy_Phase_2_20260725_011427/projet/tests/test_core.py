import json
import tempfile
import unittest
from pathlib import Path

from tcc_budy.application.conversation_service import ConversationService
from tcc_budy.providers.openai_provider import OpenAIProvider
from tcc_budy.providers.simulator import SimulatorProvider
from tcc_budy.storage.conversation_repository import ConversationRepository
from tcc_budy.storage.database import Database
from tcc_budy.storage.migrations import MigrationRunner
from tcc_budy.support.config import Settings, load_settings


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(__file__).resolve().parents[1]
        database = Database(Path(self.temp.name) / "test.sqlite3")
        MigrationRunner(database, root / "migrations").apply_all()
        self.repository = ConversationRepository(database)
        self.service = ConversationService(
            self.repository,
            SimulatorProvider(0),
            12,
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_create_send_reload_delete(self):
        conversation = self.service.create_conversation()
        result = self.service.send_message(
            conversation["id"],
            "Bonjour",
            "request-1",
        )
        self.assertIsNotNone(result["assistant_message"])
        loaded = self.service.load_conversation(conversation["id"])
        self.assertEqual(len(loaded["messages"]), 2)
        self.service.delete_conversation(conversation["id"])
        self.assertEqual(self.service.list_conversations(), [])

    def test_request_id_is_idempotent(self):
        conversation = self.service.create_conversation()
        self.service.send_message(conversation["id"], "Bonjour", "same-id")
        second = self.service.send_message(
            conversation["id"],
            "Bonjour",
            "same-id",
        )
        self.assertTrue(second["duplicate_request"])
        loaded = self.service.load_conversation(conversation["id"])
        self.assertEqual(len(loaded["messages"]), 2)

    def test_provider_failure_keeps_user_message(self):
        conversation = self.service.create_conversation()
        result = self.service.send_message(
            conversation["id"],
            "/erreur",
            "error-id",
        )
        self.assertTrue(result["provider_error"])
        loaded = self.service.load_conversation(conversation["id"])
        self.assertEqual(len(loaded["messages"]), 1)

    def test_openai_extract_output_text(self):
        settings = Settings(
            "openai",
            "test-model",
            "https://example.test",
            30,
            500,
            12,
            False,
            "Instructions",
            "secret-test",
        )
        provider = OpenAIProvider(settings)
        payload = {
            "output": [
                {
                    "type": "message",
                    "content": [
                        {"type": "output_text", "text": "Réponse"}
                    ],
                }
            ]
        }
        self.assertEqual(provider._extract_text(payload), "Réponse")

    def test_config_is_created_and_defaults_to_simulator(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            settings = load_settings(root)
            self.assertEqual(settings.provider, "simulator")
            config_path = root / "config.json"
            self.assertTrue(config_path.exists())
            data = json.loads(config_path.read_text(encoding="utf-8"))
            self.assertEqual(data["provider"], "auto")

    def test_auto_provider_uses_openai_when_secret_exists(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "secrets.json").write_text(
                json.dumps(
                    {
                        "OPENAI_API_KEY": "secret-test",
                        "OPENAI_MODEL": "test-model",
                    }
                ),
                encoding="utf-8",
            )
            settings = load_settings(root)
            self.assertEqual(settings.provider, "openai")
            self.assertEqual(settings.model, "test-model")


if __name__ == "__main__":
    unittest.main()
