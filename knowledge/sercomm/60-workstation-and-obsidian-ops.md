# 60 — 工作站与 Obsidian 多端运维

**来源**: obsidian-vault-relocate.md, obsidian_macos_ios_sync_guide.md, macos-copy-rpm-to-linux.md, macos-detect-remote-linux-os.md, linux-kernel-version-identification.md

## 一、Obsidian 多端同步方案

### 1.1 iCloud 同步（最省心方案）

```bash
# macOS 端
cd ~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/<你的仓库名称>

# iOS 端
# 在 Obsidian 中新建本地 Vault（不要勾选 Store in iCloud），然后在 Working Copy 中 Clone 你的 GitHub 仓库，并设置文件夹同步
```

### 1.2 Git + Working Copy（工程师推荐方案）

```bash
# macOS 端
cd ~/Documents/ObsidianVault
git init
git remote add origin git@github.com:yourname/your-repo.git
git add .
git commit -m "Initial commit"
git branch -M main
git push -u origin main

# iOS 端
# 在 Obsidian 中新建本地 Vault（不要勾选 Store in iCloud），然后在 Working Copy 中 Clone 你的 GitHub 仓库，并设置文件夹同步
```

### 1.3 选型建议
- 如果你的笔记体量不大、插件数量少，且主要在 Apple 生态内做即时记录，**优先使用 iCloud**
- 如果你有代码块、自动化脚本管理需求，需要严格的版本历史，或者后续可能扩展到 Linux / Windows 办公环境，**果断上 Git 方案**

---

## 二、macOS 与 Linux 文件传输

### 2.1 复制 RPM 到远程 Linux

```bash
# macOS 端
scp /本地完整路径/falcon-sensor-7.38.0-19102.el7.x86_64.rpm root@<服务器IP>:/root/

# 当前目录用法
scp ./falcon-sensor-7.38.0-19102.el7.x86_64.rpm root@<服务器IP>:/root/

# 指定 SSH 端口
scp -P 2222 ./falcon-sensor-*.rpm root@<服务器IP>:/root/

# 带进度与完整性校验
scp -v ./falcon-sensor-*.rpm root@<服务器IP>:/root/
shasum -a 256 ./falcon-sensor-*.rpm
ssh root@<服务器IP> 'sha256sum /root/falcon-sensor-*.rpm'

# 大文件或不稳定网络
rsync -avP -e 'ssh -p 22' ./falcon-sensor-*.rpm root@<服务器IP>:/root/
```

### 2.2 检测远程 Linux 发行版

```bash
# macOS 端
ssh root@<服务器IP> '
  echo "=== OS ==="
  cat /etc/os-release 2>/dev/null || true
  cat /etc/redhat-release 2>/dev/null || true
  echo "=== Kernel ==="
  uname -r
  echo "=== Kernel RPM ==="
  rpm -q kernel 2>/dev/null || true
'
```

### 2.3 Linux 内核版本识别

```bash
# macOS 端
ssh root@<服务器IP> 'uname -a'
```

> `uname -a` 只能确认内核构建标识，不能可靠确认完整发行版名称和版本。
> 内核：5.4.191
> 发行版/兼容目标标识：el7，表示 Enterprise Linux 7 ABI/生态（RHEL 7/CentOS 7 兼容）
> 架构：x86_64
> 构建时间：2022-12-12 UTC
> 重点：官方 RHEL/CentOS 7 的常见内核基线是 3.10；5.4.x 加 `.el7` 说明很可能是第三方/定制内核，或使用 EL7 用户态搭配较新内核，并非标准原生 CentOS 7 内核包。
> 准确确认 OS 的命令：
> ```bash
> cat /etc/os-release
> cat /etc/redhat-release
> rpm -q --whatprovides /etc/redhat-release
> rpm -q kernel
> ```

---

## 三、Obsidian 仓库迁移

### 3.1 迁移到新物理位置

```bash
# macOS 端
# 完全退出 Obsidian，避免同步或索引过程中产生文件不一致
# 在 Finder 中移动整个 Vault 根目录，而不是只移动 Markdown 文件。必须包含隐藏目录 `.obsidian`
# 打开 Obsidian，选择“打开其他仓库” -> “打开文件夹作为仓库”，选择新路径下的 Vault 根目录
# 确认笔记、图片附件、主题、插件、工作区正常
# 一切确认后再删除旧目录副本；若是移动操作则无需清理
```

### 3.2 跨磁盘和同步注意事项

- 跨磁盘时优先复制、验证、再删除旧库，比直接剪切更安全
- Obsidian Sync、iCloud Drive、OneDrive、Dropbox、Git 等同步工具应先暂停或等待同步完成，再迁移
- 使用相对链接、相对附件路径通常无需修改；使用绝对路径、脚本或外部工具引用旧路径时需全局搜索旧路径并更新
- 不建议用符号链接作为长期方案，部分同步、移动端和插件可能处理不一致

### 3.3 回滚

若新位置打开异常：关闭 Obsidian，使用旧库副本重新打开；不要在未确认前删除旧目录
