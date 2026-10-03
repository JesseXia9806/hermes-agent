# Sercomm IT 知识库 (Hermes Knowledge Base)

**来源**: 从 `/Users/jessexia/pplx`（Perplexity Space 工作目录）的 71 个 md 文件 + 8 个脚本中提取、去重、归类、结构化。
**整理日期**: 2026-09-13
**归属**: Jesse Xia (Sercomm IT Manager) — Hermes Agent default profile

## 用途

这是 Hermes 的**参考知识层**。稳定事实进记忆，可复用流程进技能（skills），细节证据和完整命令留在本目录。

- 记忆（memory）: 环境清单要点、目录指针、策略边界
- 技能（skills）: 可执行的操作流程（见下表"关联技能"列）
- 本目录: 完整命令、判读表、风险说明、原始案例

## 索引

| # | 主题 | 文件 | 关联技能 |
|---|------|------|---------|
| 01 | 资产与网段清单 | `01-inventory.md` | sercomm-it-environment |
| 10 | VLAN / L2-L3 / DHCP 排障 | `10-network-vlan-dhcp-troubleshooting.md` | network-switching-diagnostics |
| 11 | Cisco SVI 双向 ACL 设计 | `11-network-acl-design-cisco-svi.md` | network-switching-diagnostics |
| 12 | FortiGate WAN/NAT 判定与日志查询 | `12-fortigate-wan-nat.md` | fortigate-security-audit |
| 20 | AD / GPO / SysVol 排障 | `20-windows-ad-gpo.md` | windows-ad-gpo-wsus-ops |
| 21 | WSUS 运维与补丁推送 | `21-wsus-operations.md` | windows-ad-gpo-wsus-ops |
| 22 | 遗留 SQL Server 与旧 OS 迁移 | `22-legacy-sql-and-os-migration.md` | legacy-windows-sql-compat |
| 23 | PowerShell 执行策略与 .NET 安装 | `23-powershell-dotnet-executionpolicy.md` | legacy-windows-sql-compat |
| 24 | 文件权限（NFS / SMB / ACL） | `24-file-permissions-nfs-smb.md` | windows-file-permissions-nfs |
| 30 | 端点安全（CrowdStrike + Trend Micro） | `30-endpoint-security-crowdstrike-trendmicro.md` | endpoint-security-av-edr |
| 31 | 漏洞扫描（Nessus）与 TLS 加固 | `31-vulnerability-scanning-and-tls-hardening.md` | vulnerability-scanning-tls-hardening |
| 32 | Vodia PBX 公网侧加固 | `32-pbx-vodia-public-hardening.md` | linode-security-audit / fortigate-security-audit |
| 40 | Zabbix 运维（升级/发现/vCenter/备份） | `40-zabbix-operations.md` | zabbix-server-admin, zabbix-vmware-monitoring |
| 50 | 应用与带外设备（PaperCut / iDRAC / Synology） | `50-appliances-apps.md` | papercut-mf-admin |
| 60 | 工作站与 Obsidian 多端运维 | `60-workstation-and-obsidian-ops.md` | obsidian |
| 70 | HR 档案治理模型 | `70-hr-file-governance.md` | — |
| 71 | IT 候选人面试框架 | `71-it-interview-framework.md` | it-candidate-interview-framework |

原始文件保留在 `/Users/jessexia/pplx`（未做任何移动或删除）。镜像副本见 `_source/`。

## 全局安全边界（适用于本目录所有流程）

- **生产设备只查不改**：FortiGate、交换机、服务器、Zabbix、eHR 等生产系统的任何配置变更，必须先提案（改什么 + 为什么 + 风险 + 回退），取得 Jesse 明确批准后才执行。
- **只读优先**：排障默认只用 show/display/查询类命令，不做中断性操作（重启、清 MAC/ARP、改 PVID、删 ACL）。
- **凭据不落明文**：账号密码统一放 `~/.hermes/secrets/<system>.txt`（chmod 600），流程里只引用文件路径，密码不进命令、日志、回复。
- **敏感数据脱敏**：pcap、配置、日志对外提交前脱敏（公网 IP、内网网段、SIP 认证信息、DB 密码）。

## 已知易踩的坑（跨主题）

1. **不要用中文说明文字当命令参数**：VRP/Comware 里 `GigabitEthernet0/0/x` 是占位符，必须替换成实际端口号。
2. **排障清单要先分清对象**：主机自身拿不到管理 IP（需要 Vlanif + dhcp-alloc）与下挂终端拿不到 IP（只需 L2 放行）是完全不同的问题。
3. **不要在"验证故障"时关闭安全控制**（DHCP Snooping / IP Source Guard / ACL），会扩大攻击面。
4. **老系统补丁≠能力升级**：Windows Server 2008 R2 补 SHA-2 更新也无法获得 Azure Code Signing 支持；CentOS 6 补依赖无法跑 EL7 的 RPM。
