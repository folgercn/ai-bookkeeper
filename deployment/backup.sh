#!/bin/bash
# Ubuntu 备份脚本
# 用于定时备份 SQLite 数据库

# ==================== 配置区 ====================
BACKUP_DIR="/var/backups/ai-bookkeeper"
DATA_DIR="/opt/ai-bookkeeper/data"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30  # 保留天数

# ==================== 备份逻辑 ====================

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库文件
if [ -f "$DATA_DIR/accounting.db" ]; then
    cp "$DATA_DIR/accounting.db" "$BACKUP_DIR/accounting_$DATE.db"
    
    # 压缩备份
    gzip "$BACKUP_DIR/accounting_$DATE.db"
    
    FILE_SIZE=$(du -h "$BACKUP_DIR/accounting_$DATE.db.gz" | cut -f1)
    echo "✓ 备份成功: $BACKUP_DIR/accounting_$DATE.db.gz ($FILE_SIZE)"
else
    echo "✗ 数据库文件不存在: $DATA_DIR/accounting.db"
    exit 1
fi

# 清理过期备份
DELETED_COUNT=$(find $BACKUP_DIR -name "accounting_*.db.gz" -mtime +$RETENTION_DAYS -delete -print | wc -l)
if [ $DELETED_COUNT -gt 0 ]; then
    echo "✓ 清理了 $DELETED_COUNT 个过期备份"
fi

# 显示备份统计
BACKUP_COUNT=$(ls -1 $BACKUP_DIR/accounting_*.db.gz 2>/dev/null | wc -l)
TOTAL_SIZE=$(du -sh $BACKUP_DIR 2>/dev/null | cut -f1)
echo ""
echo "当前备份数量: $BACKUP_COUNT 个"
echo "占用空间: $TOTAL_SIZE"
echo ""
echo "备份完成!"
