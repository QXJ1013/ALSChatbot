from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from app.utils.auth import get_current_user, create_access_token
from app.utils.database import get_db

router = APIRouter()

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    diagnosis_date: Optional[datetime] = None

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    created_at: datetime

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db=Depends(get_db)):
   
    pass

@router.post("/login")
async def login(request: LoginRequest, db=Depends(get_db)):
  
    pass

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(**current_user)