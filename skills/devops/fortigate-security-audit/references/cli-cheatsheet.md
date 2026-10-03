# FortiGate CLI 命令速查表（FortiOS 7.x）

## 基本规则

| 命令类型 | 说明 | 示例 |
|:---------|:-----|:-----|
| `get` | 运行时状态/统计数据 | `get system performance status` |
| `show` | 运行配置（非默认值） | `show system global` |
| `show full` | 运行配置（含默认值） | `show full system global` |
| `diagnose` | 诊断命令 | `diagnose vpn tunnel list` |
| `execute` | 执行操作（只读账户禁用） | ❌ |
| `config` | 配置模式（只读账户禁用） | ❌ |

## 需要脱敏的输出字段

输出中可能包含敏感信息，报告中必须处理：

- `set password ENC ...` — 加密密码，完整显示即可（本身已加密）
- SSH 公钥内容 — 显示指纹即可
- 内部 IP 网段 — 按需模糊

## FortiGate grep 限制

FortiGate 的 `grep` 仅支持以下选项（不支持 `-E` `-P`）：
```
-i    Ignore case
-n    Print line numbers
-v    Select non-matching lines
-f    Print fortinet config context
-c    Only print count
-A N  Print N lines after
-B N  Print N lines before
-C N  Print N lines context
```

## 关键字段映射表

| 要检查的内容 | 命令 | 输出中查找 |
|:-------------|:-----|:-----------|
| 固件版本 | `get system status` | `Version: FortiGate-xxx v7.x.x` |
| 特征库日期 | `get system status` | `Virus-DB:`, `IPS-DB:`, `APP-DB:`, `IPS-ETDB:` |
| CPU 状态 | `get system performance status` | `CPU states:`, `CPU0 states:` |
| 内存使用 | `get system performance status` | `Memory:` |
| NPU 卸载率 | `get system performance status` | `Average NPU sessions:` |
| TrustHost | `show full system admin` | `set trusthost1` |
| 2FA | `show full system admin` | `set two-factor` |
| 管理员锁定 | `show full system global` | `admin-lockout-threshold`, `admin-lockout-duration` |
| 会话超时 | `show full system global` | `admintimeout` |
| 加密 | `show full system global` | `strong-crypto`, `ssl-min-proto-version` |
| CLI 审计 | `show full system global` | `cli-audit-log` |
| Telnet/SSH | `show full system global` | `admin-telnet`, `admin-ssh-password` |
| NTP 同步 | `diagnose sys ntp status` | `synchronized: yes` |
