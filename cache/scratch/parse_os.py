import subprocess
import json

sites = ["R1", "R2", "P2site"]
total_clients = 0
os_counts = {}

for site in sites:
    cmd = f"python3 ~/.hermes/skills/aruba-iap-inspection/scripts/rest_query.py --site {site} 'show clients'"
    print(f"Fetching {site}...", flush=True)
    try:
        output = subprocess.check_output(cmd, shell=True, text=True)
        # Parse output block
        lines = output.split('\n')
        parsing_table = False
        headers = []
        os_index = -1
        mac_index = -1
        
        for line in lines:
            line = line.strip()
            if line.startswith("Name") and "MAC Address" in line and "OS" in line:
                parsing_table = True
                # simple index split based on multiple spaces since it's a fixed width or aligned table
                # A safer approach is to find the column index of "OS" and "MAC Address" in the header string
                os_index = line.find("OS")
                mac_index = line.find("MAC Address")
                continue
            if parsing_table and line.startswith("----"):
                continue
            if parsing_table and line == "":
                parsing_table = False
                continue
                
            if parsing_table:
                # The columns are somewhat aligned. Let's extract OS.
                # Since spaces can vary, we can slice based on the header positions.
                # However, Name can have spaces. "OS" usually starts right after MAC Address.
                # Let's split by 2 or more spaces.
                import re
                parts = re.split(r'\s{2,}', line)
                if len(parts) >= 6:
                    # Usually: [0]=Name, [1]=IP, [2]=MAC, [3]=OS, [4]=ESSID, [5]=AP...
                    # Wait, if Name is empty, it might mess up. Let's use string positions based on headers.
                    # But if parts works, let's test it:
                    pass
                
                # Using fixed indices is safer: "OS" header starts at os_index
                if os_index != -1 and len(line) > os_index:
                    # Find ends:
                    # MAC is around 40-57, OS is around 59-67
                    # Let's dynamically find the next column start.
                    header_line = [l for l in lines if l.strip().startswith("Name") and "OS" in l][0]
                    # Find all matches of word boundaries in header
                    columns = [(m.start(), m.group()) for m in re.finditer(r'\S+(?:\s+\S+)*', header_line.strip())]
                    # It's complicated. Let's just use regex to match MAC Address and the word after it.
                    # MAC address format: xx:xx:xx:xx:xx:xx
                    mac_match = re.search(r'([0-9a-f]{2}(?::[0-9a-f]{2}){5})', line)
                    if mac_match:
                        mac = mac_match.group(1)
                        mac_end = mac_match.end()
                        total_clients += 1
                        
                        # OS is the next chunk of text after MAC Address.
                        # Sometimes OS can have spaces (e.g., "Win 11", "Mac OS").
                        # Let's get substring after MAC.
                        remainder = line[mac_end:].strip()
                        # The next column is ESSID. We know ESSID because it's usually "Sercomm_Employee" or "ebin".
                        # Let's split by 2+ spaces.
                        remainder_parts = re.split(r'\s{2,}', remainder)
                        if len(remainder_parts) >= 1:
                            os_val = remainder_parts[0]
                            if os_val == "" or (os_val.startswith("Sercomm") or os_val == "ebin" or os_val=="eSOP"): # missing OS column shifting
                                os_val = "Unknown/NOFP"
                            elif os_val == "NOFP":
                                os_val = "Unknown/NOFP"
                            os_counts[os_val] = os_counts.get(os_val, 0) + 1

    except Exception as e:
        print(f"Error on {site}: {e}")

print("TOTAL_CLIENTS:", total_clients)
print("OS_COUNTS:", json.dumps(os_counts, indent=4))
