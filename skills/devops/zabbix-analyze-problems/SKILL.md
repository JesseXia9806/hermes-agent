---
name: zabbix-analyze-problems
description: ���� �� 分析Zabbix问题数据并生成统计报告
---

# Zabbix �� 分析问题数据技能

分析Zabbix问题数据，按活动/已解决状态、严重度等维度进行统计，生成结构化报告。

## 使用方法

```bash
# ���� �� �� 分析问题数据（需要先获取问题数据）
PROBLEMS=$(zabbix-get-problems)
ANALYSIS=$(echo "$PROBLEMS" | zabbix-analyze-problems)

# ���� �� �� 从文件分析
zabbix-analyze-problems --file problems.json

# ���� �� �� 以JSON格式输出
zabbix-analyze-problems --format json
```

## ���� �核心工作流

### ���� �� �� 分析逻辑

```python
def analyze_problems(problems):
    analysis = {
        "total": len(problems),
        "active": [],
        "resolved": [],
        "by_severity": {
            "not_classified": 0, 
            "information": 0, 
            "warning": 0, 
            "average": 0, 
            "high": 0, 
            "disaster": 0
        }
    }
    
    for problem in problems:
        # 分类问题
        if problem.get("r_eventid") == "0" or not problem.get("r_eventid"):
            analysis["active"].append(problem)
        else:
            analysis["resolved"].append(problem)
        
        # 按严重度统计
        severity = problem.get("severity", "0")
        try:
            severity_int = int(severity)
        except (ValueError, TypeError):
            severity_int = 0
        
        severity_names = ["not_classified", "information", "warning", 
                        "average", "high", "disaster"]
        if 0 <= severity_int < len(severity_names):
            analysis["by_severity"][severity_names[severity_int]] += 1
    
    return analysis
```

## ��� � 参数说明

| 参数 | 说明 | � 默认值 |
|------|------|--------|
| `--file` | 从文件读取问题数据 | stdin |
| `--format` | 输出格式 (text/json) | text |
| `--help` | 显示帮助信息 | - |

## ��� � � 输出格式

### ���� �� 文本格式（默认）
结构化报告：
```
总问题数: 10
活动问题: 8
已解决问题: 2

按严重度分布:
  未分类: 0
  信息: 1
  警告: 5
  一般: 2
  高: 1
  灾难: 1
```

### ���� �� JSON格式
```json
{
  "total": 10,
  "active_count": 8,
  "resolved_count": 2,
  "by_severity": {
    "not_classified": 0,
    "information": 1,
    "warning": 5,
    "average": 2,
    "high": 1,
    "disaster": 1
  },
  "active_problems": [...],
  "resolved_problems": [...]
}
```

## �� 严重度定义

| 严重度值 | 严重度名称 | 含义 |
|---------|-----------|------|
| 0 | not_classified | 未分类 |
| 1 | information | 信息 |
| 2 | warning | 警告 |
| 3 | average | 一般 |
| 4 | high | 高 |
| 5 | disaster | 灾难 |

## �� 问题状态判断

- **活动问题 (Active)**: `r_eventid` == "0" 或不存在
- **已解决问题 (Resolved)**: `r_eventid` != "0" 且存在

## ��� �� � 错误处理

- 输入数据无效：返回退出码 1
- JSON解析错误：返回退出码 2
- 处理错误：返回退出码 3

## 相关技能

- `zabbix-get-problems` - ���� �� �� 获取问题数据
- `zabbix-get-vmware-devices` - ���� �� �� 获取VMware设备信息
- `zabbix-get-server-status` - ���� �� �� 获取Zabbix服务器状态