---
name: zabbix-get-server-status
description: ���� �� 从Zabbix获取服务器状态信息
---

# Zabbix �� 获取服务器状态技能

从 Zabbix 7.4 API �� 获取Zabbix服务器的基本状态信息，包括版本、监控主机数量等。

## 环境信息

| 项目 | ��� � � 值 |
|------|------|
| Zabbix URL | `https://spipzabbix.sercomm.com` |
| API 端点 | `https://spipzabbix.sercomm.com/api_jsonrpc.php` |
| 认证方式 | Bearer Token (Header) |

## 使用方法

```bash
# ���� �� �� 获取Zabbix服务器状态
SERVER_STATUS=$(zabbix-get-server-status)

# ���� �� �� 以JSON格式输出
zabbix-get-server-status --format json

# ���� �� �� 获取特定信息
VERSION=$(zabbix-get-server-status --field version)
HOST_COUNT=$(zabbix-get-server-status --field monitored_hosts)
```

## ���� �核心工作流

### ���� �� �� 获取服务器版本
```bash
# 注意：apiinfo.version 不需要认证头
version_resp=$(curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -d '{"jsonrpc":"2.0","method":"apiinfo.version","params":{},"id":1}')

version=$(echo "$version_resp" | python3 -c "import sys,json; print(json.load(sys.stdin)['result'])")
```

### ���� �� �� 获取监控主机数量
```bash
hosts_resp=$(curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc":"2.0","method":"host.get","params":{"output":["hostid"],"monitored_hosts":true},"id":1}')

host_count=$(echo "$hosts_resp" | python3 -c "import sys,json; print(len(json.load(sys.stdin)['result']))")
```

## ��� � 参数说明

| 参数 | 说明 | � 默认值 |
|------|------|--------|
| `--field` | 指定返回字段 (version/monitored_hosts/all) | all |
| `--format` | 输出格式 (text/json) | text |
| `--help` | 显示帮助信息 | - |

## ��� � � 输出格式

### ���� �� 文本格式（默认）
每行一个字段：
```
VERSION: 7.4.9
MONITORED_HOSTS: 360
```

### ���� �� JSON格式
```json
{
  "version": "7.4.9",
  "monitored_hosts": 360
}
```

### ���� �� 单字段格式
当指定 `--field` 参数时：
```
7.4.9
```

## �� 重要提示

### ���� �� apiinfo.version 的特殊要求
Zabbix 7.4 的 `apiinfo.version` 方法**不能使用** `Authorization: Bearer` 头，会报错：
```
The "apiinfo.version" method must be called without authorization header.
```

### ���� �� 其他API需要认证头
除了 `apiinfo.version`，所有其他API方法都需要 `Authorization: Bearer <token>` 头。

## ��� �� � 错误处理

- 认证失败：返回退出码 1
- API错误：返回退出码 2 并输出错误�详情
- 网�络超时：返回退出码 3

## 相关技能

- `zabbix-auth` - ���� �� �� 获取认证 token
- `zabbix-get-problems` - ���� �� �� 获取问题数据
- `zabbix-get-vmware-devices` - ���� �� �� 获取VMware设备信息