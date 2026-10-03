#!/usr/bin/env python3
"""Close Zabbix problems whose triggers have manual_close=1.
Keeps manual_close=0 problems (auto-close triggers) visible as real issues.

Usage: python3 zabbix_close_manual.py [TOKEN]
Env:   Zabbix 7.4.9 at spipzabbix.sercomm.com, Bearer-header auth, self-signed cert.
"""
import json
import urllib.request
import ssl
import datetime
import sys

API_URL = 'https://spipzabbix.sercomm.com/api_jsonrpc.php'
TOKEN = sys.argv[1] if len(sys.argv) > 1 else '<LOGIN_TOKEN>'

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def api(method, params):
    req = urllib.request.Request(
        API_URL,
        data=json.dumps({'jsonrpc': '2.0', 'method': method, 'params': params, 'id': 1}).encode(),
        headers={'Content-Type': 'application/json-rpc', 'Authorization': f'Bearer {TOKEN}'}
    )
    with urllib.request.urlopen(req, context=ctx, timeout=60) as r:
        return json.loads(r.read())

SEV = ['Not classified', 'Info', 'Warning', 'Average', 'High', 'Disaster']

# 1. All truly open problems (no recent filter = unclosed only)
problems = api('problem.get', {
    'output': ['eventid', 'name', 'severity', 'r_eventid', 'clock', 'r_clock', 'objectid'],
    'sortfield': 'eventid', 'sortorder': 'DESC', 'limit': 300,
})['result']
active = [p for p in problems if not p.get('r_eventid') or p.get('r_eventid') == '0']
print(f'Active problems: {len(active)}')

# 2. Trigger manual_close for all active problems
trigger_ids = sorted(set(p['objectid'] for p in active))
triggers = api('trigger.get', {
    'output': ['triggerid', 'description', 'manual_close', 'priority'],
    'triggerids': trigger_ids, 'limit': 300,
})['result']
trig_map = {t['triggerid']: t for t in triggers}

# 3. Classify: manual_close=1 -> closable; manual_close=0 -> real issues, keep
closable = [(p, trig_map[p['objectid']]) for p in active
            if trig_map.get(p['objectid'], {}).get('manual_close') == '1']
keep = [(p, trig_map[p['objectid']]) for p in active
        if trig_map.get(p['objectid'], {}).get('manual_close') == '0']
unknown = [p for p in active if p['objectid'] not in trig_map]
print(f'  manual_close=1 (closable): {len(closable)}')
print(f'  manual_close=0 (keep - real issues): {len(keep)}')
print(f'  unknown trigger: {len(unknown)}')

def fmt(p, t):
    clock = datetime.datetime.fromtimestamp(int(p['clock'])).strftime('%Y-%m-%d %H:%M')
    return f"[{p['eventid']}] {SEV[int(p['severity'])]:6s} {clock} {t['description'][:70]}"

print('\n=== CLOSING (manual_close=1) ===')
for p, t in closable:
    print(' ', fmt(p, t))
print('\n=== KEEPING (manual_close=0 - real issues) ===')
for p, t in keep:
    print(' ', fmt(p, t))

# 4. Execute close
if closable:
    event_ids = [p['eventid'] for p, _ in closable]
    print(f'\n>>> Closing {len(event_ids)} problems...')
    result = api('event.acknowledge', {
        'eventids': event_ids,
        'action': 1,
        'message': 'Closed by IT admin via API - trigger allows manual close'
    })
    print('Close result:', json.dumps(result))

# 5. Verify (fresh no-recent query; counts shift as new problems appear)
print('\n=== VERIFICATION ===')
after = api('problem.get', {
    'output': ['eventid', 'name', 'severity', 'r_eventid', 'objectid'],
    'sortfield': 'eventid', 'sortorder': 'DESC', 'limit': 300,
})['result']
after_active = [p for p in after if not p.get('r_eventid') or p.get('r_eventid') == '0']
print(f'Open problems after close: {len(after_active)} (was {len(active)})')
