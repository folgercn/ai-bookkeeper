from fastapi import Security, HTTPException, Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.database import get_db
from app.models.tables import User

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

async def verify_api_key(
    api_key: str = Security(api_key_header),
    db: AsyncSession = Depends(get_db)
):
    """验证 API Key (Bearer 格式)"""
    if not api_key or not api_key.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing API Key or invalid format")
    
    token = api_key.replace("Bearer ", "")
    
    result = await db.execute(select(User).where(User.api_key == token))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    
    return user
