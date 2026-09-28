import asyncio
import unittest
from unittest.mock import patch, MagicMock

from app.graph.review_graph import review_graph

class TestReviewGraph(unittest.IsolatedAsyncioTestCase):

    @patch('app.graph.review_graph.get_pr_details')
    @patch('app.graph.review_graph.get_pr_diff')
    @patch('app.graph.review_graph.retrieve_relevant_code')
    @patch('app.graph.review_graph.build_index')
    @patch('app.graph.review_graph.embed')
    @patch('app.graph.review_graph.chunk_code')
    @patch('app.graph.review_graph.load_repository')
    @patch('app.graph.review_graph.run_security_review')
    @patch('app.graph.review_graph.run_quality_review')
    @patch('app.graph.review_graph.run_testing_review')
    @patch('app.graph.review_graph.run_aggregator_agent')
    async def test_review_graph_execution(
        self, 
        mock_aggregator, mock_testing, mock_quality, mock_security, 
        mock_load, mock_chunk, mock_embed, mock_build, mock_retrieve,
        mock_diff, mock_details
    ):
        # 1. Setup mock returns for GitHub API calls
        mock_details.return_value = {"title": "Mock PR"}
        mock_diff.return_value = "diff --git a/test.py b/test.py\n+print('mocked')"
        
        # 2. Setup mock returns for RAG components
        mock_load.return_value = [{"file": "mock.py", "content": "mock code"}]
        mock_chunk.return_value = [{"file": "mock.py", "chunk": 0, "content": "mock code"}]
        mock_embed.return_value = [[0.1, 0.2, 0.3]]
        
        mock_index = MagicMock()
        mock_build.return_value = mock_index
        
        mock_rag_context = [
            {"file": "src/auth.py", "chunk": 0, "content": "mock retrieved context", "score": 0.99}
        ]
        mock_retrieve.return_value = mock_rag_context
        
        # 3. Setup mock returns for Gemini API calls
        mock_security.return_value = {"issues": [{"issue": "mock_security_issue"}]}
        mock_quality.return_value = {"issues": [{"issue": "mock_quality_issue"}]}
        mock_testing.return_value = {"issues": [{"issue": "mock_testing_issue"}]}
        mock_aggregator.return_value = {"summary": "Mock success"}
        
        # 4. Initialize test state
        initial_state = {
            "repository": "mock_owner/mock_repo",
            "pr_number": 1,
            "pr_details": {},
            "pr_diff": "",
            "retrieved_context": [],
            "security_review": {},
            "quality_review": {},
            "testing_review": {},
            "final_review": {}
        }
        
        # 5. Execute the LangGraph workflow directly
        final_state = await review_graph.ainvoke(initial_state)
        
        # 6. Verifications
        # Verify get_pr_context executed
        mock_details.assert_called_once_with("mock_owner/mock_repo", 1)
        mock_diff.assert_called_once_with("mock_owner/mock_repo", 1)
        
        # Verify retrieve_context executed successfully
        mock_load.assert_called_once_with(".")
        mock_chunk.assert_called_once()
        mock_embed.assert_called_once()
        mock_build.assert_called_once()
        mock_retrieve.assert_called_once_with("diff --git a/test.py b/test.py\n+print('mocked')", mock_chunk.return_value, mock_index, 5)
        
        # Verify retrieved_context actually appears in the state
        self.assertEqual(final_state["retrieved_context"], mock_rag_context)
        
        # Verify the specialized agents receive the retrieved context
        mock_security.assert_called_once_with("diff --git a/test.py b/test.py\n+print('mocked')", mock_rag_context)
        mock_quality.assert_called_once_with("diff --git a/test.py b/test.py\n+print('mocked')", mock_rag_context)
        mock_testing.assert_called_once_with("diff --git a/test.py b/test.py\n+print('mocked')", mock_rag_context)
        
        # Verify aggregator executed
        mock_aggregator.assert_called_once_with(
            {"issues": [{"issue": "mock_security_issue"}]},
            {"issues": [{"issue": "mock_quality_issue"}]},
            {"issues": [{"issue": "mock_testing_issue"}]},
            "diff --git a/test.py b/test.py\n+print('mocked')"
        )
        
        # Verify final review state
        self.assertEqual(final_state["final_review"]["summary"], "Mock success")

if __name__ == '__main__':
    unittest.main()
