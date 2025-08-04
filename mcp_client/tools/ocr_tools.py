"""
OCR文字识别工具模块
"""

import os
import json
import requests
from pathlib import Path


def register_ocr_tools(mcp):
    """注册OCR相关工具"""
    
    @mcp.tool
    def ocr_recognize(file_path: str, output_json_path: str = None):
        """
        OCR文字识别工具：从图片或PDF文件中提取和识别文字内容，支持中英文识别

        主要功能：
        - 图片文字识别：从JPG、PNG图片中提取文字
        - PDF文字识别：从PDF文档中识别和提取文字内容
        - 文字内容提取：将图片或PDF中的文字转换为可编辑的文本
        - 多语言支持：支持中文、英文等多种语言的文字识别

        适用场景：
        - 需要从图片中提取文字时使用此工具
        - 需要识别PDF中的文字内容时使用此工具
        - 需要将扫描件转换为文字时使用此工具
        :param file_path: 要识别的文件路径（支持JPG、PNG、PDF格式）
        :param output_json_path: 输出JSON文件路径（可选，默认为源文件名_ocr_result.json）
        :return: OCR识别结果
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return f"错误: 文件 {file_path} 不存在"

            # 检查文件格式
            file_extension = Path(file_path).suffix.lower()
            if file_extension not in [".jpg", ".jpeg", ".png", ".pdf"]:
                return f"错误: 不支持的文件格式 {file_extension}，仅支持 JPG、PNG、PDF"

            # 准备上传文件
            with open(file_path, 'rb') as file:
                files = {
                    'file': (os.path.basename(file_path), file, 'application/octet-stream')
                }

                # 发送POST请求到OCR服务
                response = requests.post(
                    'https://server0.d5data.tech:20110/ocr',
                    files=files,
                    timeout=600  # 设置60秒超时
                )

            # 检查响应状态
            if response.status_code != 200:
                return f"错误: OCR服务返回状态码 {response.status_code}, 错误信息: {response.text}"

            # 解析JSON响应
            try:
                ocr_result = response.json()
            except json.JSONDecodeError:
                return f"错误: OCR服务返回的不是有效的JSON格式"

            # 生成输出文件路径
            if output_json_path is None:
                source_file = Path(file_path)
                output_json_path = source_file.parent / f"{source_file.stem}_ocr_result.json"

            # 保存结果到JSON文件
            try:
                with open(output_json_path, 'w', encoding='utf-8') as json_file:
                    json.dump(ocr_result, json_file, ensure_ascii=False, indent=2)
            except Exception as e:
                return f"错误: 保存JSON文件失败 - {str(e)}"

            # 返回处理结果
            result_summary = {
                "status": "成功",
                "source_file": file_path,
                "output_json": str(output_json_path),
                "ocr_status": ocr_result.get("status", "unknown"),
                "filename": ocr_result.get("filename", "unknown")
            }

            # 如果OCR成功，添加结果摘要
            if ocr_result.get("status") == "success" and "results" in ocr_result:
                results = ocr_result["results"]
                if isinstance(results, dict):
                    result_summary["text_length"] = len(str(results.get("text", "")))
                    result_summary["pages_processed"] = len(results.get("pages", []))
                elif isinstance(results, str):
                    result_summary["text_length"] = len(results)

            return f"✅ OCR识别完成!\n文件: {file_path}\n结果已保存到: {output_json_path}\n状态: {result_summary['ocr_status']}\n详细信息: {json.dumps(result_summary, ensure_ascii=False, indent=2)}"

        except requests.exceptions.Timeout:
            return "错误: OCR服务请求超时，请稍后重试"
        except requests.exceptions.ConnectionError:
            return "错误: 无法连接到OCR服务，请检查网络连接"
        except Exception as e:
            return f"OCR识别时出错: {str(e)}"