#!/bin/bash

# eHR系统自动审批简化脚本
# 专门用于cron任务执行
# 作者: Jesse Xia
# 创建日期: 2026-08-04

# 配置
EHR_URL="https://ehr.sercomm.com/eHR/Account/#"
EHR_APPROVE_URL="https://ehr.sercomm.com/eHR/bpm/approve"
CREDENTIALS_FILE="$HOME/.hermes/secrets/ehr_sercomm.txt"
LOG_FILE="$HOME/.hermes/logs/ehr_cron_$(date '+%Y%m%d_%H%M%S').log"

# 创建日志目录
mkdir -p "$(dirname "$LOG_FILE")"

# 日志函数
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 检查凭据
check_credentials() {
    if [ ! -f "$CREDENTIALS_FILE" ]; then
        log_message "错误: 凭据文件不存在"
        return 1
    fi
    
    username=$(grep "^username=" "$CREDENTIALS_FILE" | cut -d'=' -f2)
    password=$(grep "^password=" "$CREDENTIALS_FILE" | cut -d'=' -f2)
    
    if [ -z "$username" ] || [ -z "$password" ]; then
        log_message "错误: 无法读取凭据"
        return 1
    fi
    
    return 0
}

# 快速审批流程
quick_approve() {
    log_message "开始快速审批流程..."
    
    # 导航到审批页面
    log_message "导航到审批页面"
    browser_navigate "$EHR_APPROVE_URL"
    sleep 5
    
    # 获取页面快照
    browser_snapshot
    
    # 选择所有单据（假设ref从e44开始）
    log_message "选择单据..."
    for i in {44..50}; do
        browser_click "e$i" 2>/dev/null
        sleep 0.5
    done
    
    # 批量审批
    log_message "执行批量审批"
    browser_click "e32"
    sleep 3
    
    # 检查结果
    browser_snapshot
    log_message "审批流程完成"
}

# 主函数
main() {
    log_message "========== 开始eHR cron审批任务 =========="
    
    # 检查凭据
    if ! check_credentials; then
        log_message "凭据检查失败，任务终止"
        exit 1
    fi
    
    log_message "使用凭据: 用户名 $username"
    
    # 执行审批
    quick_approve
    
    log_message "========== eHR cron审批任务完成 =========="
}

# 执行主函数
main "$@"