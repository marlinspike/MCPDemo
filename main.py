# main.py
import asyncio
from mcp.server.fastmcp import FastMCP

from yt import mcp as yt_mcp
from sqlite_server import mcp as sqlite_mcp

mcp = FastMCP(name="composed_server")

async def setup():
    await mcp.import_server(yt_mcp)
    await mcp.import_server(sqlite_mcp)

async def main():
    await setup()
    # now the subservers' tools are available
    mcp.run(transport="stdio")

if __name__ == "__main__":
    asyncio.run(main())
