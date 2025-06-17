from fastapi import APIRouter, Query
from typing import Dict, List, Optional
from models.song import SongResult
from services.songs_service import songs_search
from db.database import database
from services.semantic_search import semantic_search
from utils.helpers import highlight_term

router = APIRouter()

@router.get("/search")
async def search_songs(query: str = Query(..., min_length=1)) -> List[SongResult]:
    results = await songs_search(query)
    return results

@router.get("/semantic-search")
async def search_using_semantic(
    include: str = Query(..., min_length=1),
    exclude: Optional[List[str]] = Query(None),
    include_threshold: float = Query(0.45, ge=0.0, le=1.0),
    exclude_threshold: float = Query(0.4, ge=0.0, le=1.0),
    max_results: int = Query(10, ge=1, le=200),
    group_by_song: bool = Query(True)
) -> Dict:
    
    print(include)
    print(exclude)
    
    try:
        results = semantic_search.semantic_search(
            query=include,
            top_k=max_results * 3,
            similarity_threshold=include_threshold,
            exclude_queries=exclude,
            exclude_threshold=exclude_threshold,
        )
        
        if not results:
            return {
                "results": [],
                "query": include,
                "exclude": exclude,
                "message": "No results found. Try lowering the threshold."
            }
        
        if group_by_song:
            grouped = semantic_search.group_by_songs(results)
            return {
                "results": grouped[:max_results],
                "query": include,
                "exclude": exclude,
                "total_songs": len(grouped),
                "search_type": "semantic_grouped"
            }
        else:
            return {
                "results": results[:max_results],
                "query": include,
                "exclude": exclude,
                "total_matches": len(results),
                "search_type": "semantic_lines"
            }
    except Exception as e:
        return {"error": str(e), "results": []}    
    
@router.get("/search-status")
async def search_status():
    return {
        "embeddings_loaded": semantic_search.embeddings is not None,
        "total_lines": len(semantic_search.metadata) if semantic_search.metadata else 0,
        "model_name": semantic_search.model_name,
        "files_exist": {
            "embeddings": semantic_search.embeddings_file.exists(),
            "metadata": semantic_search.metadata_file.exists()
        }
    }