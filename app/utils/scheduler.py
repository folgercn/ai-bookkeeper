import asyncio
from datetime import datetime, timedelta
from sqlalchemy import update
from app.models.database import AsyncSessionLocal
from app.models.tables import StagingArea

async def cleanup_expired_staging():
    """
    后台清理任务：标记 30 分钟未处理的暂存项为已过期
    """
    while True:
        try:
            async with AsyncSessionLocal() as db:
                expire_threshold = datetime.utcnow() - timedelta(minutes=30)
                await db.execute(
                    update(StagingArea)
                    .where(
                        StagingArea.status == "pending",
                        StagingArea.created_at < expire_threshold
                    )
                    .values(status="expired")
                )
                await db.commit()
        except Exception as e:
            print(f"清理暂存区失败: {e}")
        
        await asyncio.sleep(600) # 每 10 分钟运行一次
