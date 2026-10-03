# eHR系统自动审批自动化方案

## 概述

这个自动化方案每天早晚各一次自动登录Sercomm eHR系统，检查有无待审批单据，并自动审批所有单据。

## 系统架构

### 核心组件

1. **主审批脚本** (`ehr_cron_approve.sh`)
   - 简化的审批流程，专为cron任务设计
   - 自动登录、选择单据、批量审批
   - 生成详细日志

2. **完整审批脚本** (`ehr_auto_approve.sh`)
   - 包含完整错误处理和状态检查
   - 适合手动执行和调试

3. **管理脚本** (`ehr_manager.sh`)
   - 系统状态检查
   - 手动执行审批
   - 日志查看
   - Cron任务管理

4. **周报脚本** (`ehr_weekly_report.sh`)
   - 每周日生成审批汇总报告
   - 统计成功率、单据数量等

### 执行时间表

- **上午8:00** - 检查并审批前一天晚上到早上之间的单据
- **下午18:00** - 检查并审批当天白天产生的单据
- **周日7:00** - 生成上周审批汇总报告

## 安装和配置

### 1. 确保依赖就绪

```bash
# 检查凭据文件
ls -la ~/.hermes/secrets/ehr_sercomm.txt

# 确保权限正确
chmod 600 ~/.hermes/secrets/ehr_sercomm.txt

# 检查脚本权限
ls -la ~/.hermes/scripts/
```

### 2. 设置Cron任务

```bash
# 使用管理脚本设置cron任务
~/.hermes/scripts/ehr_manager.sh setup
```

### 3. 验证安装

```bash
# 检查系统状态
~/.hermes/scripts/ehr_manager.sh status

# 查看最近日志
~/.hermes/scripts/ehr_manager.sh logs
```

## 使用方法

### 日常管理

```bash
# 检查系统状态
ehr_manager.sh status

# 手动执行审批（如需要）
ehr_manager.sh manual

# 查看最近的审批日志
ehr_manager.sh logs

# 生成测试报告
ehr_manager.sh report
```

### Cron任务管理

```bash
# 查看当前cron任务
crontab -l

# 移除cron任务
ehr_manager.sh remove

# 重新设置cron任务
ehr_manager.sh setup
```

### 日志查看

```bash
# 查看所有日志文件
ls -la ~/.hermes/logs/

# 查看最近的日志
ehr_manager.sh logs

# 查看特定日期的日志
cat ~/.hermes/logs/ehr_cron_20260804_*.log
```

## 文件结构

```
~/.hermes/
├── scripts/
│   ├── ehr_cron_approve.sh      # 主要的cron审批脚本
│   ├── ehr_auto_approve.sh      # 完整审批脚本
│   ├── ehr_weekly_report.sh    # 周报生成脚本
│   └── ehr_manager.sh          # 管理脚本
├── secrets/
│   └── ehr_sercomm.txt         # eHR系统凭据
└── logs/
    ├── ehr_cron_*.log          # 审批任务日志
    └── ehr_weekly_report_*.txt # 周报文件
```

## 配置文件

### 凭据文件 (`~/.hermes/secrets/ehr_sercomm.txt`)

```
username=2013444
password=Tina@2025100200
```

**重要**: 确保文件权限为600，密码永不写入脚本正文。

### Cron配置 (`~/.hermes/cron/ehr_crontab.conf`)

包含所有cron任务的配置详情。

## 工作流程

### 自动审批流程

1. **触发时间** - 上午8:00或下午18:00
2. **登录系统** - 使用保存的凭据登录eHR
3. **进入审批页面** - 导航到审批页面
4. **选择单据** - 自动选择所有待审批单据
5. **批量审批** - 点击Approve按钮审批所有单据
6. **记录日志** - 记录执行结果和状态
7. **生成报告** - 如有需要生成详细报告

### 错误处理

- **登录失败**: 记录错误并跳过本次执行
- **无单据**: 记录正常状态，不执行审批
- **审批失败**: 记录错误状态供后续检查
- **网络问题**: 自动重试机制

## 监控和维护

### 日常检查

```bash
# 检查系统状态
ehr_manager.sh status

# 查看最近的执行日志
ehr_manager.sh logs

# 检查cron任务
crontab -l
```

### 定期维护

1. **每周检查** - 查看周报，确认系统正常运行
2. **每月清理** - 清理旧的日志文件
3. **凭据更新** - 如密码变更，及时更新凭据文件
4. **脚本更新** - 根据系统变化更新脚本

### 故障排除

常见问题及解决方案：

1. **登录失败**
   - 检查凭据文件是否正确
   - 验证网络连接
   - 检查eHR系统是否正常

2. **单据无法选择**
   - 检查页面元素是否有变化
   - 更新脚本中的元素定位
   - 查看浏览器控制台错误

3. **审批失败**
   - 检查单据状态是否允许审批
   - 验证审批流程是否正常
   - 查看详细日志

## 安全注意事项

1. **凭据安全**
   - 密码永不写入脚本正文
   - 凭据文件权限必须为600
   - 定期检查文件完整性

2. **操作安全**
   - 所有操作遵循"只查不改"原则
   - 审批前确认单据信息
   - 保留操作日志供审计

3. **系统安全**
   - 确保脚本来源可信
   - 定期更新脚本
   - 监控异常操作

## 扩展功能

### 自定义配置

可以通过修改脚本中的配置变量来自定义行为：

- `EHR_URL` - eHR系统登录地址
- `EHR_APPROVE_URL` - 审批页面地址
- `CREDENTIALS_FILE` - 凭据文件路径
- `LOG_DIR` - 日志目录路径

### 邮件通知

可以扩展脚本以包含邮件通知功能：

- 审批成功/失败通知
- 异常情况报警
- 定期状态报告

### 集成其他系统

可以集成到更大的自动化系统中：

- 与HR系统同步
- 与项目管理工具集成
- 与监控系统集成

## 版本历史

- **v1.0.0** (2026-08-04) - 初始版本
  - 基本的自动审批功能
  - Cron任务设置
  - 日志记录和报告生成

## 联系信息

- 作者: Jesse Xia
- 创建日期: 2026-08-04
- 更新日期: 2026-08-04

---

**注意**: 此系统专为Sercomm eHR设计，如需在其他系统使用，请相应调整配置和脚本。