# 前端函数文档

本文档描述了前端 JavaScript 代码的主要函数和功能，供 LLM 理解和维护。

---

## 全局变量

```javascript
let currentBatchId = null;        // 当前暂存批次 ID
let currentMode = 'text';         // 当前输入模式：text|voice|image
let currentPage = 1;              // 当前页码
let totalPages = 1;               // 总页数
let filters = {                   // 筛选条件
    startDate: '',
    endDate: '',
    keyword: ''
};
let allExpenses = [];             // 当前加载的所有账单
let currentEditId = null;         // 当前编辑的账单 ID
```

---

## 认证相关函数

### `handleAuth()`
**功能**：处理登录/注册
**流程**：
1. 获取用户名和密码
2. 根据当前模式调用登录或注册 API
3. 保存 API Key 到 localStorage
4. 显示主应用界面

### `showApp()`
**功能**：显示主应用界面，隐藏登录界面
**调用时机**：登录成功后或页面加载时检测到已登录

### `logout()`
**功能**：退出登录
**流程**：
1. 清除 localStorage 中的 API Key
2. 刷新页面

---

## 数据加载函数

### `loadData(append = false)`
**功能**：加载账单数据
**参数**：
- `append`: 是否追加数据（用于加载更多）
**流程**：
1. 显示加载指示器
2. 构建查询参数（页码、筛选条件）
3. 并发请求账单列表和统计数据
4. 更新全局变量和 UI
5. 隐藏加载指示器

### `renderExpenses(items)`
**功能**：渲染账单列表
**参数**：
- `items`: 账单数组
**流程**：
1. 检查是否有数据
2. 生成 HTML（包含编辑和删除按钮）
3. 更新 DOM
4. 重新初始化图标

---

## 记账相关函数

### `handleSubmit()`
**功能**：提交记账内容
**流程**：
1. 根据 `currentMode` 获取输入内容
2. 调用 `API.submitRecord()`
3. 保存 `currentBatchId`
4. 渲染暂存区

### `handleImageUpload(file)`
**功能**：处理图片上传
**参数**：
- `file`: File 对象
**流程**：
1. 验证文件类型
2. 使用 FileReader 读取为 base64
3. 显示预览
4. 保存到 `imagePreview.dataset.imageData`

---

## 暂存区相关函数

### `renderStaging(items)`
**功能**：渲染暂存区的待确认记录
**参数**：
- `items`: 待确认记录数组
**流程**：
1. 生成 HTML
2. 显示暂存区
3. 更新 DOM

### `handleInteract()`
**功能**：处理对话式修改指令
**流程**：
1. 获取用户输入的指令
2. 调用 `API.interact()`
3. 根据响应更新暂存区或关闭暂存区

### `confirmAll()`
**功能**：一键确认所有记录
**流程**：
1. 调用 `API.interact()` 发送"全部确认"指令
2. 关闭暂存区
3. 刷新账单列表

---

## 筛选相关函数

### `applyFilters()`
**功能**：应用筛选条件
**流程**：
1. 从输入框获取筛选条件
2. 更新 `filters` 对象
3. 重置页码为 1
4. 重新加载数据

### `resetFilters()`
**功能**：重置筛选条件
**流程**：
1. 清空输入框
2. 重置 `filters` 对象
3. 重新加载数据

### `loadMore()`
**功能**：加载更多数据
**流程**：
1. 页码 +1
2. 调用 `loadData(true)` 追加数据

---

## 编辑相关函数

### `editExpense(id)`
**功能**：打开编辑对话框
**参数**：
- `id`: 账单 ID
**流程**：
1. 从 `allExpenses` 中找到对应记录
2. 填充表单字段
3. 保存 `currentEditId`
4. 显示编辑对话框

### `saveEdit()`
**功能**：保存编辑后的记录
**流程**：
1. 从表单获取数据
2. 调用 `API.updateExpense()`
3. 关闭对话框
4. 刷新列表

### `closeEditModal()`
**功能**：关闭编辑对话框
**流程**：
1. 隐藏对话框
2. 清空 `currentEditId`

---

## 删除相关函数

### `deleteExpense(id)`
**功能**：删除账单记录
**参数**：
- `id`: 账单 ID
**流程**：
1. 显示确认对话框
2. 调用 `API.deleteExpense()`
3. 刷新列表

---

## 配置管理函数

### `toggleSettings()`
**功能**：切换设置面板显示/隐藏

### `refreshPayees()`
**功能**：刷新成员列表
**流程**：
1. 调用 `API.getPayees()`
2. 渲染成员列表（带删除按钮）

### `addPayee()`
**功能**：添加成员
**流程**：
1. 获取输入的成员名称
2. 调用 `API.addPayee()`
3. 刷新成员列表

### `deletePayee(id)`
**功能**：删除成员
**参数**：
- `id`: 成员 ID

### `refreshAssets()`
**功能**：刷新资产列表（同成员列表）

### `addAsset()`
**功能**：添加资产（同添加成员）

### `deleteAsset(id)`
**功能**：删除资产（同删除成员）

---

## 工具函数

### `showToast(message)`
**功能**：显示提示消息
**参数**：
- `message`: 提示文本
**流程**：
1. 更新 toast 元素的文本
2. 显示 toast
3. 2秒后自动隐藏

### `updateIcon()`
**功能**：重新初始化 Lucide 图标
**调用时机**：动态更新 DOM 后

---

## 事件绑定

### 初始化事件（DOMContentLoaded）
```javascript
// 认证
document.getElementById('loginBtn').onclick = handleAuth;
document.getElementById('showRegisterBtn').onclick = toggleAuthMode;

// 记账
document.getElementById('submitBtn').onclick = handleSubmit;
document.getElementById('interactBtn').onclick = handleInteract;
document.getElementById('confirmAllBtn').onclick = confirmAll;

// 筛选
document.getElementById('applyFilterBtn').onclick = applyFilters;
document.getElementById('resetFilterBtn').onclick = resetFilters;
document.getElementById('loadMoreBtn').onclick = loadMore;

// 编辑
document.getElementById('closeEditModal').onclick = closeEditModal;
document.getElementById('saveEditBtn').onclick = saveEdit;
document.getElementById('cancelEditBtn').onclick = closeEditModal;

// 设置
document.getElementById('settingsBtn').onclick = toggleSettings;
document.getElementById('exportBtn').onclick = () => API.exportCSV();
document.getElementById('addPayeeBtn').onclick = addPayee;
document.getElementById('addAssetBtn').onclick = addAsset;

// 图片上传
document.getElementById('fileInput').onchange = (e) => handleImageUpload(e.target.files[0]);
document.getElementById('dropZone').onclick = () => fileInput.click();

// 粘贴图片
document.addEventListener('paste', (e) => {
    if (currentMode === 'image') {
        const file = e.clipboardData.items[0].getAsFile();
        if (file) handleImageUpload(file);
    }
});
```

---

## API 客户端 (api.js)

### `API.request(endpoint, method, body)`
**功能**：统一的 HTTP 请求方法
**参数**：
- `endpoint`: API 路径
- `method`: HTTP 方法（GET/POST/PUT/DELETE）
- `body`: 请求体（可选）
**返回**：Promise<响应数据>

### 主要 API 方法
- `API.login(username, password)` - 登录
- `API.register(username, password)` - 注册
- `API.submitRecord(type, content)` - 提交记账
- `API.interact(batchId, instruction)` - 对话式修改
- `API.getExpenses(params)` - 查询账单
- `API.getExpensesSummary()` - 获取统计
- `API.updateExpense(id, data)` - 更新账单
- `API.deleteExpense(id)` - 删除账单
- `API.getPayees()` - 获取成员
- `API.addPayee(name)` - 添加成员
- `API.deletePayee(id)` - 删除成员
- `API.getAssets()` - 获取资产
- `API.addAsset(name)` - 添加资产
- `API.deleteAsset(id)` - 删除资产
- `API.exportCSV()` - 导出 CSV

---

## 数据流

### 记账流程
```
用户输入 → handleSubmit() → API.submitRecord() 
→ 保存 batchId → renderStaging() → 显示暂存区
→ 用户确认/修改 → handleInteract() → API.interact()
→ 入库成功 → loadData() → 刷新列表
```

### 筛选流程
```
用户设置筛选条件 → applyFilters() → 更新 filters
→ loadData() → API.getExpenses(filters) → renderExpenses()
```

### 编辑流程
```
点击编辑按钮 → editExpense(id) → 填充表单 → 显示对话框
→ 用户修改 → saveEdit() → API.updateExpense()
→ 关闭对话框 → loadData() → 刷新列表
```

---

## 注意事项

1. **全局函数暴露**：`editExpense` 和 `deleteExpense` 需要暴露到 `window` 对象，因为在 HTML 中通过 `onclick` 调用
2. **图标更新**：动态更新 DOM 后需要调用 `updateIcon()` 重新初始化图标
3. **错误处理**：所有 API 调用都应该用 try-catch 包裹，并通过 `showToast()` 显示错误
4. **数据同步**：编辑或删除后需要重新加载数据以保持同步
