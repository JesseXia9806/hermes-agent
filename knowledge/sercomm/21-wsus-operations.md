# 21 — WSUS 运维与补丁推送

**来源**: trigger_domain_wsus_updates.md, wsus_0x80070652_fix.md, wsus_feature_updates_guidance.md + 3 个脚本
**环境**: WSUS 在域控 `SPIAD02`；客户端为 Win10/11

## 一、批量触发更新的三种方案

> Win10/11 上传统 `wuauclt /detectnow` 效果有限，主力是 **`usoclient`**（Update Session Orchestrator）。

| 方案 | 适用 | 交付物 |
|---|---|---|
| 单机脚本 | Helpdesk 现场/远程单台 | `1_WSUS_Trigger_Local.bat`（中文）/ `1_WSUS_Trigger_Local_EN.bat` |
| PowerShell + WinRM 批量 | 域控或管理终端，目标已开 WinRM | `2_WSUS_Batch_Trigger_PS.ps1` |
| PsExec 批量 | 未开 WinRM，走 SMB 管道 | `3_WSUS_Batch_Trigger_PsExec.bat`（需 `psexec.exe` 同目录）|

### 单机脚本动作序列
```bat
gpupdate /target:computer /force
wuauclt /resetauthorization /detectnow /reportnow
usoclient StartInteractiveScan
```
（`chcp 65001` + `net session` 提权检查；3~5 分钟后 WSUS 控制台更新状态）

### PowerShell 批量（WinRM）
```powershell
$Computers = Get-ADComputer -Filter 'OperatingSystem -like "*Windows 10*" -or OperatingSystem -like "*Windows 11*"' |
             Select-Object -ExpandProperty DNSHostName

Invoke-Command -ComputerName $Computers -ScriptBlock {
    Start-Process -FilePath "usoclient.exe" -ArgumentList "StartInteractiveScan" -NoNewWindow
    Start-Process -FilePath "wuauclt.exe"   -ArgumentList "/reportnow" -NoNewWindow
} -ThrottleLimit 30
```
脚本支持三种取目标方式：手输机器名 / 读 `targets.txt` / 从 AD 抓 Win10-11（`ThrottleLimit 30`，带结果汇总表与失败原因）。

### PsExec 批量（SMB，SYSTEM 权限）
```bat
psexec.exe @targets.txt -s -d -accepteula cmd.exe /c "gpupdate /target:computer /force & usoclient StartInteractiveScan & wuauclt /resetauthorization /detectnow /reportnow"
```

### COM 接口精准控制（需要记录安装结果时）
```powershell
$updateSession  = New-Object -ComObject Microsoft.Update.Session
$updateSearcher = $updateSession.CreateUpdateSearcher()
$searchResult   = $updateSearcher.Search("IsInstalled=0 and Type='Software'")
# 下载 → 收集 IsDownloaded → Microsoft.Update.UpdateColl → Installer.Install()
```

### 客户端命令速查
| 命令 | 作用 |
|---|---|
| `usoclient StartScan` | 后台静默扫描 |
| `usoclient StartInteractiveScan` | 前台交互式扫描并下载安装 |
| `usoclient StartDownload` / `StartInstall` | 单独下载 / 安装 |
| `wuauclt /resetauthorization /detectnow /reportnow` | 重置授权并向 WSUS 上报 |

## 二、错误 0x80070652

- Win32 映射：`ERROR_INSTALL_ALREADY_RUNNING (1618)`
- 根因：`msiexec.exe` 或后台更新服务被占用 / 前序安装未完成 / 重启挂起 → 升级被锁阻塞

### 修复脚本（目标机管理员 PowerShell）
```powershell
# 1. 停服务
Stop-Service -Name wuauserv, cryptSvc, bits, msiserver -Force -ErrorAction SilentlyContinue

# 2. 结束残留安装进程
Get-Process -Name msiexec, TiWorker, trustedinstaller, SetupHost -ErrorAction SilentlyContinue | Stop-Process -Force

# 3. 清理缓存（重命名而非删除，可回滚）
Rename-Item -Path "$env:windir\SoftwareDistribution" -NewName "SoftwareDistribution.old.$((Get-Date).ToString('yyyyMMddHHmmss'))" -ErrorAction SilentlyContinue
Rename-Item -Path "$env:windir\System32\catroot2"   -NewName "catroot2.old.$((Get-Date).ToString('yyyyMMddHHmmss'))" -ErrorAction SilentlyContinue

# 4. 起服务并触发
Start-Service -Name wuauserv, cryptSvc, bits, msiserver
wuauclt /resetauthorization /detectnow
usoclient StartInteractiveScan
```
补充：`sfc /scannow` + `DISM /Online /Cleanup-Image /RestoreHealth`。
若目标是升级 Win11，注意 TPM 2.0 / SecureBoot 兼容性拦截，以及 WSUS 是否下发了冲突的累积补丁。

## 三、功能更新（Feature Updates）审批策略

**结论：历史功能更新一律 Decline，不要核准。**

判定依据：
1. `This update is superseded by another update` + `Computers needing this update: 0`
2. 生命周期终止（Win10 1809/1909/2004/20H2 早已 EOS）
3. 冗余架构/语言（arm64、x86、en-gb、zh-tw）
4. 体积：单个 Feature Update ESD/ISO 3~5 GB，误核准会让 WSUS 下载数百 GB 并压垮内网

### SOP
1. WSUS 控制台全选未批准的历史功能更新（`Ctrl+A`）→ 右键 **Decline**
2. **Options → Server Cleanup Wizard** → 勾 `Unused updates and update revisions` + `Expired updates`
3. 自动化拒绝被替代更新：
```powershell
[reflection.assembly]::LoadWithPartialName("Microsoft.UpdateServices.Administration") | Out-Null
$wsus = [Microsoft.UpdateServices.Administration.AdminProxy]::GetUpdateServer("localhost",$false,8530)
$updates = $wsus.SearchUpdates("") | Where-Object { $_.IsSuperseded -and -not $_.IsDeclined }
foreach ($u in $updates) { $u.Decline() }
```
4. **Options → Products and Classifications**：不经 WSUS 分发大版本升级时，取消勾选 `Upgrades` 分类；取消已淘汰产品与 ARM64/Itanium
