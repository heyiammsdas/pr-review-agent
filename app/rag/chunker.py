def chunk_code(files: list[dict], max_lines: int = 50) -> list[dict]:
    """
    Splits the content of each file into reasonably small chunks.
    Each chunk contains: file path, chunk text, and chunk index.
    """
    chunks = []
    
    for file_obj in files:
        file_path = file_obj["file"]
        content = file_obj["content"]
        
        lines = content.split('\n')
        chunk_idx = 0
        
        for i in range(0, len(lines), max_lines):
            chunk_lines = lines[i:i + max_lines]
            chunk_text = "\n".join(chunk_lines).strip()
            
            if not chunk_text:
                continue
                
            chunks.append({
                "file": file_path,
                "chunk": chunk_idx,
                "content": chunk_text
            })
            chunk_idx += 1
            
    print(f"[RAG Chunker] Split {len(files)} files into {len(chunks)} chunks (max {max_lines} lines/chunk)")
    return chunks
