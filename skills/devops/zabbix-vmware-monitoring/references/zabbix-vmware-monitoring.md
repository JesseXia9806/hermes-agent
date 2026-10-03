# Zabbix VMware 监控详细指南

## 监控流程

### 1. 认证

从统一凭据文件读取用户名和密码，获取Zabbix API Token。

```bash
CREDS=$(cat ~/.hermes/secrets/zabbix_sercomm.txt)
ZBX_USER=$(grep '^username=' <<< "$CREDS" | cut -d= -f2)
ZBX_PASS=$(grep '^password=' <<< "$CREDS" | cut -d= -f2)

TOKEN=$(curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -d "{\"jsonrpc\":\"2.0\",\"method\":\"user.login\",\"params\":{\"username\":\"$ZBX_USER\",\"password\":\"$ZBX_PASS\"},\"id\":1}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['result'])")
```

### 2. 获取设备列表

按组ID查询VMware设备（虚拟机、ESXi主机、vCenter）。

```bash
# 定义组查询
group_queries=(
    ("32", "(vm)", "VM")
    ("71", "Cluster_Psite (vm)", "VM")
    ("84", "Datacenter/Discovered virtual machine (vm)", "VM")
    ("26", "Datacenter/vm (vm)", "VM")
    ("78", "Rsite (vm)", "VM")
    ("7", "Hypervisors", "HYPERVISOR")
    ("70", "Cluster_Psite (hypervisor)", "HYPERVISOR")
    ("24", "(hypervisor)", "HYPERVISOR")
    ("77", "Rsite (hypervisor)", "HYPERVISOR")
    ("67", "_VMWare vCenter", "VCENTER")
)

# 获取设备列表
for gid, gname, cat in group_queries; do
    resp=$(curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
        -H "Content-Type: application/json-rpc" \
        -H "Authorization: Bearer $TOKEN" \
        -d '{"jsonrpc":"2.0","method":"host.get","params":{"groupids":["'$gid'"],"output":["hostid","name","status"],"selectInterfaces":["ip","dns"],"sortfield":"name"},"id":1}')
    
    # 处理返回的设备数据
done
```

### 3. 获取性能指标

查询设备的所有监控项，并筛选关键性能指标。

```bash
# 查询设备的所有监控项
resp=$(curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
    -H "Content-Type: application/json-rpc" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"jsonrpc":"2.0","method":"item.get","params":{"hostids":["'$DEVICE_ID'"],"output":["itemid","name","key_","lastvalue","units","value_type"],"sortfield":"name"},"id":1}')

# 筛选关键性能指标
for item in $(echo "$resp" | jq -r '.result[] | @base64'); do
    _jq() {
        echo ${item} | base64 --decode | jq -r ${1}
    }
    
    key=$(_jq '.key_')
    value=$(_jq '.lastvalue')
    units=$(_jq '.units')
    
    # CPU使用率
    if [[ "$key" == *"vmware.vm.cpu.usage.perf"* ]]; then
        CPU_USAGE=$value
    fi
    
    # 内存使用率
    if [[ "$key" == *"vmware.vm.memory.usage"* ]]; then
        MEMORY_USAGE=$value
    fi
    
    # 磁盘读取
    if [[ "$key" == *"vmware.vm.vfs.dev.read"* ]]; then
        DISK_READ=$value
    fi
    
    # 磁盘写入
    if [[ "$key" == *"vmware.vm.vfs.dev.write"* ]]; then
        DISK_WRITE=$value
    fi
    
    # 网络接收
    if [[ "$key" == *"vmware.vm.net.if.in"* ]]; then
        NET_IN=$value
    fi
    
    # 网络发送
    if [[ "$key" == *"vmware.vm.net.if.out"* ]]; then
        NET_OUT=$value
    fi
    
    # 开机时间
    if [[ "$key" == *"vmware.vm.uptime"* ]]; then
        UPTIME=$value
    fi
done
```

## 常见问题

### 1. 认证失败

**错误信息**:
```
Invalid parameter "/": unexpected parameter "auth"
```

**原因**: Zabbix 7.4 API 不支持在 JSON body 中传递 `auth` 参数，必须使用 `Authorization: Bearer` Header。

**解决方案**: 确保使用以下格式：
```bash
-H "Authorization: Bearer $TOKEN"
```

### 2. 证书错误

**错误信息**:
```
SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate
```

**解决方案**: 跳过 SSL 验证。
- **Python**: 使用 `ssl.create_default_context()` 并设置 `check_hostname=False, verify_mode=CERT_NONE`。
- **cURL**: 使用 `-sk` 参数。

### 3. 查询返回空结果

**原因**:
- Token 过期。
- Group ID 错误。
- 设备不属于指定组。

**解决方案**:
1. 重新获取 Token。
2. 确认 Group ID 是否正确（在 Zabbix Web 界面验证）。
3. 检查设备是否属于该组。

### 4. 监控项Key不匹配

**现象**: 查询 "cpu" 或 "memory" 关键字找不到监控项。

**原因**: VMware 监控项Key以 `vmware.vm.*` 或 `vmware.hv.*` 开头，不是简单的 "cpu" 或 "memory"。

**解决方案**: 使用完整的Key模式搜索，例如：
```bash
"search": {"key_": ["vmware.vm.cpu.usage.perf", "vmware.vm.memory.usage"]}
```

## 最佳实践

1. **限制查询数量**: 对于大量设备，分批查询避免超时。
2. **添加超时处理**: 为API请求添加超时处理，避免长时间等待。
3. **输出进度信息**: 在处理大量设备时，输出进度信息。
4. **多Key尝试策略**: 同时尝试多种可能的监控项Key，增加找到有效数据的机会。
5. **利用已知监控项**: 如果已知某个设备有有效的监控项，先查询该设备的所有监控项，再筛选关键指标。

## 监控项Key参考

| 指标类型 | Key | 单位 | 说明 |
|-----------|-----|------|------|
| CPU使用率 | `vmware.vm.cpu.usage.perf` | % | CPU使用率百分比 |
| CPU使用量 | `vmware.vm.cpu.usage` | Hz | CPU使用量（绝对值） |
| CPU核心数 | `vmware.vm.cpu.num` | | 虚拟CPU数量 |
| 内存使用率 | `vmware.vm.memory.usage` | % | 主机内存使用率 |
| 内存使用量 | `vmware.vm.memory.size.usage.host` | B | 主机内存使用量 |
| 磁盘读取 | `vmware.vm.vfs.dev.read` | Bps | 磁盘读取速率 |
| 磁盘写入 | `vmware.vm.vfs.dev.write` | Bps | 磁盘写入速率 |
| 网络接收 | `vmware.vm.net.if.in` | Bps | 网络接收速率 |
| 网络发送 | `vmware.vm.net.if.out` | Bps | 网络发送速率 |
| 开机时间 | `vmware.vm.uptime` | uptime | VM运行时间 |

## 设备分类

| 设备类型 | 组ID | 组名称 | 监控项前缀 |
|----------|------|--------|-------------|
| 虚拟机 | 32, 71, 84, 26, 78 | (vm), Cluster_Psite (vm), Datacenter/vm (vm), Rsite (vm) | `vmware.vm.*` |
| ESXi主机 | 7, 70, 24, 77 | Hypervisors, Cluster_Psite (hypervisor), (hypervisor), Rsite (hypervisor) | `vmware.hv.*` |
| vCenter | 67 | _VMWare vCenter | `vmware.vc.*` |