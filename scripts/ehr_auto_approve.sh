#!/bin/bash

# eHR系统自动审批脚本
# 每天早晚各一次自动登录并审批所有单据
# 作者: Jesse Xia
# 创建日期: 2026-08-04

# 配置
EHR_URL="https://ehr.sercomm.com/eHR/Account/#"
EHR_APPROVE_URL="https://ehr.sercomm.com/eHR/bpm/approve"
CREDENTIALS_FILE="$HOME/.hermes/secrets/ehr_sercomm.txt"
LOG_FILE="$HOME/.hermes/logs/ehr_auto_approve.log"
BROWSER_TIMEOUT=60

# 创建日志目录
mkdir -p "$(dirname "$LOG_FILE")"

# 日志函数
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 检查依赖
check_dependencies() {
    log_message "检查依赖..."
    
    # 检查浏览器工具
    if ! command -v browser_navigate &> /dev/null; then
        log_message "错误: browser_navigate 命令不可用"
        exit 1
    fi
    
    # 检查凭据文件
    if [ ! -f "$CREDENTIALS_FILE" ]; then
        log_message "错误: 凭据文件不存在: $CREDENTIALS_FILE"
        exit 1
    fi
    
    # 检查文件权限
    if [ "$(stat -f "%A" "$CREDENTIALS_FILE")" != "600" ]; then
        log_message "警告: 凭据文件权限不正确，正在设置..."
        chmod 600 "$CREDENTIALS_FILE"
    fi
    
    log_message "依赖检查完成"
}

# 读取凭据
read_credentials() {
    log_message "读取凭据..."
    
    if [ ! -f "$CREDENTIALS_FILE" ]; then
        log_message "错误: 凭据文件不存在"
        return 1
    fi
    
    username=$(grep "^username=" "$CREDENTIALS_FILE" | cut -d'=' -f2)
    password=$(grep "^password=" "$CREDENTIALS_FILE" | cut -d'=' -f2)
    
    if [ -z "$username" ] || [ -z "$password" ]; then
        log_message "错误: 无法读取用户名或密码"
        return 1
    fi
    
    log_message "凭据读取成功"
    return 0
}

# 登录eHR系统
login_ehr() {
    log_message "开始登录eHR系统..."
    
    # 导航到登录页面
    log_message "导航到登录页面: $EHR_URL"
    browser_navigate "$EHR_URL"
    
    # 等待页面加载
    sleep 3
    
    # 输入用户名
    log_message "输入用户名: $username"
    browser_type "e10" "$username"
    sleep 1
    
    # 输入密码
    log_message "输入密码"
    browser_type "e11" "$password"
    sleep 1
    
    # 点击登录按钮
    log_message "点击登录按钮"
    browser_click "e9"
    
    # 等待登录完成
    sleep 5
    
    # 验证登录是否成功
    log_message "验证登录状态"
    browser_snapshot
    
    # 检查是否登录成功（通过检查页面内容）
    login_result=$(browser_console --expression "document.body.innerText" 2>/dev/null | grep -i "夏正洋\|夏正洋 主管" || echo "")
    
    if [ -n "$login_result" ]; then
        log_message "✅ 登录成功"
        return 0
    else
        log_message "❌ 登录失败"
        return 1
    fi
}

# 进入审批页面
navigate_to_approve() {
    log_message "进入审批页面..."
    
    # 直接导航到审批页面
    log_message "导航到审批页面: $EHR_APPROVE_URL"
    browser_navigate "$EHR_APPROVE_URL"
    
    # 等待页面加载
    sleep 5
    
    # 获取页面快照
    browser_snapshot
    
    log_message "✅ 已进入审批页面"
    return 0
}

# 检查并选择所有单据
select_all_forms() {
    log_message "检查待审批单据..."
    
    # 获取页面快照
    browser_snapshot
    
    # 查找单据复选框
    checkboxes=$(browser_console --expression "document.querySelectorAll('input[type=\"checkbox\"]').length" 2>/dev/null || echo "0")
    
    if [ "$checkboxes" -eq 0 ]; then
        log_message "ℹ️ 没有找到单据复选框"
        return 1
    fi
    
    log_message "找到 $checkboxes 个复选框"
    
    # 逐个点击复选框选择单据
    # 假设单据复选框的ref从e44开始
    form_count=0
    for i in {44..50}; do
        ref="e$i"
        if browser_click "$ref" 2>/dev/null; then
            form_count=$((form_count + 1))
            log_message "已选择单据 $form_count"
            sleep 1
        fi
    done
    
    log_message "总共选择了 $form_count 个单据"
    return $form_count
}

# 批量审批单据
approve_all_forms() {
    log_message "开始批量审批..."
    
    # 点击Approve按钮
    log_message "点击Approve按钮"
    browser_click "e32"
    
    # 等待审批完成
    sleep 3
    
    # 检查审批结果
    browser_snapshot
    
    # 检查按钮状态是否变为禁用
    approve_disabled=$(browser_console --expression "document.querySelector('button[ref=\"e32\"]')?.disabled" 2>/dev/null || echo "false")
    
    if [ "$approve_disabled" = "true" ]; then
        log_message "✅ 批量审批成功"
        return 0
    else
        log_message "⚠️ 批量审批可能未成功，按钮状态未变化"
        return 1
    fi
}

# 生成报告
generate_report() {
    log_message "生成审批报告..."
    
    local report_file="$HOME/.hermes/logs/ehr_approval_report_$(date '+%Y%m%d').txt"
    
    {
        echo "eHR系统自动审批报告"
        echo "===================="
        echo "执行时间: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "操作员: Jesse Xia"
        echo ""
        echo "系统信息:"
        echo "- eHR URL: $EHR_URL"
        echo "- 审批页面: $EHR_APPROVE_URL"
        echo ""
        echo "执行结果:"
        echo "- 登录状态: $login_status"
        echo "- 单据数量: $form_count"
        echo "- 审批结果: $approval_result"
        echo ""
        echo "详细日志:"
        echo "========="
        tail -20 "$LOG_FILE"
    } > "$report_file"
    
    log_message "报告已生成: $report_file"
}

# 主函数
main() {
    log_message "========== 开始eHR自动审批任务 =========="
    
    # 初始化变量
    login_status="失败"
    form_count=0
    approval_result="失败"
    
    # 检查依赖
    check_dependencies
    
    # 读取凭据
    if ! read_credentials; then
        log_message "无法读取凭据，任务终止"
        exit 1
    fi
    
    # 登录系统
    if login_ehr; then
        login_status="成功"
        
        # 进入审批页面
        if navigate_to_approve; then
            
            # 检查并选择单据
            if select_all_forms; then
                form_count=$?
                
                # 批量审批
                if approve_all_forms; then
                    approval_result="成功"
                else
                    approval_result="部分失败"
                fi
            else
                log_message "没有找到需要审批的单据"
                form_count=0
                approval_result="无单据"
            fi
        else
            log_message "无法进入审批页面"
        fi
    else
        log_message "登录失败，任务终止"
        exit 1
    fi
    
    # 生成报告
    generate_report
    
    log_message "========== eHR自动审批任务完成 =========="
    log_message "总结: 登录$login_status, 单据$form_count个, 审批$approval_result"
    
    # 根据结果设置退出码
    if [ "$login_status" = "成功" ] && [ "$approval_result" != "失败" ]; then
        exit 0
    else
        exit 1
    fi
}

# 运行主函数
main "$@"