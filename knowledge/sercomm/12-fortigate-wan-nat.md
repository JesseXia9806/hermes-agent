# 12 — FortiGate WAN/NAT 判定与 FortiAnalyzer 日志查询

**来源**: fortigate-wan-ip-forti60e-rhub.md, skills/faz_log_search.py, pcap-upload-guide.md, sip-log-unidirectional-audio-analysis.md

## 一、判定"真实互联网出口接口"

案例：Forti60E-RHUB

| 项目 | 值 |
|---|---|
| WAN 接口 | `internal5`（alias `Wan-Eastern100mbps`，role `wan`）|
| 接口地址 | `180.232.208.139/29` |
| 上游默认网关 | `180.232.208.137` |
| 默认路由 | `0.0.0.0/0 via 180.232.208.137, internal5` |
| Dashboard 出口探测显示 | `65.181.8.15`（≠ 接口 IP）|

**判读**：`internal5` 有有效公网 /29、link up，且承载默认路由 → 它就是出口。Dashboard 显示的地址与接口 IP 不同，说明上游存在 NAT / 透明代理 / 运营商地址转换。

### 验证命令

```shell
# 从指定接口验证出网实际源地址
execute ping-options reset
execute ping-options interface internal5
execute ping 8.8.8.8

# 看到公网地址的会话 NAT 详情
diagnose sys session filter clear
diagnose sys session filter daddr 8.8.8.8
diagnose sys session list
```

### 风险

要建**入站 VPN / VIP / 端口映射**时，必须以**实际对外可见地址 `65.181.8.15`** 为准，并确认上游设备或 ISP 已把相应端口/公网地址静态映射到 `180.232.208.139`。否则 FortiGate 上的 VIP/VPN 配置互联网侧访问不到。

## 二、FortiAnalyzer 7.6 JSON-RPC 日志查询

脚本：`~/pplx/skills/faz_log_search.py`

```bash
export FAZ_HOST=<faz-ip>
export FAZ_APIKEY=<api-key>
python3 faz_log_search.py --adom root --devid <FortiGate序列号> \
  --logtype traffic --start 2026-08-04T00:00:00 --end 2026-08-04T23:59:59 \
  --filter "srcip==10.0.0.1 and dstport==443" --limit 100
```

要点：

- 端点 `https://<FAZ_HOST>/jsonrpc`，自签证书 → `verify=False`
- 认证用 **API Key 放进 `session` 字段**（7.x 推荐，等效 session）
- 搜索是**两步式**：`add` 在 `/logview/adom/<adom>/logsearch` 创建任务拿到 `tid` → 轮询 `get /logview/adom/<adom>/logsearch/<tid>` 直到 `percentage>=100`
- `logtype`：`traffic` / `event` / `utm-ips` / `utm-virus` …
- 状态码非 0 抛错；轮询上限 30 次 × 1s

## 三、抓包取证注意事项

- 平台附件优先；若格式受限 → 压缩成 `.zip`，或（临时）改后缀 `.txt`
- 最稳妥：Wireshark → `File > Export Packet Dissections > As Plain Text`，导出纯文本再分析
- **上传前脱敏**：pcap 常含公司公网 IP、内网网段、未加密的 SIP 认证密码。必要时只导出问题 UDP RTP 流

## 四、SIP 单通语音

`call-details-*.html` 类抓包需提取 SIP/SDP/RTP 关键信息后分析（原始文档为待办，尚无结论）。排障时关注：SDP 中媒体地址/端口是否单侧不可达、NAT/防火墙是否只放行了单方向 RTP、RTP 是否单侧到达。
