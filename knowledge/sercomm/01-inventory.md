# 01 — Sercomm IT 资产与网段清单

> 只收录在 pplx 文档中被实际引用、可核对的事实。IP/角色随环境变化，使用前先验证。

## 域与身份

| 项目 | 值 |
|---|---|
| AD 域 | `sercomm.com` / `SERCOMM.COM` |
| 域控 | `SPIAD02`（同时承载 WSUS） |
| 域账号格式 | `<工号>@sercomm.com`（Jesse 工号 2013444） |
| 端点命名 | `p000053-lt02.sercomm.com`（笔记本 `-lt`）、`*-dt01`（台式） |
| 域 SSL 证书 | `Sercomm_2026.pfx`（通配/域证书） |

## 关键服务器

| 系统 | 地址 / FQDN | 备注 |
|---|---|---|
| Apex One (Trend Micro) | `10.139.66.206` | 病毒库更新主服务器，客户端分流见 KB 30 |
| PaperCut MF | `10.139.1.6` / `sp-papercut.sercomm.com` | HTTP 9191、HTTPS 9192（`/admin` 才是管理台）|
| Nessus | `spnessus.sercomm.com:8834` | RHEL 9 + 自签/企业 CA 证书 |
| Zabbix Master (P site) | `spipzabbix.sercomm.com` = `10.140.1.42` | CentOS Stream 9, RPM + MySQL 8.4, nginx + php-fpm |
| Zabbix Proxy R site | `10.139.1.44` | P→R→Q 升级顺序 |
| Zabbix Proxy Q site | `10.141.1.42` | |
| vCenter | `10.140.1.59`（Zabbix Host 侧引用） | VMware LLD 全部 Not supported 案例见 KB 40 |
| iDRAC9 (Dell) | `10.140.1.85` | SMTP 告警 RAC0225 排障见 KB 50 |
| PRTG | `10.140.1.85` | 网络监控（与 iDRAC 同址，注意区分服务） |
| FortiGate 100F | `10.100.0.142` | Rsite-Forti100F，FortiOS 7.6.7，只读账号 `sajessereadyonly` |
| 测试 Ubuntu | `124.107.126.226` | rootadmin SSH |
| Vodia PBX (CentOS 9) | 公网 `124.107.126.228/28`，GW `124.107.126.225`；内网 `10.140.210.99/24`, `192.168.100.206/24` | ens256=公网，ens192/ens224=内网 |
| Forti60E-RHUB | WAN `internal5` = `180.232.208.139/29`，上游 GW `180.232.208.137` | 对外可见出口 `65.181.8.15`（上游 NAT） |

## 网段与网关

| VLAN / 网段 | 网关 | 位置 | 备注 |
|---|---|---|---|
| `10.139.13.0/24` (VLAN713) | `10.139.13.254` | Cisco 核心 SVI | 双向 ACL 模板样本，见 KB 11 |
| `10.120.220.0/22` (VLAN112) | `10.120.223.254` | H3C `P2_Core_2.254` | 名称 `Sercomm_Employee`；池容量约 1021–1022 |
| `10.139.49.0/24` | — | 业务网段 | ACL 白名单对象 |
| `10.139.66.0/24` | — | Apex One 所在网段 | `ebinap` 中放行到任意 |
| `10.120.2.0/24` (VLAN102) | — | 交换机管理 VLAN | R1_2.102 管理地址 10.120.2.102 |
| `10.139.1.0/24` | — | 核心服务器网段 | 见下表 |
| `10.140.0.0/16` | — | P 站点 / 监控 / 测试机 | |

### 基础服务（`10.139.1.9`，ACL 中的 DHCP/DNS/NTP）

| 地址 | 角色（据 ACL 注释） |
|---|---|
| `10.139.1.9` | DHCP / DNS / NTP |
| `10.139.1.7`, `.8`, `.15`, `.17`, `10.139.1.21`, `10.139.1.76` | 核心服务器（AD/DNS/MES/MTS 类） |
| `10.140.1.23` | 跨站点服务器 |

## 网络设备实例（已排障过）

| 设备 | 型号 / 版本 | 角色 |
|---|---|---|
| `R1_2.102` | Huawei S5720S-28P-PWR-LI-AC, V200R011C10SPC600 | L2 接入；管理 `Vlanif102`=10.120.2.102；GE0/0/24 上联 `R1-L3_2.253-P2`（trunk allow 2-4094, PVID 默认 1）；GE0/0/4 = Aruba AP `BoracayRM`（trunk, PVID 109, allow 109 112-114）|
| `P2_Core_2.254` | H3C Comware | L3 核心；`Vlan-interface112` = 10.120.223.254/22；DHCP server；GE1/0/2 上联 trunk permit vlan all PVID 102；GE1/0/4 亦承载 VLAN112 |
| Cisco 核心 | IOS/IOS-XE | VLAN713 SVI 网关 + `ebinap`/`Vlan713_IN` ACL |
| Aruba 控制器 / AP | `BoracayRM` 等 | SSID→VLAN 映射，VLAN112 业务 SSID |

## 工具与脚本位置

| 工具 | 位置 |
|---|---|
| FortiAnalyzer 日志查询 | `~/pplx/skills/faz_log_search.py`（JSON-RPC，两步式 logsearch） |
| Zabbix 升级前 DB 备份 | `~/pplx/Zabbix/backup_zabbix_db_preupgrade_v3.sh` |
| WSUS 单机触发 | `~/pplx/IT/1_WSUS_Trigger_Local[_EN].bat` |
| WSUS 批量触发 (WinRM) | `~/pplx/IT/2_WSUS_Batch_Trigger_PS.ps1` |
| WSUS 批量触发 (PsExec) | `~/pplx/IT/3_WSUS_Batch_Trigger_PsExec.bat` |
| Windows ACL/Owner 递归脚本 | `~/pplx/IT/fs-fixed.ps1`, `~/pplx/IT/windows-nfs-owner-everyone.ps1` |
