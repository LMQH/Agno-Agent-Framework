"""
Database Models Module
数据库模型定义和基础类
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON

Base = declarative_base()


class BaseModel(Base):
    """基础模型类"""
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def update_from_dict(self, data: Dict[str, Any]):
        """从字典更新属性"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)


# 示例模型 - 用户表
class User(BaseModel):
    """用户模型"""
    __tablename__ = "users"

    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime, nullable=True)
    profile_data = Column(JSON, nullable=True)  # 存储额外用户信息

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"


# 示例模型 - API请求日志
class APIRequestLog(BaseModel):
    """API请求日志模型"""
    __tablename__ = "api_request_logs"

    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    user_id = Column(Integer, nullable=True)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text, nullable=True)
    request_data = Column(JSON, nullable=True)
    response_data = Column(JSON, nullable=True)
    status_code = Column(Integer, nullable=False)
    processing_time = Column(Integer, nullable=True)  # 处理时间（毫秒）
    error_message = Column(Text, nullable=True)

    def __repr__(self):
        return f"<APIRequestLog(id={self.id}, endpoint={self.endpoint}, status_code={self.status_code})>"


# 示例模型 - 系统配置
class SystemConfig(BaseModel):
    """系统配置模型"""
    __tablename__ = "system_configs"

    config_key = Column(String(100), unique=True, nullable=False)
    config_value = Column(JSON, nullable=False)
    description = Column(Text, nullable=True)
    is_system = Column(Boolean, default=False, nullable=False)  # 是否为系统级配置

    def __repr__(self):
        return f"<SystemConfig(id={self.id}, key={self.config_key})>"


# 所有模型的集合，方便导入
__all__ = [
    "Base",
    "BaseModel",
    "User",
    "APIRequestLog",
    "SystemConfig",
]
