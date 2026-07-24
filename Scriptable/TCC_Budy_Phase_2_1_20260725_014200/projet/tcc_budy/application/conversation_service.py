from dataclasses import asdict
from uuid import uuid4

from tcc_budy.support.errors import ProviderError, ValidationError


class ConversationService:
    def __init__(self, repository, provider, context_message_limit=12):
        self.repository = repository
        self.provider = provider
        self.context_message_limit = max(2, int(context_message_limit))

    def create_conversation(self):
        return self._serialize(self.repository.create("Nouvelle conversation"))

    def list_conversations(self):
        return [self._serialize(item) for item in self.repository.list_all()]

    def load_conversation(self, conversation_id):
        return {
            "conversation": self._serialize(self.repository.get_by_id(conversation_id)),
            "messages": [asdict(m) for m in self.repository.list_messages(conversation_id)],
        }

    def send_message(self, conversation_id, text, request_id=None):
        cleaned = " ".join((text or "").split())
        if not cleaned:
            raise ValidationError("Le message est vide.")
        request_id = request_id or str(uuid4())
        existing = self.repository.get_message_by_request_id(request_id)
        if existing is not None:
            assistant = self.repository.get_next_message(conversation_id, existing.sequence)
            return self._result(conversation_id, existing, assistant, duplicate=True)
        user_message = self.repository.append_message(
            conversation_id, "user", cleaned, "complete", request_id
        )
        self.repository.update_title_if_default(conversation_id, cleaned)
        return self._respond(conversation_id, user_message)

    def retry_response(self, conversation_id, user_message_id):
        user_message = self.repository.get_message(user_message_id)
        if user_message.conversation_id != conversation_id or user_message.role != "user":
            raise ValidationError("Le message à relancer n'est pas valide.")
        existing = self.repository.get_next_message(conversation_id, user_message.sequence)
        if existing is not None and existing.role == "assistant":
            return self._result(conversation_id, user_message, existing, duplicate=True)
        return self._respond(conversation_id, user_message)

    def _respond(self, conversation_id, user_message):
        history = self.repository.list_messages(conversation_id)
        context = [
            {"role": item.role, "content": item.content}
            for item in history[-self.context_message_limit:]
        ]
        try:
            text = self.provider.respond(context)
        except ProviderError as exc:
            result = self._result(conversation_id, user_message, None)
            result.update({"provider_error": True, "error_message": str(exc)})
            return result
        assistant = self.repository.append_message(
            conversation_id, "assistant", text, "complete", None
        )
        return self._result(conversation_id, user_message, assistant)

    def _result(self, conversation_id, user_message, assistant_message, duplicate=False):
        return {
            "user_message": asdict(user_message),
            "assistant_message": asdict(assistant_message) if assistant_message else None,
            "conversation": self._serialize(self.repository.get_by_id(conversation_id)),
            "duplicate_request": duplicate,
            "provider_error": assistant_message is None,
        }

    def delete_conversation(self, conversation_id):
        self.repository.delete(conversation_id)
        return {"deleted": True, "conversation_id": conversation_id}

    @staticmethod
    def _serialize(conversation):
        return asdict(conversation)
