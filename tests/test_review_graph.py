import asyncio
import unittest
from unittest.mock import patch

from app.graph.review_graph import review_graph

class TestReviewGraph(unittest.IsolatedAsyncioTestCase):

    @patch('app.graph.review_graph.get_pr_details')
    @patch('app.graph.review_graph.get_pr_diff')
    @patch('app.graph.review_graph.run_security_review')
    @patch('app.graph.review_graph.run_quality_review')
    @patch('app.graph.review_graph.run_testing_review')
    @patch('app.graph.review_graph.run_aggregator_agent')
    async def test_review_graph_execution(
        self, 
        mock_aggregator, 
        mock_testing, 
        mock_quality, 
        mock_security, 
        mock_diff, 
        mock_details
    ):
        # 1. Setup mock returns for GitHub API calls
        mock_details.return_value = {
            "title": "Mock PR",
            "number": 1,
            "state": "open",
            "html_url": "https://github.com/mock/repo/pull/1"
        }
        mock_diff.return_value = "diff --git a/test.py b/test.py\n+print('mocked')"
        
        # 2. Setup mock returns for Gemini API calls
        mock_security.return_value = {"issues": [{"issue": "mock_security_issue"}]}
        mock_quality.return_value = {"issues": [{"issue": "mock_quality_issue"}]}
        mock_testing.return_value = {"issues": [{"issue": "mock_testing_issue"}]}
        
        mock_aggregator.return_value = {
            "summary": "Mock successful aggregation.",
            "issues": [
                {"issue": "mock_security_issue"},
                {"issue": "mock_quality_issue"},
                {"issue": "mock_testing_issue"}
            ],
            "statistics": {
                "total": 3,
                "security": 1,
                "code_quality": 1,
                "testing": 1
            }
        }
        
        # 3. Initialize test state
        initial_state = {
            "repository": "mock_owner/mock_repo",
            "pr_number": 1,
            "pr_details": {},
            "pr_diff": "",
            "security_review": {},
            "quality_review": {},
            "testing_review": {},
            "final_review": {}
        }
        
        # 4. Execute the LangGraph workflow directly
        final_state = await review_graph.ainvoke(initial_state)
        
        # 5. Verify the external functions were called
        mock_details.assert_called_once_with("mock_owner/mock_repo", 1)
        mock_diff.assert_called_once_with("mock_owner/mock_repo", 1)
        mock_security.assert_called_once()
        mock_quality.assert_called_once()
        mock_testing.assert_called_once()
        
        # Verify the aggregator received the results from the parallel agents
        mock_aggregator.assert_called_once_with(
            {"issues": [{"issue": "mock_security_issue"}]},
            {"issues": [{"issue": "mock_quality_issue"}]},
            {"issues": [{"issue": "mock_testing_issue"}]}
        )
        
        # 6. Verify the final state was updated correctly
        self.assertEqual(final_state["pr_details"]["title"], "Mock PR")
        self.assertEqual(final_state["final_review"]["summary"], "Mock successful aggregation.")
        self.assertEqual(len(final_state["final_review"]["issues"]), 3)

if __name__ == '__main__':
    unittest.main()
