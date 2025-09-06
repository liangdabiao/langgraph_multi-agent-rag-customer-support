"""
文档解析器模块
"""
import os
from typing import Union


def parse_document(file_path: str) -> Union[str, None]:
    """
    根据文件扩展名解析不同格式的文档
    
    Args:
        file_path (str): 文档路径
        
    Returns:
        str: 解析后的文本内容，如果解析失败则返回None
    """
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return None
        
    try:
        if file_path.endswith('.md'):
            return _parse_markdown(file_path)
        elif file_path.endswith('.pdf'):
            return _parse_pdf(file_path)
        elif file_path.endswith('.docx'):
            return _parse_docx(file_path)
        else:
            print(f"不支持的文件格式: {file_path}")
            return None
    except Exception as e:
        print(f"解析文件时出错 {file_path}: {str(e)}")
        return None


def _parse_markdown(file_path: str) -> str:
    """解析Markdown文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def _parse_pdf(file_path: str) -> str:
    """解析PDF文件"""
    try:
        import PyPDF2
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
    except ImportError:
        print("PyPDF2库未安装")
        return None
    except Exception as e:
        print(f"解析PDF文件时出错: {str(e)}")
        return None


def _parse_docx(file_path: str) -> str:
    """解析Word文档"""
    try:
        from docx import Document
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except ImportError:
        print("python-docx库未安装")
        return None
    except Exception as e:
        print(f"解析Word文件时出错: {str(e)}")
        return None