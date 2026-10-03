# 10 — VLAN / L2-L3 / DHCP 排障方法论与实战案例

**来源**: huawei_s5720_vlan112_*.md, h3c_vlan112_gateway_config_audit.md, p2_core_vlan112_*.md, r1_2_102_*.md (共 14 篇，2026-07 案例)
**适用**: 华为 VRP、H3C Comware、Cisco IOS 的 VLAN 不通 / 终端拿不到 IP 类故障

---

## 一、先分类故障，再动手（最重要的一步）

| 现象 | 优先方向 |
|---|---|
| 客户端 169.254.x.x、持续 DHCP Discover | DHCP 地址池 / relay / snooping / 安全限制 |
| 客户端已有 VLAN IP、网关可达但跨网段不通 | ACL / 策略路由 / 防火墙 / 上游路由 |
| 客户端在无线侧未被分配到目标 VLAN | Aruba/RADIUS 的 SSID→role→VLAN 映射，DHCP 根本收不到 Discover |
| **交换机自身**拿不到管理 IP | 该机是否有 `interface Vlanif<id>` + `ip address dhcp-alloc`（与下挂终端无关）|
| **下挂终端**拿不到 IP | 接入口 `access vlan` / 上联 trunk 放行 —— 不需要交换机自身有 Vlanif |

> 关键教训：本次案例中 `R1_2.102` 的根因是**它自己不是 VLAN112 的 DHCP 客户端**（没有 Vlanif112），而不是核心 DHCP、上联 trunk 或 snooping 的问题。先确认"谁拿不到地址"。

## 二、L2 通不通 —— 三段证据法

1. **MAC 表**：`display mac-address vlan 112`（Huawei）/ `display mac-address vlan 112`（H3C）
   - 无任何动态 MAC → 流量没进这个 VLAN：查对端 trunk/hybrid 放行、端口标签、终端 VLAN 归属
   - MAC 只在单个上联口学到 → 本机 L2 正常，故障在上游/网关/ACL/路由
   - 数量持续增长（案例：128 → 130）→ 没有固定阻断
2. **端口状态**：`display interface brief`、`display port vlan interface <if>`、`display vlan 112`（看 TG/UT 标记）
3. **STP**：`display stp brief`、`display stp interface <if>` —— ROOT/FORWARDING 才算通过；不允许强制转发绕过

**判读要点**：VLAN 是**纯 Tagged**（无 access 端口）时，普通终端必须靠对端/AP 正确打标；若 AP 把业务 VLAN 以 untagged 发出，会被 PVID（案例中 VLAN109）接走。

## 三、DHCP 链路定位 —— 计数对比法

选一台测试终端，令其 release/renew，**同时**在核心侧连续看 DHCP 统计：

```text
# H3C 核心
display dhcp server statistics
display dhcp server ip-in-use            # 注意：可能只列部分 VLAN，用 '?' 确认过滤语法
display dhcp server conflict
display dhcp server expired
display dhcp relay statistics            # 若核心只做 relay
display dhcp relay client-info
```

**判定表**

| 核心看到 | 结论 |
|---|---|
| Discover 不增长 | 报文没到核心 → 二层/VLAN 归属/AP 映射问题 |
| Discover 增长、Offer=0 | 池耗尽 / 池匹配失败 / 网关掩码错 / 策略 |
| Discover 有、Offer/ACK 不返回 | relay 目标不可达、UDP 67/68 被 ACL/防火墙拦、回包路径 |
| Offer/ACK 正常但无租约 | MAC 黑洞封禁、IP Source Guard、Snooping binding 拦在 DHCP 前 |
| 租约已建、终端无网 | `display arp | include <IP>` + `ping -a <SVI IP> <client>` 再往上层查 |

**已排除项示例（案例）**：池利用率 10.05%，冲突 0，Discover 4385 / Request 4557 / Offer 1956 / ACK 3368 → DHCP 服务本身正常，问题在客户端归属侧。

## 四、配置缺陷高危清单（审计时优先看）

1. **黑洞 MAC**：`display mac-address blackhole vlan 112` —— 案例中 H3C 上有 11 条 `mac-address blackhole ... vlan 112`，命中即"完全不通"。删除单条需先确认识别与封禁原因（**安全策略，不得批量清空**）：
   ```text
   system-view
   undo mac-address blackhole <MAC> vlan 112
   save
   ```
2. **DHCP Snooping 上联口未 trusted** → Offer/ACK 被丢弃（trusted 只应给 DHCP Server/Relay 方向）
3. **交换机误配 DHCP relay**（纯 L2 管理交换机不应配）
4. **`port trunk allow-pass vlan all` / `2 to 4094`** —— 能通但不是修复方案，扩大广播域与越权面
5. **Telnet + SNMPv2c 明文管理** —— 独立安全风险，应迁 SSH/SNMPv3
6. **PVID 误改**：为了"让 VLAN 通"把 AP 口 PVID 从 109 改成 112 会让 AP 失联。应改 **AP 侧 SSID tagging/VLAN assignment**。

## 五、典型修复样例

### 5.1 交换机自身取 VLAN112 管理地址（Huawei VRP）
```text
system-view
interface Vlanif 112
 description Switch-Management-DHCP
 ip address dhcp-alloc
 undo shutdown
quit
save
```
验证：`display interface Vlanif 112` / `display ip interface brief` / `display dhcp client` / `display arp`
风险：先 `display ip interface brief` + `display current-configuration | include ip address` 确认没有其他管理 VLANIF，避免双管理地址/默认路由混乱。

### 5.2 普通终端接入口
```text
system-view
interface GigabitEthernet0/0/X
 port link-type access
 port default vlan 112
quit
save
```

### 5.3 上联 trunk（Huawei）
```text
interface GigabitEthernet0/0/X
 port link-type trunk
 port trunk allow-pass vlan 112
quit
```

## 六、命令参考

**Huawei VRP（S5720）**
```text
display interface brief
display vlan 112
display port vlan interface GigabitEthernet0/0/<n>
display current-configuration interface GigabitEthernet0/0/<n>
display mac-address dynamic vlan 112
display mac-address <终端MAC>
display arp all | include <网段或网关>
display stp brief
display dhcp client
display dhcp snooping
display dhcp snooping statistics
display ip interface brief
```

**H3C Comware（P2_Core）**
```text
display vlan 112
display interface Vlan-interface 112
display dhcp server ip-in-use ?        # 先问帮助确认过滤语法
display dhcp snooping ?
display mac-address blackhole vlan 112
display ip routing-table <client IP>
display current-configuration | include packet-filter|traffic-filter|acl|qos
```

**通用风险**：不要在无维护窗口时重启交换机、清空 MAC/ARP、批量清 DHCP 租约 —— VLAN112 案例中单台设备学习 128–130 个 MAC，误操作影响面很大。

## 七、本次案例结论快照（可作参考基线）

- `R1_2.102`（Huawei S5720）：上联 GE0/0/24 trunk allow 2-4094、VLAN112 Tagged/Up、MAC 130 条、STP 正常 → **L2 已排除**；根因是自身无 Vlanif112（不是 DHCP 客户端）。
- `P2_Core_2.254`（H3C）：SVI 10.120.223.254/22 与池 10.120.220.0/22 匹配、无 ACL/forbidden-ip 绑定、Snooping 未全局启用 → **核心侧配置无常规限制**；重点复核 11 条黑洞 MAC 与租约/统计。
- Aruba `BoracayRM`（R1 GE0/0/4）：无 VLAN112 MAC 学习，native/PVID=109 → 疑点在 AP 侧 SSID/VLAN tagging。
