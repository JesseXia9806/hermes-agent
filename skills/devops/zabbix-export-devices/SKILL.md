---
name: zabbix-export-devices
description: 从 Zabbix 7.4 API 导出设备信息（VMware VMs, Hypervisors, Cisco 交换机, FortiGate, H3C 等）为 CSV
---

# Zabbix 设备导出 Skill

从 Sercomm 的 spipzabbix.sercomm.com (Zabbix 7.4.9) 导出各类受监控设备信息。

> 相关 skill: `zabbix-problem-management` — 查询/关闭 problems（告警生命周期管理），环境与认证信息相同。

## 环境信息

| 项目 | 值 |
|------|------|
| Zabbix URL | `https://spipzabbix.sercomm.com` |
| API 端点 | `https://spipzabbix.sercomm.com/api_jsonrpc.php` |
| Zabbix 版本 | 7.4.9 |
| 用户名 | `Admin` |
| 密码 | `zabbix` |
| 证书 | 自签名 — 需跳过 SSL 验证 |

## ⚠️ Zabbix 7.4 API 关键差异

这一版 Zabbix 有**两个非常重要的非标准行为**：

1. **Auth 令牌在 Header 而非 JSON Body**
   标准 Zabbix API 在 JSON-RPC body 的 root level 放 `auth` 字段。Zabbix 7.4 这里拒绝这种方式（报错 `Invalid parameter "/": unexpected parameter "auth"`）。
   **正确方式**: `Authorization: Bearer <token>` HTTP Header。
| Zabbix 版本 | 7.4.9 |
| 用户名 | `Admin`（大小写敏感，小写 admin 会被锁定） |
| 凭据文件 | `~/.hermes/secrets/zabbix_sercomm.txt`（chmod 600，首次使用时创建） |
| 证书 | 自签名 — 需跳过 SSL 验证 |

> 🔐 **凭据规范**: 密码不写入技能正文/回复/thinking，统一存 `~/.hermes/secrets/`（每系统一文件，`username=`/`password=` 每行一个键值，chmod 600）。登录时从文件读取。

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

## 导出模式

### 模式 A: 按 Host Group 名称搜索并导出

先找到目标设备的 host group：

```bash
# 搜索包含关键词的 group
curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc":"2.0","method":"hostgroup.get","params":{"output":["groupid","name"],"search":{"name":"Switch"}},"id":1}'
```

然后查询该 group 内的所有主机并导出为 CSV：

```bash
curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc":"2.0","method":"host.get","params":{"groupids":["<GROUP_ID>"],"output":["hostid","name","status"],"selectInterfaces":["ip","dns","type"],"sortfield":"name"},"id":1}'
```

### 模式 B: 使用 Python 脚本批量导出（推荐）

现有脚本位于: `/Users/jessexia/zabbix_export_vms.py`

该脚本实现了：
- 自动登录获取 token
- 跳过自签名证书验证
- 按多个 group id 分批次查询并去重
- 输出为 CSV 格式

#### 扩展脚本用于其他设备类型

要导出交换机/FortiGate/H3C，修改脚本中 `main()` 的 `group_queries` 列表：

```python
# 示例：导出 H3C 交换机
group_queries = [
    ("52", "H3C Switch", "SWITCH"),  # groupid 需要在 Zabbix 中确认
]

# 示例：导出 FortiGate
group_queries = [
    ("XX", "FortiGate", "FIREWALL"),
]

# 示例：导出所有网络设备
group_queries = [
    ("52", "H3C Switch", "SWITCH"),
    ("XX", "Cisco Switch", "CISCO"),
    ("XX", "FortiGate", "FORTIGATE"),
]
```

### 模式 C: 直接 Python 脚本导出

对于一次性查询，用这个模板快速导出：

```python
#!/usr/bin/env python3
import json, urllib.request, ssl, csv, sys

API = "https://spipzabbix.sercomm.com/api_jsonrpc.php"
TOKEN = "<YOUR_TOKEN>"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

def api(method, params):
    req = urllib.request.Request(API,
        data=json.dumps({"jsonrpc":"2.0","method":method,"params":params,"id":1}).encode(),
        headers={"Content-Type":"application/json-rpc","Authorization":f"Bearer {TOKEN}"})
    with urllib.request.urlopen(req, context=CTX, timeout=60) as r:
        return json.loads(r.read())

# 1. 先找 group id
groups = api("hostgroup.get", {"output":["groupid","name"],"search":{"name":"Switch"}})
for g in groups["result"]:
    print(f"{g['groupid']} -> {g['name']}")

# 2. 导出选中 group 的主机
hosts = api("host.get", {
    "groupids":["52"],  # 替换为实际 groupid
    "output":["hostid","name","status"],
    "selectInterfaces":["ip","dns"],
    "sortfield":"name"
})

for h in hosts["result"]:
    ips = ";".join(i["ip"] for i in h.get("interfaces",[]) if i.get("ip"))
    print(f"{h['hostid']},{h['name']},{h['status']},{ips}")
```

## 已知 Host Group IDs (当前 Zabbix)

| Group ID | Name | 类型 |
|----------|------|------|
| 25 | Cluster_Psite (vm) | VM |
| 26 | Datacenter/vm (vm) | VM |
| 32 | (vm) | VM |
| 44 | Rsite (vm) | VM |
| 49 | Datacenter/Discovered virtual machine (vm) | VM |
| 7 | Hypervisors | HYPERVISOR |
| 22 | Cluster_Psite (hypervisor) | HYPERVISOR |
| 24 | (hypervisor) | HYPERVISOR |
| 43 | Rsite (hypervisor) | HYPERVISOR |
| 52 | H3C Switch | SWITCH |

> **注意**: Group IDs 可能在重新部署或数据迁移后变化。每次使用前先运行 `hostgroup.get` 确认。

## 常见问题

### 证书错误
```
SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate
```
解决: Python 用 `ssl.create_default_context()` + `check_hostname=False, verify_mode=CERT_NONE`
     curl 用 `-sk` 参数

### Auth 被拒绝
```
Invalid parameter "/": unexpected parameter "auth"
```
解决: 不要将 auth 放在 JSON body 的 root level。改用 `Authorization: Bearer XXX` Header。

### 查询返回空结果
- 确认 Token 未过期（重新 login 获取新 token）
- 检查 Group ID 是否正确
- 确认主机确实属于该 group（在 Zabbix Web 界面手动验证）
