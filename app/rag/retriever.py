import numpy as np
import faiss
from app.rag.embedder import embed

def retrieve_relevant_code(query: str, chunks: list[dict], index: faiss.Index, top_k: int = 5) -> list[dict]:
    """
    Given a query and a FAISS index, retrieves the top-k most relevant code chunks.
    """
    if not chunks or index.ntotal == 0:
        return []
        
    # Generate embedding for the query
    query_embedding = embed([query])[0]
    query_np = np.array([query_embedding], dtype=np.float32)
    
    # Search the index
    # k cannot exceed the number of elements in the index
    k = min(top_k, index.ntotal)
    distances, indices = index.search(query_np, k)
    
    results = []
    for i in range(k):
        chunk_idx = indices[0][i]
        distance = distances[0][i]
        
        # FAISS L2 distance: lower is better. We can invert it for a mock "score"
        score = 1.0 / (1.0 + float(distance))
        
        chunk = chunks[chunk_idx]
        results.append({
            "file": chunk["file"],
            "chunk": chunk["chunk"],
            "content": chunk["content"],
            "score": round(score, 4)
        })
        
    print(f"[RAG Retriever] Retrieved top {len(results)} chunks for query: '{query}'")
    return results
