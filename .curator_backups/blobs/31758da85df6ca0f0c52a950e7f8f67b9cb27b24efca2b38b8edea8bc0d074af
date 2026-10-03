#!/usr/bin/env bash
# verify_provider.sh — layers 1-2 of the LLM provider verification ladder.
#
# Proves: host reachable + key accepted + upstream returns a real completion.
# Does NOT prove Hermes' config path resolves — that is layer 3, run manually:
#   hermes chat -q "Reply with exactly: PROVIDER-OK" --provider <NAME> --model auto
#
# Usage:
#   ./verify_provider.sh <base_url> <api_key> [model]
# Example:
#   ./verify_provider.sh http://10.0.0.5:3001/v1 "$KEY" auto
#
# The key is never echoed in full. macOS note: `timeout` is absent on a stock
# macOS, so curl's own -m cap is the only timeout used here.

set -uo pipefail

BASE_URL="${1:?usage: verify_provider.sh <base_url> <api_key> [model]}"
API_KEY="${2:?usage: verify_provider.sh <base_url> <api_key> [model]}"
MODEL="${3:-auto}"

BASE_URL="${BASE_URL%/}"   # strip trailing slash
TMP="$(mktemp -t verifyscript.XXXXXX)"
trap 'rm -f "$TMP"' EXIT

echo "=== Target: ${BASE_URL}  (key ${API_KEY:0:12}... len=${#API_KEY}) ==="
echo

# --- Layer 1: reachability + auth -------------------------------------------
echo "[1/2] GET ${BASE_URL}/models"
CODE=$(curl -s -o "$TMP" -w '%{http_code}' -m 20 "${BASE_URL}/models" \
        -H "Authorization: Bearer ${API_KEY}")
echo "      HTTP ${CODE}"
case "$CODE" in
  200) echo "      PASS - endpoint reachable, key accepted" ;;
  401|403) echo "      FAIL - key rejected (HTTP ${CODE})"; exit 1 ;;
  000) echo "      FAIL - no response (DNS/port/TLS/timeout)"; exit 1 ;;
  *)   echo "      WARN - unexpected status"; head -c 300 "$TMP"; echo; exit 1 ;;
esac

# --- Model inventory (from the already-fetched response) --------------------
echo
echo "      Models advertised by the endpoint:"
python3 - "$TMP" <<'PY'
import json, sys
try:
    data = json.load(open(sys.argv[1]))
except Exception as exc:
    print(f"        (could not parse: {exc})"); sys.exit(0)
ids = [m.get("id", "?") for m in data.get("data", [])]
for i in ids[:40]:
    print(f"        - {i}")
if len(ids) > 40:
    print(f"        ... and {len(ids) - 40} more")
print(f"        total: {len(ids)}")
PY

# --- Layer 2: real inference ------------------------------------------------
echo
echo "[2/2] POST ${BASE_URL}/chat/completions  (model=${MODEL})"
curl -s -o "$TMP" -m 60 "${BASE_URL}/chat/completions" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"${MODEL}\",\"messages\":[{\"role\":\"user\",\"content\":\"reply with exactly: OK\"}],\"max_tokens\":20}"

python3 - "$TMP" <<'PY'
import json, sys
raw = open(sys.argv[1]).read()
try:
    d = json.loads(raw)
except Exception:
    print("      FAIL - non-JSON response:"); print(raw[:500]); sys.exit(1)

if "error" in d:
    print(f"      FAIL - endpoint error: {d['error']}"); sys.exit(1)

try:
    content = d["choices"][0]["message"]["content"]
except (KeyError, IndexError):
    print("      FAIL - no completion in response:"); print(raw[:500]); sys.exit(1)

print(f"      PASS - completion: {content!r}")
print()
# Surface the ACTUAL upstream: with a router alias like 'auto' the requested
# model is not necessarily the model that answered.
print(f"      requested model : {d.get('model', '(unknown)')}")
routed = d.get("_routed_via") or d.get("provider") or d.get("system_fingerprint")
if routed:
    print(f"      routed via      : {routed}")
usage = d.get("usage")
if usage:
    print(f"      tokens          : {usage.get('total_tokens', '?')}")
PY

echo
echo "Layers 1-2 complete. Now run the acceptance test (layer 3):"
echo "  hermes chat -q \"Reply with exactly: PROVIDER-OK\" --provider <NAME> --model ${MODEL}"
