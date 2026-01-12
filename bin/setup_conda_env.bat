@echo off
REM ============================================================================
REM Agno Multi Agent Framework - Conda 环境配置脚本 (Windows)
REM ============================================================================
REM 功能说明：
REM 1. 创建名为 agno_multi_agent_play 的 conda 虚拟环境
REM 2. 配置 Python 3.12
REM 3. 根据 requirements.txt 安装所有依赖包
REM 4. 验证环境配置是否正确
REM ============================================================================

setlocal enabledelayedexpansion

REM 设置颜色 (如果支持)
set "GREEN=[OK]"
set "RED=[ERROR]"
set "YELLOW=[WARNING]"
set "BLUE=[INFO]"

REM 环境名称
set "ENV_NAME=agno_multi_agent_play"
set "PYTHON_VERSION=3.12"

REM 获取项目根目录
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

REM 规范化路径
for %%i in ("%PROJECT_ROOT%") do set "PROJECT_ROOT=%%~fi"

echo ===================================================================
echo 🚀 Agno Multi Agent Framework - Conda 环境配置 (Windows)
echo ===================================================================
echo.

REM 检查 conda 是否安装
echo %BLUE% 检查 conda 是否已安装...
where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo %RED% 未检测到 conda！
    echo.
    echo 请先安装 conda 或 miniconda：
    echo 1. Miniconda (推荐): https://docs.conda.io/en/latest/miniconda.html
    echo 2. Anaconda: https://www.anaconda.com/products/distribution
    echo.
    echo 安装完成后，请重新运行此脚本。
    pause
    exit /b 1
)

echo %GREEN% conda 已安装
conda --version
echo.

REM 检查环境是否已存在
echo %BLUE% 检查 conda 环境 '%ENV_NAME%' 是否已存在...
conda env list | findstr /B "%ENV_NAME% " >nul 2>nul
if %errorlevel% equ 0 (
    echo %YELLOW% 环境 '%ENV_NAME%' 已存在
    echo.
    set /p "choice=是否要重新创建环境？(y/N): "
    if /i "!choice!"=="y" (
        echo %BLUE% 删除现有环境...
        conda env remove -n %ENV_NAME% -y
    ) else (
        echo %BLUE% 使用现有环境
        goto :verify_env
    )
)

REM 创建 conda 环境
echo %BLUE% 创建 conda 环境 '%ENV_NAME%' (Python %PYTHON_VERSION%)...
conda create -n %ENV_NAME% python=%PYTHON_VERSION% -y

if %errorlevel% neq 0 (
    echo %RED% conda 环境创建失败
    pause
    exit /b 1
)

echo %GREEN% conda 环境创建成功
echo.

REM 激活环境并安装依赖
echo %BLUE% 激活环境并安装依赖包...
call conda activate %ENV_NAME%

if %errorlevel% neq 0 (
    echo %RED% 无法激活 conda 环境
    pause
    exit /b 1
)

echo %GREEN% 环境激活成功
echo.

REM 检查 requirements.txt 文件
if not exist "%PROJECT_ROOT%\requirements.txt" (
    echo %RED% 未找到 requirements.txt 文件: %PROJECT_ROOT%\requirements.txt
    pause
    exit /b 1
)

echo %BLUE% 开始安装依赖包...
echo %BLUE% 这可能需要几分钟时间，请耐心等待...
echo.

REM 升级 pip
python -m pip install --upgrade pip

REM 安装依赖包
pip install -r "%PROJECT_ROOT%\requirements.txt"

if %errorlevel% neq 0 (
    echo %RED% 依赖包安装失败
    echo %BLUE% 您可以稍后手动运行: pip install -r requirements.txt
) else (
    echo %GREEN% 依赖包安装完成
)

echo.

:verify_env
REM 验证环境配置
echo %BLUE% 验证环境配置...
call conda activate %ENV_NAME%

REM 检查 Python 版本
for /f "tokens=*" %%i in ('python -c "import sys; print(f\"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}\")"') do set PYTHON_VER=%%i

echo %BLUE% Python 版本: %PYTHON_VER%

echo %PYTHON_VER% | findstr /B "3.12" >nul
if %errorlevel% equ 0 (
    echo %GREEN% Python 版本验证通过
) else (
    echo %YELLOW% Python 版本可能不匹配: %PYTHON_VER%
)

echo.
echo %BLUE% 检查关键依赖包:
echo.

REM 检查关键依赖包
set PACKAGES=fastapi uvicorn agno sqlalchemy pydantic httpx

for %%p in (%PACKAGES%) do (
    python -c "import %%p" 2>nul
    if !errorlevel! equ 0 (
        echo   [OK] %%p
    ) else (
        echo   [MISSING] %%p
    )
)

echo.
echo ===================================================================
echo 🎉 Conda 环境配置完成！
echo ===================================================================
echo.
echo 环境名称: %ENV_NAME%
echo Python 版本: %PYTHON_VERSION%
echo.
echo 激活环境命令:
echo   conda activate %ENV_NAME%
echo.
echo 常用命令:
echo   # 激活环境
echo   conda activate %ENV_NAME%
echo.
echo   # 退出环境
echo   conda deactivate
echo.
echo   # 删除环境
echo   conda env remove -n %ENV_NAME% -y
echo.
echo   # 查看环境列表
echo   conda env list
echo.
echo 项目使用:
echo   # 激活环境后，进入项目目录
echo   cd %PROJECT_ROOT%
echo.
echo   # 运行环境检查
echo   python scripts\check_python_version.py
echo.
echo   # 创建环境配置文件
echo   python scripts\create_env_files.py
echo.
echo   # 启动开发服务
echo   python start.py dev --reload
echo.
echo ===================================================================

echo %GREEN% 环境配置完成！
echo.
pause
