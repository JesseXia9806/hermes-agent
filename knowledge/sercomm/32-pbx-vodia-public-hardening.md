# 32 — Vodia PBX 公网侧安全加固

**来源**: centos9-vodia-pbx-public-security.md

## 环境
- PBX 主机：CentOS 9，Vodia PBX（pbxctrl 监听 SIP、HTTP/HTTPS、SNMP、Syslog 等）
- 网卡：
  - 公网 `ens256`，IP `124.107.126.228/28`，默认网关 `124.107.126.225`
  - 内网 `ens192` (`10.140.210.99/24`)、`ens224` (`192.168.100.206/24`)

## 已识别风险
1. **`public` 区开放端口**：SIP TCP/UDP 5060/5061、HTTP/HTTPS、过宽 RTP UDP `49152-64512`
2. **进程监听 `0.0.0.0`**：UDP 161（SNMP）、UDP 514（syslog）——应仅限内网或管理 IP
3. **`trusted` 区 target=ACCEPT**：ens192、ens224 的任意来源流量均可进入（仅在确认两网段为受控管理/语音网络时保留）

## 推荐策略（分层、最小化）

### 1. 仅向运营商 SBC 开放 SIP 与 RTP
- 在防火墙（`public` 区）只放行运营商 Session Border Controller（SBC） IP 段的：
  - SIP：TCP/UDP 5060、5061（或贵司实际端口）
  - RTP：依据 Vodia 实际配置的端口范围（不可直接放宽 `49152-64512`，先查 pbxctrl 配置再精细化）

### 2. Web 管理与 SSH 仅从 VPN/管理网进入；公网拒绝敏感端口
- 公网方向拒绝：`22` (SSH)、`23` (Telnet)、`2345`、`2346`（自定义管理端口）
- Web 管理（HTTPS）若仅用于内部，则公网方向拒绝 `443`，或仅放行特定管理 IP 段（若确有少数外部管理需求则做来源限制 + 2FA）

### 3. 公网保留 443 的唯一合理情境：Vodia WebRTC 或公网用户访问 PBX Web 服务
- 若真有此需求：
  - 使用 **反向代理 / WAF**（如 Nginx + ModSecurity）做终端 TLS 离载、统一入口、攻击防护
  - 或在防火墙做来源限制 + 会话限速

### 4. RTP 范围必须依据 Vodia 当前配置缩小
- 登录 PBX Web 管理 → 查看 **Settings > Media > RTP Port Range**，据此精确放行，**不可直接放宽到全段**
- 若范围过大，先收窄再同步防火墙

### 5. SNMP 仅允许监控服务器；使用 SNMPv3；syslog 仅允许日志服务器
- 在防火墙规则中仅放行监控服务器 IP（如 Zabbix server）向 PBX 的 UDP 161/514
- 强制使用 SNMPv3（认证+加密），不再使用 v1/v2c 明文社区名
- syslog 同理：仅许可日志聚合服务器（如前文 Zabbix）UDP/TCP 514

### 6. 日志与监控
- 开启 PBX 内置审计日志，定期导出至 SIEM
- 监控注册异常、失败注册次数、媒体中断率

## 风险提示
- 不要直接在 `public` 区放通 `0.0.0.0/0` 的大端口段，会暴露 PBX 至互联网扫描与暴力破解。
- 对于老旧终端或软件仅支持 UDP 5060/5061、RTP 宽范围的情况，应先在内网做隔离网关（SBC）进行协议转换与端口映射，再做最小化放行。