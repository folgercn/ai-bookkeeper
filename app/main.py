import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.config import settings
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, config, record, expenses, export
from app.middleware.rate_limit import RateLimitMiddleware
from app.utils.scheduler import cleanup_expired_staging

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动清理任务
    asyncio.create_task(cleanup_expired_staging())
    yield

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 限流中间件
app.add_middleware(
    RateLimitMiddleware,
    max_requests=settings.RATE_LIMIT_PER_MINUTE,
    window_seconds=60
)

# 注册路由
app.include_router(auth.router, prefix="/v1")
app.include_router(config.router, prefix="/v1")
app.include_router(record.router, prefix="/v1")
app.include_router(expenses.router, prefix="/v1")
app.include_router(export.router, prefix="/v1")

# 挂载前端静态文件
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME} API"}
