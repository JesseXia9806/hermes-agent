# 11 — Cisco SVI 双向 ACL 设计模板（VLAN713 实战版）

**来源**: vlan713_acl_fix.md, vlan713_in_acl.md, vlan713_in_core_hosts.md, ebinap_out_simplified.md, skills/skill_cisco_vlan713_acl.md

## 核心概念：SVI 上的 in / out 方向

在 `interface Vlan713`（SVI）上：

| 方向 | 含义 | 数据包特征 | 用途 |
|---|---|---|---|
| `in` | VLAN 内主机**发出**，进入 SVI 准备路由 | **源** = `10.139.13.0/24` | 控制"本网段能访问谁" |
| `out` | 其他网段路由过来，**离开** SVI 发往本 VLAN 主机 | **目的** = `10.139.13.0/24` | 控制"谁能访问本网段" |

## 典型错误（VLAN713 根因）

原配置只应用了 `ip access-group ebinap out`，但 `ebinap` 里混入了源=13.0 网段的规则（如 `deny ip 10.139.13.0 0.0.0.255 host 10.100.0.142`）。
→ 该规则在 `out` 方向**永远不会命中**，因为 out 方向包的源不可能是 13.0 网段。

**铁律**：不要把"源为本 VLAN"和"目的为本 VLAN"的控制混写在同一个 ACL 并单向应用。

## 双向模板

### IN 方向（`Vlan713_IN`）—— 本 VLAN 往外

编号规范：10–99 安全阻断｜100–199 基础服务｜200–299 业务白名单｜990 兜底 deny

```cisco
ip access-list extended Vlan713_IN
 ! 10–52：安全阻断
 10 deny ip 10.139.13.0 0.0.0.255 host 10.100.0.142        ! 禁止访问防火墙
 50 deny tcp 10.139.13.0 0.0.0.255 any eq 3389
 51 deny tcp 10.139.13.0 0.0.0.255 any eq 445
 52 deny tcp 10.139.13.0 0.0.0.255 any eq telnet

 ! 100–121：DHCP / DNS / NTP 精确放行（服务器 10.139.1.9）
 100 permit udp 10.139.13.0 0.0.0.255 host 10.139.1.9 eq bootps
 101 permit udp host 10.139.1.9 10.139.13.0 0.0.0.255 eq bootpc
 110 permit udp 10.139.13.0 0.0.0.255 host 10.139.1.9 eq domain
 111 permit udp host 10.139.1.9 10.139.13.0 0.0.0.255 eq domain
 115 permit tcp 10.139.13.0 0.0.0.255 host 10.139.1.9 eq domain
 116 permit tcp host 10.139.1.9 10.139.13.0 0.0.0.255 eq domain
 120 permit udp 10.139.13.0 0.0.0.255 host 10.139.1.9 eq ntp
 121 permit udp host 10.139.1.9 10.139.13.0 0.0.0.255 eq ntp

 ! 200–208：业务白名单（从 ebinap 的 out 规则反推"互通需求"）
 200 permit ip 10.139.13.0 0.0.0.255 10.139.49.0 0.0.0.255
 201 permit ip 10.139.13.0 0.0.0.255 host 10.139.1.7
 202 permit ip 10.139.13.0 0.0.0.255 host 10.139.1.21
 203 permit ip 10.139.13.0 0.0.0.255 host 10.139.1.76
 204 permit ip 10.139.13.0 0.0.0.255 host 10.139.1.8
 205 permit ip 10.139.13.0 0.0.0.255 10.139.66.0 0.0.0.255
 206 permit ip 10.139.13.0 0.0.0.255 host 10.139.1.17
 207 permit ip 10.139.13.0 0.0.0.255 host 10.139.1.15
 208 permit ip 10.139.13.0 0.0.0.255 host 10.140.1.23

 ! 990：兜底 deny
 990 deny ip 10.139.13.0 0.0.0.255 any
exit
```

### OUT 方向（`ebinap`）—— 谁能进本 VLAN

```cisco
ip access-list extended ebinap
 5   permit ip 10.139.49.0 0.0.0.255 10.139.13.0 0.0.0.255
 8   permit ip 10.139.66.0 0.0.0.255 any          ! 视业务决定保留
 30  permit ip host 10.139.1.9  10.139.13.0 0.0.0.255
 31  permit ip host 10.139.1.7  10.139.13.0 0.0.0.255
 40  permit ip host 10.139.1.21 10.139.13.0 0.0.0.255
 65  permit ip any host 10.139.13.140             ! 3 台对全网开放的主机
 66  permit ip any host 10.139.13.146
 67  permit ip any host 10.139.13.106
 510 permit ip host 10.139.1.76 10.139.13.0 0.0.0.255
 540 permit ip host 10.139.1.8  10.139.13.0 0.0.0.255
 999 deny ip any 10.139.13.0 0.0.0.255
exit
```

### 接口应用

```cisco
interface Vlan713
 ip address 10.139.13.254 255.255.255.0
 ip helper-address 10.139.1.9        ! DHCP relay
 ip access-group Vlan713_IN in
 ip access-group ebinap out
```

## 清理清单（把混在 out 里的源=13.0 规则挪到 in）

```cisco
ip access-list extended ebinap
 no 4        ! 13 段 <-> 防火墙（属 in）
 no 6
 no 60
 no 61
 no 62
 no 63      ! 大范围 permit 10.139.0.0/16，无业务需求即删
 no 1000    ! 禁止 13 段访问任何网段（属 in）
exit
```

## 复用方法（套用到其他 VLAN）

1. 替换网段与 SVI IP
2. 按实际 DHCP/DNS/NTP/核心服务器更新 100–121、200–208
3. 沿用编号体系（10–99 / 100–199 / 200–299 / 990）
4. 零信任演进：先保留临时 `permit any` 兜底，逐步收敛为"显式白名单 + 唯一 990 deny"

## 验证清单（每次套用后必做）

- [ ] 终端能取到 DHCP 地址（`ipconfig /renew`、`dhclient`）
- [ ] 能解析内部域名（经指定 DNS）
- [ ] NTP 校时正常
- [ ] **无法**访问防火墙 / 未白名单的核心设备
- [ ] **无法**从本 VLAN 发起 3389 / 445 / telnet 到任意目标

## 命名建议

ACL 名称带方向后缀：`ACL_VLAN713_IN` / `ACL_VLAN713_OUT`，避免后期维护与 MES/MTS 排障时误判方向。
