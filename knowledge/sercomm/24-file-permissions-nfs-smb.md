# 24 — 文件权限（NFS / SMB / ACL）

**来源**: skills/windows-nfs-permission-troubleshooting.md, nfs-set-owner-access.md, fs-fixed.ps1, windows-nfs-owner-everyone.ps1

## 核心原则

1. **先确认共享后端**：Windows Server NFS、Linux NFS、NAS NFS 的权限模型完全不同
2. **先单文件验证**，不要一上来递归整棵目录树
3. **NFS Server / NAS 是文件级 POSIX Owner/ACL 的权威端** —— Windows 映射盘通常改不了 UID/GID、POSIX mode、NFSv4 ACL
4. Windows `Everyone: FullControl` 只适用于能正确暴露 Windows ACL 的 NTFS/SMB 或 Windows Server NFS 环境；不要假设它能映射成 NFS 后端权限
5. 生产环境避免长期 `Everyone:FullControl` 或 `chmod -R 777`；优先共享组 + 最小权限

## 常见报错速查

| 报错/现象 | 根因 | 处理 |
|---|---|---|
| `not digitally signed` | ExecutionPolicy 阻止未签名脚本 | `Set-ExecutionPolicy -Scope Process Bypass -Force` |
| `MissingEqualsInNamedArgument` | 旧语法不兼容 | 改 `[CmdletBinding(SupportsShouldProcess = $true)]` |
| `NTAccount doesn't contain method new` | PS 5.1 / .NET 不支持 `::new()` | 用 `New-Object System.Security.Principal.NTAccount($Owner)` |
| `LiteralPath` 参数不存在 | 旧 PowerShell 兼容性 | 用位置参数 `Get-Acl $TargetPath` |
| `No flags can be set: inheritanceFlags` | 目录继承标志用到普通文件 | 文件用 `InheritanceFlags::None`；目录用 `ContainerInherit,ObjectInherit` |
| `Get-ChildItem -Recurse` 报 Access denied | 无某子目录列举权限 | `-ErrorAction SilentlyContinue`，记录并跳过 |
| `Attempted to perform an unauthorized operation` | 无权读写 ACL / 改 Owner，或 NFS 后端拒绝 | 分别测 `Get-Acl` / `SetOwner` / `Set-Acl`，转服务端/NAS |
| `$acl` is null | 前面的 `Get-Acl` 已失败 | 先修 `Get-Acl` 根因 |
| Windows 无法显示 Owner | POSIX UID/GID 或 NFS ACL 无法映射为 SID | 在 NFS Server/NAS 上改 owner/ACL |

## Windows 侧最小诊断（管理员 PowerShell，单文件）

```powershell
$file = 'E:\SPIFS\test\path\to\known-file.xlsx'
try {
    $acl = Get-Acl $file -ErrorAction Stop
    $acl | Format-List Owner, AccessToString
} catch {
    Write-Host "无法读取 ACL: $($_.Exception.Message)" -ForegroundColor Red
}
```

判读：
- `Get-Acl` 失败 → Windows 对该对象没有可操作安全描述符，**不要**继续 `Set-Acl`
- `Get-Acl` 成功、`Set-Acl` 失败 → 缺 `WRITE_DAC` / 服务端拒绝 ACL 写入 / NFS 映射限制
- `SetOwner` 失败但 `Set-Acl` 成功 → 只改 ACL；Owner 必须在服务端/NAS 改

## 兼容递归脚本模板（PS 5.1）

仅在单文件验证 `Get-Acl`/`Set-Acl` 可用后使用。目录/文件分别生成规则；Owner 失败不阻断 ACL 写入。

```powershell
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter(Mandatory = $true)] [string]$Path,
    [Parameter(Mandatory = $true)] [string]$Owner,
    [switch]$SkipOwner
)

$ErrorActionPreference = 'Continue'
$Root = (Resolve-Path $Path).Path
$OwnerAccount = New-Object System.Security.Principal.NTAccount($Owner)

function New-AccessRule {
    param([bool]$IsDirectory)
    if ($IsDirectory) {
        return New-Object System.Security.AccessControl.FileSystemAccessRule(
            'Everyone','Modify',
            ([System.Security.AccessControl.InheritanceFlags]::ContainerInherit -bor
             [System.Security.AccessControl.InheritanceFlags]::ObjectInherit),
            [System.Security.AccessControl.PropagationFlags]::None,
            [System.Security.AccessControl.AccessControlType]::Allow)
    }
    return New-Object System.Security.AccessControl.FileSystemAccessRule(
        'Everyone','Modify',
        [System.Security.AccessControl.InheritanceFlags]::None,
        [System.Security.AccessControl.PropagationFlags]::None,
        [System.Security.AccessControl.AccessControlType]::Allow)
}

function Set-OneAcl {
    param([string]$TargetPath)
    try {
        $item = Get-Item $TargetPath -Force -ErrorAction Stop
        $acl  = Get-Acl  $TargetPath -ErrorAction Stop
        $rule = New-AccessRule -IsDirectory $item.PSIsContainer
        if ($PSCmdlet.ShouldProcess($TargetPath, '设置 ACL')) {
            if (-not $SkipOwner) {
                try { $acl.SetOwner($OwnerAccount) }
                catch { Write-Warning "Owner 设置失败: $TargetPath -- $($_.Exception.Message)" }
            }
            $acl.SetAccessRule($rule)
            Set-Acl $TargetPath $acl -ErrorAction Stop
            Write-Host "完成: $TargetPath" -ForegroundColor Green
        }
    } catch { Write-Warning "失败: $TargetPath -- $($_.Exception.Message)" }
}

Set-OneAcl $Root
Get-ChildItem $Root -Force -Recurse -ErrorAction SilentlyContinue | ForEach-Object { Set-OneAcl $_.FullName }
```

预演：
```powershell
.\fs.ps1 -Path 'E:\SPIFS\test' -Owner 'DOMAIN\username' -SkipOwner -WhatIf
```
正式执行去掉 `-WhatIf`；先用 `-SkipOwner` 验证 ACL，Owner 不应阻断整批调整。
（现成脚本：`~/pplx/IT/fs-fixed.ps1`、`~/pplx/IT/windows-nfs-owner-everyone.ps1`）

## NFS 服务端 / NAS 处理（权威端）

Windows 上 `Get-Acl` 被拒或权限不落地时 → 停止 Windows ACL 脚本，转服务端。

```bash
# Linux NFS export 端
chown -R newuser:sharedgroup /export/SPIFS/test
find /export/SPIFS/test -type d -exec chmod 2775 {} +   # 目录可进入/可写/继承组
find /export/SPIFS/test -type f -exec chmod 0664 {} +   # 文件读写，不加执行位
chmod -R 777 /export/SPIFS/test                          # 仅紧急，高风险，不长期
```

### 服务端检查项
- NFS export 的客户端访问范围与读写设置
- `root_squash`、anonymous UID/GID、Windows↔UNIX UID/GID 映射
- 目标文件与父目录的 UID/GID、mode、POSIX ACL 或 NFSv4 ACL
- 父目录是否有 `x`（traverse）权限
- NAS 是否启用独立共享 ACL / Windows ACL 模式 / ACL 继承策略

## 平台选型

| 场景 | 推荐 |
|---|---|
| Windows 用户文件共享、AD 用户级授权 | **SMB + AD ACL** |
| Linux / ESXi / 产线设备 / 跨平台数据区 | **NFS**，权限由 NFS Server/NAS 统一管理 |
| Windows Server 自建 NFS export | 可用 `Get-NfsSharePermission` / `Grant-NfsSharePermission` 管共享级访问，但文件级 NTFS ACL 仍需服务端处理 |
