"""
API Models
API 请求和响应模型定义
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class HealthCheckResponse(BaseModel):
    """健康检查响应"""
    status: str
    service: str
    database_connected: bool
    version: str


class QueryRequest(BaseModel):
    """查询请求"""
    sql: str
    params: Optional[Dict[str, Any]] = None


class QueryResponse(BaseModel):
    """查询响应"""
    success: bool
    data: List[Dict[str, Any]]
    count: int
    message: Optional[str] = None


class TableInfoResponse(BaseModel):
    """表信息响应"""
    success: bool
    table_info: Dict[str, Any]
    message: Optional[str] = None

