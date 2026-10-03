#!/bin/bash
# Linux Security Audit Report - Ubuntu & RHEL/CentOS compatible
# Usage: scp this to target host, then: bash security_check.sh
# NOTE: Audit only — does NOT modify any system configuration.

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
