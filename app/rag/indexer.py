import faiss
import numpy as np

def build_index(embeddings: list[list[float]]) -> faiss.Index:
    """
    Builds a FAISS index from a list of vector embeddings.
    """
    if not embeddings:
        raise ValueError("Cannot build an index with empty embeddings.")
        
    dim = len(embeddings[0])
    
    # Initialize a flat L2 index
    index = faiss.IndexFlatL2(dim)
    
    # Convert embeddings to numpy array (float32 required by FAISS)
    vectors_np = np.array(embeddings, dtype=np.float32)
    
    # Add vectors to the index
    index.add(vectors_np)
    
    print(f"[RAG Indexer] Built FAISS index with {index.ntotal} vectors of dimension {dim}")
    return index
