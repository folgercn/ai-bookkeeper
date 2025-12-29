import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.models.database import get_db
from app.models.tables import User
from app.models.schemas import (
    UserRegisterRequest, UserLoginRequest, UserResponse,
    TokenResponse, APIKeyResponse, SuccessResponse
)

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

@router.post("/register", response_model=SuccessResponse)
async def register(req: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    注册功能暂时禁用 - 仅供个人使用
    如需创建用户,请使用: python scripts/create_user.py
    """
    raise HTTPException(status_code=403, detail="注册功能已禁用,此应用仅供个人使用")

# ==================== 原注册代码(已注释,可恢复) ====================
# @router.post("/register", response_model=SuccessResponse)
# async def register(req: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
#     # 检查用户是否存在
#     result = await db.execute(select(User).where(User.username == req.username))
#     if result.scalar_one_or_none():
#         raise HTTPException(status_code=400, detail="用户名已存在")
#     
#     user_id = str(uuid.uuid4())
#     api_key = f"fa_{secrets.token_hex(16)}"
#     
#     new_user = User(
#         id=user_id,
#         username=req.username,
#         password_hash=get_password_hash(req.password),
#         api_key=api_key
#     )
#     
#     db.add(new_user)
#     await db.commit()
#     
#     return SuccessResponse(data={
#         "user_id": user_id,
#         "username": req.username,
#         "api_key": api_key
#     })
# ==================== 原注册代码结束 ====================

@router.post("/login", response_model=SuccessResponse)
async def login(req: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == req.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    access_token = create_access_token(data={"sub": user.id})
    
    return SuccessResponse(data={
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.JWT_EXPIRE_MINUTES * 60,
        "api_key": user.api_key,
        "username": user.username
    })

@router.get("/api-key", response_model=SuccessResponse)
async def get_api_key(db: AsyncSession = Depends(get_db)):
    # 暂未实现认证子集，后续通过 Depends(get_current_user) 完善
    return SuccessResponse(message="该接口需要身份认证，将在后续步骤完善")
