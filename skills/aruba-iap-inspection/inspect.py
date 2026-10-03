#!/usr/bin/env python3
"""Aruba IAP 8.0 巡检脚本 - 通过 REST API 收集信息并输出 Markdown"""
import json, os, sys, base64, requests
from datetime import datetime
from pathlib import Path

SECRET = Path.home() / '.hermes' / 'secrets' / 'aruba_iap.txt'
IAP_IP = '10.120.9.1'          # 请替换为您环境中的 IAP IP
REPORT_DIR = Path.home() / 'Library' / 'Mobile Documents' / 'iCloud~md~obsidian' / \
             'Documents' / 'iPhone' / 'jesse-obsidian' / 'Hermes-AI' / 'KnowledgeBase' / 'Aruba_IAP'
REPORT_DIR.mkdir(parents=True, exist_ok=True)

if not SECRET.is_file():
    sys.stderr.write(f'缺少凭据 {SECRET}\n')
    sys.exit(1)

cred = SECRET.read_text().strip()
user, pwd = cred.split(':', 1)
auth = {'Authorization': 'Basic ' + base64.b64encode(f'{user}:{pwd}'.encode()).decode(), 'Accept': 'application/json'}

def api(ep):
    r = requests.get(f'https://{IAP_IP}:4343/v1/configuration/{ep}', headers=auth, verify=False, timeout=10)
    r.raise_for_status()
    return r.json()

def md(title, txt):
    return f'## {title}\n\n```text\n{txt}\n```\n'

ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
report = [f'# Aruba IAP 巡检报告\n', f'**采集时间:** {ts}\n', f'**目标 IAP IP:** {IAP_IP}\n']

# 1. 系统概览
v = api('system/show_version')
report.append(md('系统概览', json.dumps(v, indent=2, ensure_ascii=False)))

# 2. AP 数据库
adb = api('ap/database')
report.append(md('AP 数据库', json.dumps(adb, indent=2, ensure_ascii=False)))

# 3. BSS 表（前 5 台 AP，防止输出过长）
aps = adb.get('ap_list', [])
for ap in aps[:5]:
    mac = ap.get('ap_mac') or ap.get('ap_macos')
    if not mac: continue
    b = api(f'ap/bss-table?ap_mac={mac}')
    report.append(md(f'AP {mac} BSS', json.dumps(b, indent=2, ensure_ascii=False)))

# 4. SSID 配置
for ss in ['Sercomm_Employee','Sercomm_Customer','Ebin','Sercomm_Guest']:
    c = api(f'wlan/ssid-profile?name={ss}')
    report.append(md(f'SSID 配置: {ss}', json.dumps(c, indent=2, ensure_ascii=False)))

# 5. 当前关联客户端
a = api('ap/association')
report.append(md('当前关联客户端', json.dumps(a, indent=2, ensure_ascii=False)))

# 6. 最近系统日志
l = api('system/logging?num=50')
lines = []
for entry in l.get('log', []) if isinstance(l,dict) else l:
    msg = entry.get('message') if isinstance(entry,dict) else str(entry)
    if any(k in msg for k in ['%SEC_LOGIN-','%SYS-','%SW_MATM-']):
        lines.append(msg)
report.append(md('最近系统日志', '\\n'.join(lines) if lines else '(无匹配日志)'))

# 写入
rf = REPORT_DIR / f'Aruba_IAP_Inspection_{datetime.now():%Y%m%d_%H%M}.md'
rf.write_text(''.join(report), encoding='utf-8')
print(f'报告已写入: {rf}')

# 打印简要摘要到控制台
summary = '\n'.join(report[:5])
print(f'\n--- 巡检摘要 ---\n{summary}')