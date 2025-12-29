from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List

from app.models.database import get_db
from app.models.tables import User, Category, Payee, Asset
from app.models.schemas import SuccessResponse, ConfigItem
from app.middleware.auth import verify_api_key

router = APIRouter(prefix="/config", tags=["config"])

DEFAULT_CATEGORIES = [
    ("餐饮", "外卖", "美团,饿了么,外卖"),
    ("餐饮", "堂食", "餐厅,饭店"),
    ("餐饮", "食材采购", "买菜,超市,菜市场"),
    ("餐饮", "零食饮料", "零食,饮料,奶茶,咖啡"),
    ("交通", "交通工具", "打车,公交,地铁,打车,滴滴"),
    ("交通", "私家车", "加油,充电,停车,保养,洗车"),
    ("购物", "日用品", "日用品,纸巾,超市"),
    ("购物", "数码电器", "手机,电脑,家电,显卡"),
    ("购物", "服饰鞋包", "衣服,鞋子,包包"),
    ("居家", "生活缴费", "水电燃气,话费,物业,房租"),
    ("居家", "居家用品", "家具,家纺"),
    ("教育", "学杂费", "学费,补课,书本"),
    ("教育", "零花钱", "零花钱,压岁钱"),
    ("医疗", "医疗健康", "看病,挂号,买药,体检"),
    ("人情", "人情往来", "红包,礼金,礼物,送礼"),
    ("旅游", "旅游差旅", "机票,酒店,门票,火车,高铁"),
    ("休闲娱乐", "休闲娱乐", "电影,游戏,KTV,健身"),
    ("休闲娱乐", "兴趣爱好", "3D打印,摄影,模型"),
    ("个人护理", "个人护理", "理发,美容,护肤"),
    ("通讯", "通讯费", "话费,流量,宽带"),
    ("运动", "赛事活动", "马拉松,半马,全马,报名"),
    ("运动", "运动装备", "跑鞋,运动服"),
    ("其他", "未分类", ""),
]

async def init_user_defaults(user_id: str, db: AsyncSession):
    """初始化默认分类"""
    # 检查是否已有分类
    result = await db.execute(select(Category).where(Category.user_id == user_id))
    if result.scalars().first():
        return

    categories = [
        Category(user_id=user_id, main_name=m, sub_name=s, keywords=k)
        for m, s, k in DEFAULT_CATEGORIES
    ]
    db.add_all(categories)
    await db.commit()

@router.get("/categories", response_model=SuccessResponse)
async def get_categories(user: User = Depends(verify_api_key), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).where(Category.user_id == user.id))
    items = result.scalars().all()
    return SuccessResponse(data=[{
        "id": i.id,
        "main_name": i.main_name,
        "sub_name": i.sub_name,
        "keywords": i.keywords
    } for i in items])

@router.post("/categories/init", response_model=SuccessResponse)
async def force_init_categories(user: User = Depends(verify_api_key), db: AsyncSession = Depends(get_db)):
    await init_user_defaults(user.id, db)
    return SuccessResponse(message="初始分类已生成")

# 成员管理 (Payees)
@router.get("/payees", response_model=SuccessResponse)
async def get_payees(user: User = Depends(verify_api_key), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Payee).where(Payee.user_id == user.id))
    items = result.scalars().all()
    return SuccessResponse(data=[{"id": i.id, "name": i.name} for i in items])

@router.post("/payees", response_model=SuccessResponse)
async def add_payee(req: ConfigItem, user: User = Depends(verify_api_key), db: AsyncSession = Depends(get_db)):
    # 检查是否重复
    check = await db.execute(select(Payee).where(Payee.user_id == user.id, Payee.name == req.name))
    if check.scalar():
        return SuccessResponse(message="该成员已存在", success=False)
    
    item = Payee(user_id=user.id, name=req.name)
    db.add(item)
    await db.commit()
    return SuccessResponse(message="添加成功", data={"id": item.id, "name": item.name})

@router.post("/payees", response_model=SuccessResponse)
async def add_payee(req: ConfigItem, user: User = Depends(verify_api_key), db: AsyncSession = Depends(get_db)):
    # 检查是否重复
    check = await db.execute(select(Payee).where(Payee.user_id == user.id, Payee.name == req.name))
    if check.scalar():
        return SuccessResponse(message="该成员已存在", success=False)
    
    item = Payee(user_id=user.id, name=req.name)
    db.add(item)
    await db.commit()
    return SuccessResponse(message="添加成功", data={"id": item.id, "name": item.name})

@router.delete("/payees/{payee_id}", response_model=SuccessResponse)
async def delete_payee(payee_id: int, user: User = Depends(verify_api_key), db: AsyncSession = Depends(get_db)):
    await db.execute(delete(Payee).where(Payee.user_id == user.id, Payee.id == payee_id))
    await db.commit()
    return SuccessResponse(message="已删除")

# 资产管理 (Assets)
@router.get("/assets", response_model=SuccessResponse)
async def get_assets(user: User = Depends(verify_api_key), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Asset).where(Asset.user_id == user.id))
    items = result.scalars().all()
    return SuccessResponse(data=[{"id": i.id, "name": i.name} for i in items])

@router.post("/assets", response_model=SuccessResponse)
async def add_asset(req: ConfigItem, user: User = Depends(verify_api_key), db: AsyncSession = Depends(get_db)):
    check = await db.execute(select(Asset).where(Asset.user_id == user.id, Asset.name == req.name))
    if check.scalar():
        return SuccessResponse(message="该资产已存在", success=False)
    
    item = Asset(user_id=user.id, name=req.name)
    db.add(item)
    await db.commit()
    return SuccessResponse(message="添加成功", data={"id": item.id, "name": item.name})

@router.delete("/assets/{asset_id}", response_model=SuccessResponse)
async def delete_asset(asset_id: int, user: User = Depends(verify_api_key), db: AsyncSession = Depends(get_db)):
    await db.execute(delete(Asset).where(Asset.user_id == user.id, Asset.id == asset_id))
    await db.commit()
    return SuccessResponse(message="已删除")
