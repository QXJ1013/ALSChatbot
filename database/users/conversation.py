
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, index=True, nullable=False)
    chat_id = Column(String, unique=True, default=generate_uuid)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # stores a list of messages: [{"role": "user", "content": "..."}, ...]
    messages = Column(JSON, nullable=False)

    # generated summary by AI
    summary = Column(Text, nullable=True)

    # optional prediction fields
    stage_estimate = Column(String, nullable=True)
    needs_detected = Column(JSON, nullable=True)  # list of PNM or mapped terms

    # feedback score (e.g. 1-5 scale)
    feedback_rating = Column(Integer, nullable=True)
