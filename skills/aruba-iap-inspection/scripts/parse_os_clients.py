import subprocess
import json
import re
import sys
import os

def parse_clients_os(sites=["R1", "R2", "P2site"]):
    total_clients = 0
    os_counts = {}
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    rest_query_path = os.path.join(script_dir, 'rest_query.py')

    for site in sites:
        cmd = f"python3 {rest_query_path} --site {site} 'show clients'"
        try:
            print(f"Fetching {site}...", file=sys.stderr)
            output = subprocess.check_output(cmd, shell=True, text=True)
            lines = output.split('\n')
            parsing_table = False
            
            for line in lines:
                line = line.strip()
                if line.startswith("Name") and "MAC Address" in line and "OS" in line:
                    parsing_table = True
                    continue
                if parsing_table and line.startswith("----"):
                    continue
                if parsing_table and line == "":
                    parsing_table = False
                    continue
                    
                if parsing_table:
                    # Anchor extraction strictly on MAC Address format
                    mac_match = re.search(r'([0-9a-f]{2}(?::[0-9a-f]{2}){5})', line)
                    if mac_match:
                        mac_end = mac_match.end()
                        total_clients += 1
                        
                        # OS is the next identifiable chunk after the MAC Address
                        remainder = line[mac_end:].strip()
                        remainder_parts = re.split(r'\s{2,}', remainder)
                        if len(remainder_parts) >= 1:
                            os_val = remainder_parts[0]
                            # Clean up shifting caused by missing OS (e.g., hitting ESSID directly)
                            if os_val == "" or (os_val.startswith("Sercomm") or os_val == "ebin" or os_val == "eSOP" or os_val == "OQC_Google" or os_val == "NOFP"):
                                os_val = "Unknown/NOFP"
                            os_counts[os_val] = os_counts.get(os_val, 0) + 1

        except Exception as e:
            print(f"Error on {site}: {e}", file=sys.stderr)

    return total_clients, os_counts

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Aggregate and parse OS types from Aruba clients across sites.")
    parser.add_argument("--sites", nargs="+", default=["R1", "R2", "P2site"], help="List of sites to query")
    args = parser.parse_args()
    
    total, counts = parse_clients_os(args.sites)
    print("TOTAL_CLIENTS:", total)
    print("OS_COUNTS:", json.dumps(counts, indent=4))
