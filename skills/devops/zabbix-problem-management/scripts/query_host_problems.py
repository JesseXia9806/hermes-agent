#!/usr/bin/env python3
"""
Zabbix Problem Query Tool for Specific Host

This script demonstrates how to query problems for a specific host by IP or hostname,
following the best practices established in the zabbix-problem-management skill.
"""

import json
import urllib.request
import ssl
import sys
import argparse
from datetime import datetime

# Configuration
API_URL = "https://spipzabbix.sercomm.com/api_jsonrpc.php"
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

SEVERITY_MAP = {
    '0': 'Not classified',
    '1': 'Information', 
    '2': 'Warning',
    '3': 'Average',
    '4': 'High',
    '5': 'Disaster'
}

def get_credentials():
    """Load credentials from the standard file"""
    import os
    path = os.path.expanduser("~/.hermes/secrets/zabbix_sercomm.txt")
    with open(path, "r") as f:
        content = f.read().strip()
        return dict(line.split('=', 1) for line in content.split('\n') if '=' in line)

def get_token():
    """Get Zabbix API token"""
    creds = get_credentials()
    data = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "username": creds["username"],
            "password": creds["password"]
        },
        "id": 1
    }
    req = urllib.request.Request(API_URL, data=json.dumps(data).encode(), 
                                headers={"Content-Type": "application/json-rpc"})
    with urllib.request.urlopen(req, context=SSL_CTX, timeout=60) as resp:
        return json.loads(resp.read())["result"]

def api_call(method, params, token):
    """Make a Zabbix API call"""
    data = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    req = urllib.request.Request(API_URL, data=json.dumps(data).encode(), 
                                headers={
                                    "Content-Type": "application/json-rpc",
                                    "Authorization": f"Bearer {token}"
                                })
    with urllib.request.urlopen(req, context=SSL_CTX, timeout=60) as resp:
        response = json.loads(resp.read())
        if 'error' in response:
            print(f"API Error: {response['error']}", file=sys.stderr)
            sys.exit(1)
        return response.get('result', [])

def get_host_id_by_ip(ip_address, token):
    """Get host ID by IP address"""
    hosts = api_call('host.get', {
        'output': ['hostid', 'name'],
        'filter': {'ip': ip_address}
    }, token)
    
    if not hosts:
        print(f"No host found with IP: {ip_address}", file=sys.stderr)
        sys.exit(1)
    
    return hosts[0]['hostid'], hosts[0]['name']

def get_host_id_by_name(hostname, token):
    """Get host ID by hostname"""
    hosts = api_call('host.get', {
        'output': ['hostid', 'name'],
        'search': {'host': hostname}
    }, token)
    
    if not hosts:
        print(f"No host found matching: {hostname}", file=sys.stderr)
        sys.exit(1)
    
    return hosts[0]['hostid'], hosts[0]['name']

def get_trigger_ids_for_host(host_id, token):
    """Get all trigger IDs for a host"""
    triggers = api_call('trigger.get', {
        'output': ['triggerid'],
        'hostids': [host_id]
    }, token)
    
    return [t['triggerid'] for t in triggers]

def get_problems_for_triggers(trigger_ids, token, limit=50):
    """Get problems for specific triggers"""
    if not trigger_ids:
        return []
    
    problems = api_call('problem.get', {
        'output': ['eventid', 'name', 'severity', 'objectid', 'acknowledged', 'suppressed', 'r_eventid', 'clock', 'r_clock'],
        'objectids': trigger_ids,
        'sortfield': 'eventid',
        'sortorder': 'DESC',
        'limit': limit
    }, token)
    
    return problems

def format_problem(problem):
    """Format a problem for display"""
    clock_dt = datetime.fromtimestamp(int(problem['clock']))
    r_clock_dt = datetime.fromtimestamp(int(problem.get('r_clock', 0))) if problem.get('r_clock') else None
    
    return {
        'eventid': problem['eventid'],
        'name': problem['name'],
        'severity': SEVERITY_MAP.get(problem['severity'], problem['severity']),
        'severity_code': int(problem['severity']),
        'status': 'RESOLVED' if problem.get('r_eventid') and problem.get('r_eventid') != '0' else 'ACTIVE',
        'clock': clock_dt.strftime('%Y-%m-%d %H:%M:%S'),
        'r_clock': r_clock_dt.strftime('%Y-%m-%d %H:%M:%S') if r_clock_dt else 'N/A',
        'acknowledged': 'Yes' if problem.get('acknowledged') == '1' else 'No',
        'suppressed': 'Yes' if problem.get('suppressed') == '1' else 'No'
    }

def main():
    parser = argparse.ArgumentParser(description='Query Zabbix problems for a specific host')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--ip', help='Host IP address')
    group.add_argument('--name', help='Hostname (will use search)')
    parser.add_argument('--limit', type=int, default=50, help='Number of problems to return (default: 50)')
    parser.add_argument('--format', choices=['table', 'json'], default='table', help='Output format')
    
    args = parser.parse_args()
    
    # Get token
    print("Getting authentication token...", file=sys.stderr)
    token = get_token()
    
    # Get host ID
    if args.ip:
        host_id, host_name = get_host_id_by_ip(args.ip, token)
        print(f"Found host: {host_name} (ID: {host_id})", file=sys.stderr)
    else:
        host_id, host_name = get_host_id_by_name(args.name, token)
        print(f"Found host: {host_name} (ID: {host_id})", file=sys.stderr)
    
    # Get trigger IDs
    print("Getting trigger IDs for host...", file=sys.stderr)
    trigger_ids = get_trigger_ids_for_host(host_id, token)
    print(f"Found {len(trigger_ids)} triggers", file=sys.stderr)
    
    # Get problems
    print(f"Getting latest {args.limit} problems...", file=sys.stderr)
    problems = get_problems_for_triggers(trigger_ids, token, args.limit)
    
    if not problems:
        print("No problems found for this host.")
        return
    
    # Format problems
    formatted = [format_problem(p) for p in problems]
    
    # Output
    if args.format == 'json':
        print(json.dumps(formatted, indent=2, ensure_ascii=False))
    else:
        # Table format
        print(f"\n{host_name} - Latest {len(formatted)} Problems:")
        print("-" * 100)
        header = f"{'Event ID':<12} {'Severity':<12} {'Status':<10} {'Start Time':<20} {'End Time':<20} {'Ack':<6} {'Supp':<6} {'Name':<30}"
        print(header)
        print("-" * 100)
        
        for p in formatted:
            line = f"{p['eventid']:<12} {p['severity']:<12} {p['status']:<10} {p['clock']:<20} {p['r_clock']:<20} {p['acknowledged']:<6} {p['suppressed']:<6} {p['name'][:30]:<30}"
            print(line)
        
        print("-" * 100)
        active_count = sum(1 for p in formatted if p['status'] == 'ACTIVE')
        resolved_count = sum(1 for p in formatted if p['status'] == 'RESOLVED')
        print(f"Total: {len(formatted)} | Active: {active_count} | Resolved: {resolved_count}")

if __name__ == "__main__":
    main()