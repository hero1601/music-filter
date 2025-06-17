
from typing import List
from databases.interfaces import Record

from db.database import database


async def fetch_songs_with_lyrics(query: str) -> List[Record]:
    sql = """
        SELECT s.id, s.title, s.artist, s.external_link, l.line_number, l.lyric_line
        FROM songs s
        JOIN lyrics l ON s.id = l.song_id
        WHERE l.lyric_line ILIKE :pattern
        ORDER BY s.id, l.line_number
    """
    rows = await database.fetch_all(query=sql, values={"pattern": f"%{query}%"})
    return rows
