from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime, Text, Index, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    api_key: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_users_api_key", "api_key"),
    )

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    main_name: Mapped[str] = mapped_column(String, nullable=False)
    sub_name: Mapped[str] = mapped_column(String, nullable=False)
    keywords: Mapped[Optional[str]] = mapped_column(String)  # 逗号分隔
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "main_name", "sub_name"),
        Index("idx_categories_user", "user_id"),
    )

class Payee(Base):
    __tablename__ = "payees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "name"),
    )

class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "name"),
    )

class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date: Mapped[str] = mapped_column(String, nullable=False)  # YYYY-MM-DD
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    main_category: Mapped[str] = mapped_column(String, nullable=False)
    sub_category: Mapped[Optional[str]] = mapped_column(String)
    payee: Mapped[Optional[str]] = mapped_column(String)
    remark: Mapped[Optional[str]] = mapped_column(String)
    consumer: Mapped[Optional[str]] = mapped_column(String)
    is_essential: Mapped[int] = mapped_column(Integer, default=0)
    linked_asset: Mapped[Optional[str]] = mapped_column(String)
    hash_id: Mapped[str] = mapped_column(String, nullable=False)
    source_channel: Mapped[Optional[str]] = mapped_column(String)
    original_input: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "hash_id"),
        Index("idx_expenses_user_date", "user_id", "date"),
        Index("idx_expenses_category", "user_id", "main_category"),
    )

class StagingArea(Base):
    __tablename__ = "staging_area"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    batch_id: Mapped[str] = mapped_column(String, nullable=False)
    temp_id: Mapped[int] = mapped_column(Integer, nullable=False)
    parsed_json: Mapped[str] = mapped_column(Text, nullable=False)
    is_duplicate: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String, default="pending")  # pending/confirmed/rejected/expired
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_staging_user_batch", "user_id", "batch_id"),
    )
