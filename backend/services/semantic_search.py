from embeddings import SemanticSearchEngine

semantic_search = SemanticSearchEngine()

async def build_embeddings(database):
    try:
        success = await semantic_search.build_embeddings(database)
        if success:
            return {
                "message": "✅ Embeddings built successfully!",
                "total_lines": len(semantic_search.metadata),
                "embedding_dimensions": semantic_search.embeddings.shape[1], # type: ignore
                "model_used": semantic_search.model_name
            }
        else:
            return {"error": "Failed to build embeddings"}
    except Exception as e:
        return {"error": f"Error building embeddings: {str(e)}"}