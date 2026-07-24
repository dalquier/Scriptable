from datetime import datetime, timezone
from uuid import uuid4

from tcc_budy.domain.models import Conversation, Message
from tcc_budy.support.errors import NotFoundError


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ConversationRepository:
    def __init__(self, database):
        self.database = database

    def create(self, title: str) -> Conversation:
        conversation_id = str(uuid4())
        now = now_iso()
        with self.database.transaction() as conn:
            conn.execute(
                "INSERT INTO conversations(id,title,status,created_at,updated_at) VALUES (?,?,'active',?,?)",
                (conversation_id, title, now, now),
            )
        return self.get_by_id(conversation_id)

    def list_all(self):
        with self.database.read() as conn:
            rows = conn.execute(
                """
                SELECT c.*,
                  COALESCE((SELECT content FROM messages m WHERE m.conversation_id=c.id ORDER BY sequence DESC LIMIT 1),'') AS preview,
                  (SELECT COUNT(*) FROM messages m WHERE m.conversation_id=c.id) AS message_count
                FROM conversations c ORDER BY c.updated_at DESC
                """
            ).fetchall()
        return [self._conversation(row) for row in rows]

    def get_by_id(self, conversation_id: str) -> Conversation:
        with self.database.read() as conn:
            row = conn.execute(
                """
                SELECT c.*,
                  COALESCE((SELECT content FROM messages m WHERE m.conversation_id=c.id ORDER BY sequence DESC LIMIT 1),'') AS preview,
                  (SELECT COUNT(*) FROM messages m WHERE m.conversation_id=c.id) AS message_count
                FROM conversations c WHERE c.id=?
                """,
                (conversation_id,),
            ).fetchone()
        if not row:
            raise NotFoundError("Conversation introuvable.")
        return self._conversation(row)

    def list_messages(self, conversation_id: str):
        self.get_by_id(conversation_id)
        with self.database.read() as conn:
            rows = conn.execute(
                "SELECT * FROM messages WHERE conversation_id=? ORDER BY sequence ASC",
                (conversation_id,),
            ).fetchall()
        return [Message(**dict(row)) for row in rows]

    def append_message(self, conversation_id, role, content, status, request_id=None):
        self.get_by_id(conversation_id)
        message_id = str(uuid4())
        now = now_iso()
        with self.database.transaction() as conn:
            if request_id:
                row = conn.execute("SELECT * FROM messages WHERE request_id=?", (request_id,)).fetchone()
                if row:
                    return Message(**dict(row))
            sequence = conn.execute(
                "SELECT COALESCE(MAX(sequence),0)+1 AS n FROM messages WHERE conversation_id=?",
                (conversation_id,),
            ).fetchone()["n"]
            conn.execute(
                "INSERT INTO messages(id,conversation_id,sequence,role,content,status,request_id,created_at) VALUES (?,?,?,?,?,?,?,?)",
                (message_id, conversation_id, sequence, role, content, status, request_id, now),
            )
            conn.execute("UPDATE conversations SET updated_at=? WHERE id=?", (now, conversation_id))
        return self.get_message(message_id)

    def get_message_by_request_id(self, request_id):
        if not request_id:
            return None
        with self.database.read() as conn:
            row = conn.execute("SELECT * FROM messages WHERE request_id=?", (request_id,)).fetchone()
        return Message(**dict(row)) if row else None

    def get_message(self, message_id):
        with self.database.read() as conn:
            row = conn.execute("SELECT * FROM messages WHERE id=?", (message_id,)).fetchone()
        if not row:
            raise NotFoundError("Message introuvable.")
        return Message(**dict(row))

    def get_next_message(self, conversation_id, sequence):
        with self.database.read() as conn:
            row = conn.execute(
                "SELECT * FROM messages WHERE conversation_id=? AND sequence>? ORDER BY sequence ASC LIMIT 1",
                (conversation_id, sequence),
            ).fetchone()
        return Message(**dict(row)) if row else None

    def update_title_if_default(self, conversation_id, text):
        title = " ".join(text.strip().split())[:48] or "Nouvelle conversation"
        with self.database.transaction() as conn:
            conn.execute(
                "UPDATE conversations SET title=? WHERE id=? AND title='Nouvelle conversation'",
                (title, conversation_id),
            )

    def delete(self, conversation_id):
        with self.database.transaction() as conn:
            cursor = conn.execute("DELETE FROM conversations WHERE id=?", (conversation_id,))
            if cursor.rowcount == 0:
                raise NotFoundError("Conversation introuvable.")

    @staticmethod
    def _conversation(row):
        return Conversation(
            id=row["id"], title=row["title"], status=row["status"],
            created_at=row["created_at"], updated_at=row["updated_at"],
            last_message_preview=row["preview"], message_count=row["message_count"],
        )
