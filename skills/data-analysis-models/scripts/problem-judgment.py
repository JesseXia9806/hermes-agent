# 问题判断与模型选择技能

## 技能概述
作为分析流程的第一步，帮助判断问题的本质类型，选择最适合的分析模型。

## 使用方法
```bash
# 基本使用
data-analysis-models problem-judgment --question "我们的系统响应时间变慢了"

# 详细分析
data-analysis-models problem-judgment --question "用户流失率上升" --context "最近3个月数据"
```

## 判断维度

### 1. 数据是否有问题？
- **判断标准**: 是否偏离正常范围、目标值或历史基准
- **推荐模型**: 对比分析 (Comparison Analysis)
- **适用场景**: 
  - 性能指标是否达标
  - 错误率是否异常
  - 成本是否超预算

### 2. 变化何时开始？
- **判断标准**: 识别变化的时间点、拐点或周期性
- **推荐模型**: 趋势分析 (Trend Analysis)
- **适用场景**:
  - 系统负载突然变化
  - 用户行为模式转变
  - 业务指标周期性波动

### 3. 结果由谁构成？
- **判断标准**: 分析结果的组成结构和贡献度
- **推荐模型**: 结构分析 / Pareto分析
- **适用场景**:
  - 故障来源分布
  - 用户群体构成
  - 成本构成分析

### 4. 在哪环节损失最大？
- **判断标准**: 识别流程中最大的瓶颈或流失点
- **推荐模型**: 漏斗分析 (Funnel Analysis)
- **适用场景**:
  - 故障处理流程
  - 用户支持转化率
  - 业务流程效率

## 输出格式
```json
{
  "problem_type": "data_issue",
  "recommended_models": ["comparison-analysis", "trend-analysis"],
  "analysis_steps": [
    "收集历史基准数据",
    "对比当前数据与基准",
    "识别异常时间点"
  ],
  "success_criteria": [
    "确定是否真的存在问题",
    "找出问题的具体表现",
    "选择合适的分析模型"
  ]
}
```

## IT运维应用示例
```bash
# 场景1: 系统响应时间变慢
data-analysis-models problem-judgment --question "系统响应时间从50ms上升到200ms" --context "过去7天数据"

# 场景2: 用户投诉增加
data-analysis-models problem-judgment --question "本周用户投诉数量翻倍" --context "客服工单系统"
```

## 注意事项
- 不要一上来就套用分析方法
- 先理清楚问题本质
- 往往需要多个模型组合使用
- 确保数据质量和完整性