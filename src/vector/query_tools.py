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
        # 连接建立后，确保默认集合存在
        self._ensure_default_collection_on_init()

    def _ensure_connection(self):
        """确保 Milvus 连接已建立"""
        if not check_milvus_connection():
            get_milvus_client()
    
    def _ensure_default_collection_on_init(self):
        """初始化时确保默认集合存在"""
        try:
            # 从环境变量读取配置，如果未提供则使用默认值
            self.ensure_default_collection()
        except Exception as e:
            # 集合创建失败不应该阻止工具初始化，只记录警告
            logger.warning(f"初始化时创建默认集合失败（可忽略）: {e}")

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
        # 如果数据库不是 default，先切换到该数据库，然后获取集合
        if database and database != "default":
            try:
                from pymilvus import db
                # 切换到目标数据库
                db.using_database(database)
                # 获取集合对象
                return Collection(collection_name)
            except Exception as db_error:
                # 如果切换数据库失败，尝试使用 db_name 参数（某些版本可能支持）
                logger.debug(f"切换数据库获取集合失败，尝试其他方式: {db_error}")
                try:
                    return Collection(collection_name, db_name=database)
                except TypeError:
                    # 如果不支持 db_name 参数，使用默认数据库
                    logger.warning(f"当前 pymilvus 版本不支持多数据库功能，使用默认数据库")
                    return Collection(collection_name)
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
                # 如果指定了数据库，先切换到该数据库，然后列出集合
                try:
                    from pymilvus import db
                    # 切换到目标数据库
                    db.using_database(database)
                    # 列出集合
                    collections = utility.list_collections()
                except Exception as db_error:
                    # 如果切换数据库失败，尝试使用 db_name 参数（某些版本可能支持）
                    logger.debug(f"切换数据库列出集合失败，尝试其他方式: {db_error}")
                    try:
                        collections = utility.list_collections(db_name=database)
                    except TypeError:
                        # 如果不支持 db_name 参数，返回空列表或抛出错误
                        logger.warning(f"当前 pymilvus 版本不支持多数据库功能，无法列出数据库 {database} 的集合")
                        collections = []
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
            
            # 如果指定了数据库，先切换到该数据库，然后检查集合
            if database and database != "default":
                try:
                    from pymilvus import db
                    # 切换到目标数据库
                    db.using_database(database)
                    # 检查集合是否存在
                    return utility.has_collection(collection_name)
                except Exception as db_error:
                    # 如果切换数据库失败，尝试通过列出集合来检查
                    logger.debug(f"切换数据库检查集合失败，使用列表方式: {db_error}")
                    collections = utility.list_collections()
                    return collection_name in collections
            else:
                # 默认数据库，直接检查
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

    def create_collection(
        self,
        collection_name: str,
        dimension: int = None,
        description: str = ""
    ) -> bool:
        """
        创建集合
        
        Args:
            collection_name: 集合名称
            dimension: 向量维度（如果为None，从环境变量MILVUS_DEFAULT_COLLECTION_DIMENSION读取，默认1536）
            description: 集合描述
        
        Returns:
            bool: 是否创建成功
        """
        # 如果未提供维度，从环境变量读取
        if dimension is None:
            dimension = int(os.getenv("MILVUS_DEFAULT_COLLECTION_DIMENSION", "1536"))
        try:
            # 检查集合是否已存在
            if self.collection_exists(collection_name):
                logger.debug(f"集合 {collection_name} 已存在，跳过创建")
                return True
            
            database = self._get_database()
            
            # 定义字段
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dimension),
                FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=65535),
            ]
            
            # 创建集合模式
            schema = CollectionSchema(
                fields=fields,
                description=description or f"知识库集合: {collection_name}"
            )
            
            # 创建集合
            if database and database != "default":
                try:
                    from pymilvus import db
                    # 切换到目标数据库
                    db.using_database(database)
                    # 在目标数据库中创建集合
                    collection = Collection(
                        name=collection_name,
                        schema=schema
                    )
                except Exception as db_error:
                    # 如果切换数据库失败，尝试使用 db_name 参数（某些版本可能支持）
                    logger.debug(f"切换数据库创建集合失败，尝试其他方式: {db_error}")
                    try:
                        collection = Collection(
                            name=collection_name,
                            schema=schema,
                            db_name=database
                        )
                    except TypeError:
                        # 如果不支持 db_name 参数，在默认数据库中创建
                        logger.warning(f"当前 pymilvus 版本不支持多数据库功能，在默认数据库中创建集合")
                        collection = Collection(
                            name=collection_name,
                            schema=schema
                        )
            else:
                collection = Collection(
                    name=collection_name,
                    schema=schema
                )
            
            logger.info(f"成功创建集合: {collection_name} (维度: {dimension})")
            return True
            
        except Exception as e:
            logger.error(f"创建集合失败: {collection_name}, 错误: {e}")
            raise

    def ensure_default_collection(
        self,
        collection_name: str = None,
        dimension: int = None
    ) -> bool:
        """
        确保默认集合存在，如果不存在则创建
        
        Args:
            collection_name: 默认集合名称（如果为None，从环境变量读取）
            dimension: 向量维度（如果为None，从环境变量读取）
        
        Returns:
            bool: 是否成功
        """
        try:
            # 从环境变量读取默认集合名称
            if collection_name is None:
                collection_name = os.getenv("MILVUS_DEFAULT_COLLECTION", "agno_knowledge_default")
            
            # 从环境变量读取默认维度
            if dimension is None:
                dimension = int(os.getenv("MILVUS_DEFAULT_COLLECTION_DIMENSION", "1536"))
            
            if not self.collection_exists(collection_name):
                logger.info(f"默认集合 {collection_name} 不存在，正在创建... (维度: {dimension})")
                return self.create_collection(
                    collection_name=collection_name,
                    dimension=dimension,
                    description="Agno 默认知识库集合"
                )
            else:
                logger.debug(f"默认集合 {collection_name} 已存在")
                return True
        except Exception as e:
            logger.error(f"确保默认集合失败: {collection_name}, 错误: {e}")
            raise


# 全局向量查询工具实例
vector_tools = VectorQueryTools()


def get_vector_tools() -> VectorQueryTools:
    """获取向量查询工具实例"""
    return vector_tools

