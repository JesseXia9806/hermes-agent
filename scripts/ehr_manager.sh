#!/bin/bash

# eHR自动审批系统管理脚本
# 用于启动、停止、查看状态等管理操作
# 作者: Jesse Xia
# 创建日期: 2026-08-04

SCRIPT_DIR="$HOME/.hermes/scripts"
LOG_DIR="$HOME/.hermes/logs"
CRON_FILE="/tmp/crontab.txt"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的信息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查系统状态
check_status() {
    print_info "检查eHR自动审批系统状态..."
    
    # 检查脚本文件
    if [ -f "$SCRIPT_DIR/ehr_auto_approve_fixed.sh" ] && [ -x "$SCRIPT_DIR/ehr_auto_approve_fixed.sh" ]; then
        print_success "审批脚本(修复版): 存在且可执行"
    elif [ -f "$SCRIPT_DIR/ehr_cron_approve.sh" ] && [ -x "$SCRIPT_DIR/ehr_cron_approve.sh" ]; then
        print_success "审批脚本: 存在且可执行"
    else
        print_error "审批脚本: 不存在或不可执行"
    fi
    
    # 检查Python脚本
    if [ -f "$SCRIPT_DIR/ehr_browser_automation.py" ]; then
        print_success "Python自动化脚本: 存在"
    else
        print_error "Python自动化脚本: 不存在"
    fi
    
    # 检查凭据文件
    if [ -f "$HOME/.hermes/secrets/ehr_sercomm.txt" ]; then
        print_success "凭据文件: 存在"
    else
        print_error "凭据文件: 不存在"
    fi
    
    # 检查日志目录
    if [ -d "$LOG_DIR" ]; then
        print_success "日志目录: 存在"
        print_info "日志文件数量: $(ls -1 "$LOG_DIR"/*.log 2>/dev/null | wc -l)"
    else
        print_error "日志目录: 不存在"
    fi
    
    # 检查cron任务
    if crontab -l | grep -q "ehr_cron_approve.sh"; then
        print_success "Cron任务: 已设置"
        print_info "下次执行时间: $(crontab -l | grep 'ehr_cron_approve.sh' | head -1)"
    else
        print_error "Cron任务: 未设置"
    fi
}

# 手动执行审批
run_manual_approve() {
    print_info "手动执行审批任务..."
    
    if [ -f "$SCRIPT_DIR/ehr_cron_approve.sh" ]; then
        print_info "开始执行审批脚本..."
        "$SCRIPT_DIR/ehr_cron_approve.sh"
        print_success "审批任务执行完成"
    else
        print_error "审批脚本不存在"
    fi
}

# 查看最近的日志
view_logs() {
    print_info "查看最近的审批日志..."
    
    if [ -d "$LOG_DIR" ]; then
        recent_logs=$(ls -t "$LOG_DIR"/ehr_cron_*.log 2>/dev/null | head -5)
        
        if [ -n "$recent_logs" ]; then
            for log_file in $recent_logs; do
                echo ""
                echo "📄 $(basename "$log_file")"
                echo "📅 $(date -r "$log_file" '+%Y-%m-%d %H:%M:%S')"
                echo "📝 最近10行:"
                echo "----------------"
                tail -10 "$log_file"
                echo ""
            done
        else
            print_warning "没有找到最近的日志文件"
        fi
    else
        print_error "日志目录不存在"
    fi
}

# 生成测试报告
generate_test_report() {
    print_info "生成测试报告..."
    
    report_file="$LOG_DIR/ehr_test_report_$(date '+%Y%m%d_%H%M%S').txt"
    
    {
        echo "eHR自动审批系统测试报告"
        echo "======================"
        echo "生成时间: $(date '+%Y-%m-%d %H:%M:%S')"
        echo ""
        echo "系统状态检查:"
        echo "-------------"
        
        # 检查各个组件
        if [ -f "$SCRIPT_DIR/ehr_cron_approve.sh" ] && [ -x "$SCRIPT_DIR/ehr_cron_approve.sh" ]; then
            echo "✅ 审批脚本: 正常"
        else
            echo "❌ 审批脚本: 异常"
        fi
        
        if [ -f "$HOME/.hermes/secrets/ehr_sercomm.txt" ]; then
            echo "✅ 凭据文件: 存在"
        else
            echo "❌ 凭据文件: 不存在"
        fi
        
        if [ -d "$LOG_DIR" ]; then
            echo "✅ 日志目录: 存在"
            echo "   日志文件数: $(ls -1 "$LOG_DIR"/*.log 2>/dev/null | wc -l)"
        else
            echo "❌ 日志目录: 不存在"
        fi
        
        if crontab -l | grep -q "ehr_cron_approve.sh"; then
            echo "✅ Cron任务: 已设置"
            echo "   执行时间: $(crontab -l | grep 'ehr_cron_approve.sh' | head -1)"
        else
            echo "❌ Cron任务: 未设置"
        fi
        
        echo ""
        echo "Cron任务详情:"
        echo "-------------"
        crontab -l | grep -E "(ehr_cron|ehr_weekly)" || echo "无相关cron任务"
        
        echo ""
        echo "建议操作:"
        echo "---------"
        if ! crontab -l | grep -q "ehr_cron_approve.sh"; then
            echo "- 运行 'ehr_manager setup' 来设置cron任务"
        fi
        
        if [ ! -f "$HOME/.hermes/secrets/ehr_sercomm.txt" ]; then
            echo "- 请确保凭据文件存在"
        fi
        
    } > "$report_file"
    
    print_success "测试报告已生成: $report_file"
}

# 设置cron任务
setup_cron() {
    print_info "设置eHR自动审批cron任务..."
    
    # 创建cron文件
    cat > "$CRON_FILE" << 'EOF'
# eHR系统自动审批Cron任务
# 每天上午8点执行
0 8 * * * /Users/jessexia/.hermes/scripts/ehr_cron_approve.sh

# 每天下午6点执行  
0 18 * * * /Users/jessexia/.hermes/scripts/ehr_cron_approve.sh

# 每周日生成汇总报告
0 7 * * 0 /Users/jessexia/.hermes/scripts/ehr_weekly_report.sh
EOF
    
    # 安装cron任务
    crontab "$CRON_FILE"
    
    if [ $? -eq 0 ]; then
        print_success "Cron任务设置成功"
        print_info "任务已添加:"
        cat "$CRON_FILE"
    else
        print_error "Cron任务设置失败"
    fi
    
    # 清理临时文件
    rm -f "$CRON_FILE"
}

# 移除cron任务
remove_cron() {
    print_info "移除eHR自动审批cron任务..."
    
    # 创建新的crontab文件，排除我们的任务
    crontab -l | grep -v "ehr_cron_approve.sh" | grep -v "ehr_weekly_report.sh" | crontab -
    
    if [ $? -eq 0 ]; then
        print_success "Cron任务已移除"
    else
        print_error "移除cron任务失败"
    fi
}

# 显示帮助信息
show_help() {
    echo "eHR自动审批系统管理脚本"
    echo "========================"
    echo ""
    echo "用法: ehr_manager <命令>"
    echo ""
    echo "可用命令:"
    echo "  status     - 检查系统状态"
    echo "  manual     - 手动执行审批"
    echo "  logs       - 查看最近日志"
    echo "  report     - 生成测试报告"
    echo "  setup      - 设置cron任务"
    echo "  remove     - 移除cron任务"
    echo "  help       - 显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  ehr_manager status     # 检查系统状态"
    echo "  ehr_manager manual     # 手动执行审批"
    echo "  ehr_manager logs       # 查看最近日志"
}

# 主函数
main() {
    case "${1:-status}" in
        "status")
            check_status
            ;;
        "manual")
            run_manual_approve
            ;;
        "logs")
            view_logs
            ;;
        "report")
            generate_test_report
            ;;
        "setup")
            setup_cron
            ;;
        "remove")
            remove_cron
            ;;
        "help")
            show_help
            ;;
        *)
            print_error "未知命令: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"