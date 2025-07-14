# MCP Server Demo: YouTube Transcript & SQLite DB

This project demonstrates how an MCP (Model Context Protocol) server can inject functionality into an application without requiring the app to take any dependencies on the resource type. It provides two example MCP servers and a sample OpenAI MCP client.

## 1. YouTube Transcript Extraction (`yt.py`)

- **Purpose:** Extracts and formats transcripts from YouTube videos for LLM consumption.
- **How it works:**
  - Accepts a YouTube video URL.
  - Extracts the video ID and fetches the transcript using the `youtube-transcript-api`.
  - Formats each transcript entry as `[MM:SS] Text` for easy reading and processing.
- **Usage:**
  - Run the server in debug mode: `uv run mcp dev yt.py`
  - Use the `fetch_youtube_transcript` tool to get a formatted transcript from a YouTube URL.

## 2. SQLite Chinook DB Interaction (`sqlite_server.py`)

- **Purpose:** Provides tools to interact with the [Chinook sample database](https://github.com/lerocha/chinook-database), a sample SQLite music database.
- **Features:**
  - List all artists and genres.
  - Run arbitrary `SELECT` SQL queries (read-only).
  - Get all tracks for a given artist (using a prompt-generated SQL statement).
  - Get artist info (using the argument `name`).
- **Usage:**
  - Ensure `chinook.db` is present in the project directory.
  - Run the server: `uv run mcp dev sqlite_server.py`
  - Use the provided tools to query artists, genres, or tracks. For artist info and tracks, use the argument `name` (not `artist_name`).

  When you run #4 (client_agentsdk_mcp.py), you'll see that you only really need two tools, run_sql() and get_sqlite_schema(). The `run_sql()` tool allows you to execute any SQL query, while `get_sqlite_schema()` provides the schema of the Chinook database, which allows the LLM to understand the structure of the data, and construct appropriate queries! The other methods are there for show and tell, but are not strictly necessary for the client to function.

## 3. OpenAI MCP Client (`client.py`)

- **Purpose:** Allows conversational interaction with both MCP servers via OpenAI, using tool schemas for argument validation.
- **Usage:**
  - Configure your `.env` file (see below).
  - Run: `python client.py`
  - Type prompts such as: `get me info about the artist "AC/DC" from sqlite`

## 4. OpenAI MCP Client with Agent SDK (`client_agentsdk_mcp.py`)

- **Purpose:** Provides an OpenAI MCP client using the Agent SDK, supporting multi-agent orchestration and tool usage.
- **Features:**
  - Uses Azure OpenAI via environment variables for endpoint, key, deployment, and API version.
  - Launches two MCP tool servers: `sqlite_server.py` and `yt.py`.
  - Defines three agents:
    - **MCP Agent:** Uses both MCP tool servers for database and YouTube operations.
    - **Pirate Agent:** Answers in pirate slang (for fun, no tools).
    - **Orchestrator Agent:** Routes user prompts to the appropriate agent (MCP, Pirate, or itself) based on the request.
  - Interactive prompt loop: type a prompt and get a response from the orchestrator or a specialized agent.
- **Usage:**
  - Configure your `.env` file as described below.
  - Run: `python client_agentsdk_mcp.py`
  - Type prompts such as:
    - `get me info about the artist "AC/DC" from sqlite`
    - `talk like a pirate`
    - `get the transcript for https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=RDdQw4w9WgXcQ&start_radio=1`

## Project Structure

- `yt.py` — YouTube transcript MCP server
- `sqlite_server.py` — SQLite Chinook DB MCP server
- `client.py` — OpenAI MCP client for both servers
- `client_agentsdk_mcp.py` — OpenAI MCP client with OpenAI Agent SDK
- `chinook.db` — SQLite database file
- `pyproject.toml` — Project dependencies
- `.env.example` — Example environment configuration

## Requirements

- Python 3.13+
- Install dependencies:
  ```sh
  uv pip install -r requirements.txt
  # or, if using pyproject.toml:
  uv pip install .
  ```

## Environment Setup

Copy `.env.example` to `.env` and fill in the required values:

```
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_KEY=...
AZURE_OPENAI_DEPLOYMENT=...
SQLITE_MCP_URL=http://localhost:8001
YT_MCP_URL=http://localhost:8002
```

- Make sure both MCP servers are running and accessible at the URLs above.

## Notes
- This project is for demonstration purposes and is not production-hardened.
- The MCP servers use the [fastmcp](https://pypi.org/project/fastmcp/) and [mcp](https://pypi.org/project/mcp/) libraries.
- No direct dependency on the resource type is required in the consuming app.

---

Feel free to extend these servers or add new MCP tools for other resource types!
