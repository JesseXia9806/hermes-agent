#!/bin/bash

# eHR系统自动审批脚本 - 修复版
# 每天早晚各一次自动登录并审批所有单据
# 作者: Jesse Xia
# 创建日期: 2026-08-04

# 配置
EHR_URL="https://ehr.sercomm.com/eHR/Account/#"
EHR_APPROVE_URL="https://ehr.sercomm.com/eHR/bpm/approve"
CREDENTIALS_FILE="$HOME/.hermes/secrets/ehr_sercomm.txt"
LOG_FILE="$HOME/.hermes/logs/ehr_auto_approve.log"
PYTHON_SCRIPT="$HOME/.hermes/scripts/ehr_browser_automation.py"

# 创建日志目录
mkdir -p "$(dirname "$LOG_FILE")"

# 日志函数
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 检查依赖
check_dependencies() {
    log_message "检查依赖..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_message "错误: python3 不可用"
        exit 1
    fi
    
    # 检查凭据文件
    if [ ! -f "$CREDENTIALS_FILE" ]; then
        log_message "错误: 凭据文件不存在: $CREDENTIALS_FILE"
        exit 1
    fi
    
    # 检查Python脚本
    if [ ! -f "$PYTHON_SCRIPT" ]; then
        log_message "错误: Python脚本不存在: $PYTHON_SCRIPT"
        exit 1
    fi
    
    log_message "依赖检查完成"
}

# 读取凭据
read_credentials() {
    log_message "读取凭据..."
    
    username=$(grep "^username=" "$CREDENTIALS_FILE" | cut -d'=' -f2)
    password=$(grep "^password=" "$CREDENTIALS_FILE" | cut -d'=' -f2)
    
    if [ -z "$username" ] || [ -z "$password" ]; then
        log_message "错误: 无法读取用户名或密码"
        return 1
    fi
    
    log_message "凭据读取成功: 用户名 $username"
    return 0
}

# 执行Python脚本
run_python_script() {
    log_message "执行Python自动化脚本..."
    
    # 创建临时参数文件
    cat > /tmp/ehr_params.json << EOF
{
    "username": "$username",
    "password": "$password",
    "ehr_url": "$EHR_URL",
    "approve_url": "$EHR_APPROVE_URL"
}
EOF
    
    # 执行Python脚本
    python3 "$PYTHON_SCRIPT" /tmp/ehr_params.json
    
    local exit_code=$?
    rm -f /tmp/ehr_params.json
    
    if [ $exit_code -eq 0 ]; then
        log_message "✅ Python脚本执行成功"
        return 0
    else
        log_message "❌ Python脚本执行失败，退出码: $exit_code"
        return 1
    fi
}

# 主函数
main() {
    log_message "========== 开始eHR自动审批任务 =========="
    
    # 初始化变量
    login_status="失败"
    approval_result="失败"
    
    # 检查依赖
    check_dependencies
    
    # 读取凭据
    if ! read_credentials; then
        log_message "无法读取凭据，任务终止"
        exit 1
    fi
    
    # 执行Python脚本
    if run_python_script; then
        login_status="成功"
        approval_result="成功"
    else
        log_message "自动化执行失败"
    fi
    
    log_message "========== eHR自动审批任务完成 =========="
    log_message "总结: 登录$login_status, 审批$approval_result"
    
    # 根据结果设置退出码
    if [ "$login_status" = "成功" ] && [ "$approval_result" = "成功" ]; then
        exit 0
    else
        exit 1
    fi
}

# 运行主函数
main "$@"