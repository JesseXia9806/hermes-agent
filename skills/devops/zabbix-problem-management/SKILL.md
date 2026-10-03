---
name: zabbix-problem-management
description: 通过 Zabbix 7.4 API � 查�询、分类、关闭和验证 problems（告警事件生命周期管理）
---

# Zabbix Problem 管理 Skill

处理 Zabbix 告警问题生命周期：查询 problems、区分 ACTIVE/RESOLVED、关闭已恢复问题、验证结果。

环境信息（URL、认证、自签名证书）与 `zabbix-export-devices` skill 相同，此处不重复。

## �核心工作流（按顺序�执行）

### Step 1: 登录获取 token（Bearer Header 认证）

```bash
# � 凭据从统一文件读取（不写密码进命令/日志）
CREDS=$(cat ~/.hermes/secrets/zabbix_sercomm.txt)
ZBX_USER=$(grep '^username=' <<< "$CREDS" | cut -d= -f2)
ZBX_PASS=$(grep '^password=' <<< "$CREDS" | cut -d= -f2)

TOKEN=$(curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -d "{\"jsonrpc\":\"2.0\",\"method\":\"user.login\",\"params\":{\"username\":\"$ZBX_USER\",\"password\":\"$ZBX_PASS\"},\"id\":1}\" \
  | python3 -c \"import sys,json; print(json.load(sys.stdin)['result'])\")
```

### Step 2: � 查�询 problems 并**正确分类**

#### 方法A：全局查�询（�适用于整体情况概�览）
```bash
curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc":"2.0","method":"problem.get","params":{"output":["eventid","name","severity","objectid","acknowledged","suppressed","r_eventid","clock","r_clock"],"sortfield":"eventid","sortorder":"DESC","limit":200},"id":2}'
```

#### 方法B：按主机查�询（�适用于特定设备故�障排查——推�荐用法）
```bash
# 1. �� 获取目标主机的 hostid（示例：按IP查�询）
HOSTID=$(curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc":"2.0","method":"host.get","params":{"output":["hostid"],"filter":{"ip":"10.139.66.12"}},"id":1}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['result'][0]['hostid'])")

# 2. �� 获取该主机关联的所有 trigger IDs
TRIGGERIDS=$(curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc":"2.0","method":"trigger.get","params":{"output":["triggerid"],"hostids":['$HOSTID']},"id":1}' \
  | python3 -c "import sys,json; print(','.join([str(t['triggerid']) for t in json.load(sys.stdin)['result']]))")

# 3. � 查�询这些 trigger 对应的 problems（最近50条，按时间倒序）
curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"jsonrpc\":\"2.0\",\"method\":\"problem.get\",\"params\":{\"output\":[\"eventid\",\"name\",\"severity\",\"objectid\",\"acknowledged\",\"suppressed\",\"r_eventid\",\"clock\",\"r_clock\"],\"objectids\":[$TRIGGERIDS],\"sortfield\":\"eventid\",\"sortorder\":\"DESC\",\"limit\":50},\"id\":2}"
```

**分类规则（关�键！）**:
```python
# r_eventid == "0"（字符�串）或�缺失 = ACTIVE（问题还在发生，绝不能关闭）
# r_eventid 是非零数字字符�串 = RESOLVED（已�恢复，可关闭）
resolved = [p for p in problems if p.get('r_eventid') and p.get('r_eventid') != '0']
active   = [p for p in problems if not p.get('r_eventid') or p.get('r_eventid') == '0']
```

### Step 3: 只关闭 RESOLVED 问题

```python
# problem.close 方法在本 Zabbix 7.4.9 不存在！必须用 event.acknowledge
result = api('event.acknowledge', {
    'eventids': event_ids,       # 只传 RESOLVED 的 eventid 列表
    'action': 1,                 # 1 = close problem
    'message': 'Closed by IT admin via API - problem already recovered'
})
```

### Step 4: 验证关闭结果

```bash
# 验证时必须用【不带 recent 参数】的查询：
# recent=true 会把刚关闭的问题留在显示窗口内 → 误以为没关成功
# 不带 recent → 只返回真正 open 的问题
curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc":"2.0","method":"problem.get","params":{"output":["eventid","name","severity","r_eventid","clock"],"sortfield":"eventid","sortorder":"DESC","limit":200},"id":3}'
# 期望结果: RESOLVED-but-unclosed = 0
```

### Step 5: 关闭"可手动关闭"的问题（manual_close=1 trigger）— 用户核心诉求

用户说"把能 close 的 problems 直接 close 掉"时，通常不是只关 RESOLVED，而是指：
**trigger 配置了 `manual_close: 1` 的问题都可以关（即使还是 ACTIVE），剩下的 `manual_close: 0` 才是真正需要关注的问题。**

```python
# 1. 取所有 open problems（不带 recent）
problems = api('problem.get', {
    'output': ['eventid', 'name', 'severity', 'r_eventid', 'clock', 'objectid'],
    'sortfield': 'eventid', 'sortorder': 'DESC', 'limit': 300,
})['result']
active = [p for p in problems if not p.get('r_eventid') or p.get('r_eventid') == '0']

# 2. 批量查这些问题对应的 trigger 的 manual_close 属性
triggers = api('trigger.get', {
    'output': ['triggerid', 'description', 'manual_close', 'priority'],
    'triggerids': sorted(set(p['objectid'] for p in active)),
})['result']
trig_map = {t['triggerid']: t for t in triggers}

# 3. 分类：manual_close=1 → 可关闭；manual_close=0 → 真正的问题，保留
closable = [p for p in active if trig_map.get(p['objectid'], {}).get('manual_close') == '1']
keep     = [p for p in active if trig_map.get(p['objectid'], {}).get('manual_close') == '0']

# 4. 关闭 closable（event.acknowledge action=1），keep 全部保留
result = api('event.acknowledge', {
    'eventids': [p['eventid'] for p in closable],
    'action': 1,
    'message': 'Closed by IT admin via API - trigger allows manual close'
})
```

**验证**: 关闭后重新查 open problems（不带 recent），`manual_close=1` 的应该只剩新出现的，`manual_close=0` 的数量不变。本次实战 55 → 33（关 24，新出现 2）。

**可复用脚本**: 本 skill 自带 `scripts/zabbix_close_manual.py`（完整实现上述流程，含分类/关闭/验证），复制到本地运行即可。会话期间也曾存于 `/Users/jessexia/zabbix_close_manual.py`。

## ⚠️ Pitfalls（本次实战踩过的坑）

1. **`problem.get` 的 `sortfield` 只接受 `"eventid"`** — 用 `["clock"]` 会报
   `Invalid parameter "/sortfield/1": value must be "eventid"`。不要排序用 clock。
   （注意：此报错发生在 `recent:false` 变体；不带 recent 时 clock 也可用，但统一用 eventid 最稳。）

2. **永远检查 API 响应中的 `error` 键** — 本次第一个查询因 sortfield 报错被 `data.get('result', [])`
   静默吞掉，误读成 "0 problems"。正确写法:
   ```python
   if 'error' in data: print('API ERROR:', data['error'])
   else: problems = data.get('result', [])
   ```

3. **`r_eventid: "0"` 是字符串 "0" 在 Python 里是 truthy！** 直接 `if p.get('r_eventid')`
   会把 54 个 ACTIVE 问题误判为 RESOLVED。必须显式 `!= '0'` 判断。

4. **`problem.close` 方法不存在** — 报 `Method not found. Incorrect method "problem.close"`。
   用 `event.acknowledge` + `action: 1` 替代。

5. **ACTIVE 问题的可关闭性取决于 trigger 的 `manual_close` 属性** — 报
   `Cannot close problem: trigger does not allow manual closing` 只说明**这个 trigger** 是
   `manual_close: 0`（恢复后自动关闭）。但 **`manual_close: 1` 的 trigger 即使问题还在 ACTIVE
   也能通过 API 关闭**。判断标准:
   - `manual_close: 0` → 不能手动关（恢复后自动关），是"真正需要关注"的问题
   - `manual_close: 1` → 可以随时手动关（即使 ACTIVE），多为已知/可接受的噪音告警
   → 用户要求"关闭能 close 的、找出真正需要关心的"时，先按 trigger 的 manual_close 分类，
     只关 `manual_close: 1`，保留 `manual_close: 0` 并报告。

6. **关闭前后问题数会变化** — 查询期间可能有问题自然恢复（ACTIVE→RESOLVED）。
   验证时以最终不带 recent 的查询为准，不要纠结两次查询数字差异。

7. **`recent: true` 语义** — 包含最近关闭的问题（显示窗口内）。用于"看问题列表"可以，
   用于"验证关闭结果"会误导。验证一律用不带 recent 的查询。

## 关闭前备份（�审计记录）

```bash
# 关闭前把问题清单存 CSV 备份（eventid, name, severity, clock, r_clock）
# 本次存到 ~/zabbix_closed_problems_backup.csv
```

## � 报告格式

向用户报告时用表格:
- � 已�恢复问题 (RESOLVED): � 数量 + 关闭结果 � ✅
- �� 活动中问题 (ACTIVE): � 数量 + 保持原样 �� ⚠��️（按类型/严重度分组列出，标注重点）
- 遗留 ACTIVE 问题按告警类型分组�汇总（温度告警/端口 down/ICMP 不可达等），提示重点设备

## 参考文件和脚本

- `references/host_specific_query_example.md`: �详�细的按主机查�询示例（基于真实会话）
- `scripts/query_host_problems.py`: � 查�询特定主机problems的Python脚本（推�荐用法）
- `scripts/zabbix_close_manual.py`: 完整的问题关闭脚本（含分类/关闭/验证）
