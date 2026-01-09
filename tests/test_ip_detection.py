#!/usr/bin/env python3
"""
测试IP环境检测功能
"""

import sys
import logging
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

from src.utils.config_loader import ConfigLoader

def test_ip_detection():
    """测试IP环境检测"""
    print("=" * 60)
    print("IP环境检测测试")
    print("=" * 60)
    
    config_loader = ConfigLoader()
    
    # 显示配置的IP列表
    print("\n配置的IP列表:")
    print(f"  生产服务器: {config_loader.PROD_LIST}")
    print(f"  预演服务器: {config_loader.PREVIEW_LIST}")
    print(f"  开发服务器: {config_loader.DEV_LIST}")
    
    # 获取本机IP
    local_ip = ConfigLoader.get_local_ip()
    print(f"\n检测到的本机IP: {local_ip}")
    
    # 检测环境
    detected_env = config_loader.detect_env_by_ip()
    print(f"检测到的环境: {detected_env}")
    
    # 测试特定IP
    print("\n测试特定IP:")
    test_ips = [
        "172.16.64.100",  # 生产
        "172.16.64.104",  # 预演
        "127.0.0.1",      # 本地
        "192.168.1.10",   # 其他（应该返回dev）
    ]
    
    for test_ip in test_ips:
        env = config_loader.detect_env_by_ip(test_ip)
        print(f"  {test_ip:15} -> {env}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_ip_detection()

