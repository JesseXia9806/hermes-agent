---
name: windows-dhcp-security-audit
description: Use when analyzing Windows DHCP logs for ISO27001 audits.
version: 1.0.0
author: AI Copilot
license: MIT
metadata:
  hermes:
    tags: [dhcp, security, audit, iso27001, netclaw, devops]
    related_skills: [linux-security-audit, fortigate-ops]
---
# Windows DHCP Security & ISO 27001 Audit

## When to Use
Use this skill when processing large Windows DHCP Server log exports (typically CSV or `.log` format) to evaluate network security, identify rogue devices, assess service capacity, or generate an ISO 27001 compliance audit report.

## Workflow
1. **Execute locally via script**: Never load raw DHCP logs into the LLM context (files are typically >10MB and will crash the context or be rejected). Always use `execute_code` with a Python script to process the file line-by-line and aggregate metrics.
2. **Handle Windows encoding**: Use `encoding='latin-1'` (or `errors='ignore'`) when reading the log file to prevent `UnicodeDecodeError` caused by legacy device hostnames or strange characters.
3. **Data Extraction**: Split the CSV by comma. Format is typically `ID,Date,Time,Description,IP Address,Host Name,MAC Address`. Skip header lines and empty lines. 
4. **Key Event IDs & ISO 27001 Mapping**:
   - **Event 13** (IP conflict via Ping) -> **A.13.1 Network Security Management**: Indicates rogue static IPs or DHCP pool overlap.
   - **Event 14** (Scope Exhausted) -> **A.12.1 Capacity Management**: High risk to service availability. Needs lease time adjustment or pool expansion.
   - **Event 15** (Lease Denied) -> **A.9.2 Access Control**: Highlights MAC filtering blocks or network access policy enforcement. 
   - **Freq MAC requests** (Event 10/11) -> **A.12.4 Logging & Monitoring**: Identify DHCP floods from malfunctioning NICs.
5. **Reporting**: Structure the final output for the IT Manager in Chinese, mapping findings strictly to the ISO 27001 domains above. Include actionable recommendations (e.g., cross-checking rogue MACs in the FortiGate ARP table). Ensure adherence to the strict "只查不改" (Read-Only) operational rule.

## Pitfalls
- Do not attempt to summarize the whole file text with an LLM. Always synthesize metrics via `collections.Counter` and pass a small JSON summary back to context to write the narrative report.
- Do not use `utf-8` strictly when reading Windows DHCP logs; it often crashes mid-file on non-standard client hostnames.
- Do not make changes to systems in response to findings without explicit approval; treat the analysis as a Read-Only assessment.