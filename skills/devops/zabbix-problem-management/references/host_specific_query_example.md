# 示例：查�询特定主机的最近50个问题

以下是基于真实会话的示例，展示如何查�询IP为10.139.66.12的主机的最近50个问题。

## 环境信息
- Zabbix URL: https://spipzabbix.sercomm.com
- 版本: 7.4.9
- 认证方式: Bearer Token (Header)

## 步�骤1：获取主机ID

```bash
# �� 获取IP为10.139.66.12的主机的hostid
HOSTID=$(curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc":"2.0","method":"host.get","params":{"output":["hostid"],"filter":{"ip":"10.139.66.12"}},"id":1}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['result'][0]['hostid'])")

echo "Host ID: $HOSTID"
# � 输出示例: Host ID: 13125
```

## 步�骤2：获取主机关联的所有Trigger IDs

```bash
# �� 获取该主机关联的所有trigger IDs
TRIGGERIDS=$(curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc":"2.0","method":"trigger.get","params":{"output":["triggerid"],"hostids":['$HOSTID']},"id":1}' \
  | python3 -c "import sys,json; print(','.join([str(t['triggerid']) for t in json.load(sys.stdin)['result']]))")

echo "Trigger IDs: $TRIGGERIDS"
# � 输出示例: Trigger IDs: 70520,70521,70522,70523,70524,71181,71182,71183,71184
```

## 步�骤3：查�询这些Trigger对应的最近50个问题

```bash
# � 查�询这些trigger对应的problems（最近50条，按时间倒序）
curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"jsonrpc\":\"2.0\",\"method\":\"problem.get\",\"params\":{\"output\":[\"eventid\",\"name\",\"severity\",\"objectid\",\"acknowledged\",\"suppressed\",\"r_eventid\",\"clock\",\"r_clock\"],\"objectids\":[$TRIGGERIDS],\"sortfield\":\"eventid\",\"sortorder\":\"DESC\",\"limit\":50},\"id\":1}"
```

## 实际输出示例（基于真实会话）

```json
{
  "jsonrpc": "2.0",
  "result": [
    {
      "eventid": "28970110",
      "name": "FortiGate: SD-WAN [google dns]:[internal5]: Health check state is dead",
      "severity": "3",
      "objectid": "39524",
      "acknowledged": "0",
      "r_eventid": "0",
      "clock": "1786063227",
      "r_clock": "0",
      "suppressed": "0"
    },
    {
      "eventid": "28969914",
      "name": "HP Comware HH3C: Interface GigabitEthernet1/0/8(GigabitEthernet1/0/8 Interface): Link down",
      "severity": "3",
      "objectid": "63801",
      "acknowledged": "0",
      "r_eventid": "0",
      "clock": "1786062150",
      "r_clock": "0",
      "suppressed": "0"
    }
    // ... 更多问题记录
  ],
  "id": 1
}
```

## 结果解释

根据Zabbix 7.4的约定：
- `r_eventid == "0"` 或�缺失 = ACTIVE问题（问题仍在发生）
- `r_eventid` 是非零数字字符�串 = RESOLVED问题（已�恢复）

在上述示例中，所有问题的`r_eventid`都是"0"，表示这些都是ACTIVE问题。

## � 常见问题

### 1. � 没有返回结果？
- 确认主机IP是否正确
- � 检查该主机是否有关联的�监控项和�触发器
- �� 验证时间范�围（默认限制为最近50条）

### 2. �� 想要更多或更少的结果？
- 修改`limit`参数值（例如：`limit\":100`获取最近100条）
- �� 调整时间范�围需要使用`time_from`和`time_till`参数（Unix时间�戳）

### 3. 如何查看特定 severity 以上的问题？
�添加过�滤条件：
```json
"params": {
  "output": [...],
  "objectids": [$TRIGGERIDS],
  "sortfield": "eventid",
  "sortorder": "DESC",
  "limit": 50,
  "severities": [3,4,5]  // 只查看Warning及以上级别
}
```

## 最佳实�践

1. **先定位主机**：总是通过IP或主机名先获取精确的hostid
2. **批量获取triggers**：一次性获取所有关联trigger，�避免多次API调用
3. **使用�适当限制**：根据需求调整limit值，平�衡信息完整性和响应速度
4. **注意时区**：Zabbix返回的clock是Unix时间�戳（UTC），需要根据本地时区转换
5. **定期验证**：重要�监控对象建议建立定期查�询机制