"""
FAQ扩展主模块
"""
from .update_service import FAQUpdateService
from .document_parser import parse_document
from .data_source import DataSourceManager


__all__ = [
    "FAQUpdateService",
    "parse_document",
    "DataSourceManager"
]