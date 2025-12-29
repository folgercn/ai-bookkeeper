#!/usr/bin/env python3
"""
创建用户工具
用于在禁用公开注册后手动创建用户
"""
import asyncio
import sys
import uuid
import secrets
from getpass import getpass
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from passlib.context import CryptContext

from app.config import settings
from app.models.tables import User, Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user():
    """创建新用户"""
    print("=" * 50)
    print("家庭智能记账 - 创建用户工具")
    print("=" * 50)
    print()
    
    # 获取用户输入
    username = input("请输入用户名: ").strip()
    if not username:
        print("❌ 用户名不能为空")
        return
    
    password = getpass("请输入密码: ")
    if not password:
        print("❌ 密码不能为空")
        return
    
    password_confirm = getpass("请再次输入密码: ")
    if password != password_confirm:
        print("❌ 两次密码不一致")
        return
    
    # 创建数据库连接
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # 检查用户是否存在
        result = await session.execute(select(User).where(User.username == username))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print(f"❌ 用户名 '{username}' 已存在")
            return
        
        # 创建新用户
        user_id = str(uuid.uuid4())
        api_key = f"fa_{secrets.token_hex(16)}"
        password_hash = pwd_context.hash(password)
        
        new_user = User(
            id=user_id,
            username=username,
            password_hash=password_hash,
            api_key=api_key
        )
        
        session.add(new_user)
        await session.commit()
        
        print()
        print("✅ 用户创建成功!")
        print("-" * 50)
        print(f"用户ID: {user_id}")
        print(f"用户名: {username}")
        print(f"API Key: {api_key}")
        print("-" * 50)
        print()
        print("请妥善保管 API Key,它将用于 API 调用认证。")
    
    await engine.dispose()

if __name__ == "__main__":
    try:
        asyncio.run(create_user())
    except KeyboardInterrupt:
        print("\n\n操作已取消")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)
