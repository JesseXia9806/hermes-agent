# RFM分析技能

## 技能概述
基于Recency（最近消费时间）、Frequency（消费频率）、Monetary（消费金额）三个维度，识别高价值用户、潜在流失用户和潜力用户。

## 使用方法
```bash
# 基本RFM分析
data-analysis-models rfm-analysis --data-file "customer_transactions.csv" --date-column "purchase_date" --frequency-column "purchase_count" --monetary-column "amount"

# 多维度RFM分析
data-analysis-models rfm-analysis --data "user_behavior.csv" --dimensions "login_frequency,session_duration,feature_usage" --output "rfm_segmentation.html"
```

## 分析维度

### 1. R (Recency) - 最近度
- **时间间隔**: 距离最近行为的时间
- **活跃程度**: 用户的活跃程度
- **新鲜度**: 用户的最新程度
- **衰减分析**: 用户活跃度的衰减情况

### 2. F (Frequency) - 频率
- **行为次数**: 特定行为的执行次数
- **使用频率**: 用户的使用频率
- **参与度**: 用户的参与程度
- **规律性**: 用户行为的规律性

### 3. M (Monetary) - 价值
- **消费金额**: 用户的消费金额
- **价值贡献**: 用户的总价值贡献
- **平均价值**: 单次行为的平均价值
- **价值增长**: 用户价值的增长趋势

## 分析步骤
1. **数据准备**: 收集用户行为数据
2. **指标计算**: 计算R、F、M三个维度的指标
3. **评分标准化**: 将各维度标准化为评分
4. **群体划分**: 根据评分划分用户群体
5. **策略制定**: 针对不同群体制定策略

## 输出格式
```json
{
  "rfm_analysis": {
    "analysis_period": "2025-01-01 to 2025-12-31",
    "total_users": 10000,
    "rfm_segments": {
      "champions": {
        "count": 1500,
        "percentage": 15.0,
        "r_score": 4,
        "f_score": 4,
        "m_score": 4,
        "characteristics": "高价值忠实用户",
        "behavior": "最近活跃，高频次，高消费",
        "strategy": "保持忠诚度，提供VIP服务"
      },
      "loyal_customers": {
        "count": 2000,
        "percentage": 20.0,
        "r_score": 3,
        "f_score": 4,
        "m_score": 3,
        "characteristics": "忠实但消费中等",
        "behavior": "经常使用，消费稳定",
        "strategy": "提升消费金额，交叉销售"
      },
      "potential_loyalists": {
        "count": 1800,
        "percentage": 18.0,
        "r_score": 4,
        "f_score": 3,
        "m_score": 3,
        "characteristics": "新用户但有潜力",
        "behavior": "最近活跃，频率中等",
        "strategy": "培养使用习惯，提升忠诚度"
      },
      "at_risk": {
        "count": 1200,
        "percentage": 12.0,
        "r_score": 1,
        "f_score": 3,
        "m_score": 3,
        "characteristics": "有流失风险",
        "behavior": "最近不活跃，但曾经高频",
        "strategy": "重新激活，提供激励"
      },
      "new_customers": {
        "count": 1000,
        "percentage": 10.0,
        "r_score": 4,
        "f_score": 1,
        "m_score": 1,
        "characteristics": "新用户",
        "behavior": "最近注册，使用次数少",
        "strategy": "引导使用，建立信任"
      }
    },
    "key_metrics": {
      "high_value_users": 3500,
      "at_risk_users": 1200,
      "new_opportunities": 1000,
      "total_value": 2500000
    },
    "recommendations": [
      "重点关注Champions群体，保持他们的忠诚度",
      "对Loyal Customers进行交叉销售，提升M值",
      "对At Risk用户进行重新激活活动",
      "对新用户提供引导和支持"
    ]
  }
}
```

## IT运维应用示例
```bash
# 场景1: 系统用户RFM分析
data-analysis-models rfm-analysis \
  --data "system_usage.csv" \
  --dimensions "login_date,login_count,session_duration" \
  --scoring_method "quantile" \
  --output "system_rfm_analysis.html"

# 场景2: 服务使用RFM分析
data-analysis-models rfm-analysis \
  --data "service_usage.csv" \
  --dimensions "usage_date,usage_count,cost" \
  --weight "0.3,0.3,0.4" \
  --output "service_rfm_analysis.html"
```

## 可视化选项
- **RFM矩阵**: 展示用户在三维空间中的分布
- **群体分布图**: 展示各群体的数量和比例
- **价值金字塔**: 展示用户价值层次
- **生命周期曲线**: 展示用户生命周期阶段
- **转化漏斗**: 展示群体间的转化关系

## 高级功能
- **动态RFM**: 分析用户群体随时间的变化
- **预测模型**: 预测用户未来的行为和价值
- **个性化推荐**: 基于RFM群体制定个性化策略
- **效果评估**: 评估RFM策略的实施效果

## 注意事项
- 确保数据的准确性和完整性
- 选择合适的评分标准和方法
- 考虑业务背景和用户特征
- 定期更新RFM分析结果
- 结合其他分析方法综合判断