#!/bin/bash
# Google Drive 自动备份脚本
# 使用 rclone 将数据库备份到 Google Drive,支持版本控制

set -e  # 遇到错误立即退出

# ==================== 配置区 ====================
# 数据库路径
DB_PATH="/opt/ai-bookkeeper/ai-bookkeeper/data/accounting.db"

# 本地备份目录
LOCAL_BACKUP_DIR="/var/backups/ai-bookkeeper"

# Google Drive 远程路径 (需要先配置 rclone remote 名为 gdrive)
GDRIVE_REMOTE="gdrive:ai-bookkeeper-backups"

# 保留版本数量
KEEP_VERSIONS=30  # 保留最近30个版本

# 日期格式
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="accounting_${DATE}.db"

# ==================== 颜色输出 ====================
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ==================== 函数定义 ====================
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ==================== 检查依赖 ====================
if ! command -v rclone &> /dev/null; then
    log_error "rclone 未安装,请先安装: curl https://rclone.org/install.sh | sudo bash"
    exit 1
fi

# ==================== 创建本地备份 ====================
log_info "开始备份数据库..."

# 创建本地备份目录
mkdir -p "$LOCAL_BACKUP_DIR"

# 检查数据库文件是否存在
if [ ! -f "$DB_PATH" ]; then
    log_error "数据库文件不存在: $DB_PATH"
    exit 1
fi

# 复制数据库文件
cp "$DB_PATH" "$LOCAL_BACKUP_DIR/$BACKUP_NAME"

# 压缩备份
gzip "$LOCAL_BACKUP_DIR/$BACKUP_NAME"
BACKUP_FILE="$LOCAL_BACKUP_DIR/${BACKUP_NAME}.gz"

FILE_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
log_info "本地备份完成: $BACKUP_FILE ($FILE_SIZE)"

# ==================== 上传到 Google Drive ====================
log_info "上传到 Google Drive..."

# 检查 rclone remote 是否配置
if ! rclone listremotes | grep -q "gdrive:"; then
    log_error "rclone remote 'gdrive' 未配置"
    log_error "请运行: rclone config"
    exit 1
fi

# 上传文件
if rclone copy "$BACKUP_FILE" "$GDRIVE_REMOTE/" --progress; then
    log_info "上传成功: ${BACKUP_NAME}.gz"
else
    log_error "上传失败"
    exit 1
fi

# ==================== 清理旧版本 ====================
log_info "清理旧版本..."

# 列出所有备份文件,按时间排序
REMOTE_FILES=$(rclone lsf "$GDRIVE_REMOTE/" --files-only | grep "accounting_.*\.db\.gz" | sort -r)
FILE_COUNT=$(echo "$REMOTE_FILES" | wc -l)

if [ "$FILE_COUNT" -gt "$KEEP_VERSIONS" ]; then
    DELETE_COUNT=$((FILE_COUNT - KEEP_VERSIONS))
    log_warn "发现 $FILE_COUNT 个备份,保留 $KEEP_VERSIONS 个,删除 $DELETE_COUNT 个旧备份"
    
    # 删除旧文件
    echo "$REMOTE_FILES" | tail -n "$DELETE_COUNT" | while read -r file; do
        log_info "删除旧备份: $file"
        rclone delete "$GDRIVE_REMOTE/$file"
    done
fi

# ==================== 清理本地旧备份 ====================
log_info "清理本地旧备份..."
find "$LOCAL_BACKUP_DIR" -name "accounting_*.db.gz" -mtime +7 -delete

# ==================== 显示统计信息 ====================
GDRIVE_COUNT=$(rclone lsf "$GDRIVE_REMOTE/" --files-only | grep "accounting_.*\.db\.gz" | wc -l)
GDRIVE_SIZE=$(rclone size "$GDRIVE_REMOTE/" --json | grep -o '"bytes":[0-9]*' | cut -d: -f2)
GDRIVE_SIZE_MB=$(echo "scale=2; $GDRIVE_SIZE / 1024 / 1024" | bc)

log_info "============================================"
log_info "备份完成!"
log_info "Google Drive 备份数量: $GDRIVE_COUNT 个"
log_info "Google Drive 占用空间: ${GDRIVE_SIZE_MB} MB"
log_info "最新备份: ${BACKUP_NAME}.gz"
log_info "============================================"
