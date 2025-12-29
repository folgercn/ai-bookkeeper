import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "FamilyAccounting"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "yoursecretkeyatleast32characterslongforsecurity"

    # 数据库
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/accounting.db"

    # LLM 配置 - OpenRouter
    LLM_PROVIDER: str = "openrouter"
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "openai/gpt-4o"

    # 安全配置
    RATE_LIMIT_PER_MINUTE: int = 60
    API_KEY_LENGTH: int = 32
    JWT_EXPIRE_MINUTES: int = 1440
    
    # 个人使用限制
    ENABLE_REGISTRATION: bool = False  # 禁用公开注册
    MAX_USERS: int = 5  # 最大用户数限制

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
