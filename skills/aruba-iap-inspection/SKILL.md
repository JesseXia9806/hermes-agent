---
name: aruba-iap-inspection
description: "Use when inspecting Aruba IAPs via REST API."
version: 1.0.0
author: Hermes Curators
---

# Aruba IAP REST API Inspections

This skill provides the workflow and constraints for securely querying and controlling Aruba Instant Access Points (IAP) via their native REST API, avoiding the fragility of third-party wrappers like `instantpy` that break on CLI formatting changes.

## Procedure

1. **Credentials**: Read IAP IP, username, and password exclusively from `~/.hermes/secrets/aruba_iap.json`. The file uses a multi-site JSON structure (keys like "R1", "R2", "P2site").
   - By default, the script targets the `default_site` from the JSON.
   - To target a specific site, run `python scripts/rest_query.py --site <SiteName> "<command>"`.
2. **Session Authentication (SID)**:
   - Make a `POST` request to `https://<ip>:4343/rest/login` with JSON body: `{"user": "<username>", "passwd": "<password>"}`.
   - Extract the `sid` token from the JSON response (`parsed["sid"]`).
3. **Execute Command**:
   - Send a `GET` request to `https://<ip>:4343/rest/show-cmd?iap_ip_addr=<ip>&cmd=<URL-encoded-cmd>&sid=<sid>`.
   - The output is nested inside the `"Command output"` JSON key.
4. **Logout**:
   - Make a `POST` request to `https://<ip>:4343/rest/logout?sid=<sid>` to invalidate the session cookie.

## Pitfalls & Rules

* **Parsing AP Outputs**: Aruba CLI outputs (like `show clients`) align with unpredictable spacing, and column values (like 'OS' or 'Name') can contain spaces (e.g., 'Win 10', 'OS X'), which breaks naive `.split()`. To parse client tables, anchor extractions strictly on formatted fields like MAC addresses (`re.search(r'([0-9a-f]{2}(?::[0-9a-f]{2}){5})')`) rather than whitespace delimiters.
* **Require Admin Privileges for `/show-cmd`**: Do NOT use `monitor` or read-only accounts for issuing show commands over REST. Aruba Instant OS rigidly enforces API privileges and will return XML `<error>Invalid opcode for current user</error>` regardless of whether the command is harmless (e.g. `show version`). Only an Admin-level account works.
* **Avoid General Regex for CLI Outputs**: Beyond strict IDs like MACs/IPs, avoid regexing free-text `show-cmd` outputs. Aruba frequently changes unstructured text layouts between minor releases. 
* **Handle SSL Appropriately**: Aruba IAPs use self-signed certificates by default. Disable SSL verification but suppress insecure request warnings to keep terminal output clean.

## Associated Scripts

* `scripts/rest_query.py`: A native Python script using `urllib` to handle the SID authentication lifecycle and multi-site configuration.
* `scripts/parse_os_clients.py`: A wrapper script that queries multiple sites via `rest_query.py` to securely aggregate and categorize connected devices by their OS fingerprint using robust regex matching on MAC arrays.