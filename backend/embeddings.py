import numpy as np
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional, Union

class SemanticSearchEngine:
    def __init__(self, model_name: str = 'paraphrase-multilingual-mpnet-base-v2'):
        """
        Initialize semantic search engine
        
        Args:
            model_name: Sentence transformer model
                       'all-MiniLM-L6-v2' - Balanced (384 dim, ~80MB)
                       'all-mpnet-base-v2' - Better quality (768 dim, ~420MB)
        """
        self.model_name = model_name
        self.model = None
        self.embeddings = None
        self.metadata = []
        
        # File paths for persistence
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)
        self.embeddings_file = self.data_dir / 'line_embeddings.npy'
        self.metadata_file = self.data_dir / 'line_metadata.json'
    
    def load_model(self):
        if self.model is None:
            self.model = SentenceTransformer(self.model_name)
    
    async def build_embeddings(self, database):

        if self.model is None:
            self.load_model()
        
        # Fetch all lyric lines with song info
        sql = """
        SELECT l.id as lyric_id, l.song_id, l.line_number, l.lyric_line, 
               s.title, s.artist, s.external_link
        FROM lyrics l
        JOIN songs s ON l.song_id = s.id
        ORDER BY l.song_id, l.line_number
        """
        
        rows = await database.fetch_all(query=sql)
        
        if not rows:
            print("No lyrics found in database!")
            return False
        
        # Prepare texts and metadata
        texts = []
        metadata = []
        
        for row in rows:
            # Clean the lyric line
            lyric_text = row["lyric_line"].strip()
            if lyric_text:  # Skip empty lines
                texts.append(lyric_text)
                metadata.append({
                    "lyric_id": row["lyric_id"],
                    "song_id": row["song_id"],
                    "line_number": row["line_number"],
                    "lyric_line": lyric_text,
                    "title": row["title"],
                    "artist": row["artist"],
                    "external_link": row["external_link"]
                })
        
        if not texts:
            print("No valid lyric lines found!")
            return False
        
        # Generate embeddings in batches for memory efficiency
        batch_size = 64
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_embeddings = self.model.encode(
                batch_texts, 
                show_progress_bar=False,
                convert_to_numpy=True
            )
            all_embeddings.append(batch_embeddings)
            
            # Progress update
            processed = min(i + batch_size, len(texts))
            if processed % 1000 == 0 or processed == len(texts):
                print(f"Processed {processed}/{len(texts)} lines")
        
        # Combine all embeddings
        self.embeddings = np.vstack(all_embeddings)
        self.metadata = metadata
        
        # Save to disk
        await self.save_embeddings()
        return True
    
    async def save_embeddings(self):
        
        np.save(self.embeddings_file, self.embeddings) # type: ignore
        
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
    
    async def load_embeddings(self):
        """Load embeddings from disk"""
        if not self.embeddings_file.exists() or not self.metadata_file.exists():
            print("⚠️  Embeddings not found. Run /build-embeddings first.")
            return False
        
        self.embeddings = np.load(self.embeddings_file)
        
        with open(self.metadata_file, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
        
        print(f"✅ Embeddings loaded! {self.embeddings.shape[0]} lines ready")
        return True
    
    def semantic_search(
        self,
        query: str,
        top_k: int = 100,
        similarity_threshold: float = 0.3,
        exclude_queries: Optional[Union[str, List[str]]] = None,
        exclude_threshold: float = 0.6,
    ) -> List[Dict]:
        
        """
        Perform semantic search with optional multiple exclusions.
        
        Args:
            query: Search query (positive intent).
            top_k: Max results to return.
            similarity_threshold: Min similarity to include.
            exclude_queries: String or list of strings to exclude (negative intent).
            exclude_threshold: Similarity threshold to exclude.
            
        Returns:
            List of dict results with keys:
                - lyric line metadata
                - similarity_score
                - excluded (bool)
                - excluded_due_to (list of matched exclude query strings)
                - excluded_lines (list of tuples (exclude_query, similarity_score))
        """

        if self.model is None:
            self.load_model()

        if self.embeddings is None:
            raise ValueError("Embeddings not loaded! Call load_embeddings() first.")
        
        # Embed main query
        query_embedding = self.model.encode([query])  # type: ignore
        query_norm = np.linalg.norm(query_embedding)
        
        embedding_norms = np.linalg.norm(self.embeddings, axis=1)
        similarities = np.dot(self.embeddings, query_embedding.T).flatten()
        similarities = similarities / (embedding_norms * query_norm)
        
        indices = np.argsort(similarities)[::-1]
        candidate_song_ids = set(self.metadata[idx]['song_id'] for idx in indices)

        if exclude_queries:
            if isinstance(exclude_queries, str):
                exclude_queries = [exclude_queries]
            exclude_embeddings = self.model.encode(exclude_queries)
            exclude_norms = np.linalg.norm(exclude_embeddings, axis=1)
        else:
            exclude_embeddings = None

        songs_to_exclude = set()

        if exclude_embeddings is not None and exclude_queries is not None:
            candidate_indices = [i for i, meta in enumerate(self.metadata) 
                                 if meta['song_id'] in candidate_song_ids]

            # Compute exclusion similarity for all candidate lines
            candidate_embeddings = self.embeddings[candidate_indices]
            candidate_norms = embedding_norms[candidate_indices]

            exclude_sims = np.dot(candidate_embeddings, exclude_embeddings.T)
            exclude_sims /= (candidate_norms[:, None] * exclude_norms[None, :])

            # Check if any line in the song exceeds exclusion threshold
            for idx_in_list, global_idx in enumerate(candidate_indices):
                for ex_idx in range(len(exclude_queries)):
                    if exclude_sims[idx_in_list, ex_idx] >= exclude_threshold:
                        song_id = self.metadata[global_idx]['song_id']
                        songs_to_exclude.add(song_id)
                        break

        # Filter out results from excluded songs and below similarity threshold
        results = []
        for idx in indices:
            song_id = self.metadata[idx]['song_id']
            if song_id in songs_to_exclude:
                continue

            sim_score = similarities[idx]
            if sim_score < similarity_threshold:
                continue

            result = self.metadata[idx].copy()
            result.update({
                'similarity_score': float(sim_score),
                'excluded': False,
                'excluded_due_to': [],
                'excluded_lines': []
            })
            results.append(result)
        return results

    
    def group_by_songs(self, search_results: List[Dict]) -> List[Dict]:
        """Group search results by song"""
        songs = {}
        
        for result in search_results:
            song_id = result['song_id']
            
            if song_id not in songs:
                songs[song_id] = {
                    'song_id': song_id,
                    'title': result['title'],
                    'artist': result['artist'],
                    'external_link': result['external_link'],
                    'matched_lines': [],
                    'similarity_scores': []
                }
            
            songs[song_id]['matched_lines'].append({
                'line_number': result['line_number'],
                'lyric_line': result['lyric_line'],
                'similarity_score': result['similarity_score']
            })
            songs[song_id]['similarity_scores'].append(result['similarity_score'])
        
        # Calculate stats for each song
        for song_id in songs:
            scores = songs[song_id]['similarity_scores']
            songs[song_id]['avg_similarity'] = sum(scores) / len(scores)
            songs[song_id]['max_similarity'] = max(scores)
            songs[song_id]['total_matches'] = len(scores)
            
            # Sort lines by similarity
            songs[song_id]['matched_lines'].sort(
                key=lambda x: x['similarity_score'], 
                reverse=True
            )
            
            # Remove the scores list (not needed in response)
            del songs[song_id]['similarity_scores']
        
        # Sort songs by average similarity
        return sorted(songs.values(), key=lambda x: x['avg_similarity'], reverse=True)