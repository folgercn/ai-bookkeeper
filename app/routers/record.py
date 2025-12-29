import uuid
import json
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from typing import List

from app.models.database import get_db
from app.models.tables import User, StagingArea, Expense, Category, Payee, Asset
from app.models.schemas import RecordRequest, RecordResponse, SuccessResponse, ConfirmRequest, StagingItem, InteractionRequest
from app.middleware.auth import verify_api_key
from app.services.llm_parser import LLMParser
from app.services.auditor import Auditor
from app.services.instruction_parser import InstructionParser
from app.services.batch_manager import BatchManager
from app.utils.image import validate_and_resize_image

router = APIRouter(prefix="/record", tags=["record"])

@router.post("", response_model=SuccessResponse)
async def post_record(
    req: RecordRequest, 
    user: User = Depends(verify_api_key), 
    db: AsyncSession = Depends(get_db)
):
    parser = LLMParser()
    auditor = Auditor(db)
    
    # 1. 获取用户分类以辅助解析
    cat_result = await db.execute(select(Category).where(Category.user_id == user.id))
    user_categories = [{"main": c.main_name, "sub": c.sub_name, "keywords": c.keywords} for c in cat_result.scalars().all()]
    
    payee_result = await db.execute(select(Payee).where(Payee.user_id == user.id))
    user_payees = [p.name for p in payee_result.scalars().all()]

    asset_result = await db.execute(select(Asset).where(Asset.user_id == user.id))
    user_assets = [a.name for a in asset_result.scalars().all()]
    
    # 2. 调用 LLM 解析
    if req.type == "text":
        items = await parser.parse(req.content, user_categories, user_payees=user_payees, user_assets=user_assets, user_id=user.id)
    else:
        # 处理图片
        compressed_b64, mime = validate_and_resize_image(req.content)
        items = await parser.parse_image(compressed_b64, mime, user_categories, user_payees=user_payees, user_assets=user_assets, user_id=user.id)
    
    if not items:
        return SuccessResponse(message="未识别到任何消费条目", data={"items": []})
    
    # 3. 审计去重
    items_with_meta = await auditor.check_duplicates(user.id, items)
    
    # 4. 写入暂存区
    batch_id = str(uuid.uuid4())
    staging_entries = []
    for idx, item in enumerate(items_with_meta):
        temp_id = idx + 1
        entry = StagingArea(
            user_id=user.id,
            batch_id=batch_id,
            temp_id=temp_id,
            parsed_json=json.dumps(item, ensure_ascii=False),
            is_duplicate=1 if item.get("is_duplicate") else 0,
            status="pending"
        )
        staging_entries.append(entry)
        item["temp_id"] = temp_id # 回传给前端
    
    db.add_all(staging_entries)
    await db.commit()
    
    return SuccessResponse(data={
        "batch_id": batch_id,
        "items": items_with_meta,
        "summary": f"共识别出 {len(items_with_meta)} 条记录"
    })

@router.post("/confirm", response_model=SuccessResponse)
async def confirm_record(
    req: ConfirmRequest,
    user: User = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    if req.action == "confirm_all":
        # 批量入库
        result = await db.execute(
            select(StagingArea).where(
                StagingArea.user_id == user.id,
                StagingArea.batch_id == req.batch_id,
                StagingArea.status == "pending"
            )
        )
        entries = result.scalars().all()
        confirmed_count = 0
        for entry in entries:
            item_data = json.loads(entry.parsed_json)
            # 写入正式表
            expense = Expense(
                user_id=user.id,
                date=item_data.get("date"),
                amount=item_data.get("amount"),
                main_category=item_data.get("main_category"),
                sub_category=item_data.get("sub_category"),
                payee=item_data.get("payee"),
                remark=item_data.get("remark"),
                consumer=item_data.get("consumer"),
                is_essential=item_data.get("is_essential", 0),
                linked_asset=item_data.get("linked_asset"),
                hash_id=item_data.get("hash_id"),
                source_channel="api",
                original_input=None
            )
            db.add(expense)
            entry.status = "confirmed"
            confirmed_count += 1
        
        await db.commit()
        return SuccessResponse(data={"confirmed_count": confirmed_count})

    elif req.action == "reject_all":
        await db.execute(
            update(StagingArea)
            .where(StagingArea.user_id == user.id, StagingArea.batch_id == req.batch_id)
            .values(status="rejected")
        )
        await db.commit()
        return SuccessResponse(message="已全部取消")

@router.post("/interact", response_model=SuccessResponse)
async def interact_record(
    req: InteractionRequest,
    user: User = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    parser = LLMParser()
    instr_parser = InstructionParser(parser)
    batch_manager = BatchManager(db)
    
    # 1. 获取上下文
    context = await batch_manager.get_batch_context(user.id, req.batch_id)
    
    payee_result = await db.execute(select(Payee).where(Payee.user_id == user.id))
    context["user_payees"] = [p.name for p in payee_result.scalars().all()]

    asset_result = await db.execute(select(Asset).where(Asset.user_id == user.id))
    context["user_assets"] = [a.name for a in asset_result.scalars().all()]
    
    context["user_id"] = user.id
    
    # 2. 解析指令
    actions = await instr_parser.parse_instruction(req.instruction, context)
    
    if not actions:
        return SuccessResponse(message="未能理解您的指令，请换种说法试试", success=False)
    
    # 3. 执行操作
    await batch_manager.apply_actions(user.id, req.batch_id, actions)
    
    # 4. 返回最新状态
    new_context = await batch_manager.get_batch_context(user.id, req.batch_id)
    pending_count = len([i for i in new_context["items"] if i["status"] == "pending"])
    
    return SuccessResponse(data={
        "actions_executed": [a["type"] for a in actions],
        "remaining_pending": pending_count,
        "items": new_context["items"]
    }, message="指令执行成功")
