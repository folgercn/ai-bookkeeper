# Family Accounting 数据库备份脚本
# 用于 Windows Server 定时备份

# ==================== 配置区 ====================
$BackupDir = "C:\Backups\FamilyAccounting"
$DataDir = "C:\Apps\FamilyAccounting\data"
$Date = Get-Date -Format "yyyyMMdd_HHmmss"
$RetentionDays = 30  # 保留天数

# ==================== 备份逻辑 ====================

# 创建备份目录
if (!(Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
    Write-Host "✓ 创建备份目录: $BackupDir" -ForegroundColor Green
}

# 备份数据库文件
try {
    $SourceFile = "$DataDir\accounting.db"
    $BackupFile = "$BackupDir\accounting_$Date.db"
    
    if (Test-Path $SourceFile) {
        Copy-Item $SourceFile $BackupFile -Force
        $FileSize = (Get-Item $BackupFile).Length / 1KB
        Write-Host "✓ 备份成功: $BackupFile ($([math]::Round($FileSize, 2)) KB)" -ForegroundColor Green
    } else {
        Write-Host "✗ 数据库文件不存在: $SourceFile" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ 备份失败: $_" -ForegroundColor Red
    exit 1
}

# 清理过期备份
try {
    $DeletedCount = 0
    Get-ChildItem $BackupDir -Filter "accounting_*.db" | 
        Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-$RetentionDays) } | 
        ForEach-Object {
            Remove-Item $_.FullName -Force
            Write-Host "  删除过期备份: $($_.Name)" -ForegroundColor Yellow
            $DeletedCount++
        }
    
    if ($DeletedCount -gt 0) {
        Write-Host "✓ 清理了 $DeletedCount 个过期备份" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠ 清理过期备份时出错: $_" -ForegroundColor Yellow
}

# 显示备份统计
$BackupCount = (Get-ChildItem $BackupDir -Filter "accounting_*.db").Count
$TotalSize = (Get-ChildItem $BackupDir -Filter "accounting_*.db" | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "`n当前备份数量: $BackupCount 个" -ForegroundColor Cyan
Write-Host "占用空间: $([math]::Round($TotalSize, 2)) MB" -ForegroundColor Cyan

Write-Host "`n备份完成!" -ForegroundColor Green
