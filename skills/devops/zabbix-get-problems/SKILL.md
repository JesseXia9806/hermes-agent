---
name: zabbix-get-problems
description: ���� �� 从Zabbix获取过去24小时的问题数据
---

# Zabbix �� 获取问题数据技能

从 Zabbix 7.4 API �� 获取指定时间范�围内的问题数据，默认获取过去24小时的问题。

## 环境信息

| 项目 | ��� � � 值 |
|------|------|
| Zabbix URL | `https://spipzabbix.sercomm.com` |
| API 端点 | `https://spipzabbix.sercomm.com/api_jsonrpc.php` |
| 认证方式 | Bearer Token (Header) |

## 使用方法

```bash
# ���� �� �� 获取过去24小时的问题（需要先设置 TOKEN 环境变量）
PROBLEMS=$(zabbix-get-problems)

# ���� �� �� 获取自定义时间范�围的问题
PROBLEMS=$(zabbix-get-problems --time-from 1722940800 --time-till 1723027200)

# ���� �� 以JSON格式输出
zabbix-get-problems --format json
```

## ���� �核心工作流

### ���� �� �� 调用 problem.get API
```bash
curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc":"2.0","method":"problem.get","params":{"output":["eventid","name","severity","objectid","r_eventid","clock"],"sortfield":"eventid","sortorder":"DESC","limit":500,"time_from":'$TIME_FROM'},"id":1}'
```

## ��� � 参数说明

| 参数 | 说明 | � 默认值 |
|------|------|--------|
| `--time-from` | � 开始时间�戳（Unix timestamp） | 过去24小时 |
| `--time-till` | 结束时间�戳（Unix timestamp） | 当前时间 |
| `--limit` | 返回结果数量限制 | 500 |
| `--format` | � 输出格式 (text/json) | text |
| `--help` | 显示帮助信息 | - |

## ��� � � 输出格式

### ���� �� 文本格式（默认）
每行一个问题，字段之间用制表符分隔：
```
EVENTID	NAME	SEVERITY	OBJECTID	R_EVENTID	CLOCK
```

### ���� �� JSON格式
完整的API响应JSON数据

## ��� �� � 错误处理

- 认证失败：返回退出码 1
- API错误：返回退出码 2 并输出错误�详情
- 网�络超时：返回退出码 3

## 相关技能

- `zabbix-auth` - ���� �� �� 获取认证 token
- `zabbix-analyze-problems` - ���� �� 分�析问题数据
- `zabbix-get-vmware-devices` - ���� �� �� 获取VMware设备信息