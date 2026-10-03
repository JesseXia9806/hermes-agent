# Zabbix VMware 监控技能

## 概述

这是一个整合的Zabbix VMware监控技能，用于从Sercomm的spipzabbix.sercomm.com (Zabbix 7.4.9)获取VMware虚拟机、ESXi主机、vCenter等设备的详细性能参数。

## 功能特性

- ✅ 支持VMware虚拟机、ESXi主机、vCenter三类设备
- ✅ 统一认证流程（Bearer Token）
- ✅ 完整的性能指标监控（CPU、内存、存储、网络、开机时间）
- ✅ 支持多种输出格式（文本、JSON）
- ✅ 自动计算衍生指标（总CPU使用率、总IO、总流量）
- ✅ 错误处理和超时保护
- ✅ 友好的使用界面和快速启动脚本

## 文件结构

```
zabbix-vmware-monitoring/
├── SKILL.md                    # 技能主文档
├── README.md                   # 使用说明
├── references/
│   └── zabbix-vmware-monitoring.md  # 详细监控指南
├── scripts/
│   ├── check_vm_performance.py    # Python主脚本
│   └── quick_check.sh           # 快速启动脚本
└── templates/
    └── vm_performance_report_template.md  # 报告模板
```

## 使用方法

### 1. 快速启动

```bash
# 查看帮助
./quick_check.sh --help

# 查询所有虚拟机（限制5个）
./quick_check.sh --type vm --limit 5

# 查询特定虚拟机
./quick_check.sh --name 'R_IMD_HRFACEID_1.32'

# 查询ESXi主机（JSON格式）
./quick_check.sh --type hypervisor --format json
```

### 2. Python脚本

```bash
# 查询所有设备
python3 scripts/check_vm_performance.py

# 查询特定设备类型
python3 scripts/check_vm_performance.py --device-type vm

# 查询特定设备
python3 scripts/check_vm_performance.py --device-name 'R_IMD_HRFACEID_1.32'

# JSON格式输出
python3 scripts/check_vm_performance.py --format json

# 限制结果数量
python3 scripts/check_vm_performance.py --limit 10
```

### 3. 手动API调用

```bash
# 1. 获取Token
CREDS=$(cat ~/.hermes/secrets/zabbix_sercomm.txt)
ZBX_USER=$(grep '^username=' <<< "$CREDS" | cut -d= -f2)
ZBX_PASS=$(grep '^password=' <<< "$CREDS" | cut -d= -f2)
TOKEN=$(curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -d "{\"jsonrpc\":\"2.0\",\"method\":\"user.login\",\"params\":{\"username\":\"$ZBX_USER\",\"password\":\"$ZBX_PASS\"},\"id\":1}")

# 2. 获取设备列表
curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc":"2.0","method":"host.get","params":{"groupids":["32","71","84","26","78"],"output":["hostid","name","status"],"selectInterfaces":["ip","dns"],"sortfield":"name"},"id":1}'
```

## 环境要求

- Python 3.6+
- jq (用于JSON处理)
- curl (用于API调用)
- 统一凭据文件：`~/.hermes/secrets/zabbix_sercomm.txt`

## 凭据文件格式

```bash
username=Admin
password=zabbix
```

## 监控指标

### CPU指标
- `vmware.vm.cpu.usage.perf` - CPU使用率(%)
- `vmware.vm.cpu.usage` - CPU使用量(Hz)
- `vmware.vm.cpu.num` - 虚拟CPU数量
- `derived.cpu.usage.total` - 总CPU使用率(计算值)

### 内存指标
- `vmware.vm.memory.usage` - 内存使用率(%)
- `vmware.vm.memory.size.usage.host` - 主机内存使用量(B)
- `vmware.vm.memory.size` - 总内存大小(B)

### 存储指标
- `vmware.vm.vfs.dev.read` - 磁盘读取速率(Bps)
- `vmware.vm.vfs.dev.write` - 磁盘写入速率(Bps)
- `derived.disk.io.total` - 总IO速率(计算值)

### 网络指标
- `vmware.vm.net.if.in` - 网络接收速率(Bps)
- `vmware.vm.net.if.out` - 网络发送速率(Bps)
- `derived.net.total` - 总流量(计算值)

### 状态指标
- `vmware.vm.uptime` - 运行时间(秒)
- `derived.uptime.str` - 运行时间(可读格式)

## 设备分类

| 设备类型 | 组ID | 组名称 |
|----------|------|--------|
| 虚拟机 | 32, 71, 84, 26, 78 | (vm), Cluster_Psite (vm), Datacenter/vm (vm), Rsite (vm) |
| ESXi主机 | 7, 70, 24, 77 | Hypervisors, Cluster_Psite (hypervisor), (hypervisor), Rsite (hypervisor) |
| vCenter | 67 | _VMWare vCenter |

## 常见问题

### 1. 认证失败
确保凭据文件存在且格式正确，使用`Authorization: Bearer` Header。

### 2. 证书错误
使用`-sk`参数跳过SSL验证。

### 3. 查询返回空结果
检查Token是否过期，确认Group ID是否正确。

### 4. 监控项Key不匹配
使用完整的Key模式搜索，如`vmware.vm.cpu.usage.perf`。

## 相关技能

- `zabbix-export-devices` - 从Zabbix导出设备信息
- `zabbix-problem-management` - 管理Zabbix问题
- `zabbix-server-admin` - 管理Zabbix服务器

## 更新日志

### v1.0 (2026-08-07)
- 初始版本，整合所有VMware相关技能
- 支持虚拟机、ESXi主机、vCenter三类设备
- 提供完整的性能监控指标
- 添加Python脚本和快速启动脚本
- 提供详细的使用说明和报告模板

## 贡献

如有问题或建议，请通过以下方式联系：
- 检查参考文档：`references/zabbix-vmware-monitoring.md`
- 查看脚本源码：`scripts/check_vm_performance.py`
- 使用快速启动脚本：`scripts/quick_check.sh`
