# Ubuntu 24.04 快速部署指南

这是一个快速部署参考,详细文档请查看完整的部署方案。

## 🚀 快速部署步骤

### 1. 系统准备
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip git curl -y
```

### 2. 部署应用
```bash
# 创建目录
sudo mkdir -p /opt/ai-bookkeeper
sudo chown $USER:$USER /opt/ai-bookkeeper
cd /opt/ai-bookkeeper

# 克隆项目
git clone https://github.com/folgercn/ai-bookkeeper.git .

# 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
nano .env  # 编辑配置

# 初始化数据库
mkdir -p data
python scripts/init_db.py
```

### 3. 安装 Caddy
```bash
# 添加 Caddy 仓库
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list

# 安装
sudo apt update
sudo apt install caddy -y
```

### 4. 配置 Caddy
```bash
# 复制配置文件
sudo cp deployment/Caddyfile /etc/caddy/Caddyfile

# 编辑配置,替换域名
sudo nano /etc/caddy/Caddyfile

# 创建日志目录
sudo mkdir -p /var/log/caddy
sudo chown caddy:caddy /var/log/caddy

# 验证并启动
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl restart caddy
sudo systemctl enable caddy
```

### 5. 配置 Systemd 服务
```bash
# 复制服务文件
sudo cp deployment/ai-bookkeeper.service /etc/systemd/system/

# 设置权限
sudo chown -R www-data:www-data /opt/ai-bookkeeper
sudo chmod 755 /opt/ai-bookkeeper/data

# 启动服务
sudo systemctl daemon-reload
sudo systemctl start ai-bookkeeper
sudo systemctl enable ai-bookkeeper
```

### 6. 配置防火墙
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 7. 设置自动备份
```bash
# 复制备份脚本
sudo cp deployment/backup.sh /opt/ai-bookkeeper/scripts/
sudo chmod +x /opt/ai-bookkeeper/scripts/backup.sh

# 添加定时任务
sudo crontab -e
# 添加: 0 2 * * * /opt/ai-bookkeeper/scripts/backup.sh >> /var/log/ai-bookkeeper-backup.log 2>&1
```

## 📁 配置文件清单

- `deployment/Caddyfile` - Caddy 反向代理配置
- `deployment/ai-bookkeeper.service` - Systemd 服务配置
- `deployment/backup.sh` - 自动备份脚本

## 🔧 常用命令

```bash
# 查看服务状态
sudo systemctl status ai-bookkeeper
sudo systemctl status caddy

# 重启服务
sudo systemctl restart ai-bookkeeper
sudo systemctl restart caddy

# 查看日志
sudo journalctl -u ai-bookkeeper -f
sudo journalctl -u caddy -f

# 手动备份
sudo /opt/ai-bookkeeper/scripts/backup.sh
```

## ✅ 部署检查

- [ ] Python 3.11 已安装
- [ ] 项目已克隆
- [ ] 虚拟环境已创建
- [ ] .env 已配置
- [ ] 数据库已初始化
- [ ] Caddy 已安装并配置
- [ ] DNS 已解析(如使用域名)
- [ ] Systemd 服务已启动
- [ ] 防火墙已配置
- [ ] 自动备份已设置

完成!访问 `https://your-domain.com` 开始使用。

## 📚 详细文档

查看完整部署文档了解更多细节和故障排查。
