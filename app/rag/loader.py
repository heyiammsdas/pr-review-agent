import os

# Common directories and files to ignore during RAG indexing
IGNORE_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", "build", "dist"}
IGNORE_FILES = {".env"}

# Extensions to index
SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", 
    ".cpp", ".h", ".hpp", ".c", ".cs", ".go", ".rs"
}

def load_repository(repo_path: str) -> list[dict]:
    """
    Reads source-code files from a local repository directory.
    Ignores common binary/build directories and limits by extension.
    Returns a list of dicts with 'file' and 'content'.
    """
    loaded_files = []
    
    for root, dirs, files in os.walk(repo_path):
        # Modify dirs in-place to skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]
        
        for file in files:
            if file in IGNORE_FILES:
                continue
                
            ext = os.path.splitext(file)[1].lower()
            if ext not in SUPPORTED_EXTENSIONS:
                continue
                
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, repo_path)
            
            try:
                # Read file content safely, skipping binaries
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    loaded_files.append({
                        "file": rel_path.replace("\\", "/"),
                        "content": content
                    })
            except UnicodeDecodeError:
                # Likely a binary or unsupported encoding file, skip it
                pass
                
    print(f"[RAG Loader] Loaded {len(loaded_files)} valid source files from {repo_path}")
    return loaded_files
