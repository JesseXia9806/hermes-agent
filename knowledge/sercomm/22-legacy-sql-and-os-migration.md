# 22 — 遗留 SQL Server 与旧 OS 迁移

**来源**: sql-server-2005-attach-to-2019-compatibility.md, windows-server-2016-sql-server-2008-install.md, oracle11g-ORA-01081.md, apexone-windows2008-azure-code-signing.md, centos6-falcon-el7-compatibility.md

## 一、SQL Server 2005 → 2019 挂载/升级

**结论**：SQL Server 2019 支持从 2005（内部版本 611）升级；首次 attach/restore 后**永久升级**为 2019 格式（内部版本 904），**不能再附回 2005**。

### 必备条件
1. 使用**完整一致的 MDF + LDF**；更推荐从 2005 做完整备份后在 2019 `RESTORE`
2. 源库必须处于正常关闭/一致状态 —— **不能只复制正在运行的 MDF/LDF**
3. SQL Server 2019 服务账号对数据库文件目录有 NTFS Modify 权限
4. 不能是加密数据库文件（TDE 需先迁移证书和私钥；2005 本身无原生 TDE）
5. 含 FILESTREAM/FileTable/全文索引时，先评估组件安装状态

### 常见失败原因
- 文件不一致（MDF/LDF 非同一时间点、日志缺失/损坏、复制了在线文件）
- 路径/权限问题（服务账号无法访问 `E:\SQLData`；只读介质、压缩/加密文件系统）
- 挂载了系统库（master/model/msdb/tempdb）
- 旧功能依赖：SQL-DMO、旧 DTS 包、SQL Mail、已废弃存储过程、兼容级别 80 语法
- 外部依赖不随文件迁移：登录名、SQL Agent Job、Linked Server、Credential、Proxy、SSIS/DTS、端点、证书、服务器级权限
- 排序规则/代码页差异导致索引重建、排序/比较/查询行为变化
- 数据库状态为 SUSPECT / RECOVERY_PENDING

### 推荐迁移流程
1. 2005 上 `DBCC CHECKDB` 并处理一致性错误；记录兼容级别、排序规则、文件路径、Job、登录名
2. 完整备份（建议 `COPY_ONLY`）+ 校验备份；**不要在线复制 MDF/LDF**
3. 隔离的 2019 测试实例先 `RESTORE VERIFYONLY`，再 `WITH MOVE` 恢复到新数据盘/日志盘
4. 恢复后 `DBCC CHECKDB`、更新统计信息、验证兼容级别（先保持 100，稳定后再评估 150）、应用回归与性能测试
5. 迁移登录名（修 orphaned users）、Job、Linked Server、SSIS/DTS 与安全对象
6. 验证备份/监控/维护计划/报表/灾备后切生产

```sql
-- 直接挂载（不推荐，仅备选）
CREATE DATABASE LegacyDB
ON (FILENAME = 'E:\SQLData\LegacyDB.mdf'),
   (FILENAME = 'F:\SQLLog\LegacyDB_log.ldf')
FOR ATTACH;
GO

-- 优先：从备份恢复
RESTORE DATABASE LegacyDB
FROM DISK = 'G:\Migration\LegacyDB_2005.bak'
WITH MOVE 'LegacyDB'     TO 'E:\SQLData\LegacyDB.mdf',
     MOVE 'LegacyDB_log' TO 'F:\SQLLog\LegacyDB_log.ldf',
     RECOVERY, STATS = 5;
GO
```

## 二、Windows Server 2016 上装 SQL Server 2008

**结论**：SQL Server 2008/2008 R2 已于 **2019-07-09 结束延伸支持**，且未受官方支持在 Windows Server 2016 上运行。**不要作为新部署方案。**

推荐替代：
1. 优先升级应用到 SQL Server 2019 / 2022
2. 若应用只兼容 2008 → 隔离的 WS2012R2 / WS2008R2 虚拟机运行，最小网络访问 + 备份 + 监控 + 补丁隔离
3. 非生产环境先验证：应用连接、SQL Agent 作业、SSIS/SSRS、字符集/排序规则、备份恢复

### 静默安装范例（仅实验/已验证环境）
```powershell
$setup  = 'D:\SQL2008\setup.exe'
$config = 'D:\SQL2008\ConfigurationFile.ini'
$log    = 'C:\Temp\SQL2008-Setup.log'

Start-Process -FilePath $setup `
  -ArgumentList @('/ConfigurationFile="' + $config + '"', '/QS', '/IACCEPTSQLSERVERLICENSETERMS') `
  -Wait -PassThru -RedirectStandardOutput $log -RedirectStandardError "$log.err"
```
失败看 `C:\Program Files\Microsoft SQL Server\100\Setup Bootstrap\Log\Summary.txt`。
风险：长期未修补漏洞 + .NET/TLS/驱动/OS 组件差异；生产必须取得应用厂商兼容性声明与安全例外审批。

## 三、Oracle 11g ORA-01081

```text
ORA-01081: cannot start already-running ORACLE - shut it down first
```
根因：当前 `ORACLE_SID` 实例已启动，或残留后台进程/共享内存。

```sql
-- 1. 以 SYSDBA 登录
sqlplus / as sysdba
-- 2. 查状态
SELECT instance_name, status, database_status FROM v$instance;
-- 3. 需重启时
SHUTDOWN IMMEDIATE;
STARTUP;
-- 4. 卡住时（会触发下次启动实例恢复，勿在未知业务连接时随意用）
SHUTDOWN ABORT;
STARTUP;
```
若 SQL*Plus 显示实例未运行但 startup 仍报错 → 在 OS 层确认 SID、残留进程、环境变量后谨慎清理。

## 四、"补丁 ≠ 能力升级"的两个反例

### 4.1 Windows Server 2008 R2 的 Azure Code Signing
- 装了 KB4474419、KB4490628（甚至目录里有 KB4536952 解压包）**仍报** `The system does not support Azure Code Signing`
- 根因：Apex One Security Agent 安装程序需要 **ACS** 支持，而 WS2008 R2 **不是**支持平台；SHA-2 更新无法把它变成支持 ACS 的系统
- **停止无效尝试**：不要装 WS2012R2 的 KB5001403；不要绕过签名验证；不要用第三方历史 Agent
- 已装 KB 核验：
  ```cmd
  wmic qfe get HotFixID,InstalledOn | findstr /I "KB4474419 KB4490628 KB4536952"
  ```
  （仅有解压目录 ≠ 已安装；必须在"已安装的更新"里可见）
- 可行路径：**A** 升级 OS 到 2019/2022（推荐）；**B** 向 Trend Micro Support 索取"该 Server 版本下最后支持 WS2008R2 SP1 的官方 Agent + EOL 声明"（只能官方渠道）

### 4.2 CentOS 6 装 EL7 的 RPM
- `falcon-sensor-7.38.0-19102.el7.x86_64.rpm` 无法通过补依赖在 CentOS 6 运行：依赖 **systemd + libnl3**，EL6 是 SysV init，ABI/系统库代际不同
- **不要**用 `rpm --nodeps` 或伪造 systemd/libnl3 依赖；不要手工移植 EL7 的 systemd/glibc
- 排查：
  ```bash
  cat /etc/redhat-release; uname -r
  rpm -q systemd libnl libnl3
  rpm -qpR falcon-sensor-7.38.0-19102.el7.x86_64.rpm
  ```
- 正确包（EL6）安装示例：
  ```bash
  rpm -ivh falcon-sensor-<EL6_compatible_version>.el6.x86_64.rpm
  /opt/CrowdStrike/falconctl -s --cid='<YOUR_CID>'
  service falcon-sensor start
  chkconfig falcon-sensor on
  service falcon-sensor status
  ```
- 获取途径：Falcon Console → `Host setup and management > Sensor downloads > Linux`；控制台没有 EL6 就提 Support Case（提供 OS/架构/`uname -r`/用途/需要的"最后一个受支持 EL6 RPM"）
- 下载后校验：`rpm -qpi falcon-sensor-*.rpm`、`rpm -qpR falcon-sensor-*.rpm`（确认包名含 `.el6.x86_64.rpm` 且依赖里**不含 systemd**）
