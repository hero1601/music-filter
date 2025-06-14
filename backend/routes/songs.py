from fastapi import APIRouter, Query
from typing import List, Dict, Any
from db.database import database

router = APIRouter()

@router.get("/")
async def get_songs(limit: int = Query(10, ge=1, le=1000)) -> List[Dict[str, Any]]:
    sql = """
        SELECT DISTINCT s.id, s.title, s.artist, s.external_link
        FROM songs s
        ORDER BY s.id
        LIMIT :limit
    """
    rows = await database.fetch_all(query=sql, values={"limit": limit})
    return [
        {
            "title": row["title"],
            "artist": row["artist"],
            "external_link": row["external_link"]
        } for row in rows
    ]