# Windows Server 部署快速指南

这是一个快速部署参考,详细文档请查看完整的部署方案。

## 🚀 快速部署步骤

### 1. 准备工作
```powershell
# 安装 Python 3.11
choco install python311 -y

# 创建应用目录
mkdir C:\Apps\FamilyAccounting
cd C:\Apps\FamilyAccounting

# 上传项目文件到此目录
```

### 2. 安装依赖
```powershell
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 如果遇到执行策略错误
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境
创建 `.env` 文件:
```env
APP_ENV=production
DEBUG=false
SECRET_KEY=<运行: python -c "import secrets; print(secrets.token_urlsafe(32))">
DATABASE_URL=sqlite+aiosqlite:///C:/Apps/FamilyAccounting/data/accounting.db
OPENROUTER_API_KEY=你的密钥
```

### 4. 初始化数据库
```powershell
python scripts\init_db.py
```

### 5. 测试运行
```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000
# 访问 http://服务器IP:8000/docs 测试
```

### 6. 注册为服务
```powershell
# 安装 NSSM
choco install nssm -y

# 注册服务
nssm install FamilyAccountingAPI "C:\Apps\FamilyAccounting\venv\Scripts\python.exe"
nssm set FamilyAccountingAPI AppParameters "-m uvicorn app.main:app --host 0.0.0.0 --port 8000"
nssm set FamilyAccountingAPI AppDirectory "C:\Apps\FamilyAccounting"
nssm set FamilyAccountingAPI Start SERVICE_AUTO_START

# 启动服务
nssm start FamilyAccountingAPI
```

### 7. 配置前端(IIS)
```powershell
# 安装 IIS
Install-WindowsFeature -name Web-Server -IncludeManagementTools

# 在 IIS 管理器中:
# 1. 添加网站,物理路径指向 C:\Apps\FamilyAccounting\frontend
# 2. 复制 deployment\web.config 到 frontend 目录
# 3. 安装 URL Rewrite 和 ARR 模块
```

### 8. 配置防火墙
```powershell
New-NetFirewallRule -DisplayName "HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
```

### 9. 设置自动备份
```powershell
# 创建备份任务
$Action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File C:\Apps\FamilyAccounting\scripts\backup.ps1"
$Trigger = New-ScheduledTaskTrigger -Daily -At 2:00AM
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount
Register-ScheduledTask -TaskName "FamilyAccountingBackup" -Action $Action -Trigger $Trigger -Principal $Principal
```

## 📁 文件清单

项目已包含以下部署文件:

- `scripts/backup.ps1` - 数据库备份脚本
- `scripts/start_backend.bat` - 后端启动脚本
- `deployment/nginx.conf` - Nginx 配置示例
- `deployment/web.config` - IIS URL Rewrite 配置

## 🔧 常用命令

```powershell
# 查看服务状态
nssm status FamilyAccountingAPI

# 重启服务
nssm restart FamilyAccountingAPI

# 查看日志
Get-EventLog -LogName Application -Source FamilyAccountingAPI -Newest 50

# 手动备份
.\scripts\backup.ps1
```

## ✅ 部署检查

- [ ] Python 已安装
- [ ] 依赖已安装
- [ ] .env 已配置
- [ ] 数据库已初始化
- [ ] 后端服务运行正常
- [ ] IIS 配置完成
- [ ] 防火墙规则已添加
- [ ] 自动备份已设置

完成!访问 `http://服务器IP/` 开始使用。
