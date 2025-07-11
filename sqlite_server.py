from mcp.server.fastmcp import FastMCP
import sqlite3
from typing import List, Dict, Any

DB_PATH = 'chinook.db'  

mcp = FastMCP("sqlite-server")

# Tool: Get list of artists
@mcp.tool()
def get_artists() -> List[Dict[str, Any]]:
    """
    Retrieve a list of all artists in the database.
    
    Returns:
        List[Dict[str, Any]]: Each dict contains 'ArtistId' and 'Name' for an artist.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ArtistId, Name FROM artists")
        rows = cursor.fetchall()
        return [{"ArtistId": row[0], "Name": row[1]} for row in rows]

# Tool: Get list of genres
@mcp.tool()
def get_genres() -> List[Dict[str, Any]]:
    """
    Retrieve a list of all music genres in the database.
    
    Returns:
        List[Dict[str, Any]]: Each dict contains 'GenreId' and 'Name' for a genre.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT GenreId, Name FROM genres")
        rows = cursor.fetchall()
        return [{"GenreId": row[0], "Name": row[1]} for row in rows]

# Tool: Run a SQL SELECT statement
@mcp.tool()
def run_sql(query: str) -> List[Dict[str, Any]]:
    """
    Run a SQL SELECT statement and return the results as a list of dictionaries.
    
    Args:
        query (str): A SQL SELECT statement. Only SELECT statements are allowed.
    Returns:
        List[Dict[str, Any]]: Each dict represents a row, with column names as keys. Returns an empty list if no results or on error.
    """
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
def get_tracks_by_artist_prompt(name: str) -> str:
    """
    Generate a SQL statement to get all tracks for a given artist name.
    
    Args:
        name (str): The name of the artist.
    Returns:
        str: SQL SELECT statement for tracks by the artist.
    """
    return f'''
    SELECT tracks.Name AS TrackName, albums.Title AS AlbumTitle
    FROM tracks
    JOIN albums ON tracks.AlbumId = albums.AlbumId
    JOIN artists ON albums.ArtistId = artists.ArtistId
    WHERE artists.Name = "{name}"
    '''

# Tool: Get tracks by artist name using the prompt-generated SQL
@mcp.tool()
def get_tracks_by_artist(name: str) -> List[Dict[str, Any]]:
    """
    Get all tracks for a given artist name.

    Args:
        name (str): The name of the artist. This must be provided as 'name'.

    Returns:
        List[Dict[str, Any]]: Each dict contains 'TrackName' and 'AlbumTitle'.
    """
    query = get_tracks_by_artist_prompt(name)
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

# Tool: Get artist info (biography/metadata)
@mcp.tool()
def get_artist_info(name: str) -> Dict[str, Any]:
    """
    Get metadata about an artist by name, such as ArtistId and Name.

    Args:
        name (str): The name of the artist. This is the ONLY accepted argument.

    Returns:
        Dict[str, Any]: Dictionary with keys 'ArtistId' and 'Name', or empty dict if not found.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ArtistId, Name FROM artists WHERE Name = ?", (name,))
        row = cursor.fetchone()
        if row:
            return {"ArtistId": row[0], "Name": row[1]}
        return {}


if __name__ == "__main__":
     mcp.run(transport='stdio')