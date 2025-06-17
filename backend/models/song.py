from pydantic import BaseModel
from typing import List

class SongMatchedLine(BaseModel):
    line_number: int  
    lyric_line: str  

class SongResult(BaseModel):
    title: str
    artist: str
    external_link: str
    matched_lines: List[SongMatchedLine]
