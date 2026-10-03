#!/bin/bash
# Zabbix VMware 快速检查脚本

# 设置脚本路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/check_vm_performance.py"

# 检查Python脚本是否存在
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "错误: Python脚本不存在: $PYTHON_SCRIPT"
    exit 1
fi

# 检查凭据文件是否存在
CREDENTIALS_FILE="$HOME/.hermes/secrets/zabbix_sercomm.txt"
if [ ! -f "$CREDENTIALS_FILE" ]; then
    echo "错误: 凭据文件不存在: $CREDENTIALS_FILE"
    echo "请创建该文件并包含 username= 和 password= 行"
    exit 1
fi

# 显示帮助信息
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --type TYPE     设备类型: vm (虚拟机), hypervisor (ESXi主机), vcenter (vCenter), all (默认)"
    echo "  --name NAME     指定设备名称"
    echo "  --format JSON   输出格式: text (默认), json"
    echo "  --limit NUM     返回结果数量限制 (默认: 10)"
    echo "  --help, -h      显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 --type vm --limit 5"
    echo "  $0 --name 'R_IMD_HRFACEID_1.32'"
    echo "  $0 --type hypervisor --format json"
    exit 0
fi

# 构建Python脚本参数
PYTHON_ARGS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --type)
            PYTHON_ARGS="$PYTHON_ARGS --device-type $2"
            shift 2
            ;;
        --name)
            PYTHON_ARGS="$PYTHON_ARGS --device-name \"$2\""
            shift 2
            ;;
        --format)
            PYTHON_ARGS="$PYTHON_ARGS --format $2"
            shift 2
            ;;
        --limit)
            PYTHON_ARGS="$PYTHON_ARGS --limit $2"
            shift 2
            ;;
        *)
            echo "未知选项: $1"
            echo "使用 --help 查看帮助信息"
            exit 1
            ;;
    esac
done

# 执行Python脚本
echo "正在查询 Zabbix VMware 设备性能参数..."
echo "设备类型: $(echo "$PYTHON_ARGS" | grep -o -- '--device-type [^ ]*' | cut -d' ' -f2 || echo 'all')"
echo "----------------------------------------"
python3 $PYTHON_SCRIPT $PYTHON_ARGS
