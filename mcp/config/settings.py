"""
应用程序配置设置
"""

import os
from typing import Optional


class Config:
    """应用程序配置类"""
    
    # API配置
    DEEPSEEK_API_KEY: str = "sk-423742b032364794b29aa00daf12590e"
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEFAULT_MODEL: str = "deepseek-chat"
    
    # MCP配置
    DEFAULT_MCP_SCRIPT: str = "server.py"
    
    # 系统提示
    SYSTEM_PROMPT: str = """你是一个智能文件管理助手，必须使用提供的工具完成用户的文件操作请求。

重要规则：
1. 记住之前对话中的文件操作结果，可以在后续对话中引用
2. 当用户说"那个文件"、"刚才的文件"等时，从对话历史中找到相关文件信息
3. 保持上下文连贯，完成用户的分步操作请求

常见操作流程：
- 用户可能先让你列出文件，然后在下次对话中操作这些文件
- 用户可能引用之前的操作结果，你需要从历史记录中获取相关信息"""
    
    @classmethod
    def get_api_key(cls) -> str:
        """获取API密钥，支持环境变量覆盖"""
        return os.getenv("DEEPSEEK_API_KEY", cls.DEEPSEEK_API_KEY)
    
    @classmethod
    def get_base_url(cls) -> str:
        """获取API基础URL"""
        return os.getenv("DEEPSEEK_BASE_URL", cls.DEEPSEEK_BASE_URL)
    
    @classmethod
    def get_model(cls) -> str:
        """获取默认模型"""
        return os.getenv("DEEPSEEK_MODEL", cls.DEFAULT_MODEL)