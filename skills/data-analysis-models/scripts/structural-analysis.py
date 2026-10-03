# 结构分析技能

## 技能概述
分析结果的组成结构，找出"结果是谁构成的"，理解各部分的贡献度。

## 使用方法
```bash
# 基本结构分析
data-analysis-models structural-analysis --data-file "cost_breakdown.csv" --metric "total_cost" --components "hardware,software,maintenance"

# 多层级结构分析
data-analysis-models structural-analysis --data "department_budgets.csv" --hierarchy "company->department->team" --output "structure_analysis.html"
```

## 分析维度

### 1. 结构组成
- **比例分析**: 各组成部分占总体的百分比
- **贡献度分析**: 各部分对整体变化的贡献
- **层次结构**: 多层级组成关系

### 2. 结构变化
- **结构稳定性**: 结构随时间的变化程度
- **异常结构**: 偏离正常结构的异常情况
- **结构优化**: 识别结构优化的机会点

### 3. 结构关系
- **相关性分析**: 各组成部分之间的关联
- **依赖关系**: 识别关键依赖环节
- **平衡性**: 分析结构的均衡程度

## 分析步骤
1. **数据收集**: 收集结构化数据
2. **结构分解**: 按维度进行层级分解
3. **比例计算**: 计算各部分的比例和贡献度
4. **结构验证**: 检查结构的完整性和合理性
5. **优化建议**: 提出结构优化建议

## 输出格式
```json
{
  "structural_analysis": {
    "target_metric": "total_cost",
    "total_value": 1250000,
    "components": [
      {
        "name": "hardware",
        "value": 500000,
        "percentage": 40.0,
        "contribution_to_change": 0.6,
        "significance": "high"
      },
      {
        "name": "software",
        "value": 375000,
        "percentage": 30.0,
        "contribution_to_change": 0.3,
        "significance": "medium"
      },
      {
        "name": "maintenance",
        "value": 375000,
        "percentage": 30.0,
        "contribution_to_change": 0.1,
        "significance": "low"
      }
    ],
    "structure_stability": 0.75,
    "optimization_opportunities": [
      "硬件成本占比过高，建议优化采购策略",
      "维护成本相对稳定，继续保持"
    ]
  }
}
```

## IT运维应用示例
```bash
# 场景1: 故障来源结构分析
data-analysis-models structural-analysis \
  --data "incident_data.csv" \
  --metric "incident_count" \
  --components "server,db,application,network" \
  --period "2025-Q4" \
  --output "incident_structure.html"

# 场景2: 成本结构分析
data-analysis-models structural-analysis \
  --data "it_costs.csv" \
  --metric "total_cost" \
  --hierarchy "department->service->resource" \
  --trend-analysis \
  --output "cost_structure.html"
```

## 可视化选项
- **饼图**: 展示各部分的比例关系
- **树状图**: 展示多层级结构关系
- **瀑布图**: 展示结构变化的累积效应
- **热力图**: 展示结构变化的强度
- **桑基图**: 展示结构流动和转换

## 高级功能
- **动态结构分析**: 分析结构随时间的变化
- **敏感性分析**: 分析各部分变化对整体的影响
- **优化路径**: 提供结构优化建议
- **预测模型**: 基于历史结构进行预测

## 注意事项
- 确保数据分类的完整性和互斥性
- 考虑结构的层次性和逻辑关系
- 关注关键组成部分的变化
- 结合业务背景解释结构意义