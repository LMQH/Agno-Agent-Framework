"""
API Router
API 路由定义
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import List

from .models import (
    HealthCheckResponse,
    QueryRequest,
    QueryResponse,
    TableInfoResponse
)
from .dependencies import get_query_tools_dependency
from src.database.connection import check_database_connection
from src.database.query_tools import DatabaseQueryTools

logger = logging.getLogger(__name__)

# 创建根路由器（用于健康检查等根路径路由）
root_router = APIRouter()

# 创建 API 路由器
api_router = APIRouter(
    prefix="/api",
    tags=["API"]
)


# ============================================================================
# 健康检查路由（根路径）
# ============================================================================

@root_router.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """
    健康检查端点
    
    Returns:
        HealthCheckResponse: 健康检查响应
    """
    try:
        db_connected = check_database_connection()
        return HealthCheckResponse(
            status="healthy" if db_connected else "unhealthy",
            service="agno-backend-api",
            database_connected=db_connected,
            version="0.1.0"
        )
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return HealthCheckResponse(
            status="error",
            service="agno-backend-api",
            database_connected=False,
            version="0.1.0"
        )


# ============================================================================
# 数据库查询路由
# ============================================================================

@api_router.post("/query", response_model=QueryResponse, tags=["Database"])
async def execute_query(
    request: QueryRequest,
    query_tools: DatabaseQueryTools = Depends(get_query_tools_dependency)
):
    """
    执行数据库查询
    
    Args:
        request: 查询请求
        query_tools: 查询工具（依赖注入）
    
    Returns:
        QueryResponse: 查询响应
    
    Raises:
        HTTPException: 查询执行失败
    """
    try:
        # 执行查询
        result = query_tools.execute_query(request.sql, request.params)

        return QueryResponse(
            success=True,
            data=result,
            count=len(result),
            message="查询执行成功"
        )

    except Exception as e:
        logger.error(f"查询执行失败: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"查询执行失败: {str(e)}"
        )


@api_router.get("/tables", response_model=List[str], tags=["Database"])
async def list_tables(
    query_tools: DatabaseQueryTools = Depends(get_query_tools_dependency)
):
    """
    列出所有表
    
    Args:
        query_tools: 查询工具（依赖注入）
    
    Returns:
        List[str]: 表名列表
    
    Raises:
        HTTPException: 获取表列表失败
    """
    try:
        tables = query_tools.list_tables()
        return tables

    except Exception as e:
        logger.error(f"获取表列表失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取表列表失败: {str(e)}"
        )


@api_router.get("/tables/{table_name}/info", response_model=TableInfoResponse, tags=["Database"])
async def get_table_info(
    table_name: str,
    query_tools: DatabaseQueryTools = Depends(get_query_tools_dependency)
):
    """
    获取表信息
    
    Args:
        table_name: 表名
        query_tools: 查询工具（依赖注入）
    
    Returns:
        TableInfoResponse: 表信息响应
    
    Raises:
        HTTPException: 获取表信息失败
    """
    try:
        table_info = query_tools.get_table_info(table_name)

        return TableInfoResponse(
            success=True,
            table_info=table_info,
            message="获取表信息成功"
        )

    except Exception as e:
        logger.error(f"获取表信息失败: {e}")
        raise HTTPException(
            status_code=404,
            detail=f"获取表信息失败: {str(e)}"
        )


@api_router.get("/tables/{table_name}/count", tags=["Database"])
async def get_table_count(
    table_name: str,
    query_tools: DatabaseQueryTools = Depends(get_query_tools_dependency)
):
    """
    获取表记录数
    
    Args:
        table_name: 表名
        query_tools: 查询工具（依赖注入）
    
    Returns:
        dict: 包含表名和记录数的字典
    
    Raises:
        HTTPException: 获取表记录数失败
    """
    try:
        count = query_tools.get_table_count(table_name)
        return {"table": table_name, "count": count}

    except Exception as e:
        logger.error(f"获取表记录数失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"获取表记录数失败: {str(e)}"
        )

