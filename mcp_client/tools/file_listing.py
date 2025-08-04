"""
文件列表和查找工具模块
"""

import os
import glob


def register_file_listing_tools(mcp):
    """注册文件列表和查找相关工具"""
    
    @mcp.tool
    def list_files(directory: str):
        """
        列出指定目录下的所有文件和文件夹
        :param directory: 目录路径
        :return: 文件列表描述
        """
        try:
            if not os.path.exists(directory):
                return f"错误: 目录 {directory} 不存在"

            if not os.path.isdir(directory):
                return f"错误: {directory} 不是一个目录"

            items = os.listdir(directory)

            if not items:
                return f"目录 {directory} 是空的"

            files = []
            folders = []

            for item in items:
                item_path = os.path.join(directory, item)
                if os.path.isfile(item_path):
                    file_size = os.path.getsize(item_path)
                    files.append(f"{item} ({file_size} 字节)")
                elif os.path.isdir(item_path):
                    folders.append(item)

            result = f"目录: {directory}\n"
            result += f"共找到 {len(files)} 个文件，{len(folders)} 个文件夹\n\n"

            if folders:
                result += " 文件夹:\n"
                for folder in sorted(folders):
                    result += f"  - {folder}\n"
                result += "\n"

            if files:
                result += " 文件:\n"
                for file in sorted(files):
                    result += f"  - {file}\n"

            return result

        except Exception as e:
            return f"列出文件时出错: {str(e)}"

    @mcp.tool
    def find_files(directory: str, pattern: str):
        """
        根据模式查找文件（支持扩展名、关键词等）
        :param directory: 搜索目录
        :param pattern: 匹配模式，如 '*.pdf', '*.jpg', '*report*' 等
        :return: 匹配的文件列表
        """
        try:
            if not os.path.exists(directory):
                return f"错误: 目录 {directory} 不存在"

            if not os.path.isdir(directory):
                return f"错误: {directory} 不是一个目录"

            # 构建搜索路径
            search_path = os.path.join(directory, pattern)
            matched_files = glob.glob(search_path)

            if not matched_files:
                return f"在 {directory} 中未找到匹配 '{pattern}' 的文件"

            result = f"在 {directory} 中找到 {len(matched_files)} 个匹配 '{pattern}' 的文件:\n\n"

            for file_path in sorted(matched_files):
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                result += f" {file_name} ({file_size} 字节)\n"

            result += f"\n完整路径列表:\n"
            for file_path in sorted(matched_files):
                result += f"  - {file_path}\n"

            return result

        except Exception as e:
            return f"查找文件时出错: {str(e)}"