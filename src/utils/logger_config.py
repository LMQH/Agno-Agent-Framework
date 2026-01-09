"""
日志配置模块
提供统一的日志配置，支持文件日志和控制台日志
"""

import os
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from typing import Optional


def setup_logging(
    project_root: Optional[Path] = None,
    log_level: Optional[str] = None,
    log_to_file: bool = True,
    log_to_console: bool = True
):
    """
    配置日志系统
    
    Args:
        project_root: 项目根目录，如果为None则自动检测
        log_level: 日志级别，如果为None则从环境变量LOG_LEVEL读取
        log_to_file: 是否写入文件
        log_to_console: 是否输出到控制台
    """
    if project_root is None:
        # 自动检测项目根目录（假设此文件在 src/utils/ 下）
        project_root = Path(__file__).parent.parent.parent
    
    # 获取日志级别
    if log_level is None:
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # 转换为logging级别
    numeric_level = getattr(logging, log_level, logging.INFO)
    
    # 创建logs目录
    logs_dir = project_root / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # 生成日志文件名（时间戳格式）
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = logs_dir / f'app_{timestamp}.log'
    
    # 日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # 获取根logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # 清除已有的处理器
    root_logger.handlers.clear()
    
    # 文件日志处理器
    if log_to_file:
        file_handler = logging.FileHandler(
            log_file,
            mode='w',
            encoding='utf-8'
        )
        file_handler.setLevel(numeric_level)
        file_formatter = logging.Formatter(log_format, date_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        # 同时记录日志文件路径
        print(f"日志文件: {log_file}")
    
    # 控制台日志处理器
    if log_to_console:
        console_handler = logging.StreamHandler()
        # 控制台只显示WARNING及以上级别
        console_handler.setLevel(max(numeric_level, logging.WARNING))
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            date_format
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # 设置第三方库的日志级别
    logging.getLogger('uvicorn').setLevel(logging.WARNING)
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('fastapi').setLevel(logging.WARNING)
    
    return log_file


def get_logger(name: str) -> logging.Logger:
    """
    获取logger实例
    
    Args:
        name: logger名称，通常使用__name__
        
    Returns:
        Logger实例
    """
    return logging.getLogger(name)

