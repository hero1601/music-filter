from typing import List
from models.song import SongResult
from repo.fetch_songs import fetch_songs_with_lyrics
from utils.helpers import highlight_term

async def songs_search(query: str) -> List[SongResult]:
    rows = await fetch_songs_with_lyrics(query)
    
    results = {}
    for row in rows:
        song_id = row["id"]
        if song_id not in results:
            results[song_id] = SongResult(
                title=row["title"],
                artist=row["artist"],
                external_link=row["external_link"],
                matched_lines=[],
            )
        highlighted = highlight_term(row["lyric_line"], query)
        results[song_id].matched_lines.append(highlighted)

    return list(results.values())
