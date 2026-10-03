# 趋势分析技能

## 技能概述
通过时间序列数据分析，识别变化趋势、周期性模式和异常拐点。

## 使用方法
```bash
# 基本趋势分析
data-analysis-models trend-analysis --data-file "system_metrics.csv" --metric "response_time" --period "30d"

# 多指标趋势对比
data-analysis-models trend-analysis --data "cpu_usage,memory_usage,throughput" --start-date "2025-01-01" --end-date "2026-01-01" --output "trend_report.html"
```

## 分析维度

### 1. 趋势类型识别
- **上升趋势**: 数值持续增加
- **下降趋势**: 数值持续减少
- **平稳趋势**: 数值相对稳定
- **周期性趋势**: 按固定周期波动

### 2. 拐点检测
- **突变点**: 数值突然大幅变化
- **转折点**: 上升趋势转为下降趋势
- **异常点**: 偏离正常范围的数据点

### 3. 趋势强度
- **强趋势**: 明显的上升/下降趋势
- **弱趋势**: 不明显的趋势变化
- **无趋势**: 随机波动

## 分析步骤
1. **数据预处理**: 清洗数据，处理缺失值
2. **趋势分解**: 分离趋势、季节性和随机成分
3. **统计检验**: 使用统计方法判断趋势显著性
4. **拐点识别**: 使用算法检测趋势变化点
5. **预测建模**: 基于历史趋势进行短期预测

## 输出格式
```json
{
  "trend_analysis": {
    "metric": "response_time",
    "period": "2025-01-01 to 2026-01-01",
    "trend_type": "increasing",
    "trend_strength": "strong",
    "significance": 0.001,
    "change_rate": 15.3,
    "turning_points": [
      {
        "date": "2025-06-15",
        "type": "acceleration",
        "magnitude": 25.6
      }
    ],
    "predictions": {
      "next_7_days": [120, 125, 130, 128, 135, 140, 138],
      "confidence": 0.85
    }
  }
}
```

## IT运维应用示例
```bash
# 场景1: 系统负载趋势分析
data-analysis-models trend-analysis \
  --data "cpu_usage,memory_usage,disk_io" \
  --start-date "2025-06-01" \
  --end-date "2026-01-01" \
  --detect-outliers \
  --output "system_trend_analysis.html"

# 场景2: 故障趋势分析
data-analysis-models trend-analysis \
  --data "incident_count,resolution_time" \
  --period "90d" \
  --trend-threshold 0.1 \
  --output "incident_trend_report.html"
```

## 可视化选项
- **时间序列图**: 展示数据随时间的变化
- **移动平均线**: 平滑短期波动，显示长期趋势
- **趋势线**: 拟合线性或非线性趋势
- **异常点标记**: 突出显示检测到的异常
- **预测区间**: 显示预测的不确定性范围

## 高级功能
- **多变量趋势分析**: 分析多个指标的相关性
- **季节性分解**: 识别周期性模式
- **异常检测**: 基于统计和机器学习方法
- **预测建模**: ARIMA、Prophet等时间序列模型

## 注意事项
- 确保数据时间序列的连续性
- 考虑季节性和周期性因素
- 区分正常波动和异常变化
- 避免过度外推预测结果