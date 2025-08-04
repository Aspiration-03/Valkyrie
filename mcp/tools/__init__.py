"""
工具模块 - MCP服务器工具集合
"""

from .file_listing import register_file_listing_tools
from .file_operations import register_file_operation_tools  
from .file_deletion import register_file_deletion_tools
from .file_rename import register_file_rename_tools
from .ocr_tools import register_ocr_tools

def register_all_tools(mcp):
    """注册所有工具到MCP实例"""
    register_file_listing_tools(mcp)
    register_file_operation_tools(mcp)
    register_file_deletion_tools(mcp)
    register_file_rename_tools(mcp)
    register_ocr_tools(mcp)
    
    print("已注册所有工具模块")

__all__ = [
    'register_all_tools',
    'register_file_listing_tools',
    'register_file_operation_tools', 
    'register_file_deletion_tools',
    'register_file_rename_tools',
    'register_ocr_tools'
]