import numpy as np

def embed(texts: list[str], dim: int = 64) -> list[list[float]]:
    """
    Mock embedding function to generate a deterministic vector per text.
    In production, this would call an LLM (e.g., Gemini) to generate real embeddings.
    
    This allows local RAG testing without exhausting the Gemini API quota.
    """
    embeddings = []
    
    for text in texts:
        # Generate a deterministic seed based on the string content
        seed_value = sum(ord(c) for c in text[:100]) + len(text)
        np.random.seed(seed_value % (2**32))
        
        # Create a random vector and normalize it
        vec = np.random.normal(0, 1, dim)
        vec = vec / np.linalg.norm(vec)
        
        embeddings.append(vec.tolist())
        
    return embeddings
