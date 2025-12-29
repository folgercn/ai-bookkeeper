# API 接口文档

本文档描述了 Magical Accounting 系统的所有 API 接口，供 LLM 理解和使用。

---

## 认证接口 (auth.py)

### POST /v1/auth/register
**功能**：用户注册
**请求体**：
```json
{
  "username": "string",
  "password": "string"
}
```
**响应**：
```json
{
  "success": true,
  "data": {
    "api_key": "fa_xxxxxxxx",
    "username": "string"
  },
  "message": "注册成功"
}
```

### POST /v1/auth/login
**功能**：用户登录
**请求体**：
```json
{
  "username": "string",
  "password": "string"
}
```
**响应**：同注册接口

---

## 记账接口 (record.py)

### POST /v1/record
**功能**：提交记账内容（文字或图片）
**请求头**：`Authorization: Bearer {api_key}`
**请求体**：
```json
{
  "type": "text|image",
  "content": "string (文字内容或 base64 图片)"
}
```
**响应**：
```json
{
  "success": true,
  "data": {
    "batch_id": "string",
    "items": [
      {
        "temp_id": "string",
        "data": {
          "date": "2025-12-26",
          "amount": 50.0,
          "main_category": "餐饮",
          "sub_category": "外卖",
          "payee": "美团",
          "consumer": "老婆",
          "remark": "午餐"
        },
        "status": "pending"
      }
    ]
  }
}
```

### POST /v1/record/interact
**功能**：对话式修改暂存记录
**请求头**：`Authorization: Bearer {api_key}`
**请求体**：
```json
{
  "batch_id": "string",
  "instruction": "全部确认 | 1金额改为80 | 删除2"
}
```
**响应**：
```json
{
  "success": true,
  "data": {
    "remaining_pending": 0,
    "items": []
  }
}
```

---

## 账单管理接口 (expenses.py)

### GET /v1/expenses/summary
**功能**：获取本月和本年支出统计
**请求头**：`Authorization: Bearer {api_key}`
**响应**：
```json
{
  "success": true,
  "data": {
    "month_total": 12877.00,
    "year_total": 228201.61
  }
}
```

### GET /v1/expenses
**功能**：查询账单列表（支持筛选和分页）
**请求头**：`Authorization: Bearer {api_key}`
**查询参数**：
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认20，最大100）
- `start_date`: 开始日期（YYYY-MM-DD）
- `end_date`: 结束日期（YYYY-MM-DD）
- `main_category`: 一级分类
- `keyword`: 关键词（搜索备注、商户、消费人）

**响应**：
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "date": "2025-12-26",
        "amount": 50.0,
        "main_category": "餐饮",
        "sub_category": "外卖",
        "payee": "美团",
        "consumer": "老婆",
        "remark": "午餐",
        "is_essential": 1,
        "linked_asset": null
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 100,
      "total_pages": 5
    },
    "summary": {
      "total_amount": 5000.0,
      "category_breakdown": {
        "餐饮": 2000.0,
        "交通": 500.0
      }
    }
  }
}
```

### PUT /v1/expenses/{expense_id}
**功能**：更新单条账单记录
**请求头**：`Authorization: Bearer {api_key}`
**请求体**：
```json
{
  "date": "2025-12-26",
  "amount": 55.0,
  "main_category": "餐饮",
  "sub_category": "外卖",
  "payee": "美团",
  "consumer": "老婆",
  "remark": "午餐"
}
```
**响应**：
```json
{
  "success": true,
  "data": { /* 更新后的记录 */ },
  "message": "更新成功"
}
```

### DELETE /v1/expenses/{expense_id}
**功能**：删除单条账单记录
**请求头**：`Authorization: Bearer {api_key}`
**响应**：
```json
{
  "success": true,
  "message": "删除成功"
}
```

---

## 配置管理接口 (config.py)

### GET /v1/config/payees
**功能**：获取用户的成员列表
**请求头**：`Authorization: Bearer {api_key}`
**响应**：
```json
{
  "success": true,
  "data": [
    {"id": 1, "name": "老婆"},
    {"id": 2, "name": "老公"}
  ]
}
```

### POST /v1/config/payees
**功能**：添加成员
**请求体**：`{"name": "儿子"}`

### DELETE /v1/config/payees/{id}
**功能**：删除成员

### GET /v1/config/assets
**功能**：获取用户的资产列表
**响应**：同成员列表

### POST /v1/config/assets
**功能**：添加资产
**请求体**：`{"name": "支付宝"}`

### DELETE /v1/config/assets/{id}
**功能**：删除资产

### POST /v1/config/categories/init
**功能**：初始化默认分类（13个标准分类）

---

## 导出接口 (export.py)

### GET /v1/export/csv
**功能**：导出账单为 CSV 文件
**请求头**：`Authorization: Bearer {api_key}`
**响应**：CSV 文件下载
**字段**：日期、一级分类、二级分类、支出、参与人、备注

---

## 标准分类列表

系统内置 13 个标准一级分类：
1. 餐饮
2. 交通
3. 购物
4. 居家
5. 教育
6. 医疗
7. 人情
8. 旅游
9. 休闲娱乐
10. 个人护理
11. 通讯
12. 运动
13. 其他

---

## 错误响应格式

所有接口在出错时返回：
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述"
  }
}
```

常见错误码：
- `UNAUTHORIZED`: 未授权（API Key 无效）
- `NOT_FOUND`: 资源不存在
- `VALIDATION_ERROR`: 参数验证失败
- `INTERNAL_ERROR`: 服务器内部错误
