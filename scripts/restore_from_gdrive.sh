#!/bin/bash
# Google Drive 备份恢复脚本
# 从 Google Drive 恢复指定版本的数据库备份

set -e

# ==================== 配置区 ====================
GDRIVE_REMOTE="gdrive:ai-bookkeeper-backups"
RESTORE_DIR="/opt/ai-bookkeeper/ai-bookkeeper/data"
TEMP_DIR="/tmp/ai-bookkeeper-restore"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ==================== 检查依赖 ====================
if ! command -v rclone &> /dev/null; then
    log_error "rclone 未安装"
    exit 1
fi

# ==================== 列出可用备份 ====================
log_info "可用的备份版本:"
echo "============================================"

BACKUPS=$(rclone lsf "$GDRIVE_REMOTE/" --files-only | grep "accounting_.*\.db\.gz" | sort -r)

if [ -z "$BACKUPS" ]; then
    log_error "未找到任何备份文件"
    exit 1
fi

# 显示备份列表
i=1
declare -a BACKUP_ARRAY
while IFS= read -r line; do
    BACKUP_ARRAY[$i]="$line"
    # 提取日期时间
    DATETIME=$(echo "$line" | grep -oP '\d{8}_\d{6}')
    FORMATTED_DATE=$(echo "$DATETIME" | sed 's/\([0-9]\{4\}\)\([0-9]\{2\}\)\([0-9]\{2\}\)_\([0-9]\{2\}\)\([0-9]\{2\}\)\([0-9]\{2\}\)/\1-\2-\3 \4:\5:\6/')
    
    # 获取文件大小
    SIZE=$(rclone size "$GDRIVE_REMOTE/$line" --json | grep -o '"bytes":[0-9]*' | cut -d: -f2)
    SIZE_KB=$(echo "scale=2; $SIZE / 1024" | bc)
    
    echo "[$i] $FORMATTED_DATE - ${SIZE_KB} KB"
    ((i++))
done <<< "$BACKUPS"

echo "============================================"

# ==================== 选择备份 ====================
read -p "请选择要恢复的备份编号 (1-$((i-1))): " CHOICE

if ! [[ "$CHOICE" =~ ^[0-9]+$ ]] || [ "$CHOICE" -lt 1 ] || [ "$CHOICE" -ge "$i" ]; then
    log_error "无效的选择"
    exit 1
fi

SELECTED_BACKUP="${BACKUP_ARRAY[$CHOICE]}"
log_info "选择的备份: $SELECTED_BACKUP"

# ==================== 确认恢复 ====================
echo ""
echo -e "${YELLOW}警告: 此操作将覆盖当前数据库!${NC}"
read -p "是否继续? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    log_info "操作已取消"
    exit 0
fi

# ==================== 备份当前数据库 ====================
if [ -f "$RESTORE_DIR/accounting.db" ]; then
    BACKUP_CURRENT="$RESTORE_DIR/accounting.db.before-restore.$(date +%Y%m%d_%H%M%S)"
    log_info "备份当前数据库到: $BACKUP_CURRENT"
    cp "$RESTORE_DIR/accounting.db" "$BACKUP_CURRENT"
fi

# ==================== 下载并恢复 ====================
mkdir -p "$TEMP_DIR"

log_info "下载备份文件..."
rclone copy "$GDRIVE_REMOTE/$SELECTED_BACKUP" "$TEMP_DIR/" --progress

log_info "解压备份..."
gunzip -f "$TEMP_DIR/$SELECTED_BACKUP"

RESTORED_FILE="${SELECTED_BACKUP%.gz}"
log_info "恢复数据库..."
cp "$TEMP_DIR/$RESTORED_FILE" "$RESTORE_DIR/accounting.db"

# 设置权限
chown www-data:www-data "$RESTORE_DIR/accounting.db"
chmod 644 "$RESTORE_DIR/accounting.db"

# 清理临时文件
rm -rf "$TEMP_DIR"

log_info "============================================"
log_info "恢复完成!"
log_info "请重启应用服务:"
log_info "  sudo systemctl restart ai-bookkeeper"
log_info "============================================"
