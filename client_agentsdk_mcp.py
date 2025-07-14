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

    # Debug print to verify environment variables
    print("Endpoint:", endpoint)
    print("API Key:", api_key)
    print("Deployment:", deployment)
    print("API Version:", api_version)

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

    # Use MCPServerStdio for local FastMCP servers, using params with command and args
    sqlite_server = MCPServerStdio(params={"command": "python", "args": ["sqlite_server.py"]})
    yt_server = MCPServerStdio(params={"command": "python", "args": ["yt.py"]})

    await sqlite_server.connect()
    await yt_server.connect()

    # Use deployment name as the model for the Agents SDK
    agent = Agent(
        name="MCP Assistant",
        instructions="You are a helpful assistant. Use the available tools to help the user.",
        model=deployment,
        mcp_servers=[sqlite_server, yt_server],
    )

    #runner = Runner()

    print("Type a prompt (blank to exit):")
    while True:
        prompt = input("You: ").strip()
        if not prompt:
            break
        response = await Runner.run(agent, prompt)
        print("Model:", response)

if __name__ == "__main__":
    asyncio.run(main())
