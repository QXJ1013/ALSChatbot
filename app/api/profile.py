from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.utils.auth import get_current_user
from app.core.stage_estimator import StageEstimator

router = APIRouter()

class ProfileUpdate(BaseModel):
    mobility_level: Optional[int] = None  # 1-5
    speech_ability: Optional[int] = None  # 1-5
    daily_activities: Optional[List[str]] = None
    current_medications: Optional[List[str]] = None

class ProfileResponse(BaseModel):
    user_id: str
    current_stage: str
    stage_confidence: float
    profile_data: dict
    last_updated: datetime

@router.get("/", response_model=ProfileResponse)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """获取用户档案"""
    # TODO: 从数据库获取用户档案
    pass

@router.put("/", response_model=ProfileResponse)
async def update_profile(
    profile: ProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """更新用户档案"""
    # TODO: 更新用户档案并重新评估阶段
    pass