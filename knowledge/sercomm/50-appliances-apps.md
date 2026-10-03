# 50 — 应用与带外设备（PaperCut / iDRAC / Synology）

**来源**: papercut_interface_modes.md, papercut_reset_admin_password.md, papercut_ssl_setup.md, idrac-rac0225-smtp-debug.md, synology-abb-vmware-cbt-repair.md

## 一、PaperCut 管理与 SSL 证书配置

### 1.1 登录界面与权限模式区分
- **普通终端用户门户**：URL `http://10.139.1.6:9191/app?service=page/UserSummary`，左侧菜单显示 `Summary`, `Rates`, `Transfers`, `Transaction History`, `Recent Print Jobs`, `Jobs Pending Release`, `Web Print`。
- **管理员控制台**：URL `http://10.139.1.6:9191/admin`，左侧菜单显示 `Dashboard`, `Users`, `Groups`, `Accounts`, `Printers`, `Devices`, **`Reports`**, `Cards`, `Options` 等。

### 1.2 重置内置 Admin 密码

```bash
# 1. 停止服务
sudo systemctl stop "PaperCut Application Server"

# 2. 修改 server.properties
sudo sed -i 's/admin.password=.*/admin.password=Sercomm@2026!/' /opt/papercut/server/server.properties

# 3. 启动服务
sudo systemctl start "PaperCut Application Server"

# 4. 通过 Web 重新加密密码
登录 https://10.139.1.6:9192/admin -> Options > Advanced -> Reset admin password
```

### 1.3 配置 SSL 证书

```bash
# 1. 导入证书到 JKS Keystore
keytool -importkeystore -srckeystore "C:\Cert\sp-papercut.pfx" -srcstoretype pkcs12 -destkeystore "C:\Program Files\PaperCut MF\server\custom\my-ssl-keystore" -deststoretype JKS

# 2. 修改 server.properties
server.ssl.keystore=custom/my-ssl-keystore
server.ssl.keystore-password=SecretPass123
server.ssl.key-password=SecretPass123

# 3. 重启服务
sudo systemctl restart "PaperCut Application Server"
```

---

## 二、iDRAC SMTP 告警排障

### 2.1 根因
- **错误代码**：`RAC0225: Sending the test mail failed`
- **排查路径**：
  1. 记录 SMTP 配置（服务器、端口、加密、认证、发件人）
  2. 检查日志：`racadm getsel`（按时间搜索 RAC0225 前后）
  3. 验证 SMTP 连通：`nc -vz <SMTP_HOST> 25` / `openssl s_client -starttls smtp -connect <SMTP_HOST>:587`
  4. 检查防火墙/ACL/代理/SSL inspection

### 2.2 修复
- **SMTP Relay**：向邮件团队申请 iDRAC 管理网段/IP 的 TCP 25 或 587 放行与 relay 白名单
- **Microsoft 365**：传统 Basic Auth SMTP 已不适合作为 iDRAC 方案；优先部署内部 SMTP Relay/Exchange relay，由其转送到 M365。iDRAC 通常不能满足现代 OAuth 条件
- **TLS**：旧固件可能只支持较老 TLS/密码套件；升级 iDRAC 固件到 Dell 对应服务器型号支持的当前稳定版本，并确认 SMTP 端仍允许兼容 TLS 策略
- **DNS**：iDRAC DNS 配置要正确；若 SMTP 使用 FQDN，须能解析并能访问其返回 IP。仅用 IP 连接时，TLS 证书名称验证可能失败
- **发件人与中继**：SMTP 服务若启用 Relay Restriction，`From` 地址、源 IP、认证用户必须符合策略；邮箱别名或外部域可能被拒绝

---

## 三、Synology ABB VMware 备份报错

### 3.1 根因
- **错误**：`Changed blocks larger than virtual disk capacity`
- **排查**：VMware Changed Block Tracking（CBT）元数据异常或不同步。ABB 使用 CBT 做增量备份，但 VMware 返回的变更块范围超过当前 VMDK 的容量，常见于虚拟磁盘扩容、快照链异常、磁盘回滚/复制还原，或 CBT 元数据损坏后

### 3.2 修复

```powershell
# 1. 在 ABB 中暂停或取消该 VM 的运行中备份任务，确认没有残留快照
# 2. 在 vCenter 将目标 VM 关机（建议维护窗口执行）
# 3. 在 VM 设置中确认每块 VMDK 的 Provisioned Size；如近期扩容，确认客户机操作系统已识别容量
# 4. 重置 CBT：关闭 VM 后，在 vCenter VM Configuration Parameters 中将 `ctkEnabled=false`，并将每一块虚拟磁盘的 `scsiX:Y.ctkEnabled=false`；保存
# 5. 删除该 VM 所在数据存储目录内的 `*.ctk` 文件（仅删除 ctk 文件，严禁删除 `.vmdk`、`-flat.vmdk`、`.vmx` 文件）
# 6. 开机后重新启用 CBT：`ctkEnabled=true`，并按每块磁盘设置 `scsiX:Y.ctkEnabled=true`，然后重启一次虚拟机
# 7. 在 ABB 对该 VM 执行新的完整备份/重新保护，旧增量链不能继续使用
```

### 3.3 风险与预防
- CBT 重置会使下一次备份变为完整备份，提前确认 NAS 容量、备份窗口和网络带宽
- 不要在有运行中快照合并、Storage vMotion 或备份任务时删除 `.ctk`
- 若重置后依旧报错，优先检查并合并/修复快照链、升级 ESXi/vCenter 与 ABB 至兼容且受支持版本，并检查该 VM 是否有独立持久磁盘、RDM 或不受支持磁盘配置
