# 对比分析技能

## 技能概述
通过对比不同维度的数据，判断是否达标、是否改善、与目标对象差距多少。

## 使用方法
```bash
# 基本对比
data-analysis-models comparison-analysis --data-file "performance_metrics.csv" --baseline "2025-01" --current "2026-01"

# 多维度对比
data-analysis-models comparison-analysis --data "CPU使用率,内存使用率,响应时间" --periods "2025-Q4,2026-Q1" --output "comparison_report.html"
```

## 分析维度

### 1. 时间对比
- **同比**: 与去年同期对比
- **环比**: 与上一周期对比
- **趋势**: 多个时间点序列对比

### 2. 对象对比
- **横向对比**: 不同系统/部门/团队对比
- **纵向对比**: 同一对象不同时期对比
- **基准对比**: 与目标值/标准值对比

### 3. 统计指标
- **绝对差异**: 当前值 - 基准值
- **相对差异**: (当前值 - 基准值) / 基准值
- **变化率**: (当前值 / 基准值 - 1) * 100%

## 分析步骤
1. **确定对比基准**: 选择合适的对比对象和时间点
2. **数据标准化**: 确保数据格式和单位一致
3. **计算差异**: 计算绝对差异和相对差异
4. **显著性检验**: 判断差异是否具有统计意义
5. **可视化展示**: 使用图表直观展示对比结果

## 输出格式
```json
{
  "comparison_type": "time_period",
  "baseline": "2025-01",
  "current": "2026-01",
  "metrics": {
    "cpu_usage": {
      "baseline": 45.2,
      "current": 67.8,
      "absolute_diff": 22.6,
      "relative_diff": 0.50,
      "change_rate": 50.0
    }
  },
  "significance": "significant",
  "recommendations": [
    "CPU使用率显著上升，需要检查系统负载",
    "建议进行性能优化或扩容"
  ]
}
```

## IT运维应用示例
```bash
# 场景1: 系统性能对比
data-analysis-models comparison-analysis \
  --data "cpu_usage,memory_usage,response_time" \
  --periods "2025-12,2026-01" \
  --threshold 10 \
  --output "performance_comparison.html"

# 场景2: 故障率对比
data-analysis-models comparison-analysis \
  --data "server_errors,db_errors,app_errors" \
  --periods "2025-Q4,2026-Q1" \
  --baseline-target "error_rate < 0.1%" \
  --output "error_rate_analysis.html"
```

## 可视化选项
- **柱状图**: 展示不同时期/对象的数值对比
- **折线图**: 展示时间序列的变化趋势
- **热力图**: 展示多个维度的对比结果
- **仪表盘**: 展示关键指标的达成情况

## 注意事项
- 确保数据质量和完整性
- 选择合适的对比基准
- 考虑季节性和周期性因素
- 关注统计显著性，避免误判正常波动