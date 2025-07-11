import os
import asyncio
import json
import traceback
from dotenv import load_dotenv
from openai import AsyncOpenAI
from fastmcp import Client

def mcp_tool_to_openai(tool):
    if hasattr(tool, 'model_json_schema') and callable(tool.model_json_schema):
        schema = tool.model_json_schema()
    elif hasattr(tool, 'schema') and callable(tool.schema):
        schema = tool.schema()
    else:
        schema = getattr(tool, 'schema', {})
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": getattr(tool, "description", ""),
            "parameters": schema,
        }
    }

def serialize_tool_result(result):
    if hasattr(result, 'model_dump'):
        return result.model_dump()
    elif hasattr(result, 'dict'):
        return result.dict()
    elif isinstance(result, (list, dict, str, int, float, bool)):
        return result
    else:
        return str(result)

async def main():
    load_dotenv()
    endpoint   = os.getenv("AZURE_OPENAI_ENDPOINT").rstrip("/")
    api_key    = os.getenv("AZURE_OPENAI_KEY")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    sqlite_url = os.getenv("SQLITE_MCP_URL")
    yt_url     = os.getenv("YT_MCP_URL")
    api_version = "preview"

    openai_client = AsyncOpenAI(
        api_key=api_key,
        base_url=f"{endpoint}/openai/v1/",
        default_query={"api-version": api_version},
    )

    async with Client(sqlite_url) as sqlite_mcp, Client(yt_url) as yt_mcp:
        sqlite_tools = await sqlite_mcp.list_tools()
        yt_tools = await yt_mcp.list_tools()
        all_tools = sqlite_tools + yt_tools
        tools = [mcp_tool_to_openai(t) for t in all_tools]

        print("Type a prompt (blank to exit):")
        while True:
            prompt = input("You: ").strip()
            if not prompt:
                break

            response = await openai_client.chat.completions.create(
                model=deployment,
                messages=[{"role": "user", "content": prompt}],
                tools=tools
            )
            choice = response.choices[0].message
            if choice.tool_calls:
                tool_call = choice.tool_calls[0]
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                print(f"Tool Used: {tool_name}, Arguments: {tool_args}")
                # Debug: print before calling the tool
                if tool_name in [t.name for t in sqlite_tools]:
                    print(f"[DEBUG] Calling sqlite tool '{tool_name}' with arguments: {tool_args}")
                else:
                    print(f"[DEBUG] Calling yt tool '{tool_name}' with arguments: {tool_args}")
                try:
                    if tool_name in [t.name for t in sqlite_tools]:
                        tool_resp = await sqlite_mcp.call_tool(tool_name, tool_args)
                    else:
                        tool_resp = await yt_mcp.call_tool(tool_name, tool_args)
                    # Debug: print the raw return value
                    print(f"[DEBUG] Raw tool return value: {tool_resp}")
                    tool_text = serialize_tool_result(tool_resp.data if hasattr(tool_resp, 'data') else tool_resp)
                except Exception as e:
                    print("[DEBUG] Exception occurred during tool call:")
                    traceback.print_exc()
                    tool_text = f"[Tool error: {e}]"

                final = await openai_client.chat.completions.create(
                    model=deployment,
                    messages=[
                        {"role": "user", "content": prompt},
                        {"role": "function", "name": tool_name, "content": json.dumps(tool_text)}
                    ]
                )
                reply = final.choices[0].message.content
            else:
                reply = choice.content
            print("Model:", reply)

if __name__ == "__main__":
    asyncio.run(main())
