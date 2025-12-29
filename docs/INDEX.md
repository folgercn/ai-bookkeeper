# 项目索引

本文档提供了 Magical Accounting 项目的完整索引，帮助 LLM 快速定位和理解代码。

---

## 📂 目录结构

```
家庭记账/
├── app/                          # 后端应用
│   ├── main.py                  # FastAPI 应用入口
│   ├── config.py                # 配置管理
│   ├── models/                  # 数据模型
│   │   ├── database.py         # 数据库连接和会话管理
│   │   ├── tables.py           # SQLAlchemy ORM 模型定义
│   │   └── schemas.py          # Pydantic 请求/响应模型
│   ├── routers/                # API 路由
│   │   ├── auth.py            # 认证接口（登录/注册）
│   │   ├── record.py          # 记账接口（提交/对话修改）
│   │   ├── expenses.py        # 账单管理（查询/更新/删除）
│   │   ├── export.py          # 数据导出（CSV）
│   │   └── config.py          # 配置管理（分类/成员/资产）
│   ├── services/              # 业务逻辑
│   │   ├── llm_parser.py     # AI 解析服务（文字/图片）
│   │   ├── instruction_parser.py  # 对话指令解析
│   │   └── batch_manager.py       # 暂存批次管理
│   ├── middleware/            # 中间件
│   │   └── auth.py           # API Key 认证
│   └── utils/                # 工具函数
│       └── audit_logger.py   # 审计日志记录
├── frontend/                  # 前端应用
│   ├── index.html            # 主页面
│   ├── css/
│   │   └── style.css         # 样式文件（玻璃拟态设计）
│   └── js/
│       ├── api.js            # API 客户端封装
│       └── app.js            # 主要业务逻辑
├── prompts/                  # AI 提示词
│   └── system_prompt.md      # LLM 系统提示词模板
├── scripts/                  # 脚本
│   └── init_db.py           # 数据库初始化脚本
├── data/                     # 数据文件
│   └── accounting.db        # SQLite 数据库
├── docs/                     # 文档
│   ├── API.md               # API 接口文档
│   ├── FRONTEND.md          # 前端函数文档
│   ├── BACKEND.md           # 后端服务文档
│   └── INDEX.md             # 本文件
├── .env                      # 环境变量配置
├── .env.example             # 环境变量示例
├── requirements.txt         # Python 依赖
└── README.md                # 项目说明文档
```

---

## 🔍 快速查找

### 需要修改 AI 解析逻辑？
→ `app/services/llm_parser.py`
→ `prompts/system_prompt.md`

### 需要添加新的 API 接口？
→ `app/routers/` 目录下对应的路由文件
→ 在 `app/main.py` 中注册路由

### 需要修改数据库表结构？
→ `app/models/tables.py`
→ 修改后需要重新初始化数据库

### 需要修改前端 UI？
→ `frontend/index.html` - HTML 结构
→ `frontend/css/style.css` - 样式
→ `frontend/js/app.js` - 交互逻辑

### 需要修改 API 请求逻辑？
→ `frontend/js/api.js`

### 需要查看 API 文档？
→ `docs/API.md`
→ 或访问 http://127.0.0.1:8000/docs（Swagger UI）

---

## 📋 功能模块映射

### 用户认证
- **前端**：`frontend/js/app.js` - `handleAuth()`, `showApp()`, `logout()`
- **后端**：`app/routers/auth.py` - `register()`, `login()`
- **中间件**：`app/middleware/auth.py` - `verify_api_key()`

### 智能记账
- **前端**：`frontend/js/app.js` - `handleSubmit()`, `handleImageUpload()`
- **后端**：`app/routers/record.py` - `submit_record()`
- **AI 服务**：`app/services/llm_parser.py` - `parse_text()`, `parse_image()`

### 对话式纠错
- **前端**：`frontend/js/app.js` - `handleInteract()`, `confirmAll()`
- **后端**：`app/routers/record.py` - `interact()`
- **指令解析**：`app/services/instruction_parser.py` - `parse_instruction()`
- **批次管理**：`app/services/batch_manager.py` - `apply_actions()`

### 历史记录管理
- **前端**：`frontend/js/app.js` - `loadData()`, `renderExpenses()`, `applyFilters()`, `editExpense()`, `deleteExpense()`
- **后端**：`app/routers/expenses.py` - `list_expenses()`, `update_expense()`, `delete_expense()`

### 统计与导出
- **前端**：`frontend/js/app.js` - `loadData()`（加载统计）
- **后端**：
  - 统计：`app/routers/expenses.py` - `get_expenses_summary()`
  - 导出：`app/routers/export.py` - `export_csv()`

### 配置管理
- **前端**：`frontend/js/app.js` - `refreshPayees()`, `addPayee()`, `refreshAssets()`, `addAsset()`
- **后端**：`app/routers/config.py` - 成员和资产的 CRUD 接口

---

## 🗄️ 数据库表说明

| 表名 | 用途 | 关键字段 |
|-----|------|---------|
| `users` | 用户信息 | username, api_key |
| `expenses` | 账单记录 | date, amount, main_category, user_id |
| `categories` | 用户分类 | main_category, sub_category, user_id |
| `payees` | 成员列表 | name, user_id |
| `assets` | 资产列表 | name, user_id |
| `staging_area` | 暂存区 | batch_id, temp_id, data, status |

---

## 🔗 关键依赖

### 后端
- **FastAPI**: Web 框架
- **SQLAlchemy**: ORM
- **aiosqlite**: 异步 SQLite 驱动
- **httpx**: HTTP 客户端（调用 OpenRouter）
- **bcrypt**: 密码哈希
- **python-dotenv**: 环境变量管理

### 前端
- **Lucide Icons**: 图标库
- **原生 JavaScript**: 无框架依赖

---

## 🎯 常见任务

### 添加新的分类
1. 修改 `app/routers/config.py` 中的 `DEFAULT_CATEGORIES`
2. 更新 `prompts/system_prompt.md` 中的分类列表
3. 用户需要调用 `/config/categories/init` 初始化

### 修改 AI 提示词
1. 编辑 `prompts/system_prompt.md`
2. 重启后端服务即可生效

### 添加新的筛选条件
1. 后端：在 `app/routers/expenses.py` 的 `list_expenses()` 中添加参数
2. 前端：在 `frontend/index.html` 添加输入框
3. 前端：在 `frontend/js/app.js` 的 `applyFilters()` 中获取值

### 修改 UI 样式
1. 编辑 `frontend/css/style.css`
2. 刷新浏览器即可看到效果

---

## 📖 文档链接

- [README.md](file:///Users/fujun/node/家庭记账/README.md) - 项目说明和使用指南
- [API.md](file:///Users/fujun/node/家庭记账/docs/API.md) - API 接口文档
- [FRONTEND.md](file:///Users/fujun/node/家庭记账/docs/FRONTEND.md) - 前端函数文档
- [BACKEND.md](file:///Users/fujun/node/家庭记账/docs/BACKEND.md) - 后端服务文档

---

## 🚀 快速开始

### 开发环境设置
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 OPENROUTER_API_KEY

# 3. 初始化数据库
python scripts/init_db.py

# 4. 启动服务
uvicorn app.main:app --port 8000 --reload

# 5. 访问前端
open http://127.0.0.1:8000/frontend/index.html
```

### 调试技巧
- **查看 API 文档**：http://127.0.0.1:8000/docs
- **查看数据库**：使用 SQLite 客户端打开 `data/accounting.db`
- **查看日志**：终端输出包含所有 SQL 查询和 API 请求
- **前端调试**：浏览器开发者工具 Console 标签

---

## 💡 开发建议

1. **修改前先备份**：特别是数据库文件
2. **遵循现有代码风格**：保持一致性
3. **添加注释**：复杂逻辑需要注释说明
4. **测试后再提交**：确保功能正常
5. **更新文档**：修改后更新相关文档

---

> **最后更新**：2025-12-26
> **版本**：v1.2.0
