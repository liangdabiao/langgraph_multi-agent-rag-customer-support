"""
FAQ更新服务模块
"""
import os
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from typing import Dict, List
from .document_parser import parse_document
from .data_source import DataSourceManager
# 导入向量数据库模块
from customer_support_chat.app.services.vectordb.vectordb import VectorDB
from customer_support_chat.app.services.vectordb.chunkenizer import recursive_character_splitting


class FAQUpdateService:
    """FAQ更新服务"""
    
    def __init__(self, config_path: str = "faq_config.yaml"):
        """
        初始化FAQ更新服务
        
        Args:
            config_path (str): 配置文件路径
        """
        self.scheduler = BackgroundScheduler()
        self.data_source_manager = DataSourceManager(config_path)
        self.last_run_time = {}
        # 初始化向量数据库
        self.faq_vectordb = VectorDB(collection_name="faq_collection")
    
    def start(self):
        """启动定期更新服务"""
        # 注册定时任务
        sources = self.data_source_manager.get_local_sources()
        for source in sources:
            interval = source.get("update_interval_hours", 24)
            self.scheduler.add_job(
                self._update_source,
                'interval',
                hours=interval,
                args=[source],
                id=f"source_{source['name']}"
            )
            print(f"已注册数据源更新任务: {source['name']} (每{interval}小时)")
        
        self.scheduler.start()
        print("FAQ更新服务已启动")
    
    def stop(self):
        """停止更新服务"""
        self.scheduler.shutdown()
        print("FAQ更新服务已停止")
    
    def _update_source(self, source_config: Dict):
        """
        更新单个数据源
        
        Args:
            source_config (Dict): 数据源配置
        """
        try:
            source_name = source_config["name"]
            print(f"开始更新数据源: {source_name}")
            
            # 扫描数据源文件
            files = self.data_source_manager.scan_source_files(source_config)
            print(f"发现 {len(files)} 个文件")
            
            # 处理每个文件
            for file_info in files:
                file_path = file_info["path"]
                modified_time = file_info["modified_time"]
                
                # 检查文件是否需要更新（通过修改时间判断）
                if self._should_update_file(source_name, file_path, modified_time):
                    content = parse_document(file_path)
                    if content:
                        self._update_index(source_name, file_path, content)
                        # 更新最后处理时间
                        self._update_last_processed_time(source_name, file_path, modified_time)
                        print(f"已更新文件索引: {file_path}")
                    else:
                        print(f"无法解析文件内容: {file_path}")
            
            print(f"数据源更新完成: {source_name}")
        except Exception as e:
            print(f"更新数据源失败: {source_config['name']}, 错误: {str(e)}")
    
    def _should_update_file(self, source_name: str, file_path: str, modified_time: datetime) -> bool:
        """
        判断文件是否需要更新
        
        Args:
            source_name (str): 数据源名称
            file_path (str): 文件路径
            modified_time (datetime): 文件修改时间
            
        Returns:
            bool: 是否需要更新
        """
        # 简单实现：通过修改时间判断
        last_processed = self._get_last_processed_time(source_name, file_path)
        return not last_processed or modified_time > last_processed
    
    def _get_last_processed_time(self, source_name: str, file_path: str) -> datetime:
        """
        获取文件最后处理时间
        
        Args:
            source_name (str): 数据源名称
            file_path (str): 文件路径
            
        Returns:
            datetime: 最后处理时间
        """
        # 简化实现：使用内存存储（实际应用中应使用持久化存储）
        key = f"{source_name}_{file_path}"
        return self.last_run_time.get(key)
    
    def _update_last_processed_time(self, source_name: str, file_path: str, processed_time: datetime):
        """
        更新文件最后处理时间
        
        Args:
            source_name (str): 数据源名称
            file_path (str): 文件路径
            processed_time (datetime): 处理时间
        """
        # 简化实现：使用内存存储（实际应用中应使用持久化存储）
        key = f"{source_name}_{file_path}"
        self.last_run_time[key] = processed_time
    
    def _update_index(self, source_name: str, file_path: str, content: str):
        """
        更新索引（与向量数据库交互）
        
        Args:
            source_name (str): 数据源名称
            file_path (str): 文件路径
            content (str): 文件内容
        """
        try:
            # 1. 将内容分块
            chunks = recursive_character_splitting(content)
            print(f"将内容分块为 {len(chunks)} 个片段")
            
            # 2. 为每个块生成嵌入向量并存储到向量数据库
            for i, chunk in enumerate(chunks):
                try:
                    # 生成嵌入向量
                    embedding = self.faq_vectordb.generate_embedding(chunk)
                    
                    # 存储到向量数据库
                    # 使用文件路径作为文档ID和URL
                    self.faq_vectordb.upsert_vector(
                        doc_id=file_path,
                        chunk_text=chunk,
                        embedding=embedding,
                        url=file_path,
                        chunk_index=i
                    )
                except Exception as e:
                    print(f"处理块 {i} 时出错: {str(e)}")
                    continue
            
            print(f"成功更新索引: {file_path}")
        except Exception as e:
            print(f"更新索引失败: {file_path}, 错误: {str(e)}")