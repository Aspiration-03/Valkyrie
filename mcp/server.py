"""
简化文件管理工具 - MCP服务器 (模块化版本)


模块结构：
- tools/file_listing.py     - 文件列表和查找工具 (2个工具)
- tools/file_operations.py  - 文件移动操作工具 (2个工具)
- tools/file_deletion.py    - 文件删除工具 (3个工具)
- tools/file_rename.py      - 文件重命名工具 (3个工具)
- tools/ocr_tools.py        - OCR识别工具 (1个工具)

总计：11个工具，分布在5个专业模块中
"""

from fastmcp import FastMCP
from tools import register_all_tools

def create_mcp_server():
    """创建并配置MCP服务器"""
    # 创建MCP实例
    mcp = FastMCP()

    # 注册所有工具模块
    register_all_tools(mcp)

    return mcp

if __name__ == "__main__":
    # 创建服务器并运行
    mcp_server = create_mcp_server()
    mcp_server.run()