from mcp.server.fastmcp import FastMCP
import sqlite3
from typing import List, Dict, Any

DB_PATH = 'chinook.db'  

mcp = FastMCP("sqlite-server")

# Tool: Get list of artists
@mcp.tool()
def get_artists() -> List[Dict[str, Any]]:
    """Return a list of all artists from the database."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ArtistId, Name FROM artists")
        rows = cursor.fetchall()
        return [{"ArtistId": row[0], "Name": row[1]} for row in rows]

# Tool: Get list of genres
@mcp.tool()
def get_genres() -> List[Dict[str, Any]]:
    """Return a list of all genres from the database."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT GenreId, Name FROM genres")
        rows = cursor.fetchall()
        return [{"GenreId": row[0], "Name": row[1]} for row in rows]

# Tool: Run a SQL SELECT statement
@mcp.tool()
def run_sql(query: str) -> List[Dict[str, Any]]:
    """Run a SELECT SQL statement and return the results as a list of dicts. Only SELECT statements are allowed. Returns blank if no results."""
    if not query.strip().lower().startswith("select"):
        return []
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            if not rows:
                return []
            return [dict(zip(columns, row)) for row in rows]
        except Exception:
            return []

# Prompt: Generate SQL to get tracks by artist name
@mcp.prompt()
def get_tracks_by_artist_prompt(artist_name: str) -> str:
    """Return a SQL statement to get all tracks for a given artist name."""
    return f'''
    SELECT tracks.Name AS TrackName, albums.Title AS AlbumTitle
    FROM tracks
    JOIN albums ON tracks.AlbumId = albums.AlbumId
    JOIN artists ON albums.ArtistId = artists.ArtistId
    WHERE artists.Name = "{artist_name}"
    '''

# Tool: Get tracks by artist name using the prompt-generated SQL
@mcp.tool()
def get_tracks_by_artist(artist_name: str) -> List[Dict[str, Any]]:
    """Get all tracks for a given artist name using a prompt-generated SQL statement."""
    query = get_tracks_by_artist_prompt(artist_name)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            if not rows:
                return []
            return [dict(zip(columns, row)) for row in rows]
        except Exception:
            return []


if __name__ == "__main__":
     mcp.run(transport='stdio')