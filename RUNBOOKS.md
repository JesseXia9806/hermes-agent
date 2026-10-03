# RUNBOOKS.md

## Purpose

This file defines reusable runbook structures for Jesse Xia’s IT Manager Digital Twin.

The goal is to standardize recurring IT management and infrastructure workflows so that the agent can:
- respond consistently,
- execute low-risk operational tasks in a structured way,
- prepare change plans, reports, and SOPs,
- enforce approval boundaries for risky or destructive actions.

This file is not a memory store.  
It is a workflow and procedure index.

---

## Global Execution Rules

- Always clarify the objective before execution.
- Inspect the current state before making changes when possible.
- Prefer minimal-change actions and reversible steps.
- Include validation steps after every change.
- Include rollback considerations for configuration or infrastructure changes.
- Treat file move, rename, overwrite, delete, bulk disable, permission removal, and destructive actions as high-risk operations.
- Require explicit confirmation before any destructive, irreversible, or data-placement-changing action.
- Do not expose passwords, secrets, tokens, or sensitive internal data in outputs.
- Keep outputs concise, structured, and operationally useful.

---

## Standard Response Pattern

Each runbook should follow this structure unless the workflow explicitly defines a different format:

1. Objective
2. Scope
3. Preconditions
4. Current State Check
5. Execution Steps
6. Validation
7. Risks / Cautions
8. Rollback
9. Output / Deliverables
10. Escalation Path

---

## Runbook Template

### [RUNBOOK_NAME]

**Objective**  
Short statement of what this runbook is intended to achieve.

**Scope**  
Systems, sites, services, or teams covered by this runbook.

**Preconditions**
- Required access
- Required tools
- Required approvals
- Required maintenance window if applicable

**Inputs**
- Site / environment
- Hostname / IP / device / account / ticket number
- Time range
- Requested change or target state

**Current State Check**
- Identify current status
- Gather baseline data
- Confirm dependencies
- Confirm whether this is safe to proceed

**Execution Steps**
1. Step one
2. Step two
3. Step three

**Validation**
- Confirm service health
- Confirm user impact
- Confirm logs / status / connectivity / output
- Confirm expected state achieved

**Risks / Cautions**
- Operational risks
- Security risks
- Audit concerns
- Known failure points

**Rollback**
- How to revert
- What backup/snapshot/config export is needed
- What condition triggers rollback

**Output / Deliverables**
- Summary
- Checklist result
- Logs
- Incident note
- Report / ticket update / email draft

**Escalation Path**
- When to stop
- When to escalate
- Which team / vendor / manager should be involved

---

## Runbook Categories

## 1. Incident Response

### Incident Triage
Use when a service, site, link, or business system is reported abnormal.

Suggested sub-runbooks:
- Service outage triage
- Slow performance triage
- Site network issue triage
- Production system abnormality triage
- User-impact assessment

### Major Incident Coordination
Use for multi-team incidents with business impact.

Suggested sub-runbooks:
- Major incident bridge coordination
- Stakeholder update drafting
- Vendor escalation package preparation
- Timeline reconstruction
- Initial post-incident summary

### Root Cause & Recovery
Use after containment.

Suggested sub-runbooks:
- Root cause evidence collection
- Recovery plan drafting
- Corrective action list
- Preventive action recommendation
- Incident closure summary

---

## 2. Server & Virtualization Operations

### Server Health Check
Suggested sub-runbooks:
- Windows server health check
- Linux server health check
- Disk / CPU / memory / service utilization review
- Critical log scan
- Backup result verification

### VMware Operations
Suggested sub-runbooks:
- VM health check
- ESXi host health review
- Snapshot review and cleanup planning
- Datastore capacity review
- VM deployment checklist
- Planned shutdown / startup sequencing

### Data Center / Server Room
Suggested sub-runbooks:
- Server room daily/weekly inspection
- UPS / power / temperature check
- Rack asset verification
- Physical equipment change record
- Maintenance preparation checklist

---

## 3. Network Operations

### Office Network
Suggested sub-runbooks:
- Core switch health check
- Internet access troubleshooting
- VLAN / routing change planning
- DHCP / DNS / gateway verification
- Bandwidth and link status review

### Production Network
Suggested sub-runbooks:
- Production line network connectivity check
- MES/MTS related network dependency check
- Line-side device communication troubleshooting
- Segmentation review
- Risk assessment before production-hour changes

### WAN / MPLS / Inter-site
Suggested sub-runbooks:
- MPLS link status validation
- Site-to-site connectivity troubleshooting
- Carrier escalation preparation
- Failover verification
- WAN performance baseline review

### Firewall / Security Perimeter
Suggested sub-runbooks:
- FortiGate policy review
- NAT / VIP change checklist
- VPN account and tunnel verification
- Security log review
- Rule cleanup recommendation

---

## 4. Identity & Access Management

### AD User Lifecycle
Suggested sub-runbooks:
- New account provisioning checklist
- Account disable / termination checklist
- Group membership review
- OU compliance review
- Password-related compliance check

### Access Review
Suggested sub-runbooks:
- Privileged account review
- Shared account review
- M365 license and identity reconciliation
- Access exception approval package
- Periodic permission audit summary

### Directory / Authentication Troubleshooting
Suggested sub-runbooks:
- Login failure triage
- Account lockout analysis
- Replication / DC health check
- GPO-related impact review

---

## 5. Business Systems Support

### MES / MTS
Suggested sub-runbooks:
- Service availability check
- Dependency validation
- User-impact diagnosis
- Interface or transaction failure triage
- Production impact summary

### ERP / eHR / Internal Systems
Suggested sub-runbooks:
- Application access issue triage
- Approval workflow exception handling
- Browser / client dependency checks
- Daily pending-item reminder flow
- Escalation note preparation

### Database-Backed Services
Suggested sub-runbooks:
- Database connectivity validation
- Replication / standby health check
- Scheduled job verification
- Basic performance symptom capture

---

## 6. Change Management

### Standard Change
Suggested sub-runbooks:
- Low-risk network change
- Low-risk server configuration change
- Firewall rule request processing
- Scheduled maintenance communication
- Validation and closure checklist

### Normal / High-Impact Change
Suggested sub-runbooks:
- Pre-change checklist
- Risk review
- Business impact note
- Rollback plan
- Approval summary
- Post-change validation report

### Emergency Change
Suggested sub-runbooks:
- Emergency action justification
- Limited-scope execution
- Immediate validation
- Emergency change record completion

---

## 7. Monitoring, Reporting, and Audit

### Daily / Weekly Operations Review
Suggested sub-runbooks:
- Daily infrastructure summary
- Weekly incident and change summary
- Daily backup review
- Site health digest
- Open risk / issue list

### Compliance & Audit
Suggested sub-runbooks:
- AD compliance check
- Server patch compliance review
- Backup policy compliance review
- Access control audit
- Evidence collection package

### Management Reporting
Suggested sub-runbooks:
- Weekly IT manager report
- Monthly operations summary
- Vendor performance summary
- Capacity and risk dashboard draft
- Budget/support justification note

---

## 8. Automation Operations

### Scripted Operations
Suggested sub-runbooks:
- Safe script execution checklist
- Dry-run / test mode verification
- Scheduled task review
- Log review and exception handling
- Script result reporting

### Agent-Assisted Workflow
Suggested sub-runbooks:
- Report drafting from logs and notes
- SOP generation from validated procedures
- Decision table creation
- Ticket/email summary generation
- Multi-step task planning

### Automation Guardrails
Suggested sub-runbooks:
- Approval-required actions
- Read-only first execution mode
- High-risk operation confirmation
- Audit log retention
- Secret handling restrictions

---

## 9. Communication Templates

### Incident Communication
Suggested sub-runbooks:
- Initial incident notice
- Business impact update
- Recovery progress update
- Resolution notice
- Executive summary

### Change Communication
Suggested sub-runbooks:
- Planned maintenance notice
- Change approval summary
- Post-change result update
- User-facing advisory

### Management & Vendor Communication
Suggested sub-runbooks:
- Vendor escalation email
- Technical clarification note
- Meeting summary
- Action item tracker
- Follow-up reminder draft

---

## 10. Knowledge Capture

### Post-Work Documentation
Suggested sub-runbooks:
- Convert resolved issue into SOP
- Convert repeated task into checklist
- Capture site-specific operational notes
- Capture lessons learned
- Update known issues list

### Knowledge Quality Rules
- Prefer short, explicit, reusable procedures
- Separate facts, steps, risks, and validation clearly
- Avoid mixing temporary context into stable runbooks
- Mark approval-required steps explicitly
- Keep runbooks versioned and reviewable

---

## High-Risk Actions Requiring Explicit Confirmation

The following categories always require explicit confirmation before execution:
- Delete files or data
- Move files or data to a different location
- Rename important data objects or production resources
- Bulk disable accounts
- Remove permissions
- Overwrite configuration in production
- Firewall rule deletion
- Production network changes during active production without approval
- Any irreversible or destructive operation

---

## Recommended Future Files

To keep this file clean, detailed procedures should later be split into separate files such as:
- RUNBOOK-AD.md
- RUNBOOK-VMWARE.md
- RUNBOOK-NETWORK.md
- RUNBOOK-FIREWALL.md
- RUNBOOK-INCIDENTS.md
- RUNBOOK-REPORTING.md

RUNBOOKS.md should remain the master index and execution standard.

