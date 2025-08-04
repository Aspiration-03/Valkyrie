import asyncio
import json

from fastmcp import Client
from openai import OpenAI

from mcp.config import Config


class UserClient:
    def __init__(self, script=None, model=None):
        # 使用配置类获取默认值
        self.model = model or Config.get_model()
        self.mcp_client = Client(script or Config.DEFAULT_MCP_SCRIPT)
        self.llm_client = OpenAI(
            base_url=Config.get_base_url(),
            api_key=Config.get_api_key(),
        )
        # 保持完整的对话历史
        self.conversation_history = [
            {
                "role": "system",
                "content": Config.SYSTEM_PROMPT,
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
            print(f"\n[调用工具] {tool_name} 参数: {arguments}")

            result = await self.mcp_client.call_tool(tool_name, arguments)
            print(f"[工具结果] {result}")
            return result
        except Exception as e:
            print(f"工具执行失败: {e}")
            return f"工具执行错误: {str(e)}"

    async def chat(self, user_message: str):
        """
        单轮对话，但保持历史记录
        """
        async with self.mcp_client:
            if not self.tools:
                self.tools = await self.prepare_tools()
                print(f"可用工具: {[t['function']['name'] for t in self.tools]}")

            # 添加用户消息到历史记录
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })

            print(f"\n[用户消息] {user_message}")
            print(f"[当前历史记录长度] {len(self.conversation_history)} 条消息")

            # 使用完整的对话历史
            response = await asyncio.to_thread(
                lambda: self.llm_client.chat.completions.create(
                    model=self.model,
                    messages=self.conversation_history,
                    tools=self.tools,
                    tool_choice="auto",
                )
            )

            response_message = response.choices[0].message
            print(f"\n[AI响应] {response_message}")

            # 添加AI响应到历史记录
            self.conversation_history.append({
                "role": "assistant",
                "content": response_message.content,
                "tool_calls": response_message.tool_calls
            })

            # 处理工具调用
            if response_message.tool_calls:
                for tool_call in response_message.tool_calls:
                    tool_result = await self.execute_tool(tool_call)
                    # 添加工具结果到历史记录
                    self.conversation_history.append({
                        "role": "tool",
                        "content": str(tool_result),
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                    })

                # 获取最终响应
                second_response = await asyncio.to_thread(
                    lambda: self.llm_client.chat.completions.create(
                        model=self.model,
                        messages=self.conversation_history,
                    )
                )
                final_message = second_response.choices[0].message

                # 添加最终响应到历史记录
                self.conversation_history.append({
                    "role": "assistant",
                    "content": final_message.content
                })

                print(f"\n[AI最终回复] {final_message.content}")
                return final_message.content

            print(f"\n[AI回复] {response_message.content}")
            return response_message.content

    def clear_history(self):
        """清除对话历史（保留系统提示）"""
        self.conversation_history = self.conversation_history[:1]  # 只保留system消息
        print("对话历史已清除")

    def show_history(self):
        """显示对话历史"""
        print("\n=== 对话历史 ===")
        for i, msg in enumerate(self.conversation_history):
            role = msg["role"]
            content = msg.get("content", "")
            if role == "system":
                print(f"{i}: [系统] {content[:100]}...")
            elif role == "user":
                print(f"{i}: [用户] {content}")
            elif role == "assistant":
                print(f"{i}: [助手] {content}")
            elif role == "tool":
                print(f"{i}: [工具:{msg.get('name')}] {content[:100]}...")
        print("================")


async def main():
    user_client = UserClient()

    print("📁 智能助手启动，输入 'quit' 退出")
    print("💡 支持多轮对话，助手会记住之前的操作")
    print("命令: 'clear' 清除历史, 'history' 查看历史")
    print("=" * 50)

    while True:
        try:
            user_input = input("\n👤 USER: ")

            if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                print("👋 再见!")
                break

            if user_input.lower() == 'clear':
                user_client.clear_history()
                continue

            if user_input.lower() == 'history':
                user_client.show_history()
                continue

            if not user_input.strip():
                continue

            print("🤖 处理中...")
            response = await user_client.chat(user_input)
            print(f"\n=== 助手回复 ===")
            print(response)

        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())