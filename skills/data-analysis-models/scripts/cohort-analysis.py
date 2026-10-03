# 同期群分析技能

## 技能概述
通过跟踪特定群体的行为变化，分析用户质量随时间的变化趋势，判断新用户质量是否改善或下降。

## 使用方法
```bash
# 基本同期群分析
data-analysis-models cohort-analysis --data-file "user_behavior.csv" --cohort-column "signup_month" --metric "retention_rate"

# 多维度同期群分析
data-analysis-models cohort-analysis --data "customer_data.csv" --cohorts "acquisition_quarter" --metrics "retention,spending,engagement" --output "cohort_report.html"
```

## 分析维度

### 1. 群体划分
- **时间维度**: 按注册时间、购买时间等划分
- **行为维度**: 按用户行为特征划分
- **来源维度**: 按获客渠道划分
- **特征维度**: 按用户属性划分

### 2. 行为追踪
- **留存率**: 不同时间点的用户留存情况
- **活跃度**: 用户的活跃程度变化
- **价值贡献**: 用户的价值贡献变化
- **生命周期**: 用户生命周期长度

### 3. 趋势对比
- **群体间对比**: 不同群体的表现对比
- **时间趋势**: 同一群体随时间的变化
- **质量变化**: 用户质量的变化趋势
- **衰减规律**: 用户行为的衰减模式

## 分析步骤
1. **群体定义**: 确定同期群的划分标准
2. **数据收集**: 收集各群体的行为数据
3. **指标计算**: 计算关键指标（留存率、活跃度等）
4. **趋势分析**: 分析群体随时间的变化趋势
5. **质量评估**: 评估用户质量的变化情况

## 输出格式
```json
{
  "cohort_analysis": {
    "analysis_type": "user_retention",
    "cohort_period": "monthly",
    "time_range": "2025-01 to 2025-12",
    "cohorts": [
      {
        "cohort": "2025-01",
        "size": 1200,
        "retention_rates": [
          {"period": "month_1", "rate": 1.0},
          {"period": "month_2", "rate": 0.85},
          {"period": "month_3", "rate": 0.72},
          {"period": "month_6", "rate": 0.45}
        ],
        "avg_retention": 0.755,
        "quality_trend": "declining",
        "cohort_value": 48000
      },
      {
        "cohort": "2025-06",
        "size": 1500,
        "retention_rates": [
          {"period": "month_1", "rate": 1.0},
          {"period": "month_2", "rate": 0.88},
          {"period": "month_3", "rate": 0.78},
          {"period": "month_6", "rate": 0.52}
        ],
        "avg_retention": 0.795,
        "quality_trend": "improving",
        "cohort_value": 62000
      }
    ],
    "key_findings": {
      "new_user_quality": "improving",
      "best_performing_cohort": "2025-06",
      "retention_decay_rate": 0.15,
      "cohort_value_growth": "+29.2%"
    },
    "recommendations": [
      "2025年6月后的用户质量明显改善",
      "建议分析6月获客策略的变化",
      "继续优化获客渠道，提升用户质量"
    ]
  }
}
```

## IT运维应用示例
```bash
# 场景1: 用户质量同期群分析
data-analysis-models cohort-analysis \
  --data "user_metrics.csv" \
  --cohorts "activation_month" \
  --metrics "login_frequency,session_duration,feature_usage" \
  --period "12m" \
  --output "user_quality_cohort.html"

# 场景2: 系统用户同期群分析
data-analysis-models cohort-analysis \
  --data "system_users.csv" \
  --cohorts "onboarding_date" \
  --metrics "system_usage,error_rate,satisfaction" \
  --dimensions "department,role" \
  --output "system_cohort_analysis.html"
```

## 可视化选项
- **热力图**: 展示不同群体在不同时间点的表现
- **曲线图**: 展示群体随时间的变化趋势
- **对比图**: 不同群体的表现对比
- **生命周期曲线**: 展示用户生命周期变化
- **质量趋势图**: 展示用户质量的变化趋势

## 高级功能
- **多群体交叉分析**: 分析不同群体的交叉影响
- **预测模型**: 预测未来群体表现
- **异常检测**: 识别异常群体表现
- **归因分析**: 分析群体差异的原因

## 注意事项
- 确保群体划分的合理性和一致性
- 考虑外部因素的影响
- 保证数据的时间连续性
- 结合业务背景解释结果
- 定期更新分析结果