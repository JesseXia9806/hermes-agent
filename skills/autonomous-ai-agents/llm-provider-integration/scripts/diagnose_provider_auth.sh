#!/usr/bin/env bash
# diagnose_provider_auth.sh — triage "custom provider 401s on every model"
#
# Usage: diagnose_provider_auth.sh <base_url> <secrets_file>
#   e.g. diagnose_provider_auth.sh http://10.0.0.5:3001/v1 ~/.hermes/secrets/freellm.txt
#
# Distinguishes three different failures that all look like "401":
#   (1) gateway down        -> step 1 times out / connection refused
#   (2) credential invalid  -> step 1 = 401, step 2 = 401
#   (3) Hermes not fed the key -> step 1 = 401, step 2 = 200   <-- most common, config is FINE
#
# Never prints the secret: only a prefix + length.
set -uo pipefail

BASE_URL="${1:?usage: $0 <base_url> <secrets_file>}"
SECRETS="${2:?usage: $0 <base_url> <secrets_file>}"

if [ ! -f "$SECRETS" ]; then
  echo "ERROR: secrets file not found: $SECRETS" >&2
  exit 2
fi

# --- read the key without echoing it -----------------------------------------
KEY=$(python3 - "$SECRETS" <<'PY'
import sys
for l in open(sys.argv[1], encoding='utf-8', errors='ignore'):
    l = l.strip()
    if l.startswith('API_KEY'):
        print(l.split('=', 1)[1].strip().strip('"').strip("'")); break
PY
)

if [ -z "$KEY" ]; then
  echo "ERROR: no line starting with API_KEY= in $SECRETS" >&2
  exit 2
fi
echo "key loaded: prefix=${KEY:0:6}... len=${#KEY}"
echo

# --- step 1: gateway reachable? ----------------------------------------------
printf 'step 1  no-key  %s/models -> ' "$BASE_URL"
C1=$(curl -s -o /dev/null -w '%{http_code}' -m 15 "$BASE_URL/models" || echo 000)
echo "HTTP $C1"
case "$C1" in
  401) echo '        => gateway is HEALTHY; this is an authentication problem, not a service outage' ;;
  200) echo '        => gateway answers without auth (open endpoint) — cannot use this to judge the key' ;;
  000) echo '        => cannot connect: gateway down, wrong port, firewall, or wrong base_url. STOP HERE.'; exit 1 ;;
  *)   echo "        => unexpected; investigate the gateway";;
esac
echo

# --- step 2: is the stored credential valid? ---------------------------------
printf 'step 2  with-key %s/models -> ' "$BASE_URL"
python3 - "$BASE_URL" "$KEY" <<'PY'
import json, sys, urllib.error, urllib.request
url, key = sys.argv[1], sys.argv[2]
try:
    req = urllib.request.Request(url + "/models", headers={"Authorization": "Bearer " + key})
    r = urllib.request.urlopen(req, timeout=25)
    n = len(json.load(r).get('data', []))
    print(f"HTTP {r.status} | {n} models")
    if r.status == 200:
        print("        => credential is VALID.")
        print("           If Hermes still 401s, Hermes is not receiving the key — go to step 3.")
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}")
    print("        => credential REJECTED by the gateway: key rotated, revoked, or wrong.")
    print("           Get a fresh key from the gateway operator; do not touch config.yaml.")
except Exception as e:
    print(f"ERR {type(e).__name__}: {e}")
PY
echo

# --- step 3: what does Hermes say? -------------------------------------------
echo 'step 3  (run these manually — they are the decisive evidence)'
echo '        grep -i key_env ~/.hermes/logs/errors.log | tail -5'
echo '        grep -i -E "AuthenticationError|401" ~/.hermes/logs/agent.log | tail -5'
echo

# Current-state check FIRST: a historical log warning must not be read as a live fault.
# Cross-check every key_env declared in config.yaml against the live .env.
echo '--- live check: does every config.yaml key_env resolve in .env? ---'
python3 - <<'PY'
import os, re
try:
    cfg = open(os.path.expanduser('~/.hermes/config.yaml'), encoding='utf-8', errors='ignore').read()
    env = open(os.path.expanduser('~/.hermes/.env'), encoding='utf-8', errors='ignore').read()
except FileNotFoundError as e:
    print(f'  cannot read: {e}'); raise SystemExit

vars_ = []
for m in re.finditer(r'^\s*key_env:\s*(\S+)\s*$', cfg, re.M):
    v = m.group(1).strip().strip('"').strip("'")
    if v and v not in vars_:
        vars_.append(v)

MISSING = []
for v in vars_:
    m = re.search(rf'^{re.escape(v)}=(.*)$', env, re.M)
    if not m:
        print(f'  MISSING   {v}  -> not in .env')
        MISSING.append(v)
    elif not m.group(1).strip():
        print(f'  EMPTY     {v}  -> present but blank')
        MISSING.append(v)
    else:
        print(f'  OK        {v}  -> present, value len={len(m.group(1).strip())}')
print()
if MISSING:
    print(">>> FOUND IT (live): these key_env vars do not resolve. Fix them from the secrets file:")
    for v in MISSING:
        print(f'      {v}')
    print('    Back up first:  cp -p ~/.hermes/.env ~/.hermes/.env.bak.$(date +%Y%m%d-%H%M%S)')
    print(f'    Re-add ONLY the missing line(s) from {SECRETS}, chmod 600, then run the layer-3 test.')
else:
    print('>>> All key_env vars resolve in .env. If a 401 persists, the credential itself is bad')
    print('    (see step 2) or the wrong provider name/base_url is being called.')
PY

echo
if grep -qi 'is set but the variable is empty/unset' ~/.hermes/logs/errors.log 2>/dev/null; then
  echo "note: errors.log contains a PAST 'empty/unset' warning. Confirm it is historical with:"
  echo '      grep -i key_env ~/.hermes/logs/errors.log | tail -3   # check the timestamps'
fi
echo
echo 'step 4  did config drift, or only the credential?'
echo '        ls -lat ~/.hermes/ | head -12          # compare .env mtime vs config.yaml mtime'
echo '        ls -la ~/.hermes/backups/config/ | tail -5   # if config.yaml size matches its backup, config did NOT change'
