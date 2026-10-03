# Pareto分析技能

## 技能概述
基于80/20法则，识别关键少数和次要多数，确定问题优先级。

## 使用方法
```bash
# 基本Pareto分析
data-analysis-models pareto-analysis --data-file "error_types.csv" --value-column "count" --category-column "error_type"

# 多维度Pareto分析
data-analysis-models pareto-analysis --data "performance_issues.csv" --metrics "frequency,impact,time" --output "pareto_report.html"
```

## 分析维度

### 1. 累积贡献分析
- **80/20法则**: 识别贡献80%结果的20%因素
- **累积曲线**: 展示累积贡献度变化
- **关键因素**: 确定影响最大的关键因素

### 2. 优先级排序
- **重要性排序**: 按影响程度排序
- **紧急性评估**: 结合时间因素评估
- **综合评分**: 多维度综合评分

### 3. 聚类分析
- **高影响低频率**: 重点关注类
- **高影响高频率**: 优先处理类
- **低影响高频率**: 监控观察类
- **低影响低频率**: 忽略处理类

## 分析步骤
1. **数据收集**: 收集分类数据及对应数值
2. **排序计算**: 按数值大小排序并计算百分比
3. **累积计算**: 计算累积贡献度
4. **关键识别**: 识别80/20分界点
5. **建议制定**: 针对关键因素制定处理策略

## 输出格式
```json
{
  "pareto_analysis": {
    "total_items": 15,
    "pareto_threshold": 80,
    "categories": [
      {
        "name": "database_errors",
        "value": 1250,
        "percentage": 35.2,
        "cumulative_percentage": 35.2,
        "priority": "critical",
        "action": "立即处理"
      },
      {
        "name": "network_timeouts",
        "value": 890,
        "percentage": 25.1,
        "cumulative_percentage": 60.3,
        "priority": "high",
        "action": "优先处理"
      },
      {
        "name": "memory_leaks",
        "value": 420,
        "percentage": 11.8,
        "cumulative_percentage": 72.1,
        "priority": "medium",
        "action": "计划处理"
      }
    ],
    "key_findings": {
      "top_20_percent": 3,
      "contribute_80_percent": 72.1,
      "focus_areas": ["database_errors", "network_timeouts"]
    },
    "recommendations": [
      "重点关注数据库错误，占总错误的35.2%",
      "网络超时问题需要优先解决",
      "内存泄漏问题可以稍后处理"
    ]
  }
}
```

## IT运维应用示例
```bash
# 场景1: 故障类型Pareto分析
data-analysis-models pareto-analysis \
  --data "incidents.csv" \
  --value "resolution_time" \
  --category "error_category" \
  --threshold 80 \
  --output "incident_pareto.html"

# 场景2: 性能问题Pareto分析
data-analysis-models pareto-analysis \
  --data "performance_metrics.csv" \
  --metrics "cpu_usage,response_time,error_count" \
  --weight "0.3,0.4,0.3" \
  --output "performance_pareto.html"
```

## 可视化选项
- **Pareto柱状图**: 展示各类别的贡献度
- **累积曲线**: 展示累积贡献度变化
- **帕累托图**: 柱状图+累积曲线组合
- **优先级矩阵**: 多维度优先级展示
- **改进效果**: 展示改进前后的对比

## 高级功能
- **动态Pareto**: 分析随时间变化的优先级
- **多目标Pareto**: 多个目标的权衡分析
- **敏感性分析**: 分析阈值变化的影响
- **预测模型**: 预测未来优先级变化

## 注意事项
- 确保分类的完整性和互斥性
- 选择合适的数值指标
- 结合业务背景解释优先级
- 定期更新分析结果
- 关注关键因素的动态变化