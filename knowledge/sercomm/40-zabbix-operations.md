# 40 — Zabbix 运维（升级/发现/vCenter/备份）

**来源**: zabbix-server-admin.md, zabbix-vmware-monitoring.md, zabbix-reset-discovered-host.md, zabbix_skill_upgrade_10.140.1.42_7.4.13.md, backup_zabbix_db_preupgrade_v3.sh

## 一、Zabbix Server 管理

### 1.1 版本检查
- **API 方式（推荐，无需 SSH）**：
  ```bash
  curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
    -H "Content-Type: application/json-rpc" \
    -d '{"jsonrpc":"2.0","method":"apiinfo.version","params":{},"id":1}'
  ```
  > **注意**：`apiinfo.version` 必须不带 `Authorization: Bearer` 头（7.4 实测）。其他所有 API 方法（如 `host.get`）都需要 Bearer 头，只有此方法是例外。

- **服务器端**：
  ```bash
  ssh -o ConnectTimeout=10 -o BatchMode=yes 10.140.1.42 "zabbix_server -V | head -2"
  ```

### 1.2 升级流程（7.4.x 补丁升级）
1. **备份数据库**：
   ```bash
   ssh -o ConnectTimeout=10 -o BatchMode=yes 10.140.1.42 \
     "mkdir -p /backup && mysqldump --databases zabbix --single-transaction > /backup/zabbix_$(date +%Y%m%d).sql && ls -lh /backup/"
   ```
2. **升级组件**：
   ```bash
   ssh -o ConnectTimeout=10 -o BatchMode=yes 10.140.1.42 "yum update 'zabbix-*'"
   ```
3. **重启服务**：
   ```bash
   ssh -o ConnectTimeout=10 -o BatchMode=yes 10.140.1.42 \
     "systemctl restart zabbix-server zabbix-agent nginx php-fpm && systemctl is-active zabbix-server zabbix-agent nginx php-fpm"
   ```
4. **验证**：
   - `zabbix_server -V` → 版本号应为 7.4.13
   - API `apiinfo.version` 返回新版本
   - 数据库 schema 自动升级（7.4.x 内补丁一般自动处理，server 启动时执行）
   - UI 正常、最新数据点持续更新（监控恢复）
   - 检查 `/var/log/zabbix/zabbix_server.log` 无升级错误

### 1.3 组件清单（rpm）

zabbix-server-mysql, zabbix-web-mysql, zabbix-agent, zabbix-get, zabbix-nginx-conf, zabbix-selinux-policy, zabbix-release, zabbix-sql-scripts, zabbix-web, zabbix-web-deps

### 1.4 风险与注意事项
- **CentOS Stream 9 用 `rpm -qa` 而非 `dpkg -l` 查包**
- **敏感配置脱敏**：查看 `/etc/zabbix/zabbix_server.conf` 中 DBPassword 时，先 `sed 's/DBPassword=.*/DBPassword=[REDACTED]/'` 再输出，密码不进终端/日志/回复
- **SSH 非交互**：一律 `-o ConnectTimeout=10 -o BatchMode=yes`，避免挂起等待密码
- **升级前必须备份 + 用户批准**：生产监控系统，违反会引发事故
- **yum repolist 可能 grep 不到 zabbix**（权限/输出差异），确认 repo 存在看 `rpm -qa | grep zabbix-release` 即可
- **同系列补丁升级（7.4.9→7.4.13）风险低**，但跨大版本（7.4→8.0）需查官方升级指南和 DB schema 变更，不能直接 yum update
- **apiinfo.version 是唯一不需要 Bearer 头的 API 方法**，带 header 反而报错；其他方法缺 header 也会报错。两者方向相反，容易混淆
- **MySQL 服务单元名是 `mysqld.service`（MySQL 8.4.10）**，不是 `mysql` 也不是 `mariadb`。`systemctl is-active mysql` 会返回 `inactive`（单元不存在），易误判数据库宕机。检查数据库一律用 `systemctl is-active mysqld` / `systemctl status mysqld`
- **SSH 连接已验证可用**（2026-07-31）：`ssh -o ConnectTimeout=10 -o BatchMode=yes 10.140.1.42` root 免密，hostname=spipzabbix，CentOS Stream 9。若用户反馈"iTerm2 能连/免密正常"，直接按此命令执行，不要反复怀疑 SSH 配置

---

## 二、Zabbix VMware 监控

### 2.1 认证与性能参数获取

```bash
# Step 0: 从统一凭据文件读取（不把密码写进命令/日志）
CREDS=$(cat ~/.hermes/secrets/zabbix_sercomm.txt)
ZBX_USER=$(grep '^username=' <<< "$CREDS" | cut -d= -f2)
ZBX_PASS=$(grep '^password=' <<< "$CREDS" | cut -d= -f2)

# Step 1: 登录获取 token
TOKEN=$(curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -d "{\"jsonrpc\":\"2.0\",\"method\":\"user.login\",\"params\":{\"username\":\"$ZBX_USER\",\"password\":\"$ZBX_PASS\"},\"id\":1}")

# Step 2: 验证 token 可用 (列出 host groups)
curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc":"2.0","method":"hostgroup.get","params":{"output":["groupid","name"]},"id":1}'
```

### 2.2 获取设备列表

```bash
# 获取所有VMware设备
curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc":"2.0","method":"host.get","params":{"groupids":["32","71","84","26","78","7","70","24","77","67"],"output":["hostid","name","status"],"selectInterfaces":["ip","dns"],"sortfield":"name"},"id":1}'
```

### 2.3 获取性能参数

```bash
# 获取指定设备的所有监控项
curl -sk -X POST https://spipzabbix.sercomm.com/api_jsonrpc.php \
  -H "Content-Type: application/json-rpc" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"jsonrpc":"2.0","method":"item.get","params":{"hostids":["<DEVICE_ID>"],"output":["itemid","name","key_","lastvalue","units","value_type"],"sortfield":"name"},"id":1}'
```

### 2.4 计算关键指标

```bash
# 计算CPU使用率
CPU_USAGE=$(echo "scale=2; $CPU_USAGE_VALUE / $CPU_CORES * 100" | bc)

# 计算内存使用率
MEMORY_USAGE=$(echo "scale=2; $MEMORY_USED / $MEMORY_TOTAL * 100" | bc)

# 计算磁盘IO
TOTAL_IO=$(echo "scale=2; $READ_IO + $WRITE_IO" | bc)

# 计算网络流量
TOTAL_TRAFFIC=$(echo "scale=2; $IN_TRAFFIC + $OUT_TRAFFIC" | bc)
```

### 2.5 性能指标说明

| 指标类型 | 监控项Key | 单位 | 说明 |
|-----------|-----------|------|------|
| CPU使用率 | `vmware.vm.cpu.usage.perf[...]` | % | CPU使用率百分比 |
| CPU使用量 | `vmware.vm.cpu.usage[...]` | Hz | CPU使用量（绝对值） |
| 内存使用率 | `vmware.vm.memory.usage[...]` | % | 主机内存使用率 |
| 内存使用量 | `vmware.vm.memory.size.usage.host[...]` | B | 主机内存使用量 |
| 磁盘读取 | `vmware.vm.vfs.dev.read[...]` | Bps | 磁盘读取速率 |
| 磁盘写入 | `vmware.vm.vfs.dev.write[...]` | Bps | 磁盘写入速率 |
| 网络流量 | `vmware.vm.net.if.in[...]` / `vmware.vm.net.if.out[...]` | Bps | 网络接收/发送速率 |
| 开机时间 | `vmware.vm.uptime[...]` | uptime | VM运行时间 |

### 2.6 使用示例

```bash
# 查询特定虚拟机的性能参数
python3 vm_performance.py R_IMD_HRFACEID_1.32

# 查询结果示例
找到虚拟机: R_IMD_HRFACEID_1.32 (ID: 13146)

=== 性能参数 ===
CPU使用率: 6.38 %
CPU使用量: 1906000000.0 Hz
内存使用率: 7.99 %
主机内存使用量: 25921847296.0 B
磁盘读取: 15360.0 Bps
磁盘写入: 0.0 Bps
网络接收: 130048.0 Bps
网络发送: 224256.0 Bps
开机时间: 70天 16小时 46分钟 5秒
```

---

## 三、Zabbix 发现主机重置

### 3.1 场景
在制造网络（如厂区 P/Q/R 站点）中，经常会遇到设备 IP 变更、换线或者初次发现时套错了模板的情况。Zabbix 的网络发现（Network Discovery）带有内部缓存，如果不做彻底清理，直接删除主机后，Zabbix 可能不会立刻重新触发“添加主机”的动作。

### 3.2 标准重置三步曲（Web 端操作）

1. **物理删除现有主机**：
   - 路径：登录主控台 (https://spipzabbix.sercomm.com) -> `Data collection` (或 `Configuration`) -> `Hosts`
   - 动作：勾选那台被自动发现并加入的主机，点击底部的 **Delete**。这会清空历史数据并解绑模板。
2. **停用并重启发现规则**：
   - 路径：`Data collection` -> `Discovery`
   - 动作：找到对应的扫描规则（比如扫 Q site 产线网段的规则）。点击绿色的 `Enabled` 让它变成红色的 `Disabled`，等待 10 秒钟，再点击重新启用。
   - 目的：这会重置该网段发现规则的内部计时器，强制下一次扫描成为“全量新扫描”。
3. **检查发现动作（Action）的条件**：
   - 路径：`Alerts` -> `Actions` -> `Discovery actions`
   - 动作：确保你的自动添加动作里，没有类似于 `Uptime/Downtime >= 1h` 这样苛刻的条件。如果有，刚重启的设备可能要等很久才会被重新添加。建议测试期间只保留 `Discovery status = Up` 和 `Service type = (你要的协议)`。

### 3.3 关联技能

- `zabbix-export-devices`: 从 Zabbix 导出设备信息
- `zabbix-problem-management`: 管理 Zabbix 问题
- `zabbix-server-admin`: 管理 Zabbix 服务器

### 3.4 参考文件

- `references/zabbix-vmware-monitoring.md`: 详细的监控流程和常见问题
- `scripts/check_vm_performance.py`: 检查虚拟机性能参数的 Python 脚本
- `templates/vm_performance_report_template.md`: 虚拟机性能参数报告模板
