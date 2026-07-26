import io
import json
import os
import socket
import sys
import tempfile
import unittest
import urllib.error

PROJECT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "projet"))
sys.path.insert(0, PROJECT)

from api_client import OpenAIClient, OpenAIClientError, _extract_output_text, parse_response
from app import AssistantIAApp
from conversation import ConversationManager
from storage import Storage


class FakeResponse:
    def __init__(self, data):
        self.data = data

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.data


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "test.sqlite3")
        self.storage = Storage(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_create_add_order_restore_and_new(self):
        manager = ConversationManager(self.storage)
        first = manager.conversation_id
        manager.add_user_message("Bonjour")
        manager.add_assistant_message("Salut")
        self.assertEqual(["user", "assistant"], [m["role"] for m in manager.messages()])
        self.assertEqual(first, ConversationManager(Storage(self.path)).conversation_id)
        second = manager.new_conversation()
        self.assertNotEqual(first, second)
        self.assertEqual([], manager.messages())

    def test_management_validation_and_cascade(self):
        cid = self.storage.create_conversation()
        self.storage.rename_conversation(cid, "Titre")
        self.assertEqual("Titre", self.storage.get_conversation(cid)["title"])
        with self.assertRaises(ValueError):
            self.storage.add_message(cid, "system", "non")
        self.storage.add_message(cid, "user", "oui")
        self.storage.delete_conversation(cid)
        self.assertIsNone(self.storage.get_conversation(cid))
        self.assertEqual([], self.storage.get_messages(cid))


class ParserTests(unittest.TestCase):
    def test_direct_output_text(self):
        self.assertEqual("réponse", _extract_output_text({"output_text": " réponse "}))

    def test_nested_output_text_and_sources(self):
        raw = json.dumps({
            "output": [{
                "type": "message",
                "content": [{
                    "type": "output_text",
                    "text": "A",
                    "annotations": [{
                        "type": "url_citation",
                        "url": "https://example.com/a",
                        "title": "Source",
                    }],
                }],
            }],
        }).encode()
        result = parse_response(raw)
        self.assertEqual("A", result["text"])
        self.assertEqual("example.com", result["sources"][0]["domain"])

    def test_no_text_and_invalid_json(self):
        with self.assertRaises(OpenAIClientError):
            _extract_output_text({"output": []})
        with self.assertRaises(OpenAIClientError):
            parse_response(b"not-json")


class ClientTests(unittest.TestCase):
    def test_payload_web_toggle(self):
        messages = [{"role": "user", "content": "Bonjour"}]
        off = OpenAIClient.build_payload(messages, False)
        on = OpenAIClient.build_payload(messages, True)
        self.assertNotIn("tools", off)
        self.assertEqual([{"type": "web_search"}], on["tools"])

    def test_success_without_real_network(self):
        client = OpenAIClient("sk-test", opener=lambda *a, **k: FakeResponse(b'{"output_text":"ok"}'))
        self.assertEqual("ok", client.create_response([])["text"])

    def test_http_network_and_timeout_errors(self):
        cases = [
            urllib.error.HTTPError("url", 401, "bad", {}, io.BytesIO(b"secret")),
            urllib.error.URLError("offline"),
            socket.timeout(),
        ]
        for error in cases:
            def opener(*args, _error=error, **kwargs):
                raise _error
            with self.subTest(error=type(error).__name__):
                with self.assertRaises(OpenAIClientError):
                    OpenAIClient("sk-test", opener=opener).create_response([])


class AppTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.storage = Storage(os.path.join(self.tmp.name, "app.sqlite3"))

    def tearDown(self):
        self.tmp.cleanup()

    def test_empty_refused_and_success_saved_once(self):
        class Client:
            def create_response(self, messages, enable_web_search=False):
                return {"text": "Réponse", "sources": [], "metadata": {}}

        app = AssistantIAApp(self.storage, Client())
        with self.assertRaises(ValueError):
            app.send_message("  ")
        result = app.send_message("Question", True)
        self.assertTrue(result["web_used"])
        self.assertEqual(["user", "assistant"], [m["role"] for m in app.get_messages()])

    def test_error_keeps_user_without_fake_assistant(self):
        class FailingClient:
            def create_response(self, *args, **kwargs):
                raise OpenAIClientError("échec")

        app = AssistantIAApp(self.storage, FailingClient())
        with self.assertRaises(OpenAIClientError):
            app.send_message("À réessayer")
        self.assertEqual(["user"], [m["role"] for m in app.get_messages()])


if __name__ == "__main__":
    unittest.main()
