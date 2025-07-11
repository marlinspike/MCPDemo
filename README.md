# MCP Server Demo: YouTube Transcript & SQLite DB

This project demonstrates how an MCP (Model Context Protocol) server can inject functionality into an application without requiring the app to take any dependencies on the resource type. It provides two example MCP servers:

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
  - Get all tracks for a given artist name (using a prompt-generated SQL statement).
- **Usage:**
  - Ensure `chinook.db` is present in the project directory.
  - Run the server: `uv run mcp dev sqlite_server.py`
  - Use the provided tools to query artists, genres, or tracks.

## Project Structure

- `yt.py` — YouTube transcript MCP server
- `sqlite_server.py` — SQLite Chinook DB MCP server
- `chinook.db` — SQLite database file
- `pyproject.toml` — Project dependencies

## Requirements

- Python 3.13+
- Install dependencies:
  ```sh
  uv pip install -r requirements.txt
  # or, if using pyproject.toml:
  uv pip install .
  ```

## Notes
- This project is for demonstration purposes and is not production-hardened.
- The MCP servers use the [fastmcp](https://pypi.org/project/fastmcp/) and [mcp](https://pypi.org/project/mcp/) libraries.
- No direct dependency on the resource type is required in the consuming app.

---

Feel free to extend these servers or add new MCP tools for other resource types!
