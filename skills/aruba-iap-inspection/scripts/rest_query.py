import json
import urllib.request
import urllib.error
import urllib.parse
import ssl
import sys

def get_creds(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def run_aruba_cmd(cmd, site_name=None):
    creds_path = "/Users/jessexia/.hermes/secrets/aruba_iap.json"
    try:
        creds_data = get_creds(creds_path)
    except Exception as e:
        print(f"Error loading credentials: {e}")
        return
    
    # Handle both old flat format and new multi-site format
    if "sites" in creds_data:
        site = site_name or creds_data.get("default_site", list(creds_data["sites"].keys())[0])
        creds = creds_data["sites"].get(site)
        if not creds:
            print(f"Site '{site}' not found in credentials.")
            return
        print(f"=== Target Site: {site} ({creds.get('ip')}) ===")
    else:
        creds = creds_data

    ip = creds.get("ip")
    username = creds.get("username")
    password = creds.get("password")
    port = creds.get("port", 4343)
    
    base_url = f"https://{ip}:{port}/rest"
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    login_url = f"{base_url}/login"
    login_data = json.dumps({"user": username, "passwd": password}).encode('utf-8')
    req = urllib.request.Request(login_url, data=login_data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            resp_body = response.read().decode('utf-8')
            parsed = json.loads(resp_body)
            if parsed.get("Status") != "Success":
                print(f"Login failed: {parsed}")
                return
            sid = parsed.get("sid")
    except Exception as e:
        print(f"Connection or login error: {e}")
        return

    show_url = f"{base_url}/show-cmd?iap_ip_addr={ip}&cmd={urllib.parse.quote(cmd)}&sid={sid}"
    req_show = urllib.request.Request(show_url)
    try:
        with urllib.request.urlopen(req_show, context=ctx, timeout=10) as response:
            resp_body = response.read().decode('utf-8')
            if resp_body.strip().startswith("<"):
                print("Received XML instead of JSON. The user might not have permissions for this API.")
                return
            data = json.loads(resp_body)
            command_output = data.get("Command output", "")
            print(f"--- Output for '{cmd}' ---")
            print(command_output)
    except Exception as e:
        print(f"Error executing command: {e}")
    finally:
        try:
            logout_url = f"{base_url}/logout?sid={sid}"
            req_logout = urllib.request.Request(logout_url, data=b"{}", headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req_logout, context=ctx, timeout=5) as r:
                pass
        except:
            pass

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Query Aruba IAP via REST API")
    parser.add_argument("--site", help="Target site (e.g., R1, R2, P2site)", default=None)
    parser.add_argument("cmd", nargs="*", default=["show version"], help="Command to execute")
    args = parser.parse_args()
    
    cmd_str = " ".join(args.cmd) if isinstance(args.cmd, list) else args.cmd
    run_aruba_cmd(cmd_str, site_name=args.site)