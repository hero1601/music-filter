from contextlib import asynccontextmanager
from fastapi import FastAPI, Query
from databases import Database
import re,os
from typing import Any, List, Dict
from fastapi.middleware.cors import CORSMiddleware
from config import DATABASE_URL

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    await database.connect()
    yield
    # Shutdown code
    await database.disconnect()

print(DATABASE_URL)

app = FastAPI(lifespan=lifespan)
database = Database(DATABASE_URL)


def highlight_term(text: str, term: str) -> str:
    pattern = re.compile(re.escape(term), re.IGNORECASE)
    return pattern.sub(lambda m: f"**{m.group(0)}**", text)


@app.get("/")
async def get_songs(limit: int = Query(100, ge=1, le=1000)) -> List[Dict[str, Any]]:
    """
    Get top songs from the database.
    """
    sql = """
        SELECT DISTINCT s.id, s.title, s.artist, s.external_link
        FROM songs s
        ORDER BY s.id
        LIMIT :limit
    """
    
    rows = await database.fetch_all(query=sql, values={"limit": limit})
    
    songs = []
    for row in rows:
        songs.append({
            "id": row["id"],
            "title": row["title"],
            "artist": row["artist"],
            "external_link": row["external_link"]
        })
    
    return songs


@app.get("/search")
async def search_songs(query: str = Query(..., min_length=1)) -> Dict[str, List]:
    query_lower = query.lower()
    sql = """
        SELECT s.id, s.title, s.artist, s.external_link, l.line_number, l.lyric_line
        FROM songs s
        JOIN lyrics l ON s.id = l.song_id
        WHERE LOWER(l.lyric_line) LIKE :pattern
        ORDER BY s.id, l.line_number
    """
    rows = await database.fetch_all(query=sql, values={"pattern": f"%{query_lower}%"})

    results = {}
    for row in rows:
        song_id = row["id"]
        if song_id not in results:
            results[song_id] = {
                "id": song_id,
                "title": row["title"],
                "artist": row["artist"],
                "external_link": row["external_link"],
                "matched_lines": [],
            }
        highlighted = highlight_term(row["lyric_line"], query)
        results[song_id]["matched_lines"].append(highlighted)

    return {"results": list(results.values())}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
