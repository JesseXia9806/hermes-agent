---
name: zabbix-auth
description: �� 获取Zabbix API token认证
---

# Zabbix 认证技能

从 Zabbix 7.4 API �� 获取认证 token，使用 Bearer 头认证方式。

## 环境信息

| 项目 | � 值 |
|------|------|
| Zabbix URL | `https://spipzabbix.sercomm.com` |
| API 端点 | `https://spipzabbix.sercomm.com/api_jsonrpc.php` |
| 认证方式 | Bearer Token (Header) |
| � 凭据文件 | `~/.hermes/secrets/zabbix_sercomm.txt`（格式：username=Admin\\npassword=zabbix） |

## 使用方法

```bash
# �� 获取 token
TOKEN=$(zabbix-auth)

# 或在脚本中使用
source <(zabbix-auth --export)
```

## �核心工作流

### 步�骤1: 读取�凭据
```bash
CREDS=$(cat ~/.hermes/secrets/zabbix_sercomm.txt)
ZBX_USER=$(grep '^username=' <<< "$CREDS" | cut -d= -f2)
ZBX_PASS=$(grep '^password=' <<< "$CREDS" | cut -d= -f2)
```

### 步�骤2: 登录获取 token
```bash
TOKEN=$(curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -d '{"jsonrpc":"2.0","method":"user.login","params":{"username":"'$ZBX_USER'","password":"'$ZBX_PASS'"},"id":1}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['result'])")
```

> �� ⚠��️ **重要提示**：Zabbix 7.4 API 要求使用 `Authorization: Bearer <token>` HTTP Header，而不是在 JSON body 中放置 auth 字段。

## � 输出

- � 默认输出：纯 token 字符�串
- 使用 `--export` 参数：输出可直接 source 的环境变量声明
- �� 错误情况：返回非零退出码并输出错误信息到 stderr

## 相关技能

- `zabbix-get-problems` - �� 获取问题数据
- `zabbix-get-vmware-devices` - �� 获取VMware设备信息
- `zabbix-get-server-status` - �� 获取Zabbix服务器状态