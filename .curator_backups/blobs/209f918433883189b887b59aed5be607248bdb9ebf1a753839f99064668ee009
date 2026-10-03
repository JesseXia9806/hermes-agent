# FortiGate ISO 27001:2022 合规映射表

Annex A 控制与 FortiGate 检查项的对应关系。

## A.8 技术控制

| ISO 编号 | 控制名称 | FortiGate 检查点 | 检查命令 |
|:---------|:---------|:-----------------|:---------|
| **A.8.1** | 用户终端设备 | 不适用（防火墙而非终端） | — |
| **A.8.2** | 特权访问权限 | 管理员账户列表与角色 | `get system admin` |
| **A.8.3** | 信息访问限制 | TrustHost IP 绑定 | `show full system admin` |
| **A.8.4** | 安全认证 | 会话超时、登录锁定 | `show full system global` |
| **A.8.5** | 特权管理 | 2FA、SSH 密钥、密码策略 | `show full system admin` |
| **A.8.6** | 容量管理 | CPU/内存/会话/吞吐 | `get system performance status` |
| **A.8.7** | 系统加固 | Telnet/HTTP/TLS/HTTPS | `show full system global` |
| **A.8.8** | 技术漏洞管理 | 固件版本、特征库日期 | `get system status` |
| **A.8.9** | 配置管理 | 接口/策略/VPN 配置 | `show system interface`, `show full` |
| **A.8.10** | 信息删除 | 不适用 | — |
| **A.8.11** | 数据脱敏 | 不适用（检查日志中敏感字段） | 注意 `password ENC` |
| **A.8.12** | 数据防泄露 | UTM/IPS/防病毒策略 | 需检查 `show firewall policy` |
| **A.8.13** | 备份 | 不适用（非备份设备） | — |
| **A.8.14** | 物理安全 | Console 超时 0 | `show full system global` |
| **A.8.15** | 日志记录 | Syslog、CLI 审计、SSL 日志 | `show log syslogd`, cli-audit-log |
| **A.8.16** | 监控活动 | SNMP/NetFlow 配置 | `show system snmp`, interface netflow |
| **A.8.17** | 时钟同步 | NTP 状态 | `diagnose sys ntp status` |
| **A.8.18** | 特权工具 | SUID/管理员权限分级 | `show system accprofile` |
| **A.8.19** | 工控系统 | OT-Detect 特征库 | `get system status` → OT-Detect-DB |
| **A.8.20** | 网络安全 | 策略/VPN/NAT 配置 | `get router info routing-table all` |
| **A.8.21** | 网络隔离 | VLAN/VDOM 配置 | `show system interface`, vdom-mode |
| **A.8.22** | 服务隔离 | 管理接口独立 | mgmt 接口状态 |
| **A.8.23** | Web 过滤 | UTM Web 过滤策略 | 需检查策略配置 |
| **A.8.24** | 加密技术 | TLS/SSH/IPsec 加密算法 | `show full system global` |

## 严重度分级标准

| 等级 | 标签 | 判定条件 |
|:----:|:----:|:---------|
| 🔴 **高危** | Critical | 公网可访问管理接口、无 2FA、无日志、TrustHost 全开 |
| 🟠 **中危** | High | 运行不安全协议、关键安全控制关闭、无监控 |
| 🟡 **低危** | Medium | 配置不符合最佳实践但非即时风险、使用已弃用算法 |
| 🔵 **注意** | Info | 闲置接口、非关键告警、可优化项 |
