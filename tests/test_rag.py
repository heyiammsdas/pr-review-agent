import os
import shutil
import tempfile
import unittest

from app.rag.loader import load_repository
from app.rag.chunker import chunk_code
from app.rag.embedder import embed
from app.rag.indexer import build_index
from app.rag.retriever import retrieve_relevant_code

class TestRAG(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory structure for testing loader
        self.test_dir = tempfile.mkdtemp()
        
        # Valid python file
        with open(os.path.join(self.test_dir, "main.py"), "w") as f:
            f.write("def hello():\n    print('world')\n" * 100) # Ensure multiple chunks
            
        # Ignored text file
        with open(os.path.join(self.test_dir, "notes.txt"), "w") as f:
            f.write("Some notes")
            
        # Ignored dot directory
        os.makedirs(os.path.join(self.test_dir, ".git"))
        with open(os.path.join(self.test_dir, ".git", "config"), "w") as f:
            f.write("git config")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_loader(self):
        files = load_repository(self.test_dir)
        # Should only load main.py, ignoring notes.txt and .git files
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]["file"], "main.py")
        self.assertTrue("def hello()" in files[0]["content"])

    def test_chunker(self):
        files = [{"file": "test.py", "content": "line1\nline2\nline3\nline4\nline5"}]
        # Set max_lines to 2 to test chunking
        chunks = chunk_code(files, max_lines=2)
        
        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0]["chunk"], 0)
        self.assertEqual(chunks[0]["content"], "line1\nline2")
        self.assertEqual(chunks[1]["chunk"], 1)
        self.assertEqual(chunks[1]["content"], "line3\nline4")
        self.assertEqual(chunks[2]["chunk"], 2)
        self.assertEqual(chunks[2]["content"], "line5")

    def test_embedder_and_indexer(self):
        texts = ["chunk 1", "chunk 2"]
        embeddings = embed(texts, dim=64)
        
        self.assertEqual(len(embeddings), 2)
        self.assertEqual(len(embeddings[0]), 64)
        
        index = build_index(embeddings)
        self.assertEqual(index.ntotal, 2)
        self.assertEqual(index.d, 64)

    def test_retrieval(self):
        # Full pipeline test
        chunks = [
            {"file": "a.py", "chunk": 0, "content": "auth module logic"},
            {"file": "b.py", "chunk": 0, "content": "database connection strings"},
            {"file": "c.py", "chunk": 0, "content": "unrelated front end code"}
        ]
        
        texts = [c["content"] for c in chunks]
        embeddings = embed(texts, dim=64)
        index = build_index(embeddings)
        
        query = "auth logic"
        results = retrieve_relevant_code(query, chunks, index, top_k=2)
        
        self.assertEqual(len(results), 2)
        self.assertIn("file", results[0])
        self.assertIn("score", results[0])
        # Note: Since embeddings are deterministic mocks, we can't assert semantic correctness,
        # but we can verify the structure and that it returns the requested top_k.

if __name__ == '__main__':
    unittest.main()
