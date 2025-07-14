import os
import asyncio
import logging
logging.disable(logging.CRITICAL)
from dotenv import load_dotenv
from agents.agent import Agent
from agents.mcp.server import MCPServerStdio
from agents import Runner, set_default_openai_client
from openai import AsyncAzureOpenAI

async def main():
    load_dotenv()
    endpoint   = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key    = os.getenv("AZURE_OPENAI_API_KEY")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")

    if not endpoint or not api_key or not deployment:
        print("One or more required environment variables are missing. Please check your .env file.")
        return

    endpoint = endpoint.rstrip("/")
    # Create OpenAI client using Azure OpenAI
    openai_client = AsyncAzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint,
        azure_deployment=deployment
    )
    set_default_openai_client(openai_client)

    # MCP tools servers
    sqlite_server = MCPServerStdio(params={"command": "python", "args": ["sqlite_server.py"]})
    yt_server = MCPServerStdio(params={"command": "python", "args": ["yt.py"]})
    await sqlite_server.connect()
    await yt_server.connect()

    # MCP Agent (with tools)
    mcp_agent = Agent(
        name="MCP Agent",
        instructions=(
            "You are the MCP Agent. Use the available tools to help the user. Only answer if the orchestrator hands off to you. "
            "When you use a tool, always include the full tool output in your response unless the user specifically asks for a summary."
        ),
        model=deployment,
        mcp_servers=[sqlite_server, yt_server],
    )

    # Pirate Agent (no tools)
    pirate_agent = Agent(
        name="Pirate Agent",
        instructions="You are a pirate. Always answer like a pirate, with nautical slang and pirate accent. Only answer if the orchestrator hands off to you.",
        model=deployment,
        mcp_servers=[],
    )

    # Orchestrator Agent (helpful assistant, can hand off to Pirate or MCP agent)
    orchestrator_agent = Agent(
        name="Orchestrator",
        instructions=(
            "You are a helpful assistant. Handoff to the Pirate Agent for pirate-style answers, "
            "or to the MCP Agent for database/YouTube/tool requests. Otherwise, answer yourself."
        ),
        model=deployment,
        handoffs=[pirate_agent, mcp_agent],  # Use handoffs, not tools
    )

    print("Type a prompt (blank to exit):")
    while True:
        prompt = input("You: ").strip()
        if not prompt:
            break
        response = await Runner.run(orchestrator_agent, prompt)
        print("Model:", response)

if __name__ == "__main__":
    asyncio.run(main())
