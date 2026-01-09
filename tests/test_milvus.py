#!/usr/bin/env python3
"""
测试 Milvus 向量数据库连接功能
"""

import sys
import logging
import os
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

# 加载环境配置
from dotenv import load_dotenv
from src.utils.config_loader import get_config_loader

# 加载环境配置
config_loader = get_config_loader()
env_type = config_loader.load_config(
    auto_detect_ip=True,
    project_root=project_root
)

from src.vector.connection import (
    get_milvus_client,
    check_milvus_connection,
    close_milvus_connection,
    milvus_connection
)
from src.vector.query_tools import get_vector_tools


def test_milvus_connection():
    """测试 Milvus 连接"""
    print("=" * 60)
    print("Milvus 向量数据库连接测试")
    print("=" * 60)
    
    # 显示配置信息
    print("\nMilvus 配置信息:")
    print(f"  主机: {os.getenv('MILVUS_HOST', 'localhost')}")
    print(f"  端口: {os.getenv('MILVUS_PORT', '19530')}")
    print(f"  数据库: {os.getenv('MILVUS_DATABASE', 'default')}")
    if os.getenv('MILVUS_USER'):
        print(f"  用户: {os.getenv('MILVUS_USER')}")
    else:
        print("  用户: 未配置（使用默认）")
    
    print("\n" + "-" * 60)
    
    # 测试 1: 连接测试
    print("\n[测试 1] 连接测试")
    try:
        client = get_milvus_client()
        print("  ✓ 连接成功")
    except Exception as e:
        print(f"  ✗ 连接失败: {e}")
        return False
    
    # 测试 2: 健康检查
    print("\n[测试 2] 健康检查")
    try:
        is_healthy = check_milvus_connection()
        if is_healthy:
            print("  ✓ 健康检查通过")
        else:
            print("  ✗ 健康检查失败")
            return False
    except Exception as e:
        print(f"  ✗ 健康检查异常: {e}")
        return False
    
    # 测试 3: 数据库信息
    print("\n[测试 3] 数据库信息")
    try:
        database = milvus_connection.database
        print(f"  当前数据库: {database}")
        print("  ✓ 数据库信息获取成功")
    except Exception as e:
        print(f"  ✗ 获取数据库信息失败: {e}")
    
    # 测试 4: 列出集合
    print("\n[测试 4] 列出集合")
    try:
        vector_tools = get_vector_tools()
        collections = vector_tools.list_collections()
        print(f"  找到 {len(collections)} 个集合:")
        for collection_name in collections:
            try:
                count = vector_tools.get_collection_count(collection_name)
                print(f"    - {collection_name} ({count} 个实体)")
            except Exception:
                print(f"    - {collection_name}")
        print("  ✓ 列出集合成功")
    except Exception as e:
        print(f"  ✗ 列出集合失败: {e}")
    
    # 测试 5: 连接状态
    print("\n[测试 5] 连接状态")
    try:
        print(f"  连接状态: {'已连接' if milvus_connection._connected else '未连接'}")
        print("  ✓ 连接状态检查成功")
    except Exception as e:
        print(f"  ✗ 检查连接状态失败: {e}")
    
    print("\n" + "=" * 60)
    print("所有测试完成")
    print("=" * 60)
    
    return True


def test_milvus_cleanup():
    """清理测试连接"""
    try:
        close_milvus_connection()
        print("\n✓ 已关闭 Milvus 连接")
    except Exception as e:
        print(f"\n✗ 关闭连接失败: {e}")


if __name__ == "__main__":
    try:
        success = test_milvus_connection()
        if success:
            print("\n✓ 所有测试通过")
        else:
            print("\n✗ 部分测试失败")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 测试执行异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # 清理连接
        test_milvus_cleanup()

