import asyncio
import json
from typing import List, Dict
from fastmcp import Client
from openai import OpenAI


class UserClient:
    def __init__(self, script="server.py", model="deepseek-chat"):
        self.model = model
        self.mcp_client = Client(script)
        self.llm_client = OpenAI(
            base_url="https://api.deepseek.com",
            api_key="sk-423742b032364794b29aa00daf12590e",
        )
        self.messages = [
            {
                "role": "system",
                "content": "你是一个AI助手，必须使用提供的工具回答问题。当用户询问需要工具处理的问题时，你必须调用工具。",
            }
        ]
        self.tools = []

    async def prepare_tools(self):
        tools = await self.mcp_client.list_tools()
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                },
            }
            for tool in tools
        ]

    async def execute_tool(self, tool_call):
        try:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"\n[调用工具] {tool_name} 参数: {arguments}")  # 调试输出

            # 这里假设mcp_client有call_tool方法
            result = await self.mcp_client.call_tool(tool_name, arguments)
            print(f"[工具结果] {result}")  # 调试输出
            return result
        except Exception as e:
            print(f"工具执行失败: {e}")
            return f"工具执行错误: {str(e)}"

    async def chat(self, messages: List[Dict]):
        async with self.mcp_client:
            if not self.tools:
                self.tools = await self.prepare_tools()
                print(
                    f"可用工具: {[t['function']['name'] for t in self.tools]}"
                )  # 调试输出

            print("\n[发送给AI的消息]")  # 调试输出
            for msg in messages:
                print(f"{msg['role']}: {msg['content']}")

            response = await asyncio.to_thread(
                lambda: self.llm_client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools,
                    tool_choice="auto",
                )
            )

            response_message = response.choices[0].message
            print(f"\n[AI初始响应] {response_message}")  # 调试输出

            self.messages.append(response_message)

            # 处理工具调用
            if response_message.tool_calls:
                for tool_call in response_message.tool_calls:
                    tool_result = await self.execute_tool(tool_call)
                    self.messages.append(
                        {
                            "role": "tool",
                            "content": str(tool_result),
                            "tool_call_id": tool_call.id,
                            "name": tool_call.function.name,
                        }
                    )

                # 获取最终响应
                second_response = await asyncio.to_thread(
                    lambda: self.llm_client.chat.completions.create(
                        model=self.model,
                        messages=self.messages,
                    )
                )
                final_message = second_response.choices[0].message
                self.messages.append(final_message)
                print(f"\n[AI最终回复] {final_message.content}")  # 最终输出
                return final_message.content

            print(f"\n[AI回复] {response_message.content}")  # 直接输出
            return response_message.content


async def main():
    user_client = UserClient()
    response = await user_client.chat(
        [
            {"role": "user", "content": "杭州今天天气怎么样"},
        ]
    )
    print("\n=== 最终答案 ===")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
