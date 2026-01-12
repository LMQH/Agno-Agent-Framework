#!/usr/bin/env python3
"""
Python 版本检查脚本
检查当前 Python 版本是否满足项目要求 (Python 3.12+)
"""

import sys
import os
from pathlib import Path

REQUIRED_PYTHON_VERSION = (3, 12, 0)
REQUIRED_PYTHON_STRING = "3.12.0"

def check_python_version():
    """检查 Python 版本"""
    current_version = sys.version_info
    current_string = f"{current_version.major}.{current_version.minor}.{current_version.micro}"

    print("Python 版本检查")
    print(f"当前版本: Python {current_string}")
    print(f"要求版本: Python {REQUIRED_PYTHON_STRING}+")

    if current_version < REQUIRED_PYTHON_VERSION:
        print("[ERROR] Python 版本不符合要求！")
        print(f"请升级到 Python {REQUIRED_PYTHON_STRING} 或更高版本。")
        print("\n推荐的安装方式:")
        print("1. 使用 pyenv:")
        print("   pyenv install 3.12.0")
        print("   pyenv global 3.12.0")
        print("\n2. 使用 conda:")
        print("   conda create -n agno python=3.12")
        print("   conda activate agno")
        print("\n3. 下载安装包:")
        print("   https://www.python.org/downloads/")
        return False
    else:
        print("[OK] Python 版本检查通过！")
        return True

def check_dependencies():
    """检查关键依赖是否可用"""
    required_modules = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pydantic',
        'httpx'
    ]

    print("\n依赖包检查:")
    missing_modules = []

    for module in required_modules:
        try:
            __import__(module)
            print(f"[OK] {module}")
        except ImportError:
            print(f"[MISSING] {module}")
            missing_modules.append(module)

    if missing_modules:
        print(f"\n[WARNING] 缺少 {len(missing_modules)} 个依赖包")
        print("请运行以下命令安装:")
        print("pip install -r requirements.txt")
        return False
    else:
        print("\n[OK] 所有关键依赖包已安装")
        return True

if __name__ == "__main__":
    print("=" * 50)
    print("Agno Multi Agent Framework - 环境检查")
    print("=" * 50)

    # 检查 Python 版本
    version_ok = check_python_version()

    # 检查依赖
    deps_ok = check_dependencies()

    print("\n" + "=" * 50)
    if version_ok and deps_ok:
        print("[SUCCESS] 环境检查通过！可以开始开发。")
        print("\n接下来:")
        print("1. 创建环境配置文件: python scripts/create_env_files.py")
        print("2. 启动开发服务: python start.py dev --reload")
    else:
        print("[ERROR] 环境检查失败！请解决上述问题后重试。")
        sys.exit(1)
