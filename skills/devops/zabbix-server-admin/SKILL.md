---
name: zabbix-server-admin
description: "Zabbix 服务器管理: 版本检查、官方最新版本对比、升级流程(备份→yum→重启→验证)、服务器维护操作。适用于 spipzabbix.sercomm.com (10.140.1.42)。"
---

# Zabbix Server Administration Skill

管理 Sercomm Zabbix 服务器 (spipzabbix)。覆盖版本检查、升级、维护。与 zabbix-export-devices(设备导出)、zabbix-problem-management(告警关闭)构成 Zabbix 技能家族,本技能管"服务器本身"。

## 环境信息

| 项目 | 值 |
|------|------|
| 服务器 | spipzabbix = 10.140.1.42 |
| OS | CentOS Stream 9 |
| 安装方式 | RPM (zabbix-release-7.4-3.el9) |
| 数据库 | MySQL (mysqld) |
| Web | nginx + PHP |
| SSH | `ssh 10.140.1.42`(root,~/.ssh/config 已有条目) |
| API | https://spipzabbix.sercomm.com/api_jsonrpc.php (Bearer header) |

## 版本检查

### 方式 1: API(推荐,无需 SSH)
```bash
curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -d '{"jsonrpc":"2.0","method":"apiinfo.version","params":{},"id":1}'
```
⚠️ **apiinfo.version 必须不带 `Authorization: Bearer` 头**(7.4 实测):
带 header 会报 `The "apiinfo.version" method must be called without authorization header.`
其余所有 API 方法(host.get 等)都需要 Bearer 头,只有此方法是例外。

### 方式 2: 服务器端
```bash
ssh -o ConnectTimeout=10 -o BatchMode=yes 10.140.1.42 "zabbix_server -V | head -2"
```

### 最新版本查询
访问 https://www.zabbix.com/download_sources → "Zabbix 7.4" 行 → Release 列。
已知基线 (2026-07-31): 当前 7.4.9, 最新 7.4.13 (2026-07-29 发布)。

## 升级流程 (7.4.x 补丁升级)

⚠️ **生产系统,遵循只查不改策略**: 任何变更必须先提案(改什么+为什么+风险),经用户明确批准 (clarify 确认) 后才执行。

1. **备份数据库** — 升级前必须备份,回滚靠它
   ```bash
   ssh -o ConnectTimeout=10 -o BatchMode=yes 10.140.1.42 \
     "mkdir -p /backup && mysqldump --databases zabbix --single-transaction > /backup/zabbix_$(date +%Y%m%d).sql && ls -lh /backup/"
   ```

2. **升级组件**
   ```bash
   # 先进行模拟升级，确保没有意外的依赖变更
   ssh -o ConnectTimeout=10 -o BatchMode=yes 10.140.1.42 "dnf upgrade --assumeno \\
     --disablerepo=epel,epel-next,epel-cisco-openh264 \\
     zabbix-server-mysql \\
     zabbix-web \\
     zabbix-web-mysql \\
     zabbix-web-deps \\
     zabbix-nginx-conf \\
     zabbix-agent \\
     zabbix-get \\
     zabbix-sql-scripts \\
     zabbix-selinux-policy"
   
   # 确认模拟无异常后，进行实际升级
   ssh -o ConnectTimeout=10 -o BatchMode=yes 10.140.1.42 "dnf upgrade -y \\
     --disablerepo=epel,epel-next,epel-cisco-openh264 \\
     zabbix-server-mysql \\
     zabbix-web \\
     zabbix-web-mysql \\
     zabbix-web-deps \\
     zabbix-nginx-conf \\
     zabbix-agent \\
     zabbix-get \\
     zabbix-sql-scripts \\
     zabbix-selinux-policy"
   ```

3. **重启服务**
   ```bash
   ssh -o ConnectTimeout=10 -o BatchMode=yes 10.140.1.42 \
     "systemctl restart zabbix-server zabbix-agent nginx php-fpm && systemctl is-active zabbix-server zabbix-agent nginx php-fpm"
   ```

4. **验证**
   - `zabbix_server -V` → 版本号应为 7.4.13
   - API `apiinfo.version` 返回新版本
   - 数据库 schema 自动升级(7.4.x 内补丁一般自动处理,server 启动时执行)
   - UI 正常、最新数据点持续更新(监控恢复)
   - 检查 `/var/log/zabbix/zabbix_server.log` 无升级错误

## 组件清单 (rpm)

zabbix-server-mysql, zabbix-web-mysql, zabbix-agent, zabbix-get, zabbix-nginx-conf, zabbix-selinux-policy, zabbix-release, zabbix-sql-scripts, zabbix-web, zabbix-web-deps

## Pitfalls

1. **CentOS Stream 9 用 `rpm -qa` 而非 `dpkg -l`** 查包。
2. **敏感配置脱敏**: 查看 `/etc/zabbix/zabbix_server.conf` 中 DBPassword 时,先 `sed 's/DBPassword=.*/DBPassword=[REDACTED]/'` 再输出,密码不进终端/日志/回复。
3. **SSH 非交互**: 一律 `-o ConnectTimeout=10 -o BatchMode=yes`,避免挂起等待密码。
4. **升级前必须备份 + 用户批准**: 生产监控系统,违反会引发事故。
5. **yum repolist 可能 grep 不到 zabbix**(权限/输出差异),确认 repo 存在看 `rpm -qa | grep zabbix-release` 即可。
6. **同系列补丁升级 (7.4.9→7.4.13) 风险低**,但跨大版本 (7.4→8.0) 需查官方升级指南和 DB schema 变更,不能直接 yum update。
7. **apiinfo.version 是唯一不需要 Bearer 头的 API 方法**,带 header 反而报错;其他方法缺 header 也会报错。两者方向相反,容易混淆。
8. **MySQL 服务单元名是 `mysqld.service`(MySQL 8.4.10)**,不是 `mysql` 也不是 `mariadb`。`systemctl is-active mysql` 会返回 `inactive`(单元不存在),易误判数据库宕机。检查数据库一律用 `systemctl is-active mysqld` / `systemctl status mysqld`。
9. **SSH 连接已验证可用**(2026-07-31): `ssh -o ConnectTimeout=10 -o BatchMode=yes 10.140.1.42` root 免密,hostname=spipzabbix,CentOS Stream 9。若用户反馈"iTerm2 能连/免密正常",直接按此命令执行,不要反复怀疑 SSH 配置。

## 关联技能
- `zabbix-export-devices` — 设备信息导出 (VMware/Cisco/FortiGate/H3C)
- `zabbix-problem-management` — 告警关闭/分类
