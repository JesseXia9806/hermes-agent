import urllib.request
import urllib.error
import ssl
import json
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def try_login(pwd):
    req = urllib.request.Request("https://10.139.9.1:4343/rest/login", data=json.dumps({"user": "monitor", "passwd": pwd}).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=5) as r:
            return json.loads(r.read().decode('utf-8'))
    except Exception as e:
        return str(e)

for p in ["Amis#20261003", '"Amis#20261003"', "Amis"]:
    print(f"pwd={p} -> {try_login(p)}")
