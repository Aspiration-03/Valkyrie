"""
1.创建mcp实例
2.创建函数
3.@mcp.tool
4.run
"""

from fastmcp import FastMCP

mcp = FastMCP()


@mcp.tool
def get_weather(city: str):
    """
    获取对应城市天气
    :param city: 城市
    :return: 城市天气描述
    """
    return f"{city}今天天气晴，18摄氏度"


if __name__ == "__main__":
    mcp.run()
