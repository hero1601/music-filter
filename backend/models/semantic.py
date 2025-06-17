from pydantic import BaseModel, Field
from typing import List, Optional

class SemanticMatchLine(BaseModel):
    line_number: Optional[int] = None
    lyric_line: str
    similarity_score: Optional[float] = Field(None, description="Similarity score for this line")

class SemanticResult(BaseModel):
    song_id: Optional[int] = None
    title: Optional[str] = None
    artist: Optional[str] = None
    external_link: Optional[str] = None
    matched_lines: List[SemanticMatchLine] = []

class SemanticSearchResponse(BaseModel):
    results: List[SemanticResult]
    query: str
    exclude: Optional[List[str]] = None
    total_songs: Optional[int] = None
    total_matches: Optional[int] = None
    search_type: str
    message: Optional[str] = None
