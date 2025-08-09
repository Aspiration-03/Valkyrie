"""
文件重命名工具模块
"""

import os
import json
import time
from typing import Union, List, Dict
from datetime import datetime


def register_file_rename_tools(mcp):
    """注册文件重命名相关工具"""
    
    @mcp.tool
    def rename_file(file_path: str, new_name: str, keep_extension: bool = True):
        """
        重命名指定文件，支持保持原扩展名或完全自定义新名称
        :param file_path: 要重命名的文件完整路径
        :param new_name: 新的文件名（可包含或不包含扩展名）
        :param keep_extension: 是否保持原文件扩展名（默认True）
        :return: 重命名操作结果
        """
        try:
            # 检查源文件是否存在
            if not os.path.exists(file_path):
                return json.dumps({
                    "status": "error",
                    "message": f"源文件不存在: {file_path}",
                    "old_path": file_path,
                    "new_path": None
                }, ensure_ascii=False)

            if not os.path.isfile(file_path):
                return json.dumps({
                    "status": "error",
                    "message": f"路径不是文件: {file_path}",
                    "old_path": file_path,
                    "new_path": None
                }, ensure_ascii=False)

            # 获取文件信息
            file_dir = os.path.dirname(file_path)
            old_filename = os.path.basename(file_path)
            old_name, old_extension = os.path.splitext(old_filename)

            # 处理新文件名
            if keep_extension:
                # 保持原扩展名
                new_name_without_ext = os.path.splitext(new_name)[0]  # 移除可能包含的扩展名
                final_new_name = new_name_without_ext + old_extension
            else:
                # 使用完整的新名称
                final_new_name = new_name

            # 构建新的完整路径
            new_file_path = os.path.join(file_dir, final_new_name)

            # 检查新文件名是否已存在
            if os.path.exists(new_file_path):
                return json.dumps({
                    "status": "error",
                    "message": f"目标文件名已存在: {final_new_name}",
                    "old_path": file_path,
                    "new_path": new_file_path,
                    "old_name": old_filename,
                    "new_name": final_new_name
                }, ensure_ascii=False)

            # 检查新文件名是否包含非法字符
            illegal_chars = ['<', '>', ':', '"', '|', '?', '*']
            if any(char in final_new_name for char in illegal_chars):
                return json.dumps({
                    "status": "error",
                    "message": f"文件名包含非法字符: {final_new_name}",
                    "illegal_chars": illegal_chars,
                    "old_path": file_path,
                    "new_path": None
                }, ensure_ascii=False)

            # 执行重命名操作
            try:
                os.rename(file_path, new_file_path)

                # 获取文件大小信息
                file_size = os.path.getsize(new_file_path)

                return json.dumps({
                    "status": "success",
                    "message": f"文件重命名成功",
                    "old_path": file_path,
                    "new_path": new_file_path,
                    "old_name": old_filename,
                    "new_name": final_new_name,
                    "file_size": file_size,
                    "file_size_readable": f"{file_size} 字节",
                    "directory": file_dir,
                    "extension_kept": keep_extension,
                    "extension": old_extension if keep_extension else os.path.splitext(final_new_name)[1]
                }, ensure_ascii=False, indent=2)

            except PermissionError:
                return json.dumps({
                    "status": "error",
                    "message": "权限不足，无法重命名文件",
                    "old_path": file_path,
                    "new_path": new_file_path
                }, ensure_ascii=False)
            except OSError as e:
                return json.dumps({
                    "status": "error",
                    "message": f"重命名失败: {str(e)}",
                    "old_path": file_path,
                    "new_path": new_file_path
                }, ensure_ascii=False)

        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"重命名操作时出错: {str(e)}",
                "old_path": file_path,
                "new_path": None
            }, ensure_ascii=False)

    @mcp.tool
    def batch_rename_files(file_paths: Union[str, List[str]], rename_pattern: str, keep_extension: bool = True):
        """
        批量重命名文件，支持多种命名模式
        :param file_paths: 要重命名的文件路径列表（可以是JSON字符串或列表）
        :param rename_pattern: 重命名模式，支持占位符：
                              - {index}: 序号 (1, 2, 3...)
                              - {index:03d}: 带前导零的序号 (001, 002, 003...)
                              - {old_name}: 原文件名（不含扩展名）
                              - {timestamp}: 当前时间戳
                              例如: "document_{index:03d}", "{old_name}_backup", "file_{timestamp}"
        :param keep_extension: 是否保持原文件扩展名（默认True）
        :return: 批量重命名操作结果
        """
        try:
            # 处理输入参数
            if isinstance(file_paths, str):
                try:
                    # 尝试解析JSON字符串
                    parsed = json.loads(file_paths)
                    if isinstance(parsed, dict) and "file_paths" in parsed:
                        file_paths = parsed["file_paths"]
                    elif isinstance(parsed, list):
                        file_paths = parsed
                    else:
                        file_paths = [file_paths]
                except:
                    file_paths = [file_paths]

            if not file_paths:
                return json.dumps({
                    "status": "error",
                    "message": "文件路径列表为空",
                    "results": []
                }, ensure_ascii=False)

            results = []
            success_count = 0
            total_count = len(file_paths)
            timestamp = int(time.time())

            for index, file_path in enumerate(file_paths, 1):
                try:
                    # 检查源文件是否存在
                    if not os.path.exists(file_path):
                        results.append({
                            "file_path": file_path,
                            "status": "error",
                            "message": "文件不存在"
                        })
                        continue

                    if not os.path.isfile(file_path):
                        results.append({
                            "file_path": file_path,
                            "status": "error",
                            "message": "路径不是文件"
                        })
                        continue

                    # 获取文件信息
                    file_dir = os.path.dirname(file_path)
                    old_filename = os.path.basename(file_path)
                    old_name, old_extension = os.path.splitext(old_filename)

                    # 生成新文件名
                    new_name = rename_pattern.format(
                        index=index,
                        old_name=old_name,
                        timestamp=timestamp
                    )

                    # 处理扩展名
                    if keep_extension:
                        final_new_name = new_name + old_extension
                    else:
                        final_new_name = new_name

                    # 构建新的完整路径
                    new_file_path = os.path.join(file_dir, final_new_name)

                    # 检查新文件名是否已存在
                    if os.path.exists(new_file_path):
                        results.append({
                            "file_path": file_path,
                            "status": "error",
                            "message": f"目标文件名已存在: {final_new_name}",
                            "old_name": old_filename,
                            "new_name": final_new_name
                        })
                        continue

                    # 执行重命名
                    os.rename(file_path, new_file_path)

                    file_size = os.path.getsize(new_file_path)

                    results.append({
                        "file_path": file_path,
                        "status": "success",
                        "message": "重命名成功",
                        "old_path": file_path,
                        "new_path": new_file_path,
                        "old_name": old_filename,
                        "new_name": final_new_name,
                        "file_size": file_size,
                        "index": index
                    })

                    success_count += 1

                except PermissionError:
                    results.append({
                        "file_path": file_path,
                        "status": "error",
                        "message": "权限不足，无法重命名"
                    })
                except Exception as e:
                    results.append({
                        "file_path": file_path,
                        "status": "error",
                        "message": f"重命名失败: {str(e)}"
                    })

            # 返回结果摘要
            summary = {
                "status": "completed",
                "message": f"批量重命名完成: 成功 {success_count}/{total_count} 个文件",
                "total_files": total_count,
                "success_count": success_count,
                "failed_count": total_count - success_count,
                "rename_pattern": rename_pattern,
                "keep_extension": keep_extension,
                "timestamp": timestamp,
                "results": results
            }

            return json.dumps(summary, ensure_ascii=False, indent=2)

        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"批量重命名时出错: {str(e)}",
                "results": []
            }, ensure_ascii=False)

    @mcp.tool
    def rename_with_rules(file_paths: Union[str, List[str]], rules: Dict[str, str]):
        """
        根据规则批量重命名文件，支持文本替换、大小写转换等
        :param file_paths: 要重命名的文件路径列表
        :param rules: 重命名规则字典，支持的规则：
                     - "replace": {"old_text": "new_text"} 文本替换
                     - "case": "lower/upper/title" 大小写转换
                     - "prefix": "前缀文本" 添加前缀
                     - "suffix": "后缀文本" 添加后缀（在扩展名前）
                     - "remove_chars": "要移除的字符" 移除指定字符
        :return: 基于规则的重命名结果
        """
        try:
            # 处理输入参数
            if isinstance(file_paths, str):
                try:
                    parsed = json.loads(file_paths)
                    if isinstance(parsed, dict) and "file_paths" in parsed:
                        file_paths = parsed["file_paths"]
                    elif isinstance(parsed, list):
                        file_paths = parsed
                    else:
                        file_paths = [file_paths]
                except:
                    file_paths = [file_paths]

            if not file_paths:
                return json.dumps({
                    "status": "error",
                    "message": "文件路径列表为空",
                    "results": []
                }, ensure_ascii=False)

            results = []
            success_count = 0
            total_count = len(file_paths)

            for file_path in file_paths:
                try:
                    if not os.path.exists(file_path) or not os.path.isfile(file_path):
                        results.append({
                            "file_path": file_path,
                            "status": "error",
                            "message": "文件不存在或不是文件"
                        })
                        continue

                    # 获取文件信息
                    file_dir = os.path.dirname(file_path)
                    old_filename = os.path.basename(file_path)
                    old_name, extension = os.path.splitext(old_filename)

                    new_name = old_name

                    # 应用规则
                    if "replace" in rules and isinstance(rules["replace"], dict):
                        for old_text, new_text in rules["replace"].items():
                            new_name = new_name.replace(old_text, new_text)

                    if "case" in rules:
                        case_rule = rules["case"].lower()
                        if case_rule == "lower":
                            new_name = new_name.lower()
                        elif case_rule == "upper":
                            new_name = new_name.upper()
                        elif case_rule == "title":
                            new_name = new_name.title()

                    if "remove_chars" in rules:
                        chars_to_remove = rules["remove_chars"]
                        for char in chars_to_remove:
                            new_name = new_name.replace(char, "")

                    if "prefix" in rules:
                        new_name = rules["prefix"] + new_name

                    if "suffix" in rules:
                        new_name = new_name + rules["suffix"]

                    # 构建新文件名
                    final_new_name = new_name + extension
                    new_file_path = os.path.join(file_dir, final_new_name)

                    # 如果名称没有变化，跳过
                    if old_filename == final_new_name:
                        results.append({
                            "file_path": file_path,
                            "status": "skipped",
                            "message": "文件名未发生变化",
                            "old_name": old_filename,
                            "new_name": final_new_name
                        })
                        continue

                    # 检查目标文件是否存在
                    if os.path.exists(new_file_path):
                        results.append({
                            "file_path": file_path,
                            "status": "error",
                            "message": f"目标文件已存在: {final_new_name}",
                            "old_name": old_filename,
                            "new_name": final_new_name
                        })
                        continue

                    # 执行重命名
                    os.rename(file_path, new_file_path)

                    results.append({
                        "file_path": file_path,
                        "status": "success",
                        "message": "重命名成功",
                        "old_path": file_path,
                        "new_path": new_file_path,
                        "old_name": old_filename,
                        "new_name": final_new_name
                    })

                    success_count += 1

                except Exception as e:
                    results.append({
                        "file_path": file_path,
                        "status": "error",
                        "message": f"处理失败: {str(e)}"
                    })

            summary = {
                "status": "completed",
                "message": f"规则重命名完成: 成功 {success_count}/{total_count} 个文件",
                "total_files": total_count,
                "success_count": success_count,
                "failed_count": total_count - success_count,
                "skipped_count": len([r for r in results if r.get("status") == "skipped"]),
                "applied_rules": rules,
                "results": results
            }

            return json.dumps(summary, ensure_ascii=False, indent=2)

        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"规则重命名时出错: {str(e)}",
                "results": []
            }, ensure_ascii=False)