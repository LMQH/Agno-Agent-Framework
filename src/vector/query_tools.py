"""
Milvus Vector Query Tools Module
Milvus 向量查询工具，提供基本的向量数据库操作方法
"""

from typing import List, Dict, Any, Optional
from pymilvus import Collection, utility, FieldSchema, CollectionSchema, DataType
import logging
import os
from .connection import get_milvus_client, check_milvus_connection, milvus_connection

logger = logging.getLogger(__name__)


class VectorQueryTools:
    """Milvus 向量查询工具类"""

    def __init__(self):
        """初始化向量查询工具"""
        self._ensure_connection()

    def _ensure_connection(self):
        """确保 Milvus 连接已建立"""
        if not check_milvus_connection():
            get_milvus_client()

    def _get_database(self) -> str:
        """获取当前使用的数据库名称"""
        return milvus_connection.database

    def _get_collection(self, collection_name: str) -> Collection:
        """
        获取集合对象（支持指定数据库）

        Args:
            collection_name: 集合名称

        Returns:
            Collection 对象
        """
        database = self._get_database()
        # 如果数据库不是 default，需要在集合名称前加上数据库名
        if database and database != "default":
            return Collection(collection_name, db_name=database)
        return Collection(collection_name)

    def list_collections(self) -> List[str]:
        """
        列出所有集合

        Returns:
            集合名称列表
        """
        try:
            database = self._get_database()
            if database and database != "default":
                # 如果指定了数据库，列出该数据库下的集合
                collections = utility.list_collections(db_name=database)
            else:
                collections = utility.list_collections()
            return collections
        except Exception as e:
            logger.error(f"列出集合失败: {e}")
            raise

    def collection_exists(self, collection_name: str) -> bool:
        """
        检查集合是否存在

        Args:
            collection_name: 集合名称

        Returns:
            bool: 集合是否存在
        """
        try:
            database = self._get_database()
            if database and database != "default":
                return utility.has_collection(collection_name, db_name=database)
            return utility.has_collection(collection_name)
        except Exception as e:
            logger.error(f"检查集合存在性失败: {collection_name}, 错误: {e}")
            raise

    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """
        获取集合信息

        Args:
            collection_name: 集合名称

        Returns:
            集合信息字典
        """
        try:
            if not self.collection_exists(collection_name):
                raise ValueError(f"集合 {collection_name} 不存在")

            collection = self._get_collection(collection_name)
            collection.load()

            # 获取集合统计信息
            num_entities = collection.num_entities
            
            # 获取字段信息
            schema = collection.schema
            fields_info = []
            for field in schema.fields:
                fields_info.append({
                    "name": field.name,
                    "type": str(field.dtype),
                    "is_primary": field.is_primary,
                    "auto_id": field.auto_id,
                })

            return {
                "name": collection_name,
                "num_entities": num_entities,
                "fields": fields_info,
            }

        except Exception as e:
            logger.error(f"获取集合信息失败: {collection_name}, 错误: {e}")
            raise

    def search_vectors(
        self,
        collection_name: str,
        vectors: List[List[float]],
        limit: int = 10,
        expr: Optional[str] = None,
        output_fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        向量相似度搜索

        Args:
            collection_name: 集合名称
            vectors: 查询向量列表
            limit: 返回结果数量
            expr: 过滤表达式（可选）
            output_fields: 需要返回的字段列表（可选）

        Returns:
            搜索结果列表
        """
        try:
            if not self.collection_exists(collection_name):
                raise ValueError(f"集合 {collection_name} 不存在")

            collection = self._get_collection(collection_name)
            collection.load()

            # 获取向量字段名（通常是第一个向量字段）
            vector_field = None
            for field in collection.schema.fields:
                if field.dtype == DataType.FLOAT_VECTOR or field.dtype == DataType.BINARY_VECTOR:
                    vector_field = field.name
                    break

            if not vector_field:
                raise ValueError(f"集合 {collection_name} 中没有找到向量字段")

            # 执行搜索
            search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
            results = collection.search(
                data=vectors,
                anns_field=vector_field,
                param=search_params,
                limit=limit,
                expr=expr,
                output_fields=output_fields
            )

            # 格式化结果
            formatted_results = []
            for hits in results:
                hit_list = []
                for hit in hits:
                    hit_data = {
                        "id": hit.id,
                        "distance": hit.distance,
                        "score": hit.score if hasattr(hit, 'score') else None,
                    }
                    # 添加其他字段
                    if hasattr(hit, 'entity') and hit.entity:
                        for key, value in hit.entity.items():
                            if key != vector_field:  # 不返回向量数据
                                hit_data[key] = value
                    hit_list.append(hit_data)
                formatted_results.append(hit_list)

            return formatted_results[0] if len(formatted_results) == 1 else formatted_results

        except Exception as e:
            logger.error(f"向量搜索失败: {collection_name}, 错误: {e}")
            raise

    def get_collection_count(self, collection_name: str) -> int:
        """
        获取集合中的实体数量

        Args:
            collection_name: 集合名称

        Returns:
            实体数量
        """
        try:
            if not self.collection_exists(collection_name):
                raise ValueError(f"集合 {collection_name} 不存在")

            collection = self._get_collection(collection_name)
            return collection.num_entities

        except Exception as e:
            logger.error(f"获取集合数量失败: {collection_name}, 错误: {e}")
            raise


# 全局向量查询工具实例
vector_tools = VectorQueryTools()


def get_vector_tools() -> VectorQueryTools:
    """获取向量查询工具实例"""
    return vector_tools

