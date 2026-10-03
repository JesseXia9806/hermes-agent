# Zabbix VMware 性能巡检报告模板

## 报告信息

- **报告生成时间**: {{timestamp}}
- **巡检范围**: {{device_type}}
- **设备总数**: {{total_devices}}
- **正常设备**: {{normal_devices}}
- **异常设备**: {{abnormal_devices}}

## 设备性能概览

### 资源使用率统计

| 资源类型 | 平均使用率 | 最高使用率 | 警告阈值 | 严重阈值 |
|----------|-------------|-------------|----------|----------|
| CPU | {{avg_cpu}}% | {{max_cpu}}% | 80% | 90% |
| 内存 | {{avg_memory}}% | {{max_memory}}% | 85% | 95% |
| 磁盘IO | {{avg_disk_io}} | {{max_disk_io}} | 100MB/s | 200MB/s |
| 网络流量 | {{avg_net}} | {{max_net}} | 100Mbps | 200Mbps |

### 设备分类统计

| 设备类型 | 数量 | 平均CPU使用率 | 平均内存使用率 | 平均运行时间 |
|----------|------|---------------|----------------|--------------|
| 虚拟机 | {{vm_count}} | {{vm_avg_cpu}}% | {{vm_avg_memory}}% | {{vm_avg_uptime}} |
| ESXi主机 | {{hv_count}} | {{hv_avg_cpu}}% | {{hv_avg_memory}}% | {{hv_avg_uptime}} |
| vCenter | {{vc_count}} | {{vc_avg_cpu}}% | {{vc_avg_memory}}% | {{vc_avg_uptime}} |

## 详细设备信息

### 🚨 高负载设备（CPU > 80% 或内存 > 85%）

{{#high_load_devices}}
#### {{name}} ({{hostid}})
- **状态**: {{status}}
- **IP地址**: {{ip}}
- **CPU使用率**: {{cpu_usage}}%
- **内存使用率**: {{memory_usage}}%
- **磁盘IO**: {{disk_io}} {{disk_io_units}}
- **网络流量**: {{net_traffic}} {{net_traffic_units}}
- **运行时间**: {{uptime}}

**建议**: 
- {{recommendation}}
{{/high_load_devices}}

### ⚠️ 异常设备

{{#abnormal_devices}}
#### {{name}} ({{hostid}})
- **状态**: {{status}}
- **IP地址**: {{ip}}
- **问题**: {{issue}}
- **建议**: {{recommendation}}
{{/abnormal_devices}}

### 📊 正常设备

{{#normal_devices}}
#### {{name}} ({{hostid}})
- **状态**: {{status}}
- **IP地址**: {{ip}}
- **CPU使用率**: {{cpu_usage}}%
- **内存使用率**: {{memory_usage}}%
- **磁盘IO**: {{disk_io}} {{disk_io_units}}
- **网络流量**: {{net_traffic}} {{net_traffic_units}}
- **运行时间**: {{uptime}}
{{/normal_devices}}

## 性能趋势分析

### CPU使用率趋势
- **平均使用率**: {{avg_cpu_trend}}%
- **峰值使用率**: {{max_cpu_trend}}%
- **使用率分布**: 
  - 0-50%: {{cpu_low}} 设备
  - 50-80%: {{cpu_medium}} 设备
  - 80-90%: {{cpu_high}} 设备
  - 90-100%: {{cpu_critical}} 设备

### 内存使用率趋势
- **平均使用率**: {{avg_memory_trend}}%
- **峰值使用率**: {{max_memory_trend}}%
- **使用率分布**:
  - 0-50%: {{memory_low}} 设备
  - 50-85%: {{memory_medium}} 设备
  - 85-95%: {{memory_high}} 设备
  - 95-100%: {{memory_critical}} 设备

## 建议和行动计划

### 🔧 立即行动项
{{#immediate_actions}}
- [ ] {{action}}
{{/immediate_actions}}

### 📋 短期优化项
{{#short_term_actions}}
- [ ] {{action}}
{{/short_term_actions}}

### 🏗️ 长期规划项
{{#long_term_actions}}
- [ ] {{action}}
{{/long_term_actions}}

## 监控建议

### 告警阈值调整
1. **CPU使用率**: 当前 {{current_cpu_threshold}}% → 建议调整为 {{new_cpu_threshold}}%
2. **内存使用率**: 当前 {{current_memory_threshold}}% → 建议调整为 {{new_memory_threshold}}%
3. **磁盘IO**: 当前 {{current_disk_threshold}} → 建议调整为 {{new_disk_threshold}}
4. **网络流量**: 当前 {{current_net_threshold}} → 建议调整为 {{new_net_threshold}}

### 监控优化
1. **新增监控项**: 
   - {{new_monitoring_items}}
2. **监控频率调整**: 
   - {{monitoring_frequency_changes}}
3. **告警规则优化**: 
   - {{alert_rule_changes}}

## 附录

### 监控项Key映射
| 指标类型 | Key | 单位 | 说明 |
|----------|-----|------|------|
| CPU使用率 | vmware.vm.cpu.usage.perf | % | CPU使用率百分比 |
| 内存使用率 | vmware.vm.memory.usage | % | 主机内存使用率 |
| 磁盘读取 | vmware.vm.vfs.dev.read | Bps | 磁盘读取速率 |
| 磁盘写入 | vmware.vm.vfs.dev.write | Bps | 磁盘写入速率 |
| 网络接收 | vmware.vm.net.if.in | Bps | 网络接收速率 |
| 网络发送 | vmware.vm.net.if.out | Bps | 网络发送速率 |
| 开机时间 | vmware.vm.uptime | uptime | VM运行时间 |

### 设备组ID映射
| 设备类型 | 组ID | 组名称 |
|----------|------|--------|
| 虚拟机 | 32, 71, 84, 26, 78 | (vm), Cluster_Psite (vm), Datacenter/vm (vm), Rsite (vm) |
| ESXi主机 | 7, 70, 24, 77 | Hypervisors, Cluster_Psite (hypervisor), (hypervisor), Rsite (hypervisor) |
| vCenter | 67 | _VMWare vCenter |

---
*报告生成工具: Zabbix VMware Monitoring Skill*  
*生成时间: {{timestamp}}*