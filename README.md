# 🗂️ Valkyrie - 智能文件管理 MCP 服务器

一个基于 **MCP (Model Context Protocol)** 协议的模块化文件管理工具集，提供强大的文件操作、OCR识别等功能。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastMCP](https://img.shields.io/badge/FastMCP-Latest-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ 项目特色

- 🏗️ **模块化架构** - 代码结构清晰，易于维护和扩展
- 🔧 **11个专业工具** - 覆盖文件管理的各个方面
- 🤖 **MCP协议支持** - 与AI助手无缝集成
- 📝 **OCR识别** - 支持图片和PDF文字提取
- ⚙️ **配置管理** - 支持环境变量配置
- 🛡️ **安全设计** - 删除操作需要确认，预览机制

## 📁 项目结构

```
Valkyrie/
├── mcp/
│   ├── server.py              # 🚀 MCP服务器主入口
│   ├── client.py              # 📞 客户端连接器
│   ├── config/                # ⚙️ 配置管理
│   │   ├── __init__.py
│   │   └── settings.py        # 🔧 集中配置
│   └── tools/                 # 🛠️ 工具模块集合
│       ├── __init__.py        # 📦 工具注册器
│       ├── file_listing.py    # 📋 文件列表和查找
│       ├── file_operations.py # 🔄 文件移动操作
│       ├── file_deletion.py   # 🗑️ 文件删除管理
│       ├── file_rename.py     # ✏️ 文件重命名
│       └── ocr_tools.py       # 👁️ OCR文字识别
├── data/                      # 📂 示例数据目录
└── README.md                  # 📖 项目文档
```

## 🛠️ 工具清单

### 📋 文件列表与查找 (2个工具)
- **`list_files`** - 列出目录下所有文件和文件夹
- **`find_files`** - 根据模式查找文件（支持通配符）

### 🔄 文件移动操作 (2个工具)
- **`move_files`** - 移动单个或批量文件/文件夹
- **`move_files_by_pattern`** - 根据模式批量移动文件

### 🗑️ 文件删除管理 (3个工具)
- **`delete_files`** - 删除指定文件/文件夹（安全确认）
- **`delete_files_by_pattern`** - 根据模式批量删除文件
- **`safe_cleanup`** - 安全清理旧文件（按时间和模式）

### ✏️ 文件重命名 (3个工具)
- **`rename_file`** - 重命名单个文件
- **`batch_rename_files`** - 批量重命名（支持模式）
- **`rename_with_rules`** - 基于规则的智能重命名

### 👁️ OCR文字识别 (1个工具)
- **`ocr_recognize`** - 从图片/PDF提取文字内容

## 🚀 快速开始

### 1. 环境要求

```bash
Python 3.10+
pip install fastmcp openai requests
```

### 2. 安装依赖

```bash
# 克隆项目
git clone <your-repo-url>
cd Valkyrie

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置设置

创建环境变量或修改 `mcp/config/settings.py`：

```bash
# 可选：设置API密钥（如果使用OCR功能）
export DEEPSEEK_API_KEY="your-api-key"
export DEEPSEEK_BASE_URL="https://api.deepseek.com"
export DEEPSEEK_MODEL="deepseek-chat"
```

### 4. 启动服务器

```bash
# 启动MCP服务器
cd mcp
python server.py
```

### 5. 使用客户端

```bash
# 连接到MCP服务器
python client.py
```

## 💡 使用示例

### 文件管理操作

```python
# 列出目录文件
list_files(directory="./data")

# 查找PDF文件
find_files(directory="./data", pattern="*.pdf")

# 移动所有PDF到新目录
move_files_by_pattern(
    source_directory="./data", 
    pattern="*.pdf", 
    target_directory="./documents"
)

# 安全删除临时文件（预览模式）
delete_files_by_pattern(
    directory="./temp", 
    pattern="*.tmp", 
    confirm=False  # 预览模式
)

# 批量重命名文件
batch_rename_files(
    file_paths=["file1.txt", "file2.txt"],
    rename_pattern="document_{index:03d}",
    keep_extension=True
)
```

### OCR文字识别

```python
# 识别图片中的文字
ocr_recognize(
    file_path="./data/image.jpg",
    output_json_path="./result.json"
)

# 识别PDF文档
ocr_recognize(file_path="./data/document.pdf")
```

## ⚙️ 配置说明

### 基础配置 (`mcp/config/settings.py`)

```python
class Config:
    # API配置
    DEEPSEEK_API_KEY = "your-api-key"
    DEEPSEEK_BASE_URL = "https://api.deepseek.com"
    DEFAULT_MODEL = "deepseek-chat"
    
    # MCP配置
    DEFAULT_MCP_SCRIPT = "server.py"
    
    # 支持环境变量覆盖
    @classmethod
    def get_api_key(cls):
        return os.getenv("DEEPSEEK_API_KEY", cls.DEEPSEEK_API_KEY)
```

### 环境变量支持

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DEEPSEEK_API_KEY` | API密钥 | 配置文件中的值 |
| `DEEPSEEK_BASE_URL` | API基础URL | `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | 使用的模型 | `deepseek-chat` |

## 🔒 安全特性

### 删除保护机制
- **预览模式** - 所有删除操作默认为预览模式
- **确认机制** - 需要明确设置 `confirm=True` 才会真正删除
- **详细信息** - 显示要删除的文件大小、数量等信息

### 文件操作安全
- **路径验证** - 检查文件路径的合法性
- **权限检查** - 处理权限不足的情况
- **错误处理** - 完善的异常处理机制

## 🧩 模块化设计

### 工具模块独立性
每个工具模块都是独立的，可以：
- 🔧 **独立维护** - 修改某个功能不影响其他模块
- 📦 **独立使用** - 可以在其他项目中重用
- 🔍 **独立测试** - 便于单元测试和调试

### 扩展新工具
添加新工具只需要：

1. 在 `tools/` 目录创建新模块
2. 实现工具函数并用 `@mcp.tool` 装饰
3. 在 `tools/__init__.py` 中注册

```python
# tools/new_tool.py
def register_new_tools(mcp):
    @mcp.tool
    def new_function():
        """新工具功能"""
        pass

# tools/__init__.py
from .new_tool import register_new_tools

def register_all_tools(mcp):
    # ... 其他工具
    register_new_tools(mcp)
```

## 📊 性能特性

- ⚡ **异步处理** - 支持异步文件操作
- 🚀 **批量操作** - 高效的批量文件处理
- 💾 **内存优化** - 合理的内存使用策略
- 📈 **可扩展** - 支持大规模文件操作

## 🤝 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📝 更新日志

### v1.0.0 (当前版本)
- ✨ 模块化架构重构
- 🛠️ 11个专业文件管理工具
- 👁️ OCR文字识别功能
- ⚙️ 配置管理系统
- 🔒 安全删除机制

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 支持

如有问题或建议，请：
- 📧 提交 Issue
- 💬 参与 Discussions
- 📖 查看文档

---

**⭐ 如果这个项目对你有帮助，请给个星标支持！**