import asyncio
import sys
import os

# 将项目根目录添加到 python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import engine
from app.models.tables import Base

async def init_db():
    print("正在初始化数据库表...")
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # 如果需要重新开始可以取消注释
        await conn.run_sync(Base.metadata.create_all)
    print("数据库表初始化完成。")

if __name__ == "__main__":
    asyncio.run(init_db())
