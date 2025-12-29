from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import Dict, Any, List
import json

from app.models.tables import StagingArea, Expense, Category
from app.utils.hash import generate_hash_id

class BatchManager:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_batch_context(self, user_id: str, batch_id: str) -> Dict[str, Any]:
        """获取用于 LLM 解析的批次上下文"""
        # 获取暂存条目
        result = await self.db.execute(
            select(StagingArea).where(
                StagingArea.user_id == user_id,
                StagingArea.batch_id == batch_id
            )
        )
        entries = result.scalars().all()
        
        # 获取用户分类
        cat_result = await self.db.execute(
            select(Category).where(Category.user_id == user_id)
        )
        categories = [{"main": c.main_name, "sub": c.sub_name} for c in cat_result.scalars().all()]

        return {
            "batch_id": batch_id,
            "items": [
                {
                    "temp_id": e.temp_id,
                    "status": e.status,
                    "data": json.loads(e.parsed_json)
                } for e in entries
            ],
            "categories": categories
        }

    async def apply_actions(self, user_id: str, batch_id: str, actions: List[Dict[str, Any]]):
        """执行解析后的操作序列"""
        for action in actions:
            action_type = action.get("type")
            targets = action.get("targets", [])

            if action_type == "confirm":
                await self._confirm_items(user_id, batch_id, targets)
            elif action_type == "modify":
                await self._modify_items(user_id, batch_id, targets, action.get("modifications", {}))
            elif action_type == "delete":
                await self._delete_items(user_id, batch_id, targets)
            elif action_type == "cancel_all":
                await self._cancel_batch(user_id, batch_id)
        
        await self.db.commit()

    async def _confirm_items(self, user_id: str, batch_id: str, temp_ids: List[int]):
        from app.services.category_learner import CategoryLearner
        learner = CategoryLearner(self.db)
        
        for tid in temp_ids:
            res = await self.db.execute(
                select(StagingArea).where(
                    StagingArea.user_id == user_id,
                    StagingArea.batch_id == batch_id,
                    StagingArea.temp_id == tid,
                    StagingArea.status == "pending"
                )
            )
            entry = res.scalar_one_or_none()
            if entry:
                data = json.loads(entry.parsed_json)
                
                # 只有当置信度低或者标记为已修改时，我们才触发强烈倾向的学习（这里简化为全部确认即学习）
                if data.get("remark") and data.get("main_category"):
                    await learner.learn_from_correction(
                        user_id, 
                        data["remark"], 
                        data["main_category"], 
                        data.get("sub_category")
                    )

                expense = Expense(
                    user_id=user_id,
                    date=data.get("date"),
                    amount=data.get("amount"),
                    main_category=data.get("main_category"),
                    sub_category=data.get("sub_category"),
                    payee=data.get("payee"),
                    remark=data.get("remark"),
                    consumer=data.get("consumer"),
                    is_essential=data.get("is_essential", 0),
                    linked_asset=data.get("linked_asset"),
                    hash_id=data.get("hash_id") or generate_hash_id(user_id, data.get("date"), data.get("amount"), data.get("remark"), data.get("payee")),
                    source_channel="interact"
                )
                self.db.add(expense)
                entry.status = "confirmed"

    async def _modify_items(self, user_id: str, batch_id: str, temp_ids: List[int], mods: Dict[str, Any]):
        for tid in temp_ids:
            res = await self.db.execute(
                select(StagingArea).where(
                    StagingArea.user_id == user_id,
                    StagingArea.batch_id == batch_id,
                    StagingArea.temp_id == tid
                )
            )
            entry = res.scalar_one_or_none()
            if entry:
                data = json.loads(entry.parsed_json)
                data.update(mods)
                # 重新计算 hash_id 以防修改了核心字段
                data["hash_id"] = generate_hash_id(user_id, data.get("date"), data.get("amount"), data.get("remark"), data.get("payee"))
                entry.parsed_json = json.dumps(data, ensure_ascii=False)

    async def _delete_items(self, user_id: str, batch_id: str, temp_ids: List[int]):
        await self.db.execute(
            update(StagingArea)
            .where(StagingArea.user_id == user_id, StagingArea.batch_id == batch_id, StagingArea.temp_id.in_(temp_ids))
            .values(status="rejected")
        )

    async def _cancel_batch(self, user_id: str, batch_id: str):
        await self.db.execute(
            update(StagingArea)
            .where(StagingArea.user_id == user_id, StagingArea.batch_id == batch_id)
            .values(status="rejected")
        )
