#!/bin/bash
# Linux Security Audit Script
# Usage: scp to /tmp/ on target, then: bash /tmp/linux-security-audit.sh
# DO NOT add set -e — one failed command should not block the rest.

echo "==========================================="
echo "  Linux Security Audit Report"
echo "  $(date -u '+%Y-%m-%d %H:%M UTC')"
echo "==========================================="

echo ""
echo "=== 1. SYSTEM INFO ==="
hostname
uname -a
cat /etc/os-release 2>/dev/null || cat /etc/lsb-release 2>/dev/null
echo "Uptime:"
uptime

echo ""
echo "=== 2. USER ACCOUNTS ==="
echo "--- Users with shell access ---"
grep -E '/bin/.*sh' /etc/passwd | grep -vE 'nologin|/usr/sbin/nologin' || echo "(none)"
echo ""
echo "--- Sudoers ---"
head -30 /etc/sudoers 2>/dev/null || echo "(no sudoers)"
echo ""
echo "--- Sudoers.d ---"
ls -la /etc/sudoers.d/ 2>/dev/null || echo "(no sudoers.d)"
for f in /etc/sudoers.d/*; do
  [ -f "$f" ] || continue
  echo "=== $f ==="
  cat "$f" 2>/dev/null
done

echo ""
echo "=== 3. SSH CONFIGURATION ==="
egrep -v '^#|^$' /etc/ssh/sshd_config 2>/dev/null | \
  grep -iE '(permitrootlogin|passwordauthentication|pubkeyauthentication|port|allowusers|denyusers|permitemptypasswords|clientaliveinterval|clientalivecountmax|maxauthtries|maxsessions|x11forwarding|listenaddress)' || echo "(not found)"

echo ""
echo "=== 4. NETWORK & FIREWALL ==="
echo "--- Listening Ports ---"
ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null
echo ""
echo "--- Firewall ---"
if command -v ufw &>/dev/null; then
  ufw status 2>/dev/null
elif dpkg -l ufw 2>/dev/null | grep -q '^rc'; then
  echo "(UFW package removed but config persists — rc state)"
  iptables -L -n -v 2>/dev/null | head -20
elif command -v iptables &>/dev/null; then
  iptables -L -n -v 2>/dev/null | head -20 || echo "(empty ruleset)"
else
  echo "(no firewall detected)"
fi

echo ""
echo "=== 5. RUNNING SERVICES ==="
systemctl list-units --type=service --state=running 2>/dev/null | head -40 || echo "(no systemd)"

echo ""
echo "=== 6. SYSTEM UPDATES ==="
apt list --upgradable 2>/dev/null | head -30

echo ""
echo "=== 7. RESOURCE USAGE ==="
df -h /
free -h

echo ""
echo "=== 8. AUTHENTICATION LOGS ==="
echo "--- Last 10 logins ---"
last -10 2>/dev/null || echo "(no wtmp)"
echo ""
echo "--- Failed logins (last 10) ---"
lastb -10 2>/dev/null || echo "(no btmp)"
echo ""
echo "--- fail2ban ---"
fail2ban-client status 2>/dev/null || echo "(not installed)"

echo ""
echo "=== 9. SCHEDULED TASKS ==="
echo "--- User crontab ---"
crontab -l 2>/dev/null || echo "(none)"
echo ""
echo "--- System cron dirs ---"
ls /etc/cron.d/ 2>/dev/null || echo "(empty)"
ls /etc/cron.daily/ 2>/dev/null || echo "(empty)"

echo ""
echo "=== 10. SECURITY HARDENING ==="
echo "--- SUID binaries ---"
find /usr /bin /sbin /lib -type f -perm -4000 2>/dev/null | sort
echo ""
echo "--- World-writable system files ---"
find /etc /bin /sbin /usr/bin /usr/sbin -type f -perm -o+w 2>/dev/null | head -20 || echo "(none)"
echo ""
echo "--- .rhosts / hosts.equiv ---"
ls -la /etc/hosts.equiv 2>/dev/null || echo "(none)"
find / -maxdepth 3 -name .rhosts 2>/dev/null || echo "(none)"

echo ""
echo "=== 11. KERNEL & DOCKER ==="
echo "--- SELinux / AppArmor ---"
getenforce 2>/dev/null || aa-status 2>/dev/null || echo "(neither active)"
echo ""
echo "--- Loaded modules (first 10) ---"
lsmod 2>/dev/null | head -10
echo ""
echo "--- Docker containers ---"
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}' 2>/dev/null || echo "(not installed)"

echo ""
echo "=== 12. TEMPORARY DIRECTORIES ==="
echo "--- /tmp/ (first 10) ---"
ls -la /tmp/ 2>/dev/null | head -10
echo ""
echo "--- /dev/shm (first 10) ---"
ls -la /dev/shm/ 2>/dev/null | head -10 || echo "(empty)"

echo ""
echo "==========================================="
echo "  Audit Complete: $(date -u '+%Y-%m-%d %H:%M UTC')"
echo "==========================================="
