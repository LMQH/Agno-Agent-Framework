"""
Database Configuration Module
数据库相关配置管理
"""

import os
from typing import Dict, Any
from pathlib import Path


class DatabaseConfig:
    """数据库配置管理类"""

    def __init__(self):
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """从环境变量加载数据库配置（Agno专用数据库）"""
        return {
            "host": os.getenv("AGNO_MYSQL_HOST", os.getenv("MYSQL_HOST", "localhost")),
            "port": int(os.getenv("AGNO_MYSQL_PORT", os.getenv("MYSQL_PORT", "3306"))),
            "user": os.getenv("AGNO_MYSQL_USER", os.getenv("MYSQL_USER", "root")),
            "password": os.getenv("AGNO_MYSQL_PASSWORD", os.getenv("MYSQL_PASSWORD", "password")),
            "database": os.getenv("AGNO_MYSQL_DB_SCHEMA", os.getenv("AGNO_MYSQL_DATABASE", os.getenv("MYSQL_DATABASE", "agno_backend"))),
            "charset": "utf8mb4",
            "pool_size": int(os.getenv("MYSQL_POOL_SIZE", "20")),
            "pool_recycle": int(os.getenv("MYSQL_POOL_RECYCLE", "3600")),
            "echo": os.getenv("MYSQL_ECHO", "false").lower() == "true",
        }

    @property
    def connection_string(self) -> str:
        """获取数据库连接字符串"""
        config = self._config
        return f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}"

    @property
    def database_url(self) -> str:
        """获取完整的数据库URL（包含数据库名）"""
        config = self._config
        return f"{self.connection_string}/{config['database']}?charset={config['charset']}"

    @property
    def pool_config(self) -> Dict[str, Any]:
        """获取连接池配置"""
        config = self._config
        return {
            "pool_size": config["pool_size"],
            "pool_recycle": config["pool_recycle"],
            "echo": config["echo"],
        }

    def get_config(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self._config.copy()


# 全局配置实例
db_config = DatabaseConfig()


def get_database_config() -> DatabaseConfig:
    """获取数据库配置实例"""
    return db_config
