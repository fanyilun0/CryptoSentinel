#!/bin/bash

###############################################################################
# 推文发送脚本
# 功能：从最新的建议文件中提取市场周期分析并发送推文
###############################################################################

# 设置脚本错误时退出
set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 切换到项目根目录
cd "$SCRIPT_DIR"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 显示脚本开始
log_info "==================================================="
log_info "推文发送脚本启动"
log_info "时间: $(date '+%Y-%m-%d %H:%M:%S')"
log_info "==================================================="

# 检查虚拟环境
if [ ! -d "venv" ]; then
    log_error "未找到虚拟环境目录 'venv'"
    log_info "请先运行: python3 -m venv venv"
    exit 1
fi

# 激活虚拟环境
log_info "激活虚拟环境..."
source venv/bin/activate

# 检查Python模块是否存在
if [ ! -f "src/utils/tweet_sender.py" ]; then
    log_error "未找到推文发送模块: src/utils/tweet_sender.py"
    exit 1
fi

# 设置推文API URL（可以通过环境变量覆盖）
TWEET_API_URL="${TWEET_API_URL:-http://localhost:8000/tweet}"
log_info "推文API URL: $TWEET_API_URL"

# 检查是否指定了特定的建议文件
if [ -n "$1" ]; then
    ADVICE_FILE="$1"
    log_info "使用指定的建议文件: $ADVICE_FILE"
    
    # 检查文件是否存在
    if [ ! -f "$ADVICE_FILE" ]; then
        log_error "指定的建议文件不存在: $ADVICE_FILE"
        exit 1
    fi
    
    # 执行Python脚本（指定文件）
    log_info "开始处理并发送推文..."
    python3 src/utils/tweet_sender.py --file "$ADVICE_FILE" --api-url "$TWEET_API_URL"
else
    # 使用最新的建议文件
    log_info "自动获取最新的建议文件..."
    
    # 执行Python脚本（自动获取最新文件）
    log_info "开始处理并发送推文..."
    python3 src/utils/tweet_sender.py --api-url "$TWEET_API_URL"
fi

# 检查执行结果
if [ $? -eq 0 ]; then
    log_info "==================================================="
    log_info "✅ 推文发送成功！"
    log_info "==================================================="
    exit 0
else
    log_error "==================================================="
    log_error "❌ 推文发送失败"
    log_error "==================================================="
    exit 1
fi

