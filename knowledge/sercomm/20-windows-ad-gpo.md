# 20 — AD / GPO / SysVol 排障

**来源**: gpo_sysvol_gpt_ini_fix.md, gpo_sysvol_resolution_guide.md
**案例**: 客户端 `p000053-lt02` 无法读取
`\\SERCOMM.COM\SysVol\SERCOMM.COM\Policies\{5C94A7C8-575A-4E55-A87F-B766E88C1A8D}\gpt.ini`

## 排查顺序（固定）

**客户端 DNS/SMB 连通性 → 该 GPO 的 NTFS/读取权限 → 多域控间 SysVol (DFSR) 复制**

## 三大根因（按概率）

| 根因 | 占比 | 说明 |
|---|---|---|
| **GPO 委派读取权限缺失**（MS16-072） | ~80% | 修改 Security Filtering 时移除了 `Authenticated Users`，计算机账号读不到 gpt.ini |
| 多域控 SysVol (DFSR) 复制丢失 | — | GPO在某台 DC 创建/修改，未同步到客户端命中的 DC |
| 客户端 DNS / SMB 通信异常 | — | 网卡 DNS 指向公共 DNS（如 8.8.8.8）而非域控；跨 VLAN/VPN 时 445/88 受限、MTU 分片被丢 |

## 步骤一：域控端修 GPO 权限（最关键）

1. 登录域控 `SPIAD02` → `Win+R` → `gpmc.msc`
2. 按 GUID 定位 GPO（域节点右键搜索 `{5C94A7C8-575A-4E55-A87F-B766E88C1A8D}`）
3. 选中 GPO → **Delegation（委派）** → **Advanced（高级）**
4. 检查是否有 `Authenticated Users` 或 `Domain Computers`
   - 缺失 → `Add` 添加 `Domain Computers` → 勾选 **Read**（**无需** Apply）
5. OK 保存

## 步骤二：强制全域 SysVol 同步

```cmd
repadmin /syncall /Aped
```

同时确认域控本机磁盘路径存在文件：
`C:\Windows\SYSVOL\sysvol\sercomm.com\Policies\{5C94A7C8-575A-4E55-A87F-B766E88C1A8D}\gpt.ini`

## 步骤三：客户端诊断与验证（管理员 PowerShell）

```powershell
# 1. 解析与当前 DC
nltest /dsgetdc:SERCOMM.COM
nslookup SERCOMM.COM

# 2. 关键端口连通性（SMB 445 / Kerberos 88 / DNS 53 / RPC 135）
$DC = (nltest /dsgetdc:SERCOMM.COM | Select-String "DC:").ToString().Split("\")[-1].Trim()
445, 88, 53, 135 | ForEach-Object {
    $port = $_
    $res = Test-NetConnection -ComputerName $DC -Port $port
    [PSCustomObject]@{ DC = $DC; Port = $port; Success = $res.TcpTestSucceeded }
}

# 3. 直接读 gpt.ini
$GPOPath = "\\SERCOMM.COM\SysVol\SERCOMM.COM\Policies\{5C94A7C8-575A-4E55-A87F-B766E88C1A8D}\gpt.ini"
if (Test-Path $GPOPath) { Write-Host "[OK] 可访问"; Get-Content $GPOPath }
else { Write-Host "[FAIL] 无法访问，检查网络/权限/DFS" -ForegroundColor Red }

# 4. 清票据与缓存
klist purge
ipconfig /flushdns
nbtstat -R

# 5. 强制刷新组策略
gpupdate /target:computer /force
```

## 常见排错对照表

| 排查项 | 常见根因 | 修复 |
|---|---|---|
| DNS 配置 | 网卡主 DNS 指向公共 DNS | 改为内网域控 IP（`SPIAD02` 等）|
| GPO 权限 | Security Filtering 移除了 Authenticated Users | Delegation → Advanced 重新加 `Domain Computers` 读权限 |
| DFS/SMB 拦截 | 防火墙拦 445，或 DFS Client 驱动被禁 | 检查 ACL/安全组策略；确认 `mrxsmb`、`Dfs` 服务运行 |
| 跨网段/VPN MTU | VPN 下 SMB 大包分片被丢 | 查客户端 MTU、IPsec/SSL VPN MSS 钳制 |
