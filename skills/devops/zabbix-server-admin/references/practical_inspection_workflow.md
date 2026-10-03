# Zabbix VMware Inspection Practical Workflow

## Overview
This workflow was developed during actual Zabbix VMware inspection (2026-08-07) when the existing document-type skills required direct API calling.

## Key Discoveries

### 1. Authentication Pattern
```bash
# Get credentials from secure file
CREDS=$(cat ~/.hermes/secrets/zabbix_sercomm.txt)
ZBX_USER=$(grep '^username=' <<< "$CREDS" | cut -d= -f2)
ZBX_PASS=$(grep '^password=' <<< "$CREDS" | cut -d= -f2)

# Login to get token
TOKEN=$(curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -d "{\"jsonrpc\":\"2.0\",\"method\":\"user.login\",\"params\":{\"username\":\"$ZBX_USER\",\"password\":\"$ZBX_PASS\"},\"id\":1}")

# Extract token from response
TOKEN=$(echo "$TOKEN" | python3 -c "import sys, json; print(json.load(sys.stdin)['result'])")
```

### 2. Zabbix Server Status Check
```bash
# Version check (NO auth header for apiinfo.version)
curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -d '{"jsonrpc":"2.0","method":"apiinfo.version","params":{},"id":1}'

# Host count check (REQUIRES auth header)
curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc":"2.0","method":"host.get","params":{"output":["hostid"],"monitored_hosts":true},"id":1}'
```

### 3. VMware Device Discovery
**Pitfall**: Name-based filtering doesn't work. Use template-based filtering:

```bash
# Find VMware template
curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc":"2.0","method":"template.get","params":{"output":["templateid","name"],"filter":{"name":["VMware"]}},"id":1}'

# Get hosts using VMware template
curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc":"2.0","method":"host.get","params":{"output":["hostid","name","status"],"templateids":["10173"]},"id":1}'
```

### 4. Problem Data Analysis
```bash
# Get problems from last 24 hours
curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc":"2.0","method":"problem.get","params":{"output":["eventid","name","severity","objectid","r_eventid","clock"],"sortfield":"eventid","sortorder":"DESC","limit":500,"time_from":1723113600},"id":1}'
```

## Common Pitfalls

### 1. Authentication Header Confusion
- **apiinfo.version**: NO auth header required
- **All other APIs**: REQUIRES `Authorization: Bearer $TOKEN`
- Error: "The 'apiinfo.version' method must be called without authorization header"

### 2. VMware Discovery Issues
- **Don't rely on name filtering**: "VMware" may not be in host names
- **Use template filtering**: Find hosts using VMware template (ID: 10173)
- **Check status**: Status "0" = monitored, "1" = unavailable

### 3. Problem Status Classification
- **Active problems**: `r_eventid` == "0" or missing
- **Resolved problems**: `r_eventid` != "0" and present
- **Severity levels**: 0=not_classified, 1=information, 2=warning, 3=average, 4=high, 5=disaster

## Quick Commands Reference

### Get Token
```bash
curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -d '{"jsonrpc":"2.0","method":"user.login","params":{"username":"Admin","password":"zabbix"},"id":1}'
```

### Get Version
```bash
curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -d '{"jsonrpc":"2.0","method":"apiinfo.version","params":{},"id":1}'
```

### Get VMware Hosts
```bash
curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc":"2.0","method":"host.get","params":{"output":["hostid","name","status"],"templateids":["10173"]},"id":1}'
```

### Get Problems
```bash
curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc":"2.0","method":"problem.get","params":{"output":["eventid","name","severity","objectid","r_eventid","clock"],"sortfield":"eventid","sortorder":"DESC","limit":500,"time_from":1723113600},"id":1}'
```