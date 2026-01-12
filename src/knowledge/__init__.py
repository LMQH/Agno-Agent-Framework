"""
Knowledge Package
知识库模块
"""

from .config import (
    create_knowledge,
    get_knowledge_contents_db,
    get_knowledge_vector_db,
    get_knowledge_embedder,
)

__all__ = [
    'create_knowledge',
    'get_knowledge_contents_db',
    'get_knowledge_vector_db',
    'get_knowledge_embedder',
]

