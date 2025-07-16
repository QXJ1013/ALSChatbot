from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
import structlog

from app.core.chat_engine import ChatEngine
from app.core.context_memory import ContextMemory
from app.utils.auth import get_current_user

router = APIRouter()
logger = structlog.get_logger()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    recommendations: Optional[List[dict]] = None
    stage_info: Optional[dict] = None
    emotion: Optional[dict] = None
    needs: Optional[List[str]] = None

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    ALS Semantic Assistant Chat Endpoint
    Handles multi-turn conversation and returns AI-generated response.
    """
    try:
        # Get or create a session_id
        session_id = request.session_id or str(uuid.uuid4())
        logger.info("Processing chat request", user_id=current_user["id"], session_id=session_id)

        # Initialize chat engine for this user/session
        chat_engine = ChatEngine(user_id=current_user["id"], session_id=session_id)

        # Process the user message through full AI pipeline
        response_data: Dict[str, Any] = await chat_engine.process_message(
            message=request.message
        )

        return ChatResponse(
            response=response_data["response"],
            session_id=session_id,
            recommendations=response_data.get("recommendations"),
            stage_info=response_data.get("stage_info"),
            emotion=response_data.get("emotion"),
            needs=response_data.get("needs")
        )

    except Exception as e:
        logger.error("Chat processing failed", error=str(e))
        raise HTTPException(status_code=500, detail="Chat processing failed. Please try again later.")
