"""
配置加载器 - 支持多种配置源和IP自动检测
参考 config_loader.py 的设计模式
"""

import os
import sys
import socket
import platform
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class ConfigLoader:
    """配置加载器 - 支持从环境变量、文件、IP自动检测等多种方式加载配置"""
    
    def __init__(self):
        """初始化配置加载器，加载IP映射配置"""
        self._load_ip_mapping()
    
    def _load_ip_mapping(self):
        """从配置文件加载IP映射（使用列表方式，参考 env_loader.py）"""
        # 默认列表
        self.PROD_LIST = []
        self.PREVIEW_LIST = []
        self.DEV_LIST = ['127.0.0.1', 'localhost']
        
        # 尝试从配置文件加载
        try:
            # 从 src/utils/ip_env_mapping.py 加载
            from . import ip_env_mapping as mapping_module
            
            if hasattr(mapping_module, 'PROD_LIST'):
                self.PROD_LIST = mapping_module.PROD_LIST
                logger.debug(f"从配置文件加载生产服务器列表: {len(self.PROD_LIST)} 个IP")
            
            if hasattr(mapping_module, 'PREVIEW_LIST'):
                self.PREVIEW_LIST = mapping_module.PREVIEW_LIST
                logger.debug(f"从配置文件加载预演服务器列表: {len(self.PREVIEW_LIST)} 个IP")
            
            if hasattr(mapping_module, 'DEV_LIST'):
                self.DEV_LIST = mapping_module.DEV_LIST
                logger.debug(f"从配置文件加载开发服务器列表: {len(self.DEV_LIST)} 个IP")
        except Exception as e:
            logger.warning(f"加载IP映射配置失败，使用默认配置: {e}")
    
    @staticmethod
    def get_local_ip() -> Optional[str]:
        """
        跨平台获取本地 IP 地址（参考 env_loader.py 的实现）
        - Linux: 优先尝试 eth0（云服务器内网 IP），失败则回退到 socket.connect
        - Windows/macOS: 使用 socket.connect 获取默认出口 IP
        
        Returns:
            本机IP地址字符串，如果获取失败返回 "127.0.0.1"
        """
        system = platform.system().lower()
        
        if system == "linux":
            # 尝试直接读取 eth0（适用于云服务器）
            try:
                import fcntl
                import struct
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                ip = socket.inet_ntoa(fcntl.ioctl(
                    s.fileno(),
                    0x8915,  # SIOCGIFADDR，用于"获取接口地址"
                    struct.pack('256s', b'eth0')
                )[20:24])
                logger.debug(f"[Linux] 通过 eth0 获取内网 IP: {ip}")
                s.close()
                return ip
            except Exception as e:
                logger.debug(f"读取 eth0 失败，回退到通用方法: {e}")
        
        # 通用方法：适用于 Windows / macOS / Linux 回退
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # 连接到公网地址（不会发送数据）
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            logger.debug(f"[{system}] 通过 socket.connect 获取 IP: {ip}")
            return ip
        except Exception as e:
            logger.error(f"获取本地 IP 失败: {e}")
            return "127.0.0.1"
    
    def detect_env_by_ip(self, ip: Optional[str] = None) -> Optional[str]:
        """
        根据IP地址检测环境类型（参考 env_loader.py 的实现）
        
        Args:
            ip: IP地址，如果为None则自动获取本机IP
            
        Returns:
            环境类型字符串 (dev/show/prod)，如果无法检测返回None
        """
        if ip is None:
            ip = ConfigLoader.get_local_ip()
        
        if ip is None:
            logger.warning("无法获取本机IP地址，跳过IP环境检测")
            return None
        
        logger.debug(f"检测到本机IP: {ip}")
        
        # 检查生产服务器列表
        if ip in self.PROD_LIST:
            logger.debug(f"当前IP地址 {ip} 在生产服务器列表中，加载生产环境配置")
            return "prod"
        
        # 检查预演服务器列表
        if ip in self.PREVIEW_LIST:
            logger.debug(f"当前IP地址 {ip} 在预演服务器列表中，加载预演环境配置")
            return "show"
        
        # 其他IP默认使用开发环境（包括 127.0.0.1）
        logger.debug(f"当前IP地址 {ip} 未在生产或预演服务器列表中，加载开发环境配置")
        return "dev"
    
    @staticmethod
    def load_from_env_file(env_file: Path) -> bool:
        """
        从环境变量文件加载配置
        
        Args:
            env_file: 环境变量文件路径
            
        Returns:
            是否成功加载
        """
        if not env_file.exists():
            return False
        
        load_dotenv(env_file, override=True)
        logger.debug(f"从文件加载配置: {env_file}")
        return True
    
    @staticmethod
    def load_from_env_type(env_type: str, project_root: Optional[Path] = None) -> bool:
        """
        根据环境类型加载对应的配置文件
        
        Args:
            env_type: 环境类型 (dev/show/prod)
            project_root: 项目根目录，如果为None则自动检测
            
        Returns:
            是否成功加载
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        
        # 优先尝试 .env.{env_type}，如果不存在则尝试 env.{env_type}
        env_file = project_root / f'.env.{env_type}'
        if not env_file.exists():
            env_file = project_root / f'env.{env_type}'
        
        return ConfigLoader.load_from_env_file(env_file)
    
    def load_config(
        self,
        env_type: Optional[str] = None,
        config_file: Optional[str] = None,
        auto_detect_ip: bool = True,
        project_root: Optional[Path] = None
    ) -> str:
        """
        统一配置加载入口
        
        优先级：
        1. 命令行参数或 env_type 参数
        2. 环境变量 APP_ENV_TYPE
        3. IP自动检测（如果启用）
        4. 默认值 (dev)
        
        Args:
            env_type: 直接指定的环境类型（优先级最高）
            config_file: 指定的配置文件路径（如果提供，直接加载该文件）
            auto_detect_ip: 是否启用IP自动检测
            project_root: 项目根目录
            
        Returns:
            实际使用的环境类型字符串
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        
        detected_env = None
        
        # 优先级1: 命令行参数
        if len(sys.argv) > 1:
            arg = sys.argv[1]
            if arg in ['dev', 'show', 'prod']:
                detected_env = arg
                logger.debug(f"从命令行参数获取环境类型: {detected_env}")
        
        # 优先级2: 直接传入的 env_type 参数
        if not detected_env and env_type:
            detected_env = env_type
            logger.debug(f"从参数获取环境类型: {detected_env}")
        
        # 优先级3: 环境变量
        if not detected_env:
            detected_env = os.getenv('APP_ENV_TYPE')
            if detected_env:
                logger.debug(f"从环境变量 APP_ENV_TYPE 获取环境类型: {detected_env}")
        
        # 优先级4: IP自动检测
        if not detected_env and auto_detect_ip:
            detected_env = self.detect_env_by_ip()
            if detected_env:
                logger.debug(f"通过IP自动检测获取环境类型: {detected_env}")
        
        # 优先级5: 默认值
        if not detected_env:
            detected_env = 'dev'
            logger.debug(f"使用默认环境类型: {detected_env}")
        
        # 如果指定了配置文件，直接加载
        if config_file:
            config_path = Path(config_file)
            if config_path.is_absolute():
                ConfigLoader.load_from_env_file(config_path)
            else:
                ConfigLoader.load_from_env_file(project_root / config_path)
            logger.debug(f"从指定配置文件加载: {config_file}")
            return detected_env
        
        # 优先级1: 加载本地覆盖文件 .env（如果存在）
        local_env_file = project_root / '.env'
        if local_env_file.exists():
            ConfigLoader.load_from_env_file(local_env_file)
            logger.debug("已加载本地覆盖配置: .env")
        else:
            # 优先级2: 加载环境特定的配置文件
            if ConfigLoader.load_from_env_type(detected_env, project_root):
                logger.debug(f"已加载环境配置: .env.{detected_env}")
            else:
                # 优先级3: 从系统环境变量加载
                load_dotenv()
                logger.warning(f"未找到 .env.{detected_env} 文件，使用系统环境变量")
        
        # 设置环境变量，供其他模块使用
        os.environ['APP_ENV_TYPE'] = detected_env
        
        return detected_env
    
    @staticmethod
    def get_config_dict() -> Dict[str, Any]:
        """
        获取当前所有配置的字典形式
        
        Returns:
            配置字典
        """
        return {
            'APP_ENV': os.getenv('APP_ENV', 'development'),
            'APP_HOST': os.getenv('APP_HOST', '0.0.0.0'),
            'APP_PORT': int(os.getenv('APP_PORT', '8000')),
            'APP_ENV_TYPE': os.getenv('APP_ENV_TYPE', 'dev'),
            # Agno专用数据库配置
            'AGNO_MYSQL_HOST': os.getenv('AGNO_MYSQL_HOST', os.getenv('MYSQL_HOST', 'localhost')),
            'AGNO_MYSQL_PORT': int(os.getenv('AGNO_MYSQL_PORT', os.getenv('MYSQL_PORT', '3306'))),
            'AGNO_MYSQL_USER': os.getenv('AGNO_MYSQL_USER', os.getenv('MYSQL_USER', 'root')),
            'AGNO_MYSQL_DB_SCHEMA': os.getenv('AGNO_MYSQL_DB_SCHEMA', os.getenv('AGNO_MYSQL_DATABASE', os.getenv('MYSQL_DATABASE', 'agno_backend'))),
            # 业务数据库配置
            'BUSINESS_MYSQL_HOST': os.getenv('BUSINESS_MYSQL_HOST', os.getenv('MYSQL_HOST', 'localhost')),
            'BUSINESS_MYSQL_PORT': int(os.getenv('BUSINESS_MYSQL_PORT', os.getenv('MYSQL_PORT', '3306'))),
            'BUSINESS_MYSQL_USER': os.getenv('BUSINESS_MYSQL_USER', os.getenv('MYSQL_USER', 'root')),
            'BUSINESS_MYSQL_DATABASES': os.getenv('BUSINESS_MYSQL_DATABASES', ''),
            # Agno数据库表名配置
            'WORKFLOW_SESSION_TABLE': os.getenv('WORKFLOW_SESSION_TABLE', 'workflow_sessions'),
            'TEAM_SESSION_TABLE': os.getenv('TEAM_SESSION_TABLE', 'team_sessions'),
            'AGENT_SESSION_TABLE': os.getenv('AGENT_SESSION_TABLE', 'agent_sessions'),
            'AGNO_MEMORY_TABLE': os.getenv('AGNO_MEMORY_TABLE', 'agno_tags_memories'),
            'AGNO_TRACES_TABLE': os.getenv('AGNO_TRACES_TABLE', 'agno_tags_traces'),
            'AGNO_SPANS_TABLE': os.getenv('AGNO_SPANS_TABLE', 'agno_tags_spans'),
            'AGNO_METRICS_TABLE': os.getenv('AGNO_METRICS_TABLE', 'agno_tags_metrics'),
            'AGNO_EVAL_TABLE': os.getenv('AGNO_EVAL_TABLE', 'agno_tags_evaluations'),
            'AGNO_KNOWLEDGE_TABLE': os.getenv('AGNO_KNOWLEDGE_TABLE', 'agno_tags_knowledge'),
            'AGNO_CULTURE_TABLE': os.getenv('AGNO_CULTURE_TABLE', 'agno_tags_culture'),
            'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
        }
    
    def add_prod_ip(self, ip: str):
        """
        动态添加生产服务器IP
        
        Args:
            ip: IP地址
        """
        if ip not in self.PROD_LIST:
            self.PROD_LIST.append(ip)
            logger.debug(f"添加生产服务器IP: {ip}")
    
    def add_preview_ip(self, ip: str):
        """
        动态添加预演服务器IP
        
        Args:
            ip: IP地址
        """
        if ip not in self.PREVIEW_LIST:
            self.PREVIEW_LIST.append(ip)
            logger.debug(f"添加预演服务器IP: {ip}")
    
    def add_dev_ip(self, ip: str):
        """
        动态添加开发服务器IP
        
        Args:
            ip: IP地址
        """
        if ip not in self.DEV_LIST:
            self.DEV_LIST.append(ip)
            logger.debug(f"添加开发服务器IP: {ip}")


# 全局配置加载器实例（延迟初始化）
_config_loader: Optional[ConfigLoader] = None


def get_config_loader() -> ConfigLoader:
    """获取配置加载器实例（单例模式）"""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader
