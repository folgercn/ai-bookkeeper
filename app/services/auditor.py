from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
from app.models.tables import Expense
from app.utils.hash import generate_hash_id

class Auditor:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_duplicates(self, user_id: str, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量检查条目是否重复
        为每个条目添加 is_duplicate 标志和 hash_id
        """
        for item in items:
            h_id = generate_hash_id(
                user_id=user_id,
                date=item.get("date"),
                amount=item.get("amount"),
                remark=item.get("remark"),
                payee=item.get("payee")
            )
            item["hash_id"] = h_id
            
            # 检查数据库中是否存在该 hash_id
            result = await self.db.execute(
                select(Expense).where(
                    Expense.user_id == user_id,
                    Expense.hash_id == h_id
                )
            )
            if result.scalar_one_or_none():
                item["is_duplicate"] = True
            else:
                item["is_duplicate"] = False
        
        return items
