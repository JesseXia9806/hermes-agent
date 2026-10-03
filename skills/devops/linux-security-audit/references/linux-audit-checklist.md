# Linux (Ubuntu) Remote Security Audit Checklist

Run on: target Linux host via SSH
Script: `scripts/linux-security-audit.sh` (SCP'd to `/tmp/`)

## Command Cheat Sheet (for ad-hoc in-session use)

### User & Access
```
cat /etc/passwd | grep -E '/bin/.*sh' | grep -vE 'nologin'
cat /etc/sudoers.d/* 2>/dev/null
grep -E 'PermitRootLogin|PasswordAuthentication|PubkeyAuthentication' /etc/ssh/sshd_config
```

### Network
```
ss -tlnp
ufw status verbose
iptables -L -n --line-numbers
```

### Security Status
```
last -10
lastb -10
fail2ban-client status
aa-status
apt list --upgradable 2>/dev/null | grep -i security
```

### Docker
```
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}'
docker stats --no-stream
```

## Severity Matrix

| Severity | Color | Response |
|----------|-------|----------|
| High | 🔴 | Fix immediately or within 24h |
| Medium | 🟠 | Fix within 1 week |
| Low | 🟡 | Schedule for next maintenance window |
| Note | 🔵 | Monitor, no immediate action needed |

## Firewall Edge Cases

| Symptom | Likely Cause | Action |
|---------|-------------|--------|
| `ufw` command not found; `dpkg -l ufw` shows `^rc` | UFW package was purged but old rules remain in kernel | `apt-get install -y ufw && ufw --force reset` then reconfigure |
| `ufw status` shows old rules for non-existent services (80, 443, 3306) | Services removed but rules persist | `ufw status numbered`, then `ufw delete <num>` per stale rule |
| iptables/nftables shows DOCKER, DOCKER-FORWARD chains but Docker is gone | Docker removed, chains are harmless residue | Leave them or `sudo nft flush ruleset` (⚠️ wipes everything) |

## nftables Note

Ubuntu 24.04 uses nftables under the hood. UFW adds rules to nftables via `iptables-legacy` translation. Docker also adds DOCKER chains to nftables. When Docker is removed, these chains persist in memory (they are invisible from `iptables -L` but visible in `nft list ruleset`). They are inactive when no Docker processes exist.
