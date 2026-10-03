drawio-skill at ~/.hermes/skills/drawio-skill/ (v1.28.1). drawio CLI on PATH (Homebrew wrapper, v30.2.4); v30+ supports Mermaid→.drawio and ELK --layout.
§
macOS sec scan: batch processes, network, launch agents, profiles, login items, SSH config. Table format (✅/⚠️/❌).
§
SSH audit: never use set -e / stderr redirect in loops. SCP to /tmp/.
§
Word docs: 'uv pip install --system python-docx'; run script via terminal tool (not execute_code).
§
FortiGate 100F (internal IP). Read-only auditing via fortigate-security-audit. Always "只查不改", explicit approval for modifications.
§
Video2Text at ~/.video2text/ (sawyerbutton fork). CLI: video2text/mp4-to-text/v2t. faster-whisper; ctranslate2 no MPS → CPU; tiny/base models best on this Mac.
§
Zabbix 7.4.9 @ spipzabbix.sercomm.com (10.140.1.42, CentOS9): Bearer auth, Admin/zabbix, skip SSL verify. root console ready. CSV ~/zabbix_vmware_export.csv. Skills: zabbix-export-devices, zabbix-problem-management, zabbix-server-admin.
§
Sercomm eHR (ehr.sercomm.com): user 2013444 (夏正洋). Workflow in skill `ehr-approval-workflow`. 定时审批用 cronjob LLM 模式加载技能,勿写 shell 脚本调 browser_*(那是 agent 工具)。
§
凭据统一存放: 所有系统帐密存 ~/.hermes/secrets/ 下,每系统一个文件(如 ehr_sercomm.txt),chmod 600,文件名即系统标识。密码永不写入技能正文/聊天/thinking,登录时从文件读取。
§
FreeLLMAPI(FREELLM, 用户自建 OpenAI 兼容网关)已配为 Hermes custom provider: base_url http://124.107.126.226:3001/v1 (V1/v1 均可), provider 默认 model=auto, 凭据备份 ~/.hermes/secrets/freellm.txt. 上游偶发不稳(auto 会自动跳过).
§
Domain: sercomm.com (SERCOMM.COM); Domain Controller: SPIAD02
§
Node 10.139.1.5 (logserver, RHEL 9): Hosts Hermes container & Nginx. Natively hosts PostgreSQL 16 (port 5432, user: postgres, pw: Amis#201920261002). Contains 'mes_raw_data' (Oracle MES) and 'hikvision_attendance' (MS SQL) for AI Text-to-SQL analytics.
§
Sercomm Hikvision attendance & MES raw data architecture on 10.139.1.5: PostgreSQL 16 bare-metal setup. DBs: hcp_cache (ODS layer, incremental cron sync every 30m from MS SQL 10.139.1.32), hikvision_attendance (DW star-schema with dim_employee, dim_attendance_machine, fact_swipe_log, agg_daily_attendance), and mes_raw_data. FDW cross-database engine aggregates daily attendance every 30m (at :10 and :40).