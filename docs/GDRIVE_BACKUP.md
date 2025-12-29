# Google Drive 自动备份配置指南

本文档说明如何配置数据库自动备份到 Google Drive,支持版本控制。

---

## 📋 前提条件

- Ubuntu 24.04 服务器
- Google 账号
- rclone 工具

---

## 🚀 快速配置

### 1. 安装 rclone

```bash
# 安装 rclone
curl https://rclone.org/install.sh | sudo bash

# 验证安装
rclone version
```

### 2. 配置 Google Drive

```bash
# 启动配置向导
rclone config

# 按照提示操作:
# n) New remote
# name> gdrive
# Storage> drive (选择 Google Drive)
# client_id> (直接回车,使用默认)
# client_secret> (直接回车)
# scope> 1 (Full access)
# root_folder_id> (直接回车)
# service_account_file> (直接回车)
# Edit advanced config? n
# Use auto config? n (服务器环境选择 n)

# 会显示一个 URL,在本地浏览器打开
# 授权后复制验证码粘贴回来

# Configure this as a team drive? n
# y) Yes this is OK
# q) Quit config
```

### 3. 测试连接

```bash
# 列出 Google Drive 根目录
rclone lsd gdrive:

# 创建备份目录
rclone mkdir gdrive:ai-bookkeeper-backups
```

### 4. 设置备份脚本权限

```bash
cd /opt/ai-bookkeeper/ai-bookkeeper
chmod +x scripts/backup_to_gdrive.sh
chmod +x scripts/restore_from_gdrive.sh
```

### 5. 测试备份

```bash
# 手动运行一次备份
sudo ./scripts/backup_to_gdrive.sh
```

### 6. 设置定时备份

```bash
# 编辑 root 用户的 crontab
sudo crontab -e

# 添加以下行(每天凌晨2点备份)
0 2 * * * /opt/ai-bookkeeper/ai-bookkeeper/scripts/backup_to_gdrive.sh >> /var/log/gdrive-backup.log 2>&1

# 或者每6小时备份一次
0 */6 * * * /opt/ai-bookkeeper/ai-bookkeeper/scripts/backup_to_gdrive.sh >> /var/log/gdrive-backup.log 2>&1
```

---

## 📦 备份功能

### 自动备份特性

- ✅ **版本控制**: 保留最近30个版本
- ✅ **自动压缩**: 使用 gzip 压缩,节省空间
- ✅ **自动清理**: 删除超过30个版本的旧备份
- ✅ **本地缓存**: 本地保留7天备份
- ✅ **错误处理**: 备份失败会报错并退出

### 备份文件命名

```
accounting_20251229_020000.db.gz
          ^^^^^^^^_^^^^^^
          日期      时间
```

---

## 🔄 恢复备份

### 查看可用备份

```bash
rclone lsf gdrive:ai-bookkeeper-backups/
```

### 使用恢复脚本

```bash
# 运行恢复脚本
sudo ./scripts/restore_from_gdrive.sh

# 按照提示选择要恢复的版本
# 脚本会自动:
# 1. 列出所有可用备份
# 2. 备份当前数据库
# 3. 下载并恢复选定版本
# 4. 设置正确的权限
```

### 手动恢复

```bash
# 1. 列出备份
rclone lsf gdrive:ai-bookkeeper-backups/

# 2. 下载特定备份
rclone copy gdrive:ai-bookkeeper-backups/accounting_20251229_020000.db.gz /tmp/

# 3. 解压
gunzip /tmp/accounting_20251229_020000.db.gz

# 4. 备份当前数据库
sudo cp /opt/ai-bookkeeper/ai-bookkeeper/data/accounting.db \
        /opt/ai-bookkeeper/ai-bookkeeper/data/accounting.db.backup

# 5. 恢复
sudo cp /tmp/accounting_20251229_020000.db \
        /opt/ai-bookkeeper/ai-bookkeeper/data/accounting.db

# 6. 设置权限
sudo chown www-data:www-data /opt/ai-bookkeeper/ai-bookkeeper/data/accounting.db
sudo chmod 644 /opt/ai-bookkeeper/ai-bookkeeper/data/accounting.db

# 7. 重启服务
sudo systemctl restart ai-bookkeeper
```

---

## 📊 监控备份

### 查看备份日志

```bash
# 查看最近的备份日志
sudo tail -f /var/log/gdrive-backup.log

# 查看最近50行
sudo tail -n 50 /var/log/gdrive-backup.log
```

### 检查 Google Drive 空间

```bash
# 查看备份占用空间
rclone size gdrive:ai-bookkeeper-backups/

# 列出所有备份文件
rclone ls gdrive:ai-bookkeeper-backups/ --max-depth 1
```

### 手动触发备份

```bash
sudo /opt/ai-bookkeeper/ai-bookkeeper/scripts/backup_to_gdrive.sh
```

---

## ⚙️ 高级配置

### 调整保留版本数

编辑 `scripts/backup_to_gdrive.sh`:
```bash
KEEP_VERSIONS=30  # 改为你想要的数量,如 60
```

### 调整备份频率

```bash
# 编辑 crontab
sudo crontab -e

# 每天备份一次(凌晨2点)
0 2 * * * /opt/ai-bookkeeper/ai-bookkeeper/scripts/backup_to_gdrive.sh >> /var/log/gdrive-backup.log 2>&1

# 每6小时备份一次
0 */6 * * * /opt/ai-bookkeeper/ai-bookkeeper/scripts/backup_to_gdrive.sh >> /var/log/gdrive-backup.log 2>&1

# 每小时备份一次
0 * * * * /opt/ai-bookkeeper/ai-bookkeeper/scripts/backup_to_gdrive.sh >> /var/log/gdrive-backup.log 2>&1
```

### 备份到多个位置

```bash
# 配置第二个 remote (如 Dropbox)
rclone config

# 修改备份脚本,添加第二个上传目标
rclone copy "$BACKUP_FILE" "dropbox:ai-bookkeeper-backups/" --progress
```

---

## 🔒 安全建议

1. **加密备份**: rclone 支持加密,可以在配置时启用
2. **限制访问**: Google Drive 文件夹设为私有
3. **定期测试恢复**: 每月测试一次恢复流程
4. **监控备份**: 设置告警,备份失败时通知

---

## ❓ 故障排查

### 问题 1: rclone 未找到

```bash
# 重新安装
curl https://rclone.org/install.sh | sudo bash
```

### 问题 2: 授权失败

```bash
# 删除旧配置重新配置
rclone config delete gdrive
rclone config
```

### 问题 3: 权限错误

```bash
# 确保脚本有执行权限
chmod +x scripts/backup_to_gdrive.sh

# 确保以 root 运行
sudo ./scripts/backup_to_gdrive.sh
```

### 问题 4: 空间不足

```bash
# 检查 Google Drive 空间
rclone about gdrive:

# 清理旧备份
rclone delete gdrive:ai-bookkeeper-backups/ --min-age 90d
```

---

## 📝 备份策略建议

### 个人使用
- **频率**: 每天1次
- **保留**: 30个版本(约1个月)

### 重度使用
- **频率**: 每6小时1次
- **保留**: 60个版本(约15天)

### 关键数据
- **频率**: 每小时1次
- **保留**: 168个版本(7天)
- **额外**: 每周备份到第二个位置

---

## ✅ 配置检查清单

- [ ] rclone 已安装
- [ ] Google Drive remote 已配置
- [ ] 备份脚本有执行权限
- [ ] 手动备份测试成功
- [ ] crontab 定时任务已设置
- [ ] 备份日志正常记录
- [ ] 恢复流程已测试

完成以上步骤后,你的数据将自动备份到 Google Drive,并支持版本控制!
