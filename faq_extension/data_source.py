"""
FAQ数据源管理模块
"""
import os
import yaml
from typing import List, Dict
from datetime import datetime


class DataSourceManager:
    """数据源管理器"""
    
    def __init__(self, config_path: str = "faq_config.yaml"):
        """
        初始化数据源管理器
        
        Args:
            config_path (str): 配置文件路径
        """
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            print(f"配置文件不存在: {self.config_path}")
            return {}
            
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    
    def get_local_sources(self) -> List[Dict]:
        """
        获取本地数据源配置
        
        Returns:
            List[Dict]: 本地数据源配置列表
        """
        return self.config.get("local_sources", [])
    
    def scan_source_files(self, source_config: Dict) -> List[Dict[str, str]]:
        """
        扫描数据源中的文件
        
        Args:
            source_config (Dict): 数据源配置
            
        Returns:
            List[Dict[str, str]]: 文件信息列表，包含路径和修改时间
        """
        source_path = source_config.get("path", "")
        file_patterns = source_config.get("file_patterns", [])
        
        if not os.path.exists(source_path):
            print(f"数据源目录不存在: {source_path}")
            return []
        
        files = []
        for root, _, filenames in os.walk(source_path):
            for filename in filenames:
                # 检查文件是否匹配配置的模式
                matched = any(filename.endswith(pattern.replace("*", "")) for pattern in file_patterns)
                if matched:
                    file_path = os.path.join(root, filename)
                    mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    files.append({
                        "path": file_path,
                        "modified_time": mod_time
                    })
        
        return files