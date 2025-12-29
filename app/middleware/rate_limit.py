import time
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

class RateLimiter:
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = window_seconds
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        now = time.time()
        window_start = now - self.window
        
        # 清理过期记录
        self.requests[client_id] = [
            t for t in self.requests[client_id] if t > window_start
        ]
        
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        self.requests[client_id].append(now)
        return True

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.limiter = RateLimiter(max_requests, window_seconds)
    
    async def dispatch(self, request: Request, call_next):
        # 简单起见，这里按 IP 限流，如果后续有 user_id 可以按 user_id
        client_ip = request.client.host
        if not self.limiter.is_allowed(client_ip):
            return JSONResponse(
                status_code=429,
                content={"success": False, "error": {"code": "RATE_LIMITED", "message": "请求过于频繁"}}
            )
        return await call_next(request)
