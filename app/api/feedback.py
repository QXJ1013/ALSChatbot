from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

from app.utils.auth import get_current_user
from app.utils.database import get_db

router = APIRouter()

class FeedbackRequest(BaseModel):
    category: str  # 'qol', 'recommendation', 'chat'
    rating: int  # 1-5
    content: Optional[str] = None
    metadata: Optional[Dict] = None

class FeedbackResponse(BaseModel):
    feedback_id: str
    received_at: datetime
    status: str

@router.post("/", response_model=FeedbackResponse)
async def submit_feedback(
    feedback: FeedbackRequest,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """SUBMIT FEEDBACK"""

    pass

@router.get("/qol-history")
async def get_qol_history(
    current_user: dict = Depends(get_current_user),
    days: int = 30
):
    """GET QoL HISTORY
"""
    
    pass