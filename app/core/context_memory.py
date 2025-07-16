from typing import Dict, List, Any
import json
import asyncio
from datetime import datetime
import redis.asyncio as redis

from database.users.conversation import Conversation  # Make sure it's importable
from sqlalchemy.orm import Session
from db.session import get_session  # Your SQLAlchemy session provider

class ContextMemory:
    """Conversation memory context manager with Redis and DB fallback."""

    _redis_client: redis.Redis = None

    @classmethod
    def initialize(cls, redis_url: str = "redis://localhost:6379"):
        cls._redis_client = redis.from_url(redis_url)

    @classmethod
    async def cleanup(cls):
        if cls._redis_client:
            await cls._redis_client.close()

    @classmethod
    async def get_context(cls, session_id: str) -> Dict[str, Any]:
        key = f"context:{session_id}"
        try:
            data = await cls._redis_client.get(key)
            if data:
                return json.loads(data)
        except Exception:
            pass

        return {
            "session_id": session_id,
            "messages": [],
            "turn_count": 0,
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat()
        }

    @classmethod
    async def update_context(cls, session_id: str, user_message: str, assistant_response: str):
        context = await cls.get_context(session_id)

        context["messages"].append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.utcnow().isoformat()
        })
        context["messages"].append({
            "role": "assistant",
            "content": assistant_response,
            "timestamp": datetime.utcnow().isoformat()
        })

        context["turn_count"] += 1
        context["last_updated"] = datetime.utcnow().isoformat()

        # Keep only the last 20 messages
        if len(context["messages"]) > 20:
            context["messages"] = context["messages"][-20:]

        try:
            key = f"context:{session_id}"
            await cls._redis_client.setex(
                key, 86400, json.dumps(context)  # 24h expiry
            )
        except Exception:
            pass

    @classmethod
    async def get_dialogue_history(cls, session_id: str) -> List[Dict[str, str]]:
        """Return the formatted message history for summarization or LLM input"""
        context = await cls.get_context(session_id)
        return context.get("messages", [])

    @classmethod
    async def persist_to_database(cls, session_id: str, user_id: str, db: Session = None):
        """Save context as a conversation record to the database"""
        context = await cls.get_context(session_id)

        if db is None:
            db = get_session()

        convo = Conversation(
            user_id=user_id,
            chat_id=session_id,
            messages=context.get("messages", []),
            stage_estimate=None,
            needs_detected=None,
            feedback_rating=None,
            summary=None,
        )

        db.add(convo)
        db.commit()
        db.refresh(convo)
        return convo

    @classmethod
    async def clear_context(cls, session_id: str):
        """Manually clear Redis context (e.g., after saving or reset)"""
        try:
            await cls._redis_client.delete(f"context:{session_id}")
        except Exception:
            pass
