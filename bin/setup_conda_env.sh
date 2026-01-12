#!/bin/bash
# ============================================================================
# Agno Multi Agent Framework - Conda 环境配置脚本
# ============================================================================
# 功能说明：
# 1. 创建名为 agno_multi_agent_play 的 conda 虚拟环境
# 2. 配置 Python 3.12
# 3. 根据 requirements.txt 安装所有依赖包
# 4. 验证环境配置是否正确
# ============================================================================

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 环境名称
ENV_NAME="agno_multi_agent_play"
PYTHON_VERSION="3.12"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 检查 conda 是否安装
check_conda() {
    log_info "检查 conda 是否已安装..."

    if command_exists conda; then
        log_success "conda 已安装"
        # 显示 conda 版本
        conda --version
        return 0
    elif command_exists mamba; then
        log_warning "检测到 mamba，将使用 mamba 替代 conda"
        # 设置使用 mamba
        CONDA_CMD="mamba"
        log_success "mamba 已安装"
        mamba --version
        return 0
    else
        log_error "未检测到 conda 或 mamba！"
        echo ""
        echo "请先安装 conda 或 miniconda："
        echo "1. Miniconda (推荐): https://docs.conda.io/en/latest/miniconda.html"
        echo "2. Anaconda: https://www.anaconda.com/products/distribution"
        echo "3. Mambaforge: https://github.com/conda-forge/miniforge#mambaforge"
        echo ""
        echo "安装完成后，请重新运行此脚本。"
        exit 1
    fi
}

# 检查 Python 版本兼容性
check_python_compatibility() {
    log_info "检查系统 Python 版本..."

    if command_exists python3; then
        PYTHON_VERSION_SYS=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
        log_info "系统 Python 版本: $PYTHON_VERSION_SYS"

        # 检查是否满足最低要求
        if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 12, 0) else 1)"; then
            log_success "系统 Python 版本满足要求 (>= 3.12.0)"
        else
            log_warning "系统 Python 版本较低，但 conda 将使用指定版本"
        fi
    else
        log_warning "未检测到 python3，但 conda 环境会安装指定版本"
    fi
}

# 检查环境是否已存在
check_env_exists() {
    log_info "检查 conda 环境 '$ENV_NAME' 是否已存在..."

    if conda env list | grep -q "^$ENV_NAME "; then
        log_warning "环境 '$ENV_NAME' 已存在"
        echo ""
        read -p "是否要重新创建环境？(y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "删除现有环境..."
            conda env remove -n "$ENV_NAME" -y
            return 1
        else
            log_info "使用现有环境"
            return 0
        fi
    else
        log_info "环境 '$ENV_NAME' 不存在，将创建新环境"
        return 1
    fi
}

# 创建 conda 环境
create_conda_env() {
    log_info "创建 conda 环境 '$ENV_NAME' (Python $PYTHON_VERSION)..."

    if [ "$CONDA_CMD" = "mamba" ]; then
        mamba create -n "$ENV_NAME" python="$PYTHON_VERSION" -y
    else
        conda create -n "$ENV_NAME" python="$PYTHON_VERSION" -y
    fi

    if [ $? -eq 0 ]; then
        log_success "conda 环境创建成功"
    else
        log_error "conda 环境创建失败"
        exit 1
    fi
}

# 激活环境并安装依赖
install_dependencies() {
    log_info "激活环境并安装依赖包..."

    # 激活环境
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate "$ENV_NAME"

    if [ $? -ne 0 ]; then
        log_error "无法激活 conda 环境"
        exit 1
    fi

    log_success "环境激活成功"

    # 检查 requirements.txt 文件
    REQUIREMENTS_FILE="$PROJECT_ROOT/requirements.txt"
    if [ ! -f "$REQUIREMENTS_FILE" ]; then
        log_error "未找到 requirements.txt 文件: $REQUIREMENTS_FILE"
        exit 1
    fi

    log_info "开始安装依赖包..."
    log_info "这可能需要几分钟时间，请耐心等待..."

    # 安装 pip 工具
    pip install --upgrade pip

    # 安装依赖包
    pip install -r "$REQUIREMENTS_FILE"

    if [ $? -eq 0 ]; then
        log_success "依赖包安装完成"
    else
        log_error "依赖包安装失败"
        log_info "您可以稍后手动运行: pip install -r requirements.txt"
    fi
}

# 验证环境配置
verify_environment() {
    log_info "验证环境配置..."

    # 激活环境
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate "$ENV_NAME"

    # 检查 Python 版本
    PYTHON_VER=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
    log_info "Python 版本: $PYTHON_VER"

    if [[ $PYTHON_VER == 3.12* ]]; then
        log_success "Python 版本验证通过"
    else
        log_warning "Python 版本可能不匹配: $PYTHON_VER"
    fi

    # 检查关键依赖包
    echo ""
    log_info "检查关键依赖包:"

    PACKAGES=("fastapi" "uvicorn" "agno" "sqlalchemy" "pydantic" "httpx")
    MISSING_PACKAGES=()

    for package in "${PACKAGES[@]}"; do
        if python -c "import $package" 2>/dev/null; then
            echo -e "  ${GREEN}✓${NC} $package"
        else
            echo -e "  ${RED}✗${NC} $package"
            MISSING_PACKAGES+=("$package")
        fi
    done

    echo ""
    if [ ${#MISSING_PACKAGES[@]} -eq 0 ]; then
        log_success "所有关键依赖包检查通过"
    else
        log_warning "以下依赖包可能缺失: ${MISSING_PACKAGES[*]}"
        log_info "请手动检查: pip list | grep -E '($(IFS=\|; echo "${PACKAGES[*]}"))'"
    fi
}

# 显示使用说明
show_usage() {
    echo ""
    echo "================================================================="
    echo "🎉 Conda 环境配置完成！"
    echo "================================================================="
    echo ""
    echo "环境名称: $ENV_NAME"
    echo "Python 版本: $PYTHON_VERSION"
    echo ""
    echo "激活环境命令:"
    echo "  conda activate $ENV_NAME"
    echo ""
    echo "常用命令:"
    echo "  # 激活环境"
    echo "  conda activate $ENV_NAME"
    echo ""
    echo "  # 退出环境"
    echo "  conda deactivate"
    echo ""
    echo "  # 删除环境"
    echo "  conda env remove -n $ENV_NAME -y"
    echo ""
    echo "  # 查看环境列表"
    echo "  conda env list"
    echo ""
    echo "项目使用:"
    echo "  # 激活环境后，进入项目目录"
    echo "  cd $PROJECT_ROOT"
    echo ""
    echo "  # 运行环境检查"
    echo "  python scripts/check_python_version.py"
    echo ""
    echo "  # 创建环境配置文件"
    echo "  python scripts/create_env_files.py"
    echo ""
    echo "  # 启动开发服务"
    echo "  python start.py dev --reload"
    echo ""
    echo "================================================================="
}

# 主函数
main() {
    echo "================================================================="
    echo "🚀 Agno Multi Agent Framework - Conda 环境配置"
    echo "================================================================="
    echo ""

    # 检查 conda
    check_conda

    # 检查 Python 兼容性
    check_python_compatibility

    # 检查环境是否存在
    if check_env_exists; then
        # 环境已存在，跳过创建，直接验证
        log_info "验证现有环境..."
        verify_environment
        show_usage
        return 0
    fi

    # 创建环境
    create_conda_env

    # 安装依赖
    install_dependencies

    # 验证环境
    verify_environment

    # 显示使用说明
    show_usage

    log_success "环境配置完成！"
}

# 运行主函数
main "$@"
