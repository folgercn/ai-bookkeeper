from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Dict, Any

from app.models.tables import Category

class CategoryLearner:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def learn_from_correction(self, user_id: str, remark: str, main_name: str, sub_name: str):
        """
        当用户修改分类时，将备注作为关键词学习，提高下次识别准确率
        """
        if not remark or not main_name:
            return

        # 查找对应分类
        result = await self.db.execute(
            select(Category).where(
                Category.user_id == user_id,
                Category.main_name == main_name,
                Category.sub_name == sub_name
            )
        )
        category = result.scalar_one_or_none()
        
        if category:
            keywords = category.keywords.split(",") if category.keywords else []
            clean_remark = remark.strip()
            if clean_remark not in keywords:
                keywords.append(clean_remark)
                category.keywords = ",".join(keywords)
                # 标记已修改，后续 commit
