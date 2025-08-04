"""
文件删除工具模块
"""

import os
import shutil
import glob
import time
from typing import Union, List
from datetime import datetime


def register_file_deletion_tools(mcp):
    """注册文件删除相关工具"""
    
    @mcp.tool
    def delete_files(file_paths: Union[str, List[str]], confirm: bool = False):
        """
        删除指定的文件或文件夹，支持单个或批量操作
        :param file_paths: 要删除的文件/文件夹路径，可以是单个路径字符串或路径列表
        :param confirm: 确认删除标志，设为True才会真正执行删除操作
        :return: 删除操作结果
        """
        try:
            # 统一处理为列表格式
            if isinstance(file_paths, str):
                items_to_delete = [file_paths]
            else:
                items_to_delete = file_paths

            # 安全检查：如果没有确认，只显示要删除的内容
            if not confirm:
                preview_info = []
                total_size = 0

                for file_path in items_to_delete:
                    if not os.path.exists(file_path):
                        preview_info.append(f"  {file_path}: 文件/文件夹不存在")
                        continue

                    if os.path.isfile(file_path):
                        file_size = os.path.getsize(file_path)
                        total_size += file_size
                        preview_info.append(f"  {file_path} ({file_size} 字节)")
                    elif os.path.isdir(file_path):
                        # 计算文件夹大小
                        folder_size = 0
                        file_count = 0
                        for root, dirs, files in os.walk(file_path):
                            for file in files:
                                file_count += 1
                                folder_size += os.path.getsize(os.path.join(root, file))
                        total_size += folder_size
                        preview_info.append(f"  {file_path} (包含 {file_count} 个文件，共 {folder_size} 字节)")

                warning_msg = f"  删除预览 (总共 {len(items_to_delete)} 个项目，{total_size} 字节)\n\n"
                warning_msg += "\n".join(preview_info)
                warning_msg += f"\n\n❗ 这是预览模式，文件尚未删除。"
                warning_msg += f"\n如需执行删除，请设置 confirm=True"

                return warning_msg

            results = []
            success_count = 0
            total_count = len(items_to_delete)

            for file_path in items_to_delete:
                # 检查文件是否存在
                if not os.path.exists(file_path):
                    results.append(f"  {file_path}: 文件/文件夹不存在")
                    continue

                try:
                    if os.path.isfile(file_path):
                        # 删除文件
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        results.append(f"  {os.path.basename(file_path)}: 文件删除成功 ({file_size} 字节)")
                        success_count += 1

                    elif os.path.isdir(file_path):
                        # 删除文件夹及其内容
                        folder_name = os.path.basename(file_path)
                        shutil.rmtree(file_path)
                        results.append(f"  {folder_name}: 文件夹删除成功")
                        success_count += 1

                except PermissionError:
                    results.append(f"  {os.path.basename(file_path)}: 权限不足，无法删除")
                except OSError as e:
                    results.append(f"  {os.path.basename(file_path)}: 删除失败 - {str(e)}")
                except Exception as e:
                    results.append(f"  {os.path.basename(file_path)}: 删除失败 - {str(e)}")

            # 生成结果摘要
            if total_count == 1:
                summary = "🗑️  单个项目删除操作完成\n\n"
            else:
                summary = f"🗑️  批量删除操作完成: 成功 {success_count}/{total_count} 个项目\n\n"

            return summary + "\n".join(results)

        except Exception as e:
            return f"删除操作时出错: {str(e)}"

    @mcp.tool
    def delete_files_by_pattern(directory: str, pattern: str, confirm: bool = False):
        """
        根据模式批量删除文件（如删除所有临时文件）
        :param directory: 目标目录
        :param pattern: 文件模式，如 '*.tmp', '*.log', '*backup*' 等
        :param confirm: 确认删除标志，设为True才会真正执行删除操作
        :return: 删除操作结果
        """
        try:
            if not os.path.exists(directory):
                return f"错误: 目录 {directory} 不存在"

            if not os.path.isdir(directory):
                return f"错误: {directory} 不是一个目录"

            # 查找匹配的文件
            search_path = os.path.join(directory, pattern)
            matched_files = glob.glob(search_path)

            if not matched_files:
                return f"在 {directory} 中未找到匹配 '{pattern}' 的文件"

            # 安全检查：如果没有确认，只显示要删除的文件
            if not confirm:
                preview_info = []
                total_size = 0

                for file_path in sorted(matched_files):
                    file_name = os.path.basename(file_path)
                    if os.path.isfile(file_path):
                        file_size = os.path.getsize(file_path)
                        total_size += file_size
                        preview_info.append(f"  {file_name} ({file_size} 字节)")
                    elif os.path.isdir(file_path):
                        preview_info.append(f"  {file_name} (文件夹)")

                warning_msg = f"  模式删除预览 (匹配 '{pattern}')\n"
                warning_msg += f"目录: {directory}\n"
                warning_msg += f"找到 {len(matched_files)} 个匹配项，总大小 {total_size} 字节\n\n"
                warning_msg += "\n".join(preview_info)
                warning_msg += f"\n\n 这是预览模式，文件尚未删除。"
                warning_msg += f"\n如需执行删除，请设置 confirm=True"

                return warning_msg

            results = []
            success_count = 0
            total_count = len(matched_files)
            total_size_deleted = 0

            for file_path in sorted(matched_files):
                file_name = os.path.basename(file_path)

                try:
                    if os.path.isfile(file_path):
                        # 删除文件
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        total_size_deleted += file_size
                        results.append(f"  {file_name}: 删除成功 ({file_size} 字节)")
                        success_count += 1

                    elif os.path.isdir(file_path):
                        # 删除文件夹
                        shutil.rmtree(file_path)
                        results.append(f"  {file_name}: 文件夹删除成功")
                        success_count += 1

                except PermissionError:
                    results.append(f"  {file_name}: 权限不足，无法删除")
                except OSError as e:
                    results.append(f"  {file_name}: 删除失败 - {str(e)}")
                except Exception as e:
                    results.append(f"  {file_name}: 删除失败 - {str(e)}")

            # 生成结果摘要
            summary = f"🗑️  模式匹配删除操作完成: 成功 {success_count}/{total_count} 个文件\n"
            summary += f"匹配模式: {pattern}\n"
            summary += f"目录: {directory}\n"
            summary += f"删除文件总大小: {total_size_deleted} 字节\n\n"

            return summary + "\n".join(results)

        except Exception as e:
            return f"模式匹配删除时出错: {str(e)}"

    @mcp.tool
    def safe_cleanup(directory: str, days_old: int = 7, file_patterns: List[str] = None, confirm: bool = False):
        """
        安全清理目录：删除指定天数前的旧文件（可指定文件类型）
        :param directory: 要清理的目录
        :param days_old: 删除多少天前的文件（默认7天）
        :param file_patterns: 文件模式列表，如 ['*.tmp', '*.log']，None表示所有文件
        :param confirm: 确认删除标志，设为True才会真正执行删除操作
        :return: 清理操作结果
        """
        try:
            if not os.path.exists(directory):
                return f"错误: 目录 {directory} 不存在"

            if not os.path.isdir(directory):
                return f"错误: {directory} 不是一个目录"

            # 计算时间阈值
            cutoff_time = time.time() - (days_old * 24 * 60 * 60)
            cutoff_date = datetime.fromtimestamp(cutoff_time).strftime('%Y-%m-%d %H:%M:%S')

            # 查找符合条件的文件
            files_to_delete = []

            if file_patterns is None:
                # 所有文件
                for item in os.listdir(directory):
                    item_path = os.path.join(directory, item)
                    if os.path.isfile(item_path) and os.path.getmtime(item_path) < cutoff_time:
                        files_to_delete.append(item_path)
            else:
                # 按模式匹配
                for pattern in file_patterns:
                    search_path = os.path.join(directory, pattern)
                    matched_files = glob.glob(search_path)
                    for file_path in matched_files:
                        if os.path.isfile(file_path) and os.path.getmtime(file_path) < cutoff_time:
                            files_to_delete.append(file_path)

            if not files_to_delete:
                return f"在 {directory} 中未找到 {days_old} 天前的旧文件"

            # 去重
            files_to_delete = list(set(files_to_delete))

            # 安全检查：如果没有确认，只显示要删除的文件
            if not confirm:
                preview_info = []
                total_size = 0

                for file_path in sorted(files_to_delete):
                    file_name = os.path.basename(file_path)
                    file_size = os.path.getsize(file_path)
                    file_date = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
                    total_size += file_size
                    preview_info.append(f"  {file_name} ({file_size} 字节, 修改时间: {file_date})")

                warning_msg = f"  安全清理预览\n"
                warning_msg += f"目录: {directory}\n"
                warning_msg += f"清理 {days_old} 天前的文件 (早于 {cutoff_date})\n"
                warning_msg += f"文件模式: {file_patterns if file_patterns else '所有文件'}\n"
                warning_msg += f"找到 {len(files_to_delete)} 个旧文件，总大小 {total_size} 字节\n\n"
                warning_msg += "\n".join(preview_info)
                warning_msg += f"\n\n❗ 这是预览模式，文件尚未删除。"
                warning_msg += f"\n如需执行删除，请设置 confirm=True"

                return warning_msg

            # 执行删除
            results = []
            success_count = 0
            total_size_deleted = 0

            for file_path in sorted(files_to_delete):
                file_name = os.path.basename(file_path)

                try:
                    file_size = os.path.getsize(file_path)
                    file_date = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
                    os.remove(file_path)
                    total_size_deleted += file_size
                    results.append(f"  {file_name}: 删除成功 ({file_size} 字节, {file_date})")
                    success_count += 1

                except PermissionError:
                    results.append(f"  {file_name}: 权限不足，无法删除")
                except Exception as e:
                    results.append(f"  {file_name}: 删除失败 - {str(e)}")

            # 生成结果摘要
            summary = f"🧹 安全清理操作完成: 成功 {success_count}/{len(files_to_delete)} 个文件\n"
            summary += f"目录: {directory}\n"
            summary += f"清理标准: {days_old} 天前的文件\n"
            summary += f"文件模式: {file_patterns if file_patterns else '所有文件'}\n"
            summary += f"删除文件总大小: {total_size_deleted} 字节\n\n"

            return summary + "\n".join(results)

        except Exception as e:
            return f"安全清理时出错: {str(e)}"