---
name: zabbix-api-operations
description: Use when working with Sercomm Zabbix 7.4 API for auth and巡检.
---

# Zabbix API Operations for Sercomm

Class-level procedures for working with spipzabbix.sercomm.com Zabbix 7.4 API in read-only巡检 mode. Covers auth, server status, problem retrieval and analysis with correct headers and payload shapes.

## Environment

| Item | Value |
|------|-------|
| Zabbix URL | https://spipzabbix.sercomm.com |
| API endpoint | https://spipzabbix.sercomm.com/api_jsonrpc.php |
| Auth | Bearer Token header |
| Credentials | Admin / zabbix |

## Core workflow

1. Obtain API version without auth
   ```bash
   curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
     -H "Content-Type: application/json-rpc" \
     -d '{"jsonrpc":"2.0","method":"apiinfo.version","params":{},"id":1}'
   ```
   apiinfo.version must be called WITHOUT Authorization header.

2. Authenticate
   ```bash
   curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
     -H "Content-Type: application/json-rpc" \
     -d '{"jsonrpc":"2.0","method":"user.login","params":{"username":"Admin","password":"zabbix"},"id":1}'
   ```
   params is an object with username and password. Array form is invalid.

3. Use token for subsequent calls
   ```bash
   -H "Authorization: Bearer $TOKEN" \
   -H "Content-Type: application/json-rpc"
   ```

4. Get monitored hosts count
   ```bash
   method: host.get
   params: {"output":["hostid"],"monitored_hosts":true}
   ```

5. Get problems for past 24h
   ```bash
   method: problem.get
   params: {"output":["eventid","name","severity","objectid","r_eventid","clock"],"sortfield":"eventid","sortorder":"DESC","limit":500,"time_from":$TIME_FROM}
   ```
   Active problem = r_eventid is 0 or empty.

## Pitfalls

- Content-Type must be application/json-rpc. Using application/json leads to 32601 Method not found or incorrect API errors.
- apiinfo.version must NOT include Authorization header; adding it returns "method must be called without authorization header".
- user.login params must be object {username,password}. Passing array triggers "Invalid parameter" error.
- All methods except apiinfo.version require Authorization: Bearer <token> header.
- Production firewalls and Zabbix are read-only. Do not modify configuration without explicit approval.
