from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime
import csv
import io

from app.models.database import get_db
from app.models.tables import User, Expense
from app.middleware.auth import verify_api_key

router = APIRouter(prefix="/export", tags=["export"])

@router.get("/csv")
async def export_csv(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    main_category: Optional[str] = None,
    user: User = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    query = select(Expense).where(Expense.user_id == user.id)
    if start_date: query = query.where(Expense.date >= start_date)
    if end_date: query = query.where(Expense.date <= end_date)
    if main_category: query = query.where(Expense.main_category == main_category)
    
    query = query.order_by(Expense.date.desc())
    result = await db.execute(query)
    items = result.scalars().all()

    # 创建内存中的 CSV
    output = io.StringIO()
    # 添加 BOM (utf-8-sig) 以便 Excel 直接打开不乱码
    output.write('\ufeff')
    
    writer = csv.writer(output)
    writer.writerow(["日期", "一级分类", "二级分类", "支出", "参与人", "备注"])
    
    for i in items:
        writer.writerow([
            i.date,
            i.main_category,
            i.sub_category or "",
            f"{float(i.amount):.2f}",
            i.consumer or i.payee or "", # 优先显示消费人，无则显示商户
            i.remark or ""
        ])
    
    csv_content = output.getvalue()
    output.close()
    
    filename = f"expenses_{datetime.now().strftime('%Y%m%d%H%M')}.csv"
    
    return StreamingResponse(
        io.BytesIO(csv_content.encode("utf-8-sig")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
