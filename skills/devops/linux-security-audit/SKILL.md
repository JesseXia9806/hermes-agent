---
name: linux-security-audit
description: "对远程 Linux 服务器执行 12 项安全审计检查并输出结构化报告（Ubuntu & RHEL/CentOS）"
metadata:
  hermes:
    tags: [security, audit, linux, ubuntu, centos, rhel]
---

# Linux 安全审计工作流

## 适用场景
- 对远程 Linux 服务器（Ubuntu / RHEL / CentOS）进行安全检查
- 输出结构化审计报告：通过项、关注项、攻击面总结
- **仅检查，不执行任何卸载或配置变更**

## 前置条件
- 已配置 SSH 免密登录（密钥认证）
- 用户有 sudo 权限
- 本地 `~/.ssh/config` 已配好 Host 别名（如 `Host ubuntu-prod`）

---

## 步骤 1：准备审计脚本

以下脚本兼容 Ubuntu 24.04 和 RHEL 9 / CentOS Stream / Rocky / Alma。

脚本路径：参考 skill 内 `references/security_check.sh`，或每次执行时从记忆生成。

```bash
scp /tmp/security_check.sh <host-alias>:/tmp/
ssh <host-alias> "bash /tmp/security_check.sh"
```

### 审计脚本内容（12 项）

```bash
#!/bin/bash
# Linux Security Audit Report
echo "==========================================="
echo "  Linux Security Audit Report"
echo "  $(date -u '+%Y-%m-%d %H:%M UTC')"
echo "==========================================="
echo ""; echo "=== 1. SYSTEM INFO ==="
hostname; uname -a
cat /etc/os-release 2>/dev/null || cat /etc/redhat-release 2>/dev/null
uptime

echo ""; echo "=== 2. USER ACCOUNTS ==="
grep -E '/bin/.*sh' /etc/passwd | grep -vE 'nologin|/usr/sbin/nologin'
head -30 /etc/sudoers 2>/dev/null
ls -la /etc/sudoers.d/ 2>/dev/null
for f in /etc/sudoers.d/*; do [ -f "$f" ] && echo "=== $f ===" && cat "$f" 2>/dev/null; done

echo ""; echo "=== 3. SSH CONFIGURATION ==="
egrep -v '^#|^$' /etc/ssh/sshd_config 2>/dev/null | grep -iE \
  '(permitrootlogin|passwordauthentication|pubkeyauthentication|port|allowusers|denyusers|permitemptypasswords|clientaliveinterval|clientalivecountmax|maxauthtries|maxsessions|x11forwarding|listenaddress)'

echo ""; echo "=== 4. NETWORK & FIREWALL ==="
ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null
which ufw 2>/dev/null && sudo ufw status 2>/dev/null
which firewall-cmd 2>/dev/null && sudo firewall-cmd --list-all 2>/dev/null
sudo iptables -L -n 2>/dev/null | head -20

echo ""; echo "=== 5. RUNNING SERVICES ==="
systemctl list-units --type=service --state=running 2>/dev/null | head -40

echo ""; echo "=== 6. SYSTEM UPDATES ==="
which apt 2>/dev/null && apt list --upgradable 2>/dev/null | head -20
which dnf 2>/dev/null && dnf check-update 2>/dev/null | head -20

echo ""; echo "=== 7. RESOURCE USAGE ==="; df -h /; free -h

echo ""; echo "=== 8. AUTHENTICATION LOGS ==="
last -10 2>/dev/null; lastb -10 2>/dev/null
fail2ban-client status 2>/dev/null || echo "(not installed)"

echo ""; echo "=== 9. SCHEDULED TASKS ==="
crontab -l 2>/dev/null
ls /etc/cron.d/ 2>/dev/null; ls /etc/cron.daily/ 2>/dev/null

echo ""; echo "=== 10. SECURITY HARDENING ==="
find /usr /bin /sbin /lib -type f -perm -4000 2>/dev/null | sort
find /etc /bin /sbin /usr/bin /usr/sbin -type f -perm -o+w 2>/dev/null | head -20
ls -la /etc/hosts.equiv 2>/dev/null

echo ""; echo "=== 11. KERNEL & CONTAINERS ==="
getenforce 2>/dev/null || aa-status 2>/dev/null || echo "(neither active)"
lsmod 2>/dev/null | head -10
docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}' 2>/dev/null || echo "(not installed)"
podman ps -a 2>/dev/null || echo "(not installed)"

echo ""; echo "=== 12. TEMPORARY DIRECTORIES ==="
ls -la /tmp/ 2>/dev/null | head -10
ls -la /dev/shm/ 2>/dev/null | head -5

echo ""; echo "==========================================="
echo "  Audit Complete: $(date -u '+%Y-%m-%d %H:%M UTC')"
echo "==========================================="
```

完整脚本见 skill 内 `references/security_check.sh`。

---

## 步骤 2：执行审计

```bash
scp ~/.hermes/skills/devops/linux-security-audit/references/security_check.sh <host-alias>:/tmp/
ssh <host-alias> "bash /tmp/security_check.sh"
```

---

## 步骤 3：输出审计报告

审计完成后，按以下模板整理报告：

```
## 🔍 Linux 安全审计报告
**主机**: {hostname} | **OS**: {os_version} | **Kernel**: {kernel}
**运行时长**: {uptime} | **负载**: {load}

### ✅ 通过项（绿色）
| 检查项 | 状态 | 说明 |
|:-------|:----:|:-----|

### ⚠️ 关注项（按严重度排序）
| # | 严重度 | 问题 | 建议 |
|:-:|:------:|:-----|:-----|

### 📊 资源
- 磁盘: {total} / 已用 {used} ({used_percent}%)
- 内存: {total} / 使用 {used}

### 🔒 攻击面总结
| 端口 | 服务 | 状态 |
|:----|:-----|:----:|
```

严重度分级规则：
- 🔴 **高危** — 端口暴露公网、无密码保护的服务、root 远程登录开启
- 🟠 **中危** — 防火墙未启用、X11Forwarding 开启、NOPASSWD sudo
- 🟡 **低危** — 有可用但非安全更新、日志未记录
- 🔵 **注意** — 可疑 IP 登录、容器重启、AppArmor/SELinux 未 enforce

---

## 常见陷阱（审计专用）

1. **SSH 执行长命令超时** — 分步骤执行，apt update 设 `timeout >= 120`
2. **`2>/dev/null` 与 `for` 循环** — macOS bash 不支持 `for f in *.d/* 2>/dev/null`，改用 `[ -f "$f" ] || continue`
3. **`lastb` 在无失败记录时返回非零** — 用 `|| echo` 保护
4. **`docker ps` 需 socket 权限** — 非 root 用户需属于 docker 组才能执行
5. **RHEL 没有 `ufw`** — 用 `firewall-cmd` 检查；Ubuntu 没有 `firewalld`
6. **自建仓库的 `apt list --upgradable` 输出可能很多行** — 用 `head -20` 截断

---

## 与 ISO 27001 的关系

> ⚠️ **这 12 项检查只覆盖 ISO 27001:2022 Annex A 技术控制的 ~24%，整体 93 项控制的 ~9%。**  
> 适用于**日常安全基线巡检**，不能替代完整的合规审计。

完整 ISO 27001 覆盖率对照表详见 skill 内 `references/iso27001-coverage.md`。

如需要 ISO 27001 差距分析，请要求加载对应的技能或模板。
