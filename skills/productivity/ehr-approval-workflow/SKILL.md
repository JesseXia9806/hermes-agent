---
name: ehr-approval-workflow
description: Sercomm eHR 系统登录与审批流程：登录、进入 Approve 待办列表、检查/核准请假单、销假单、补考勤单。密码存于本地凭据文件，不写入技能正文。
---

# eHR 审批工作流 Skill

Sercomm eHR 系统的登录与审批操作流程。目标:登录后进入 "My Approve",检查部下提交的请假单/销假单/补考勤单并核准。

## 环境信息

| 项目 | 值 |
|------|------|
| eHR URL | `https://ehr.sercomm.com/eHR/Account/#` |
| Approve 页面 | `https://ehr.sercomm.com/eHR/bpm/approve` |
| 用户名 | `2013444`(显示名: 夏正洋) |
| 凭据文件 | `~/.hermes/secrets/ehr_sercomm.txt`(权限 600,含 username/password) |
| 系统 | Sercomm PRD,基于旧版 jQuery + Kendo UI,界面为英文 |

**安全约定**: 密码**永不**写入技能正文/回复/thinking。登录时从凭据文件读取或要求用户提供,不硬编码。

## 📁 凭据统一存放规范(适用于所有系统)

所有系统的账号密码统一存放在 `~/.hermes/secrets/`:
- 每系统一个文件,文件名 = 系统标识,如 `ehr_sercomm.txt`、`zabbix_sercomm.txt`、`fortigate_rsite.txt`
- 文件内容格式: `username=<user>` + `password=<pass>`(每行一个键值)
- 权限一律 `chmod 600`(仅本人可读写)
- 创建: `mkdir -p ~/.hermes/secrets && printf 'username=...\npassword=...\n' > ~/.hermes/secrets/<name>.txt && chmod 600 ~/.hermes/secrets/<name>.txt`
- 读取: `cat ~/.hermes/secrets/<name>.txt` 后按行解析
- 密码永不写入技能正文、聊天回复、thinking 或任何日志

## 登录流程

1. 打开 `https://ehr.sercomm.com/eHR/Account/#`
2. 页面为 SPA(单页应用),登录表单有两个文本框:
   - 第一个 = Employee ID(输入 `2013444`)
   - 第二个 = 密码(从 `~/.hermes/secrets/ehr_sercomm.txt` 读取)
3. 点击 "Login" 按钮
4. 登录成功后顶部显示用户名"夏正洋",地址变为 `https://ehr.sercomm.com/eHR/`

## 进入 Approve 列表

1. 顶部导航点击 **Process Center** → 展开子菜单
2. 点击 **Approve** (或直接访问 `https://ehr.sercomm.com/eHR/bpm/approve`)
3. 页面顶部是筛选区,包含复选框:
   - **I sign off** (默认勾选) — 显示我已签署/待我签署的
   - **Agent Approval** (默认勾选) — 代理审批
   - **I handle** — 我处理的
   - **Agent processing** — 代理处理中
4. 表格列: 复选框 | Form | Applicant | Priority | Hold Days | Last Approver | Application time | Process Subject

## ⚠️ 关键行为与陷阱

1. **默认筛选已勾选 "I sign off" + "Agent Approval"**。如果 Agent Approval 显示为
   `disabled + checked`,说明 JS 强制锁定它;用 `browser_console` 可改 `disabled=false` 再取消勾选,
   但**点击 Search 后可能被 JS 恢复勾选**。若确认列表为空,不必纠结筛选,先确认再操作。

2. **"No items to display" = 确实没有待办**。本系统表格无数据时显示该文本。
   **已实测(2026-07-31): Approve 列表为空,没有任何待审批表单**。这是正常状态,不代表登录失败。

3. **验证空列表的正确方式**:
   - `browser_snapshot` 看 accessibility tree
   - 用 `browser_console` 执行 `document.body.innerText` 查找 "No items to display"
   - 或查 `tbody tr` 数量为 0
   - ⚠️ 不要为了排除问题反复点击 Search/All Forms/修改筛选——空列表就是空列表,直接向用户报告。

4. **browser_console 中 fetch() 被安全策略阻止** (Blocked: sensitive browser JavaScript primitive)。
   无法直接在页面上下文发网络请求,依赖页面自身的 JS 加载数据。

5. **vision 分析可能不可用** (No LLM provider configured for task=vision),此时用
   `browser_console` 读取 `document.body.innerText` 代替截图理解。

6. **页面用旧版 jQuery + Kendo UI**,console 会刷 JQMIGRATE 警告,属正常噪音,不是错误。

## 审批操作(有待办时)

1. 在 Approve 列表勾选目标表单前的复选框
2. 点击 **Approve** 按钮(绿色)核准,或 **Reject** 拒绝
3. 若需查看表单详情,点击对应行的 "Form" 链接
4. ⚠️ **核准/拒绝 = 修改性操作**,执行前先向用户展示表单清单(申请人/类型/时间)并确认

## 批量审批操作

1. **选择所有单据**: 逐个勾选需要审批的单据复选框
2. **批量审批**: 点击 **Approve** 按钮进行批量审批
3. **状态确认**: 
   - 审批按钮变为禁用状态表示操作成功
   - Search按钮也变为禁用状态表示系统正在处理
4. **无需添加审批意见**: 直接点击Approve按钮，系统自动处理

## 实际案例(2026-08-04)

已成功处理的加班申请单：
- **Overtime Application Form 271826**: Jomar Apellido, 11小时休息日加班
- **Overtime Application Form 271824**: Jomar Apellido, 10小时常规加班(5天)

批量审批后按钮状态变化：
- ✅ Approve按钮 → disabled (操作成功提交)
- ✅ Search按钮 → disabled (系统处理中)

## 执行日志功能

### 日志文件位置
- **日志路径**: `~/.hermes/logs/ehr_approval.log`
- **权限**: `chmod 600` (仅本人可读写)
- **格式**: JSON结构化日志，便于查询和分析

### 日志记录内容
每次执行时自动记录以下信息：
```json
{
  "timestamp": "2026-08-09T15:30:45+08:00",
  "execution_id": "ehr_20260809_153045",
  "user": "2013444",
  "login_status": "success",
  "pending_forms": [
    {
      "form_id": "Overtime Application Form 271826",
      "applicant": "Jomar Apellido",
      "form_type": "Overtime Application",
      "application_time": "2026-08-09 10:00:00",
      "subject": "11小时休息日加班申请"
    }
  ],
  "approved_forms": [
    {
      "form_id": "Overtime Application Form 271826",
      "applicant": "Jomar Apellido",
      "form_type": "Overtime Application",
      "approval_time": "2026-08-09 15:30:45"
    }
  ],
  "total_pending": 1,
  "total_approved": 1,
  "execution_duration": "2m 15s"
}
```

### 日志管理命令
- **查看最新日志**: `tail -n 50 ~/.hermes/logs/ehr_approval.log`
- **搜索特定表单**: `grep "Overtime Application Form" ~/.hermes/logs/ehr_approval.log`
- **按日期查询**: `grep "2026-08-09" ~/.hermes/logs/ehr_approval.log`
- **统计审批数量**: `grep "total_approved" ~/.hermes/logs/ehr_approval.log | awk '{sum+=$3} END {print "Total approved:", sum}'`

### 日志创建示例
```bash
# 创建日志目录
mkdir -p ~/.hermes/logs

# 查看历史记录
cat ~/.hermes/logs/ehr_approval.log | jq .
```

## 报告格式

- 登录状态: ✅ 成功 / ❌ 失败原因
- 待办数量: N 条(请假单 X、销假单 Y、补考勤单 Z)
- 每条: 申请人 | 表单类型 | 申请时间 | 主题
- 空列表时明确说明:"没有待审批表单",不再做多余尝试

## 日志查询示例

### 查询某一天的审批情况
```bash
grep "2026-08-09" ~/.hermes/logs/ehr_approval.log | jq '.approved_forms[]'
```

### 统计审批数量
```bash
grep "total_approved" ~/.hermes/logs/ehr_approval.log | awk -F'"' '{sum+=$4} END {print "总计审批数量:", sum}'
```

### 查看特定申请人的审批记录
```bash
grep "Jomar Apellido" ~/.hermes/logs/ehr_approval.log
```
