# 30 — 端点安全（CrowdStrike + Trend Micro Apex One）

**来源**: ApexOne_ActiveUpdate_62_Debug.md, ApexOne_Threat_Count_Clear.md, CrowdStrike_TrendMicro_BadImage.md, apexone_update_agent_setup.md, trend-micro-smart-scan-vs-conventional-scan.md, skills/crowdstrike-falcon-legacy-windows-root-certificate-fix.md, falcon-sensor-proxy-log-analysis.md

## 一、Trend Micro Apex One 运维与排障

### 1.1 病毒库更新客户端分流（Update Agent）
**目的**：避免所有 Security Agent 并发向主服务器 `10.139.66.206` 请求更新导致网络拥塞。

**实施步骤**：
1. **指定 Update Agent**：
   - 在各网段/车间选 1~2 台常开且稳定的端点
   - 控制台：`Agents > Agent Management` -> 选中目标机器 -> `Settings > Update Agent Settings`
   - 勾选要分发的内容（Components、Domain Settings、Security Agent programs and hotfixes）-> Save
2. **配置客户端更新来源分流（按 IP / 子网）**：
   - 控制台：`Updates > Agents > Update Source` -> 选择 `Customized update source` -> `Add`
   - 输入网段 IP 范围（如 `10.139.67.1-10.139.67.254`），关联对应网段的 Update Agent（建议勾选"使用 IP 地址连线"）
   - 勾选："当无法连接更新代理时，直接连接 Trend Micro ActiveUpdate 官方服务器更新"作为回退
   - Save and Notify Agents
3. **风控**：
   - 跨 VLAN 需放行 Update Agent 通信端口（默认高位端口/HTTPS 监听端口）
   - 保证 Update Agent 本身只从主服务器 `10.139.66.206` 拉取更新

### 1.2 Smart Scan vs. Conventional Scan（本地扫描）
| 维度 | Smart Scan | Conventional Scan |
|---|---|---|
| 端点开销 | 较低（仅保留 Smart Scan Agent Pattern） | 较高（完整病毒特征库下发到端点） |
| 断网/隔离网 | 依赖 Smart Protection Server / 云端 | 基于已下载模式库本地扫描 |
| 推荐场景 | 一般办公网/可出网终端（内部配 2+ 台 Smart Protection Server） | 生产线、OT、MES/MTS、隔离 VLAN、网络不稳定区域 |

### 1.3 ActiveUpdate 错误 62
- **现象**：`ActiveUpdate was unable to verify security information. The local trusted information database is corrupted. (62)`
- **定位**：
  1. 检查 Smart Scan 是否正常（可能只是个别 Component 失败）
  2. 检查服务器时间/时区/NTP（时间偏差会导致签名/证书校验失败）
  3. 检查 HTTPS / 代理 / SSL Inspection，更新域名**避开 HTTPS 解密**
- **修复**：重启 `Apex One Master Service` -> 手动 Update -> 通过内置机制/官方 KB 专用工具重建可信数据库 -> 备份 `PCCSRV\Log`

### 1.4 Agent Management 威胁计数清理
- **现象**：已处置威胁但 Agent 列表界面数字不清零。
- **说明**：数字是历史事件计数，不能手工改数，也不建议改 SQL。
- **清除步骤**：
  1. 导出 `Logs > Security Risk Logs` 留存
  2. 控制台清除历史日志（或在 `Administration > Settings > Log Maintenance` 设置保留天数如 7 天自动清理）
  3. 强制端点 `Update Now` 或等待心跳上报刷新

---

## 二、CrowdStrike Falcon Sensor 运维与冲突处理

### 2.1 卸载工具与 Trend Micro 冲突（Bad Image / 错误 0xc0000428）
- **现象**：运行 `CSFalconServiceUninstallTool_x64.exe` 报 `0xc0000428`（签名无法验证），指向 Apex One 的 `TmUmEvt64.dll`。
- **根因**：Apex One 尝试注入行为监控 DLL，但 CrowdStrike 开启了代码完整性保护而拒绝该 DLL 载入。
- **解决**：
  - **方案 1（最稳妥）**：进入 **Windows 安全模式** 运行卸载工具
  - **方案 2（批量）**：在 Apex One 控制台 `Behavior Monitoring` 将卸载工具加为批准程序/信任例外
  - **方案 3**：临时卸载 Apex One -> 卸载 CrowdStrike -> 重新安装 Apex One

### 2.2 旧版 Windows 安装缺根证书修复（0x80096002）
- **现象**：WS2008R2 / Win7 安装日志报 `Could not find certificate` / `Failed to create certificate chain (0x80096002)`。
- **排查**：
  1. 日志找 `Name`、`Thumbprint`（SHA-1）、`Store: Root`
  2. 验证安装包签名：`Get-AuthenticodeSignature 'D:\WindowsSensor.exe'`（Status: Valid 说明安装包无损坏，是 Bootstrapper 前置检查拦截）
- **修复**：
  1. 从正常 Windows 10/11 (`certlm.msc` -> 受信任的根证书颁发机构) 导出指纹完全一致的 `.cer` 文件
  2. 导入到问题机器的 **Local Computer (LocalMachine) Root 证书库**：
     ```cmd
     certutil -addstore -f Root "C:\Temp\RequiredRoot.cer"
     certutil -store Root <Thumbprint>
     ```
  3. 常见缺失项：GlobalSign Root R6（指纹 `8094640EB5A7A1CA119C1FDDD59F810263A7FBD1`）等

### 2.3 Falcon 日志：代理读取失败但直连成功
- **现象**：日志出现 `c0000225` 提示代理配置不存在/无法读取，但后续显示 `Connected directly to ...:443` 和 `Certificate verified!`。
- **结论**：**非故障**。Sensor 在查询代理未果后已成功回退为直连出网。只需在 Falcon Console 核对 `Last Seen` 状态即可。若环境强制走代理，用 `falconctl` 配置代理参数。
