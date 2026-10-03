#!/bin/bash

# eHR系统周报生成脚本
# 每周日生成上周审批汇总报告
# 作者: Jesse Xia
# 创建日期: 2026-08-04

# 配置
LOG_DIR="$HOME/.hermes/logs"
REPORT_FILE="$LOG_DIR/ehr_weekly_report_$(date '+%Y%m%d').txt"
PREVIOUS_WEEK_LOGS="$LOG_DIR/ehr_cron_$(date -v -7d '+%Y%m%d')*.log"

# 创建报告目录
mkdir -p "$LOG_DIR"

# 生成周报
generate_weekly_report() {
    echo "eHR系统自动审批周报"
    echo "===================="
    echo "报告生成时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "报告周期: $(date -v -7d '+%Y-%m-%d') 至 $(date '+%Y-%m-%d')"
    echo ""
    
    # 统计数据
    echo "📊 本周统计"
    echo "-----------"
    
    # 查找上周的日志文件
    if ls $PREVIOUS_WEEK_LOGS 1> /dev/null 2>&1; then
        echo "总执行次数: $(ls $PREVIOUS_WEEK_LOGS | wc -l) 次"
        
        # 统计成功次数
        success_count=$(grep -r "登录成功" $PREVIOUS_WEEK_LOGS | wc -l)
        echo "成功登录次数: $success_count 次"
        
        # 统计审批次数
        approve_count=$(grep -r "批量审批成功" $PREVIOUS_WEEK_LOGS | wc -l)
        echo "成功审批次数: $approve_count 次"
        
        # 统计单据总数
        total_forms=$(grep -r "总共选择了" $PREVIOUS_WEEK_LOGS | awk -F' ' '{sum+=$3} END {print sum}')
        echo "处理单据总数: ${total_forms:-0} 个"
        
        echo ""
    else
        echo "⚠️ 未找到上周日志文件"
        echo ""
    fi
    
    # 详细记录
    echo "📋 详细记录"
    echo "-----------"
    if ls $PREVIOUS_WEEK_LOGS 1> /dev/null 2>&1; then
        for log_file in $PREVIOUS_WEEK_LOGS; do
            if [ -f "$log_file" ]; then
                echo ""
                echo "📅 $(basename "$log_file" | sed 's/ehr_cron_//' | sed 's/\.log$//')"
                echo "时间戳: $(head -1 "$log_file" | cut -d'[' -f2 | cut -d']' -f1)"
                
                # 提取关键信息
                login_status=$(grep "登录.*成功\|登录.*失败" "$log_file" | tail -1)
                form_count=$(grep "总共选择了" "$log_file" | tail -1)
                approval_result=$(grep "审批.*成功\|审批.*失败" "$log_file" | tail -1)
                
                echo "登录状态: ${login_status:-未知}"
                echo "单据数量: ${form_count:-未知}"
                echo "审批结果: ${approval_result:-未知}"
            fi
        done
    else
        echo "暂无详细记录"
    fi
    
    echo ""
    echo "💡 备注"
    echo "-----"
    echo "- 自动审批任务每天执行两次（上午8点，下午6点）"
    echo "- 如需查看详细日志，请查看对应日期的日志文件"
    echo "- 如遇异常情况，请检查凭据文件和网络连接"
}

# 主函数
main() {
    echo "生成eHR系统周报..."
    generate_weekly_report > "$REPORT_FILE"
    echo "周报已生成: $REPORT_FILE"
}

# 执行主函数
main "$@"