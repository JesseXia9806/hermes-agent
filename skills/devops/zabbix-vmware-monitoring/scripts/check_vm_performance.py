#!/usr/bin/env python3
"""
Zabbix VMware 性能查询脚本

用于查询 Zabbix 7.4 中 VMware 虚拟机、ESXi 主机、vCenter 等设备的详细性能参数。
"""

import json
import urllib.request
import ssl
import sys
import argparse
from datetime import timedelta

# 配置
API_URL = "https://spipzabbix.sercomm.com/api_jsonrpc.php"
CREDENTIALS_FILE = "~/.hermes/secrets/zabbix_sercomm.txt"

# 跳过 SSL 验证
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

# VMware 设备组
VM_GROUPS = ["32", "71", "84", "26", "78"]
HV_GROUPS = ["7", "70", "24", "77"]
VCENTER_GROUPS = ["67"]

# 监控项Key映射
METRIC_KEYS = {
    "cpu_usage": ["vmware.vm.cpu.usage.perf", "vmware.hv.cpu.usage.perf"],
    "cpu_usage_hz": ["vmware.vm.cpu.usage", "vmware.hv.cpu.usage"],
    "cpu_cores": ["vmware.vm.cpu.num", "vmware.hv.cpu.num"],
    "memory_usage": ["vmware.vm.memory.usage", "vmware.hv.memory.usage"],
    "memory_used": ["vmware.vm.memory.size.usage.host", "vmware.hv.memory.size.usage.host"],
    "memory_total": ["vmware.vm.memory.size", "vmware.hv.memory.size"],
    "disk_read": ["vmware.vm.vfs.dev.read", "vmware.hv.vfs.dev.read"],
    "disk_write": ["vmware.vm.vfs.dev.write", "vmware.hv.vfs.dev.write"],
    "net_in": ["vmware.vm.net.if.in", "vmware.hv.net.if.in"],
    "net_out": ["vmware.vm.net.if.out", "vmware.hv.net.if.out"],
    "uptime": ["vmware.vm.uptime", "vmware.hv.uptime"],
    "boottime": ["custom.vm.boottime", "custom.hv.boottime"]
}

def get_credentials():
    """从凭据文件读取用户名和密码"""
    import os
    path = os.path.expanduser(CREDENTIALS_FILE)
    with open(path, "r") as f:
        content = f.read().strip()
        return dict(line.split('=', 1) for line in content.split('\n') if '=' in line)

def get_token():
    """获取 Zabbix API Token"""
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

def api(method, params, token):
    """调用 Zabbix API"""
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
        return json.loads(resp.read())

def get_devices(group_ids, token):
    """获取指定组的设备列表"""
    devices = []
    for gid in group_ids:
        resp = api("host.get", {
            "groupids": [gid],
            "output": ["hostid", "name", "status"],
            "selectInterfaces": ["ip", "dns"]
        }, token)
        
        if "result" in resp:
            for device in resp["result"]:
                device["group_id"] = gid
                devices.append(device)
    
    return devices

def get_metrics(device_id, token):
    """获取设备的所有监控项"""
    resp = api("item.get", {
        "hostids": [device_id],
        "output": ["itemid", "name", "key_", "lastvalue", "units", "value_type"],
        "sortfield": "name"
    }, token)
    
    return resp.get("result", [])

def extract_metrics(items):
    """从监控项中提取关键指标"""
    metrics = {}
    
    for item in items:
        key = item.get("key_")
        value = item.get("lastvalue")
        units = item.get("units", "")
        
        for metric_name, key_patterns in METRIC_KEYS.items():
            for pattern in key_patterns:
                if pattern in key:
                    try:
                        # 转换为浮点数
                        if value.isdigit():
                            value = float(value)
                        elif value.replace('.', '', 1).isdigit():
                            value = float(value)
                        
                        metrics[metric_name] = {
                            "value": value,
                            "units": units,
                            "key": key
                        }
                    except (ValueError, AttributeError):
                        # 非数值类型
                        metrics[metric_name] = {
                            "value": value,
                            "units": units,
                            "key": key
                        }
    
    return metrics

def format_uptime(seconds):
    """将秒数转换为可读格式"""
    if not isinstance(seconds, (int, float)):
        return "N/A"
    
    try:
        seconds = int(float(seconds))
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{days}天 {hours}小时 {minutes}分钟 {seconds}秒"
    except (ValueError, TypeError):
        return "N/A"

def main():
    parser = argparse.ArgumentParser(description='查询Zabbix中VMware设备性能参数')
    parser.add_argument('--device-type', choices=['vm', 'hypervisor', 'vcenter', 'all'], default='all', 
                       help='设备类型: vm (虚拟机), hypervisor (ESXi主机), vcenter (vCenter), all (所有)')
    parser.add_argument('--device-name', help='指定设备名称')
    parser.add_argument('--format', choices=['text', 'json'], default='text', help='输出格式')
    parser.add_argument('--limit', type=int, default=10, help='返回结果数量限制')
    args = parser.parse_args()
    
    # 获取 Token
    token = get_token()
    
    # 选择设备组
    group_ids = []
    if args.device_type in ['vm', 'all']:
        group_ids.extend(VM_GROUPS)
    if args.device_type in ['hypervisor', 'all']:
        group_ids.extend(HV_GROUPS)
    if args.device_type in ['vcenter', 'all']:
        group_ids.extend(VCENTER_GROUPS)
    
    # 获取设备列表
    devices = get_devices(group_ids, token)
    
    if args.device_name:
        devices = [d for d in devices if args.device_name.lower() in d["name"].lower()]
    
    if not devices:
        print(f"未找到符合条件的设备")
        sys.exit(1)
    
    # 限制结果数量
    devices = devices[:args.limit]
    
    # 获取性能指标
    results = []
    for device in devices:
        print(f"正在查询设备: {device['name']} (ID: {device['hostid']})", file=sys.stderr)
        
        items = get_metrics(device["hostid"], token)
        metrics = extract_metrics(items)
        
        # 计算衍生指标
        if "cpu_usage" in metrics and "cpu_cores" in metrics:
            try:
                metrics["cpu_usage_total"] = {
                    "value": round(metrics["cpu_usage"]["value"] * metrics["cpu_cores"]["value"] / 100, 2),
                    "units": "%",
                    "key": "derived.cpu.usage.total"
                }
            except (KeyError, TypeError, ValueError):
                pass
        
        if "disk_read" in metrics and "disk_write" in metrics:
            try:
                metrics["disk_io_total"] = {
                    "value": metrics["disk_read"]["value"] + metrics["disk_write"]["value"],
                    "units": metrics["disk_read"]["units"],
                    "key": "derived.disk.io.total"
                }
            except (KeyError, TypeError):
                pass
        
        if "net_in" in metrics and "net_out" in metrics:
            try:
                metrics["net_total"] = {
                    "value": metrics["net_in"]["value"] + metrics["net_out"]["value"],
                    "units": metrics["net_in"]["units"],
                    "key": "derived.net.total"
                }
            except (KeyError, TypeError):
                pass
        
        if "uptime" in metrics:
            metrics["uptime_str"] = {
                "value": format_uptime(metrics["uptime"]["value"]),
                "units": "",
                "key": "derived.uptime.str"
            }
        
        # 准备结果
        result = {
            "name": device["name"],
            "hostid": device["hostid"],
            "status": device["status"],
            "ip": device.get("interfaces", [{}])[0].get("ip", "N/A"),
            "metrics": metrics
        }
        
        results.append(result)
    
    # 输出结果
    if args.format == "json":
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        for result in results:
            print(f"设备名称: {result['name']}")
            print(f"设备ID: {result['hostid']}")
            print(f"状态: {'正常' if result['status'] == '0' else '异常'}")
            print(f"IP地址: {result['ip']}")
            print("\n=== 性能指标 ===")
            
            for metric_name, data in result["metrics"].items():
                print(f"{metric_name.replace('_', ' ').title()}: {data['value']} {data['units']}")
            
            print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()