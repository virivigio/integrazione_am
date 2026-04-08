import uuid
from datetime import datetime, timedelta


class SessionManager:
    def __init__(self, ttl_hours: int = 24):
        self._sessions: dict[str, dict] = {}
        self._ttl = timedelta(hours=ttl_hours)

    def get_or_create(self, session_id: str | None) -> tuple[str, list]:
        """Return (session_id, conversation_history). Creates new session if needed."""
        if session_id and session_id in self._sessions:
            session = self._sessions[session_id]
            session["last_activity"] = datetime.now()
            return session_id, session["history"]

        new_id = str(uuid.uuid4())
        self._sessions[new_id] = {
            "history": [],
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
        }
        return new_id, self._sessions[new_id]["history"]

    def get_history(self, session_id: str) -> list | None:
        session = self._sessions.get(session_id)
        if session is None:
            return None
        session["last_activity"] = datetime.now()
        return session["history"]

    def delete(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def cleanup_expired(self):
        now = datetime.now()
        expired = [
            sid for sid, s in self._sessions.items()
            if now - s["last_activity"] > self._ttl
        ]
        for sid in expired:
            del self._sessions[sid]


session_manager = SessionManager()
