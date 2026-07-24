from dataclasses import asdict
from uuid import uuid4

from tcc_budy.support.errors import ProviderError, ValidationError


class ConversationService:
    def __init__(self, repository, provider):
        self.repository = repository
        self.provider = provider

    def create_conversation(self):
        return self._serialize_conversation(
            self.repository.create("Nouvelle conversation")
        )

    def list_conversations(self):
        return [self._serialize_conversation(c) for c in self.repository.list_all()]

    def load_conversation(self, conversation_id):
        conversation = self.repository.get_by_id(conversation_id)
        messages = self.repository.list_messages(conversation_id)
        return {
            "conversation": self._serialize_conversation(conversation),
            "messages": [asdict(m) for m in messages],
        }

    def send_message(self, conversation_id, text, request_id=None):
        cleaned = " ".join((text or "").split())
        if not cleaned:
            raise ValidationError("Le message est vide.")

        request_id = request_id or str(uuid4())
        existing = self.repository.get_message_by_request_id(request_id)
        if existing is not None:
            next_message = self.repository.get_next_message(
                conversation_id, existing.sequence
            )
            return {
                "user_message": asdict(existing),
                "assistant_message": asdict(next_message) if next_message else None,
                "conversation": self._serialize_conversation(
                    self.repository.get_by_id(conversation_id)
                ),
                "duplicate_request": True,
                "provider_error": next_message is None,
            }

        user_message = self.repository.append_message(
            conversation_id, "user", cleaned, "complete", request_id
        )
        self.repository.update_title_if_default(conversation_id, cleaned)
        return self._respond_to_saved_user_message(conversation_id, user_message)

    def retry_response(self, conversation_id, user_message_id):
        user_message = self.repository.get_message(user_message_id)
        if user_message.conversation_id != conversation_id or user_message.role != "user":
            raise ValidationError("Le message à relancer n’est pas valide.")

        existing_next = self.repository.get_next_message(
            conversation_id, user_message.sequence
        )
        if existing_next is not None and existing_next.role == "assistant":
            return {
                "user_message": asdict(user_message),
                "assistant_message": asdict(existing_next),
                "conversation": self._serialize_conversation(
                    self.repository.get_by_id(conversation_id)
                ),
                "duplicate_request": True,
            }
        return self._respond_to_saved_user_message(conversation_id, user_message)

    def _respond_to_saved_user_message(self, conversation_id, user_message):
        try:
            assistant_text = self.provider.respond(user_message.content)
        except ProviderError as exc:
            return {
                "user_message": asdict(user_message),
                "assistant_message": None,
                "conversation": self._serialize_conversation(
                    self.repository.get_by_id(conversation_id)
                ),
                "provider_error": True,
                "error_message": str(exc),
            }

        assistant_message = self.repository.append_message(
            conversation_id, "assistant", assistant_text, "complete", None
        )
        return {
            "user_message": asdict(user_message),
            "assistant_message": asdict(assistant_message),
            "conversation": self._serialize_conversation(
                self.repository.get_by_id(conversation_id)
            ),
            "provider_error": False,
        }

    def delete_conversation(self, conversation_id):
        self.repository.delete(conversation_id)
        return {"deleted": True, "conversation_id": conversation_id}

    @staticmethod
    def _serialize_conversation(conversation):
        return asdict(conversation)
