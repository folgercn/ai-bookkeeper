"""
JWT 自动续期中间件

每次请求时检查 JWT 是否即将过期(剩余时间少于7天),
如果是,则自动颁发新的 token 并通过响应头返回
"""
from datetime import datetime, timedelta
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError

from app.config import settings

class JWTRefreshMiddleware(BaseHTTPMiddleware):
    """JWT 自动续期中间件"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # 只处理认证请求
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return response
        
        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            
            # 检查过期时间
            exp = payload.get("exp")
            if not exp:
                return response
            
            exp_datetime = datetime.fromtimestamp(exp)
            now = datetime.utcnow()
            time_remaining = exp_datetime - now
            
            # 如果剩余时间少于7天,自动续期
            REFRESH_THRESHOLD = timedelta(days=7)
            if time_remaining < REFRESH_THRESHOLD:
                # 创建新 token
                new_payload = payload.copy()
                new_exp = now + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
                new_payload["exp"] = new_exp
                
                new_token = jwt.encode(new_payload, settings.SECRET_KEY, algorithm="HS256")
                
                # 通过响应头返回新 token
                response.headers["X-New-Token"] = new_token
                response.headers["X-Token-Refreshed"] = "true"
                
        except JWTError:
            # Token 无效或已过期,不处理
            pass
        
        return response
