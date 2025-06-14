# from contextlib import asynccontextmanager
# from fastapi import FastAPI, Query
# from databases import Database
# import re,os
# from typing import Any, List, Dict
# from fastapi.middleware.cors import CORSMiddleware
# from backend.embeddings import SemanticSearchEngine
# from config import DATABASE_URL

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup code
#     await database.connect()
#     yield
#     # Shutdown code
#     await database.disconnect()

# async def build_embeddings():
#     """
#     Build embeddings for all lyrics (run this once initially)
#     """
#     try:
#         success = await semantic_search.build_embeddings(database)
#         if success:
#             return {
#                 "message": "✅ Embeddings built successfully!",
#                 "total_lines": len(semantic_search.metadata),
#                 "embedding_dimensions": semantic_search.embeddings.shape[1],
#                 "model_used": semantic_search.model_name
#             }
#         else:
#             return {"error": "Failed to build embeddings"}
#     except Exception as e:
#         return {"error": f"Error building embeddings: {str(e)}"}


# app = FastAPI(lifespan=lifespan)
# database = Database(DATABASE_URL)
# semantic_search = SemanticSearchEngine()


# def highlight_term(text: str, term: str) -> str:
#     pattern = re.compile(re.escape(term), re.IGNORECASE)
#     return pattern.sub(lambda m: f"**{m.group(0)}**", text)


# @app.get("/")
# async def get_songs(limit: int = Query(10, ge=1, le=1000)) -> List[Dict[str, Any]]:
#     """
#     Get top songs from the database.
#     """
#     sql = """
#         SELECT DISTINCT s.id, s.title, s.artist, s.external_link
#         FROM songs s
#         ORDER BY s.id
#         LIMIT :limit
#     """
    
#     rows = await database.fetch_all(query=sql, values={"limit": limit})
    
#     songs = []
#     for row in rows:
#         songs.append({
#             "title": row["title"],
#             "artist": row["artist"],
#             "external_link": row["external_link"]
#         })
    
#     return songs


# @app.get("/search")
# async def search_songs(query: str = Query(..., min_length=1)) -> Dict[str, List]:
#     query_lower = query.lower()
#     sql = """
#         SELECT s.id, s.title, s.artist, s.external_link, l.line_number, l.lyric_line
#         FROM songs s
#         JOIN lyrics l ON s.id = l.song_id
#         WHERE l.lyric_line ILIKE :pattern
#         ORDER BY s.id, l.line_number
#     """
#     rows = await database.fetch_all(query=sql, values={"pattern": f"%{query_lower}%"})

#     results = {}
#     for row in rows:
#         song_id = row["id"]
#         if song_id not in results:
#             results[song_id] = {
#                 "title": row["title"],
#                 "artist": row["artist"],
#                 "external_link": row["external_link"],
#                 "matched_lines": [],
#             }
#         highlighted = highlight_term(row["lyric_line"], query)
#         results[song_id]["matched_lines"].append(highlighted)

#     return {"results": list(results.values())}

# @app.get("/semantic-search")
# async def semantic_search_endpoint(
#         query: str = Query(..., min_length=1, description="Search query"),
#         similarity_threshold: float = Query(0.3, ge=0.0, le=1.0, description="Minimum similarity (0-1)"),
#         max_results: int = Query(50, ge=1, le=200, description="Maximum results"),
#         group_by_song: bool = Query(True, description="Group results by song")
#     ) -> Dict:
#     """
#     Semantic search endpoint - finds lyrics similar in meaning to your query
#     """
#     try:
#         # Perform semantic search
#         results = semantic_search.semantic_search(
#             query=query,
#             top_k=max_results * 3,  # Get more results for grouping
#             similarity_threshold=similarity_threshold
#         )
        
#         if not results:
#             return {
#                 "results": [],
#                 "query": query,
#                 "message": f"No results found. Try lowering similarity_threshold (currently {similarity_threshold})",
#                 "suggestion": "Try similarity_threshold=0.2 for broader results"
#             }
        
#         if group_by_song:
#             # Group results by song
#             grouped_results = semantic_search.group_by_songs(results)
#             final_results = grouped_results[:max_results]
            
#             return {
#                 "results": final_results,
#                 "query": query,
#                 "total_songs": len(final_results),
#                 "total_line_matches": len(results),
#                 "search_type": "semantic_grouped"
#             }
#         else:
#             # Return individual lines
#             return {
#                 "results": results[:max_results],
#                 "query": query,
#                 "total_matches": len(results),
#                 "search_type": "semantic_lines"
#             }
    
#     except Exception as e:
#         return {
#             "error": str(e),
#             "query": query,
#             "results": []
#         }

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],  # React dev server
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import songs, search
from db.database import lifespan
from services.semantic_search import semantic_search

app = FastAPI(lifespan=lifespan)

app.include_router(songs.router)
app.include_router(search.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
