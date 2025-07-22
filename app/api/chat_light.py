from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.core.chat_engine_light import ChatEngineLight

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        engine = ChatEngineLight()
        reply = await engine.get_response(request.message)
        return ChatResponse(response=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
