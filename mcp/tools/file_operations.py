"""
文件移动操作工具模块
"""

import os
import shutil
import glob
from typing import Union, List


def register_file_operation_tools(mcp):
    """注册文件操作相关工具"""
    
    @mcp.tool
    def move_files(source_items: Union[str, List[str]], target_directory: str):
        """
        移动文件或文件夹到目标目录，支持单个或批量操作，自动创建目标目录
        :param source_items: 源文件/文件夹路径，可以是单个路径字符串或路径列表
        :param target_directory: 目标目录路径
        :return: 移动操作结果
        """
        try:
            # 统一处理为列表格式
            if isinstance(source_items, str):
                items_to_move = [source_items]
            else:
                items_to_move = source_items

            # 自动创建目标目录
            if not os.path.exists(target_directory):
                try:
                    os.makedirs(target_directory)
                    print(f"自动创建目标目录: {target_directory}")
                except Exception as e:
                    return f"错误: 无法创建目标目录 {target_directory} - {str(e)}"
            elif not os.path.isdir(target_directory):
                return f"错误: {target_directory} 存在但不是目录"

            results = []
            success_count = 0
            total_count = len(items_to_move)

            for source_path in items_to_move:
                # 检查源文件是否存在
                if not os.path.exists(source_path):
                    results.append(f" {source_path}: 源文件/文件夹不存在")
                    continue

                # 获取文件名
                item_name = os.path.basename(source_path)
                target_path = os.path.join(target_directory, item_name)

                # 检查目标位置是否已存在
                if os.path.exists(target_path):
                    results.append(f" {item_name}: 目标位置已存在同名文件/文件夹")
                    continue

                try:
                    # 执行移动操作
                    shutil.move(source_path, target_path)

                    # 判断移动的是文件还是文件夹
                    item_type = "文件夹" if os.path.isdir(target_path) else "文件"
                    results.append(f" {item_name}: {item_type}移动成功")
                    success_count += 1

                except PermissionError:
                    results.append(f" {item_name}: 权限不足，无法移动")
                except Exception as e:
                    results.append(f" {item_name}: 移动失败 - {str(e)}")

            # 生成结果摘要
            if total_count == 1:
                summary = "单个文件移动操作完成\n\n"
            else:
                summary = f"批量移动操作完成: 成功 {success_count}/{total_count} 个项目\n\n"

            return summary + "\n".join(results)

        except Exception as e:
            return f"移动操作时出错: {str(e)}"

    @mcp.tool
    def move_files_by_pattern(source_directory: str, pattern: str, target_directory: str):
        """
        根据模式批量移动文件（如移动所有pdf文件）
        :param source_directory: 源目录
        :param pattern: 文件模式，如 '*.pdf', '*.jpg', '*report*' 等
        :param target_directory: 目标目录
        :return: 移动操作结果
        """
        try:
            if not os.path.exists(source_directory):
                return f"错误: 源目录 {source_directory} 不存在"

            if not os.path.isdir(source_directory):
                return f"错误: {source_directory} 不是一个目录"

            # 查找匹配的文件
            search_path = os.path.join(source_directory, pattern)
            matched_files = glob.glob(search_path)

            if not matched_files:
                return f"在 {source_directory} 中未找到匹配 '{pattern}' 的文件"

            # 自动创建目标目录
            if not os.path.exists(target_directory):
                try:
                    os.makedirs(target_directory)
                    print(f" 自动创建目标目录: {target_directory}")
                except Exception as e:
                    return f"错误: 无法创建目标目录 {target_directory} - {str(e)}"
            elif not os.path.isdir(target_directory):
                return f"错误: {target_directory} 存在但不是目录"

            results = []
            success_count = 0
            total_count = len(matched_files)

            for source_path in sorted(matched_files):
                file_name = os.path.basename(source_path)
                target_path = os.path.join(target_directory, file_name)

                # 检查目标位置是否已存在
                if os.path.exists(target_path):
                    results.append(f" {file_name}: 目标位置已存在同名文件")
                    continue

                try:
                    # 执行移动操作
                    shutil.move(source_path, target_path)
                    file_size = os.path.getsize(target_path)
                    results.append(f" {file_name}: 移动成功 ({file_size} 字节)")
                    success_count += 1

                except PermissionError:
                    results.append(f" {file_name}: 权限不足，无法移动")
                except Exception as e:
                    results.append(f" {file_name}: 移动失败 - {str(e)}")

            # 生成结果摘要
            summary = f"模式匹配移动操作完成: 成功 {success_count}/{total_count} 个文件\n"
            summary += f"匹配模式: {pattern}\n"
            summary += f"源目录: {source_directory}\n"
            summary += f"目标目录: {target_directory}\n\n"

            return summary + "\n".join(results)

        except Exception as e:
            return f"模式匹配移动时出错: {str(e)}"