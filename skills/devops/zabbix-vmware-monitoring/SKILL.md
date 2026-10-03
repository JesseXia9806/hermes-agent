---
name: zabbix-vmware-monitoring
description: 从 Zabbix 7.4 API 获取 VMware 虚拟机、ESXi 主机、vCenter 等设备的详细性能参数
---

# Zabbix VMware 监控技能

从 Sercomm 的 spipzabbix.sercomm.com (Zabbix 7.4.9) 获取 VMware 虚拟机、ESXi 主机、vCenter 等设备的详细性能参数。

## 环境信息

| 项目 | 值 |
|------|------|
| Zabbix URL | `https://spipzabbix.sercomm.com` |
| API 端点 | `https://spipzabbix.sercomm.com/api_jsonrpc.php` |
| Zabbix 版本 | 7.4.9 |
| 用户名 | `Admin` |
| 密码 | `zabbix` |
| 证书 | 自签名 — 需跳过 SSL 验证 |

## 认证流程

```bash
# Step 0: 从统一凭据文件读取（不把密码写进命令/日志）
CREDS=$(cat ~/.hermes/secrets/zabbix_sercomm.txt)
ZBX_USER=$(grep '^username=' <<< "$CREDS" | cut -d= -f2)
ZBX_PASS=$(grep '^password=' <<< "$CREDS" | cut -d= -f2)

# Step 1: 登录获取 token
TOKEN=$(curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -d "{\"jsonrpc\":\"2.0\",\"method\":\"user.login\",\"params\":{\"username\":\"$ZBX_USER\",\"password\":\"$ZBX_PASS\"},\"id\":1}")

# Step 2: 验证 token 可用 (列出 host groups)
curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc":"2.0","method":"hostgroup.get","params":{"output":["groupid","name"]},"id":1}'
```

## 监控流程

### 1. 获取设备列表

```bash
# 获取所有VMware设备
curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc":"2.0","method":"host.get","params":{"groupids":["32","71","84","26","78","7","70","24","77","67"],"output":["hostid","name","status"],"selectInterfaces":["ip","dns"],"sortfield":"name"},"id":1}'
```

### 2. 获取性能参数

```bash
# 获取指定设备的所有监控项
curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc":"2.0","method":"item.get","params":{"hostids":["<DEVICE_ID>"],"output":["itemid","name","key_","lastvalue","units","value_type"],"sortfield":"name"},"id":1}'
```

### 3. 计算关键指标

```bash
# 计算CPU使用率
CPU_USAGE=$(echo "scale=2; $CPU_USAGE_VALUE / $CPU_CORES * 100" | bc)

# 计算内存使用率
MEMORY_USAGE=$(echo "scale=2; $MEMORY_USED / $MEMORY_TOTAL * 100" | bc)

# 计算磁盘IO
TOTAL_IO=$(echo "scale=2; $READ_IO + $WRITE_IO" | bc)

# 计算网络流量
TOTAL_TRAFFIC=$(echo "scale=2; $IN_TRAFFIC + $OUT_TRAFFIC" | bc)
```

## 性能指标说明

| 指标类型 | 监控项Key | 单位 | 说明 |
|-----------|-----------|------|------|
| CPU使用率 | `vmware.vm.cpu.usage.perf[...]` | % | CPU使用率百分比 |
| CPU使用量 | `vmware.vm.cpu.usage[...]` | Hz | CPU使用量（绝对值） |
| 内存使用率 | `vmware.vm.memory.usage[...]` | % | 主机内存使用率 |
| 内存使用量 | `vmware.vm.memory.size.usage.host[...]` | B | 主机内存使用量 |
| 磁盘读取 | `vmware.vm.vfs.dev.read[...]` | Bps | 磁盘读取速率 |
| 磁盘写入 | `vmware.vm.vfs.dev.write[...]` | Bps | 磁盘写入速率 |
| 网络流量 | `vmware.vm.net.if.in[...]` / `vmware.vm.net.if.out[...]` | Bps | 网络接收/发送速率 |
| 开机时间 | `vmware.vm.uptime[...]` | uptime | VM运行时间 |

## 使用示例

```bash
# 查询特定虚拟机的性能参数
python3 vm_performance.py R_IMD_HRFACEID_1.32

# 查询结果示例
找到虚拟机: R_IMD_HRFACEID_1.32 (ID: 13146)

=== 性能参数 ===
CPU使用率: 6.38 %
CPU使用量: 1906000000.0 Hz
内存使用率: 7.99 %
主机内存使用量: 25921847296.0 B
磁盘读取: 15360.0 Bps
磁盘写入: 0.0 Bps
网络接收: 130048.0 Bps
网络发送: 224256.0 Bps
开机时间: 70天 16小时 46分钟 5秒
```

## 相关技能

- `zabbix-export-devices`: 从Zabbix导出设备信息
- `zabbix-problem-management`: 管理Zabbix问题
- `zabbix-server-admin`: 管理Zabbix服务器

## 参考文件

- `references/zabbix-vmware-monitoring.md`: 详细的监控流程和常见问题
- `scripts/check_vm_performance.py`: 检查虚拟机性能参数的Python脚本
- `templates/vm_performance_report_template.md`: 虚拟机性能参数报告模板