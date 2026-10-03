---
name: zabbix-daily-english-report
description: 生成并发送Zabbix英文全局巡检报告(Top5主机+ActionPlan)至Obsidian及邮件
---

# Zabbix Daily English Inspection Report

Use this skill when you need to run the daily IT infrastructure inspection. It automatically:
1. Pulls all current unresolved alerts from Zabbix (without a 24-hour time ceiling, to catch lingering critical problems).
2. Maps alerts to their originating Hosts.
3. Groups the problems into IT management categories (Temperature, High Error Rate, Link Down, CPU/Memory Resource Pressure, etc.).
4. Formats it nicely into an English Markdown **Top-5 Device list** with **Action Plans**.
5. Writes the report to Jesse's local Obsidian Vault (`Hermes-AI/Daily_Reports`).
6. Dispatches the report directly to `spimd@sercomm.com` via internal SMTP (`smtptp02.sercomm.com`).

## 依赖 / Dependencies
- **Zabbix API Access**: Reads Zabbix API token via local password stash (`~/.hermes/secrets/zabbix_sercomm.txt`).
- **Python Libraries**: Standard libraries (`requests`, `json`, `urllib3`, `smtplib`, `datetime`).

## 核心执行脚本 / Execution Script
In the conversation, use the `execute_code` tool to run this complete self-contained script. 

```python
import requests
import json
import urllib3
import os
import datetime
import smtplib
from collections import defaultdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Disable unverified HTTPS request warnings
urllib3.disable_warnings()

def load_zabbix_token():
    creds_path = os.path.expanduser("~/.hermes/secrets/zabbix_sercomm.txt")
    with open(creds_path, "r", encoding="utf-8") as f:
        creds = dict(line.strip().split('=', 1) for line in f if '=' in line)
    
    login_payload = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {"username": creds.get('username'), "password": creds.get('password')},
        "id": 1
    }
    resp = requests.post("https://spipzabbix.sercomm.com/api_jsonrpc.php", json=login_payload, verify=False, timeout=10)
    return resp.json().get('result')

def run_daily_inspection():
    zabbix_url = "https://spipzabbix.sercomm.com/api_jsonrpc.php"
    token = load_zabbix_token()
    headers = {"Content-Type": "application/json-rpc", "Authorization": f"Bearer {token}"}

    # 1. Fetch all unresolved problems (no time limit)
    prob_payload = {
        "jsonrpc": "2.0", "method": "problem.get",
        "params": {"output": ["eventid", "objectid", "name", "severity", "clock"], "recent": False, "limit": 5000},
        "id": 2
    }
    probs = requests.post(zabbix_url, headers=headers, json=prob_payload, verify=False, timeout=30).json().get("result", [])

    # 2. Get triggers to map Hostnames
    trigger_ids = list(set([p['objectid'] for p in probs]))
    trig_payload = {
        "jsonrpc": "2.0", "method": "trigger.get",
        "params": {"output": ["triggerid"], "triggerids": trigger_ids, "selectHosts": ["name"]},
        "id": 3
    }
    triggers = {t['triggerid']: t for t in requests.post(zabbix_url, headers=headers, json=trig_payload, verify=False, timeout=30).json().get("result", [])}

    # 3. Categorize
    summary = defaultdict(list)
    for p in probs:
        name_lower = p['name'].lower()
        trigger = triggers.get(p['objectid'], {})
        host_name = trigger.get('hosts', [{'name': 'Unknown'}])[0]['name']
        item = {"host": host_name, "issue": p['name'], "severity": int(p['severity']), "clock": int(p['clock'])}
        
        if any(kw in name_lower for kw in ["temperature", "fan", "高温", "thermal"]):
            summary["Environment & Hardware (Temperature/Fans)"].append(item)
        elif "high error rate" in name_lower or "error" in name_lower:
            summary["Network Quality Degradation (High Error Rate)"].append(item)
        elif "speed" in name_lower:
            summary["Port Speed Anomalies (Speed Downgrade)"].append(item)
        elif "link down" in name_lower or "down" in name_lower:
            summary["Port & Link Disconnections (Link Down)"].append(item)
        elif "unreachable" in name_lower or "ping" in name_lower:
            summary["Host Unreachable (Ping Loss)"].append(item)
        elif any(kw in name_lower for kw in ["cpu", "memory", "disk", "space", "utilization"]):
            summary["Resource Pressure (CPU/Mem/Disk)"].append(item)
        else:
            summary["Others/Misc"].append(item)

    # 4. Construct Markdown
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    report_lines = [
        f"# {today_str} Daily IT Inspection Report", "",
        "## Global Active Alerts Summary (Zabbix)", "",
        f"*Total unresolved issues across the environment: {len(probs)}*\n"
    ]

    cat_blueprints = {
        "Environment & Hardware (Temperature/Fans)": ("CRITICAL", "Physical risks & hardware degradation. Overheating >65°C can cause module burnouts.", [
            "1. **Physical Audit:** IT onsite personnel must proceed to MDF/IDF cabinets immediately. Verify AC cooling.",
            "2. **Hardware Check:** Verify fan status/noise. RMA if faulty."
        ]),
        "Network Quality Degradation (High Error Rate)": ("HIGH", "Packet drops, slowness or disconnections.", [
            "1. **Cabling Layer:** Replace aged patch cords. Clean fiber LC connectors or swap SFP.",
            "2. **Config Layer:** Check Duplex Mismatch. Hardcode port speed if needed."
        ]),
        "Port Speed Anomalies (Speed Downgrade)": ("MEDIUM", "Often points to aged cabling or duplex mismatch.", [
            "1. **Investigation:** Caused by auto-negotiation failure. Replace Ethernet cable."
        ]),
        "Resource Pressure (CPU/Mem/Disk)": ("MEDIUM/HIGH", "VM/Server constraints leading to sluggishness.", [
            "1. **Compute:** Hot-add CPU/RAM via vCenter if utilization persists above 90%.",
            "2. **Storage:** Purge old logs, truncate temp tables, or utilize LVM volume extension."
        ]),
        "Port & Link Disconnections (Link Down)": ("MEDIUM", "Port down events. Often obsolete items.", [
            "1. **Audit & Prune:** If corresponding equipment is obsolete, Shutdown the port so Zabbix stops triggering."
        ]),
        "Host Unreachable (Ping Loss)": ("HIGH", "Severe network or OS unresponsiveness.", ["1. Verify OS boot state or upstream route logic."]),
        "Others/Misc": ("INFO/LOW", "Miscellaneous warnings requiring individual triaging.", [])
    }

    for cat, (sev, imp, actions) in cat_blueprints.items():
        items = summary.get(cat, [])
        if not items: continue

        report_lines.append(f"### 📍 {cat} ({len(items)} active events)")
        report_lines.append(f"**Severity:** {sev} | **Impact:** {imp}\n")
        report_lines.append("**Affected Top 5 Devices:**")
        
        items_sorted = sorted(items, key=lambda x: (x['severity'], x['clock']), reverse=True)
        seen_hosts, top_display = set(), []
        for i in items_sorted:
            if i['host'] not in seen_hosts:
                seen_hosts.add(i['host'])
                top_display.append(f"- **{i['host']}** : {i['issue']}")
            if len(top_display) == 5: break
            
        if len(top_display) < 5 and len(items_sorted) > len(top_display):
            for i in items_sorted[:5]:
                if f"- **{i['host']}** : {i['issue']}" not in top_display:
                    top_display.append(f"- **{i['host']}** : {i['issue']}")
                    
        report_lines.extend(top_display)
        
        if actions:
            report_lines.append("\n**Action Plan:**")
            report_lines.extend(actions)
        report_lines.append("\n---\n")

    md_content = "\n".join(report_lines)

    # 5. Write to Obsidian
    base_dir = "/Users/jessexia/Library/Mobile Documents/iCloud~md~obsidian/Documents/iPhone/jesse-obsidian/Hermes-AI/Daily_Reports"
    os.makedirs(base_dir, exist_ok=True)
    filepath = os.path.join(base_dir, f"{today_str}-Zabbix-Daily-Report.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Obsidian doc generated: {filepath}")

    # 6. Send Email
    msg = MIMEMultipart()
    msg["From"] = "jesse_xia@sercomm.com"
    msg["To"] = "spimd@sercomm.com"
    msg["Subject"] = f"Zabbix Daily IT Inspection Report ({today_str})"
    msg.attach(MIMEText(md_content, "plain", "utf-8"))

    try:
        server = smtplib.SMTP("smtptp02.sercomm.com", 25, timeout=10)
        server.sendmail(msg["From"], msg["To"], msg.as_string())
        server.quit()
        print("Email sent successfully to spimd@sercomm.com via smtptp02.sercomm.com.")
    except Exception as e:
        print(f"Warning: Email sending failed: {e}")

run_daily_inspection()
```