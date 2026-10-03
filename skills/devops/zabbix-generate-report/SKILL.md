---
name: zabbix-generate-report
description: ���� �� 根据分析结果生成Zabbix巡检报告
---

# Zabbix �� 生成巡检报告技能

根据分析结果生成结构化的Zabbix巡检报告，包含健康状态、风险点、建议措施等。

## 使用方法

```bash
# ���� �� �� 生成报告（需要先获取分析结果）
ANALYSIS=$(zabbix-analyze-problems)
REPORT=$(echo "$ANALYSIS" | zabbix-generate-report)

# ���� �� �� 从文件生成报告
zabbix-generate-report --file analysis.json

# ���� �� �� 保存到文件
zabbix-generate-report --output report.txt
```

## ���� �核心工作流

### ���� �� �� 报告生成逻辑

```python
def generate_report(problems_analysis, vmware_devices, zabbix_status):
    report = []
    
    # 报告标题
    report.append("=" * 60)
    report.append("Zabbix VMWare全局巡检报告")
    report.append(f"巡检时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"时间范围: 过去24小时")
    report.append("=" * 60)
    
    # 1. Zabbix服务器健康状态
    report.append("\n【1. Zabbix服务器健康状态】")
    report.append(f"总体健康结论: Zabbix服务器运行正常，版本{zabbix_status['version']}，监控{zabbix_status['monitored_hosts']}台主机")
    
    zabbix_risks = []
    if problems_analysis['active']:
        zabbix_risks.append(f"存在{len(problems_analysis['active'])}个活动告警需要关注")
    
    if zabbix_risks:
        report.append(f"主要风险点:")
        for i, risk in enumerate(zabbix_risks[:3], 1):
            report.append(f"  {i}. {risk}")
    
    # 2. VMware ESXi主机健康状态
    report.append("\n【2. VMware ESXi主机健康状态】")
    if vmware_devices['hypervisors']:
        report.append(f"总体健康结论: {len(vmware_devices['hypervisors'])}台ESXi主机运行基本正常")
        
        esxi_risks = []
        for hypervisor in vmware_devices['hypervisors']:
            if hypervisor['status'] != '0':  # 0表示监控中
                esxi_risks.append(f"{hypervisor['name']}状态异常")
        
        if problems_analysis['by_severity']['high'] > 0 or problems_analysis['by_severity']['disaster'] > 0:
            esxi_risks.append(f"存在{problems_analysis['by_severity']['high']}个高风险和{problems_analysis['by_severity']['disaster']}个灾难性告警")
        
        if esxi_risks:
            report.append(f"主要风险点:")
            for i, risk in enumerate(esxi_risks[:3], 1):
                report.append(f"  {i}. {risk}")
    else:
        report.append("总体健康结论: 未发现ESXi主机")
        report.append("主要风险点: 1. ESXi主机可能未正确添加到Zabbix监控")
    
    # 3. VMware虚拟机健康状态
    report.append("\n【3. VMware虚拟机健康状态】")
    if vmware_devices['vms']:
        report.append(f"总体健康结论: {len(vmware_devices['vms'])}台虚拟机运行基本正常")
        
        vm_risks = []
        for vm in vmware_devices['vms']:
            if vm['status'] != '0':  # 0表示监控中
                vm_risks.append(f"{vm['name']}状态异常")
        
        # 检查CPU相关问题
        cpu_problems = [p for p in problems_analysis['active'] if 'cpu' in p.get('name', '').lower()]
        if cpu_problems:
            vm_risks.append(f"{len(cpu_problems)}个虚拟机CPU相关问题")
        
        if vm_risks:
            report.append(f"主要风险点:")
            for i, risk in enumerate(vm_risks[:3], 1):
                report.append(f"  {i}. {risk}")
    else:
        report.append("总体健康结论: 未发现虚拟机")
        report.append("主要风险点: 1. 虚拟机可能未正确添加到Zabbix监控")
    
    # 4. VMware vCenter健康状态
    report.append("\n【4. VMware vCenter健康状态】")
    if vmware_devices['vcenters']:
        report.append(f"总体健康结论: {len(vmware_devices['vcenters'])}台vCenter运行正常")
        
        vcenter_risks = []
        for vcenter in vmware_devices['vcenters']:
            if vcenter['status'] != '0':
                vcenter_risks.append(f"{vcenter['name']}状态异常")
        
        if vcenter_risks:
            report.append(f"主要风险点:")
            for i, risk in enumerate(vcenter_risks[:3], 1):
                report.append(f"  {i}. {risk}")
    else:
        report.append("总体健康结论: 未发现vCenter")
        report.append("主要风险点: 1. vCenter可能未正确添加到Zabbix监控")
    
    # 5. 问题统计汇总
    report.append("\n【5. 问题统计汇总】")
    report.append(f"总问题数: {problems_analysis['total']}")
    report.append(f"活动问题: {len(problems_analysis['active'])}")
    report.append(f"已解决问题: {len(problems_analysis['resolved'])}")
    
    report.append("\n按严重度分布:")
    severity_names = ["未分类", "信息", "警告", "一般", "高", "灾难"]
    for i, (severity, count) in enumerate(problems_analysis['by_severity'].items()):
        if count > 0:
            report.append(f"  {severity_names[i]}: {count}")
    
    # 6. 建议措施
    report.append("\n【6. 建议措施】")
    suggestions = []
    
    if problems_analysis['active']:
        suggestions.append("1. 立即处理活动告警，优先处理高/灾难级别告警")
    
    if problems_analysis['by_severity']['warning'] > 10:
        suggestions.append("2. 警告级别告警过多，建议检查监控阈值设置")
    
    if len(vmware_devices['vms']) > 0 and len([p for p in problems_analysis['active'] if 'cpu' in p.get('name', '').lower()]) > 0:
        suggestions.append("3. 虚拟机CPU使用率异常，建议资源扩容或优化应用")
    
    if len(vmware_devices['hypervisors']) == 0:
        suggestions.append("4. ESXi主机未监控，建议添加VMware监控模板")
    
    if len(vmware_devices['vcenters']) == 0:
        suggestions.append("5. vCenter未监控，建议添加vCenter监控")
    
    for i, suggestion in enumerate(suggestions, 1):
        report.append(f"  {suggestion}")
    
    # 7. 可写成Hermes技能的巡检流程
    report.append("\n【7. 可写成Hermes技能的巡检流程】")
    skill_suggestions = [
        "zabbix-vmware-health-check: 自动化VMWare环境健康巡检",
        "zabbix-performance-trend-analysis: 性能趋势分析和预测",
        "zabbix-capacity-planning: 容量规划和资源优化建议",
        "zabbix-automated-response: 告警自动响应和自愈流程",
        "zabbix-compliance-check: 合规性检查和审计报告"
    ]
    
    for i, skill in enumerate(skill_suggestions, 1):
        report.append(f"  {i}. {skill}")
    
    return "\n".join(report)
```

## ��� � 参数说明

| 参数 | 说明 | � 默认值 |
|------|------|--------|
| `--file` | 从文件读取分析结果 | stdin |
| `--output` | 输出文件路径 | stdout |
| `--help` | 显示帮助信息 | - |

## ��� � � 输出格式

### ���� �� 文本格式（默认）
结构化报告，包含：
1. Zabbix服务器健康状态
2. VMware ESXi主机健康状态
3. VMware虚拟机健康状态
4. VMware vCenter健康状态
5. 问题统计汇总
6. 建议措施
7. 可写成Hermes技能的巡检流程

### ���� �� JSON格式
```json
{
  "zabbix_server": {
    "status": "正常",
    "version": "7.4.9",
    "monitored_hosts": 360,
    "risks": [
      "存在10个活动告警需要关注"
    ]
  },
  "vmware_esxi": {
    "status": "基本正常",
    "count": 12,
    "risks": [
      "存在1个高风险和0个灾难性告警"
    ]
  },
  "vmware_vms": {
    "status": "基本正常",
    "count": 209,
    "risks": [
      "R_Jeffy_FTP_testlog_66.152-bak状态异常",
      "R_Jeffy_FTP_testlog_66.152_2026-08-05_12-47-54状态异常"
    ]
  },
  "vmware_vcenter": {
    "status": "正常",
    "count": 3,
    "risks": []
  },
  "problems": {
    "total": 10,
    "active": 10,
    "resolved": 0,
    "by_severity": {
      "warning": 6,
      "average": 3,
      "high": 1
    }
  },
  "suggestions": [
    "立即处理活动告警，优先处理高/灾难级别告警"
  ],
  "skill_suggestions": [
    "zabbix-vmware-health-check: 自动化VMWare环境健康巡检",
    "zabbix-performance-trend-analysis: 性能趋势分析和预测",
    "zabbix-capacity-planning: 容量规划和资源优化建议",
    "zabbix-automated-response: 告警自动响应和自愈流程",
    "zabbix-compliance-check: 合规性检查和审计报告"
  ]
}
```

## �� 报告结构

1. **Zabbix服务器健康状态**：版本、监控主机数量、风险点
2. **VMware ESXi主机健康状态**：主机数量、状态、风险点
3. **VMware虚拟机健康状态**：虚拟机数量、状态、风险点
4. **VMware vCenter健康状态**：vCenter数量、状态、风险点
5. **问题统计汇总**：总问题数、活动问题、已解决问题、严重度分布
6. **建议措施**：针对风险点的建议
7. **可写成Hermes技能的巡检流程**：推荐的技能列表

## ��� �� � 错误处理

- 输入数据无效：返回退出码 1
- JSON解析错误：返回退出码 2
- 处理错误：返回退出码 3

## 相关技能

- `zabbix-analyze-problems` - ���� �� 分析问题数据
- `zabbix-get-vmware-devices` - ���� �� �� 获取VMware设备信息
- `zabbix-get-server-status` - ���� �� �� 获取Zabbix服务器状态