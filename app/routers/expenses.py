from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, delete as sql_delete
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from app.models.database import get_db
from app.models.tables import User, Expense
from app.models.schemas import SuccessResponse
from app.middleware.auth import verify_api_key

router = APIRouter(prefix="/expenses", tags=["expenses"])

# 更新记录的请求模型
class ExpenseUpdate(BaseModel):
    date: Optional[str] = None
    amount: Optional[float] = None
    main_category: Optional[str] = None
    sub_category: Optional[str] = None
    payee: Optional[str] = None
    consumer: Optional[str] = None
    remark: Optional[str] = None
    is_essential: Optional[int] = None
    linked_asset: Optional[str] = None

@router.get("/summary", response_model=SuccessResponse)
async def get_expenses_summary(
    user: User = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    now = datetime.now()
    current_month_prefix = now.strftime("%Y-%m-")
    current_year_prefix = now.strftime("%Y-")

    # 本月支出
    month_query = select(func.sum(Expense.amount)).where(
        Expense.user_id == user.id,
        Expense.date.like(f"{current_month_prefix}%")
    )
    # 本年支出
    year_query = select(func.sum(Expense.amount)).where(
        Expense.user_id == user.id,
        Expense.date.like(f"{current_year_prefix}%")
    )

    month_result = await db.execute(month_query)
    year_result = await db.execute(year_query)

    return SuccessResponse(data={
        "month_total": float(month_result.scalar() or 0.0),
        "year_total": float(year_result.scalar() or 0.0)
    })

@router.get("", response_model=SuccessResponse)
async def list_expenses(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    main_category: Optional[str] = None,
    payee: Optional[str] = None,
    keyword: Optional[str] = None,  # 新增：关键词搜索
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: User = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    # 构建查询
    query = select(Expense).where(Expense.user_id == user.id)
    
    if start_date:
        query = query.where(Expense.date >= start_date)
    if end_date:
        query = query.where(Expense.date <= end_date)
    if main_category:
        query = query.where(Expense.main_category == main_category)
    if payee:
        query = query.where(Expense.payee == payee)
    if keyword:
        # 在备注、商户、消费人中搜索关键词
        query = query.where(
            (Expense.remark.like(f"%{keyword}%")) |
            (Expense.payee.like(f"%{keyword}%")) |
            (Expense.consumer.like(f"%{keyword}%"))
        )

    # 计算总数
    count_query = select(func.count()).select_from(query.subquery())
    total_count = await db.execute(count_query)
    total = total_count.scalar()

    # 分页和排序
    query = query.order_by(Expense.date.desc(), Expense.id.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    items = result.scalars().all()

    # 统计汇总
    summary_query = select(
        func.sum(Expense.amount),
        Expense.main_category
    ).where(Expense.user_id == user.id).group_by(Expense.main_category)
    
    # 同样应用日期过滤
    if start_date: summary_query = summary_query.where(Expense.date >= start_date)
    if end_date: summary_query = summary_query.where(Expense.date <= end_date)
    
    summary_result = await db.execute(summary_query)
    category_summary = {row[1]: row[0] for row in summary_result.all()}
    total_amount = sum(category_summary.values())

    return SuccessResponse(data={
        "items": [
            {
                "id": i.id,
                "date": i.date,
                "amount": i.amount,
                "main_category": i.main_category,
                "sub_category": i.sub_category,
                "payee": i.payee,
                "consumer": i.consumer,
                "remark": i.remark,
                "is_essential": i.is_essential,
                "linked_asset": i.linked_asset
            } for i in items
        ],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size
        },
        "summary": {
            "total_amount": float(total_amount),
            "category_breakdown": {k: float(v) for k, v in category_summary.items()}
        }
    })

@router.put("/{expense_id}", response_model=SuccessResponse)
async def update_expense(
    expense_id: int,
    data: ExpenseUpdate,
    user: User = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """更新单条记录"""
    # 查找记录
    query = select(Expense).where(
        Expense.id == expense_id,
        Expense.user_id == user.id
    )
    result = await db.execute(query)
    expense = result.scalar_one_or_none()
    
    if not expense:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    # 更新字段
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(expense, key, value)
    
    await db.commit()
    await db.refresh(expense)
    
    return SuccessResponse(message="更新成功", data={
        "id": expense.id,
        "date": expense.date,
        "amount": expense.amount,
        "main_category": expense.main_category,
        "sub_category": expense.sub_category,
        "payee": expense.payee,
        "consumer": expense.consumer,
        "remark": expense.remark,
        "is_essential": expense.is_essential,
        "linked_asset": expense.linked_asset
    })

@router.delete("/{expense_id}", response_model=SuccessResponse)
async def delete_expense(
    expense_id: int,
    user: User = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    """删除单条记录"""
    # 查找并删除
    query = sql_delete(Expense).where(
        Expense.id == expense_id,
        Expense.user_id == user.id
    )
    result = await db.execute(query)
    await db.commit()
    
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    return SuccessResponse(message="删除成功")
