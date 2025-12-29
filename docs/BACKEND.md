# 后端服务文档

本文档描述了后端 Python 代码的主要模块和函数，供 LLM 理解和维护。

---

## 项目结构

```
app/
├── main.py                 # FastAPI 应用入口
├── config.py              # 配置管理
├── models/                # 数据模型
│   ├── database.py       # 数据库连接
│   ├── tables.py         # ORM 模型
│   └── schemas.py        # Pydantic 模型
├── routers/              # API 路由
│   ├── auth.py          # 认证接口
│   ├── record.py        # 记账接口
│   ├── expenses.py      # 账单管理
│   ├── export.py        # 数据导出
│   └── config.py        # 配置管理
├── services/            # 业务逻辑
│   ├── llm_parser.py   # AI 解析服务
│   ├── instruction_parser.py  # 指令解析
│   └── batch_manager.py       # 批次管理
├── middleware/          # 中间件
│   └── auth.py         # 认证中间件
└── utils/              # 工具函数
    └── audit_logger.py # 审计日志
```

---

## 核心模块

### main.py
**功能**：FastAPI 应用入口
**主要内容**：
- 创建 FastAPI 应用实例
- 注册路由
- 配置 CORS
- 静态文件服务

```python
app = FastAPI(title="Magical Accounting API")
app.add_middleware(CORSMiddleware, ...)
app.include_router(auth_router)
app.include_router(record_router)
app.include_router(expenses_router)
app.include_router(export_router)
app.include_router(config_router)
```

### config.py
**功能**：配置管理
**主要变量**：
- `OPENROUTER_BASE_URL`: OpenRouter API 地址
- `OPENROUTER_API_KEY`: OpenRouter API 密钥
- `DATABASE_URL`: 数据库连接字符串
- `APP_NAME`: 应用名称

---

## 数据模型 (models/)

### tables.py - ORM 模型

#### User
**字段**：
- `id`: 主键
- `username`: 用户名（唯一）
- `password_hash`: 密码哈希
- `api_key`: API 密钥（唯一）
- `created_at`: 创建时间
- `updated_at`: 更新时间

#### Expense
**字段**：
- `id`: 主键
- `user_id`: 用户 ID（外键）
- `date`: 交易日期
- `amount`: 金额
- `main_category`: 一级分类
- `sub_category`: 二级分类
- `payee`: 商户/收款方
- `consumer`: 消费人
- `remark`: 备注
- `is_essential`: 是否必需品
- `linked_asset`: 关联资产
- `hash_id`: 哈希 ID（防重复）
- `source_channel`: 来源渠道
- `original_input`: 原始输入
- `created_at`: 创建时间

#### Category
**字段**：
- `id`: 主键
- `user_id`: 用户 ID
- `main_category`: 一级分类
- `sub_category`: 二级分类
- `created_at`: 创建时间

#### Payee
**字段**：
- `id`: 主键
- `user_id`: 用户 ID
- `name`: 成员名称
- `created_at`: 创建时间

#### Asset
**字段**：
- `id`: 主键
- `user_id`: 用户 ID
- `name`: 资产名称
- `created_at`: 创建时间

#### StagingArea
**字段**：
- `id`: 主键
- `batch_id`: 批次 ID
- `user_id`: 用户 ID
- `temp_id`: 临时 ID
- `data`: JSON 数据
- `status`: 状态（pending/confirmed/expired）
- `created_at`: 创建时间

### schemas.py - Pydantic 模型

#### SuccessResponse
```python
class SuccessResponse(BaseModel):
    success: bool = True
    data: Optional[Any] = None
    message: str = "操作成功"
```

#### ErrorResponse
```python
class ErrorResponse(BaseModel):
    success: bool = False
    error: dict
```

---

## 路由模块 (routers/)

### auth.py - 认证接口

#### `register(username, password, db)`
**功能**：用户注册
**流程**：
1. 检查用户名是否已存在
2. 生成密码哈希
3. 生成 API Key
4. 创建用户记录
5. 返回 API Key

#### `login(username, password, db)`
**功能**：用户登录
**流程**：
1. 查找用户
2. 验证密码
3. 返回 API Key

### record.py - 记账接口

#### `submit_record(type, content, user, db)`
**功能**：提交记账内容
**参数**：
- `type`: 输入类型（text/image）
- `content`: 内容（文字或 base64 图片）
- `user`: 当前用户
- `db`: 数据库会话
**流程**：
1. 调用 LLMParser 解析内容
2. 创建批次 ID
3. 保存到暂存区
4. 返回解析结果

#### `interact(batch_id, instruction, user, db)`
**功能**：对话式修改暂存记录
**参数**：
- `batch_id`: 批次 ID
- `instruction`: 用户指令
- `user`: 当前用户
- `db`: 数据库会话
**流程**：
1. 获取暂存记录
2. 调用 InstructionParser 解析指令
3. 执行修改/删除/确认操作
4. 返回剩余待确认数量

### expenses.py - 账单管理

#### `get_expenses_summary(user, db)`
**功能**：获取本月和本年支出统计
**返回**：`{month_total, year_total}`

#### `list_expenses(params, user, db)`
**功能**：查询账单列表
**参数**：
- `start_date`: 开始日期
- `end_date`: 结束日期
- `main_category`: 一级分类
- `keyword`: 关键词
- `page`: 页码
- `page_size`: 每页数量
**返回**：`{items, pagination, summary}`

#### `update_expense(expense_id, data, user, db)`
**功能**：更新单条账单
**流程**：
1. 查找记录
2. 验证权限
3. 更新字段
4. 提交事务

#### `delete_expense(expense_id, user, db)`
**功能**：删除单条账单
**流程**：
1. 查找记录
2. 验证权限
3. 删除记录
4. 提交事务

### export.py - 数据导出

#### `export_csv(user, db)`
**功能**：导出账单为 CSV
**流程**：
1. 查询所有账单
2. 生成 CSV 内容
3. 添加 UTF-8 BOM
4. 返回文件响应

### config.py - 配置管理

#### `get_payees(user, db)`
**功能**：获取成员列表

#### `add_payee(name, user, db)`
**功能**：添加成员

#### `delete_payee(id, user, db)`
**功能**：删除成员

#### `get_assets(user, db)`
**功能**：获取资产列表

#### `add_asset(name, user, db)`
**功能**：添加资产

#### `delete_asset(id, user, db)`
**功能**：删除资产

#### `init_categories(user, db)`
**功能**：初始化默认分类
**流程**：
1. 检查是否已初始化
2. 批量插入 13 个标准分类
3. 提交事务

---

## 服务模块 (services/)

### llm_parser.py - AI 解析服务

#### `class LLMParser`

##### `parse_text(text, user_id, db)`
**功能**：解析文字输入
**流程**：
1. 获取用户配置（分类、成员、资产）
2. 构建系统提示词
3. 调用 OpenRouter API
4. 解析 JSON 响应
5. 记录审计日志
6. 返回解析结果

##### `parse_image(image_base64, user_id, db)`
**功能**：解析图片输入
**流程**：
1. 获取用户配置
2. 构建包含图片的提示词
3. 调用 OpenRouter API（vision 模型）
4. 解析 JSON 响应
5. 记录审计日志
6. 返回解析结果

### instruction_parser.py - 指令解析

#### `class InstructionParser`

##### `parse_instruction(instruction, items)`
**功能**：解析用户指令
**参数**：
- `instruction`: 用户输入的指令
- `items`: 当前暂存记录列表
**流程**：
1. 构建提示词
2. 调用 OpenRouter API
3. 解析 JSON 响应
4. 返回操作列表

**支持的操作类型**：
- `confirm`: 确认记录
- `modify`: 修改记录
- `delete`: 删除记录

### batch_manager.py - 批次管理

#### `class BatchManager`

##### `create_batch(user_id, items, db)`
**功能**：创建暂存批次
**流程**：
1. 生成批次 ID
2. 为每条记录生成临时 ID
3. 保存到 StagingArea 表
4. 返回批次信息

##### `apply_actions(batch_id, actions, db)`
**功能**：应用操作到暂存记录
**参数**：
- `batch_id`: 批次 ID
- `actions`: 操作列表
**流程**：
1. 遍历操作列表
2. 根据操作类型执行：
   - confirm: 移动到 Expense 表
   - modify: 更新暂存记录
   - delete: 删除暂存记录
3. 返回剩余待确认数量

---

## 中间件 (middleware/)

### auth.py - 认证中间件

#### `verify_api_key(authorization, db)`
**功能**：验证 API Key
**参数**：
- `authorization`: Authorization 头（Bearer token）
- `db`: 数据库会话
**流程**：
1. 提取 API Key
2. 查询用户
3. 返回用户对象或抛出 401 错误

---

## 工具模块 (utils/)

### audit_logger.py - 审计日志

#### `log_llm_interaction(user_id, input_type, input_content, output, db)`
**功能**：记录 LLM 交互日志
**参数**：
- `user_id`: 用户 ID
- `input_type`: 输入类型（text/image）
- `input_content`: 输入内容
- `output`: LLM 输出
- `db`: 数据库会话

---

## 数据库操作

### 连接管理
```python
# database.py
async def get_db():
    async with async_session() as session:
        yield session
```

### 查询示例
```python
# 查询账单
query = select(Expense).where(Expense.user_id == user.id)
result = await db.execute(query)
items = result.scalars().all()

# 插入记录
expense = Expense(**data)
db.add(expense)
await db.commit()
await db.refresh(expense)

# 更新记录
expense.amount = 100
await db.commit()

# 删除记录
await db.execute(delete(Expense).where(Expense.id == id))
await db.commit()
```

---

## 环境变量

必需的环境变量（.env 文件）：
```env
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_API_KEY=sk-or-xxx
DATABASE_URL=sqlite+aiosqlite:///./data/accounting.db
APP_NAME=Magical Accounting
```

---

## 启动流程

1. 加载环境变量
2. 初始化数据库连接
3. 创建 FastAPI 应用
4. 注册路由和中间件
5. 启动 Uvicorn 服务器

```bash
uvicorn app.main:app --port 8000 --reload
```

---

## 注意事项

1. **异步操作**：所有数据库操作都是异步的，需要使用 `await`
2. **事务管理**：修改操作后需要 `await db.commit()`
3. **错误处理**：使用 `HTTPException` 抛出 HTTP 错误
4. **密码安全**：使用 bcrypt 哈希密码
5. **API Key 生成**：使用 `secrets.token_urlsafe()` 生成随机密钥
