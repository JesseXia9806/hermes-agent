# 23 — PowerShell 执行策略与 .NET Framework 安装

**来源**: powershell-execution-policy-bypass.md, windows-powershell-executionpolicy-winutil.md, powershell-install-dotnet-framework-47.md

## 一、未签名脚本无法执行（安全处理）

### 单次运行（推荐，不落盘策略）
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\fs.ps1 -Path 'E:\SPIFS\test' -Owner '2013444@sercomm.com' -WhatIf
```
`Process` 范围只影响当前窗口，关闭即失效，**不写入** LocalMachine / CurrentUser。

### 不改策略的启动方式
```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'E:\SPIFS\test\fs.ps1' -Path 'E:\SPIFS\test' -Owner '2013444@sercomm.com' -WhatIf
# PowerShell 7:
pwsh.exe -NoProfile -ExecutionPolicy Bypass -File .\winutil.ps1
```

### 文件来自下载/邮件
```powershell
Get-Item .\winutil.ps1 -Stream Zone.Identifier -ErrorAction SilentlyContinue   # 检查下载标记
Unblock-File -LiteralPath .\winutil.ps1                                       # 核验来源与哈希后解除
```

### 判断策略来源
```powershell
Get-ExecutionPolicy -List
```
若 `MachinePolicy` 或 `UserPolicy` 不是 `Undefined` → **GPO 强制**，`Process Bypass` 通常覆盖不了。
**正确长期方案**：用企业代码签名证书签名脚本，或由域管理员对测试 OU / 指定设备开受控例外。**不要绕过企业 GPO。**

### WinUtil 风险
WinUtil 会请求管理员权限并可能改系统设置、软件、服务。**只在 Win11 测试机/个人管理设备**用；不要在 Windows Server 2008 或生产服务器用；也不能用它解决 Apex One 的 Azure Code Signing 兼容性问题。

## 二、安装 .NET Framework 4.7.x

**版本选择**：优先 **4.7.2**（满足 VS Installer 的"4.7.2 or higher"）或 4.8.1。**4.7.0 不满足要求。**

```powershell
# 已有安装包
$installer = 'C:\Install\NDP472-KB4054530-x86-x64-AllOS-ENU.exe'
Start-Process -FilePath $installer -ArgumentList '/q /norestart' -Wait -PassThru
if ($LASTEXITCODE -in 0, 3010, 1641) { Write-Host "完成，退出码：$LASTEXITCODE" }
else { throw "安装失败，退出代码：$LASTEXITCODE" }
```

```powershell
# 联网下载离线包
$uri = 'https://download.microsoft.com/download/8/6/4/8647A3A4-0A6C-4C78-91EF-A2D49E0B20C2/NDP472-KB4054530-x86-x64-AllOS-ENU.exe'
$installer = "$env:TEMP\NDP472-KB4054530-x86-x64-AllOS-ENU.exe"
Invoke-WebRequest -Uri $uri -OutFile $installer
$p = Start-Process -FilePath $installer -ArgumentList '/q /norestart' -Wait -PassThru
if ($p.ExitCode -notin 0, 3010, 1641) { throw "安装失败，退出代码：$($p.ExitCode)" }
```

### 验证
```powershell
$release = (Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full' -ErrorAction Stop).Release
if ($release -ge 461808) { '.NET Framework 4.7.2 或更高已安装' } else { '版本低于 4.7.2' }
```

### 注意
- 必须以**管理员身份**运行 Windows PowerShell
- 退出码 `0` 成功；`3010` / `1641` 成功但需重启
- 安装后 `Restart-Computer -Force`
