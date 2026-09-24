import unittest
from unittest.mock import patch, MagicMock
from app.services.formatter import format_review_as_markdown
from app.services.github import post_pr_comment

class TestGitHubComment(unittest.TestCase):

    def test_markdown_formatting(self):
        mock_review = {
            "summary": "The PR adds a new print statement.",
            "issues": [
                {
                    "severity": "High",
                    "category": "Security",
                    "file": "src/auth.py",
                    "line": 42,
                    "issue": "Hardcoded secret",
                    "suggestion": "Use env var"
                }
            ],
            "statistics": {
                "total": 1,
                "security": 1,
                "code_quality": 0,
                "testing": 0
            }
        }
        
        md = format_review_as_markdown(mock_review)
        self.assertIn("## 🤖 AI PR Review", md)
        self.assertIn("The PR adds a new print statement.", md)
        self.assertIn("#### 🔴 High", md)
        self.assertIn("- **Security**", md)
        self.assertIn("`src/auth.py`", md)
        self.assertIn("Hardcoded secret", md)
        self.assertIn("| Security | 1 |", md)
        
    @patch('app.services.github.httpx.post')
    @patch('app.services.github.os.getenv')
    def test_github_comment_success(self, mock_getenv, mock_post):
        mock_getenv.return_value = "fake_token"
        
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"html_url": "https://github.com/test/repo/issue/1#comment"}
        mock_post.return_value = mock_response
        
        url = post_pr_comment("test/repo", 1, "Hello World")
        self.assertEqual(url, "https://github.com/test/repo/issue/1#comment")
        
        # Verify request construction
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://api.github.com/repos/test/repo/issues/1/comments")
        self.assertEqual(kwargs['headers']['Authorization'], "Bearer fake_token")
        self.assertEqual(kwargs['json'], {"body": "Hello World"})
        
    @patch('app.services.github.httpx.post')
    @patch('app.services.github.os.getenv')
    def test_github_api_failure(self, mock_getenv, mock_post):
        mock_getenv.return_value = "fake_token"
        
        import httpx
        # Mock an HTTP error
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"message": "Forbidden"}
        
        mock_post.side_effect = httpx.HTTPStatusError("Error", request=MagicMock(), response=mock_response)
        
        url = post_pr_comment("test/repo", 1, "Hello World")
        self.assertEqual(url, "")
        
    @patch('app.services.github.httpx.post')
    @patch('app.services.github.os.getenv')
    def test_invalid_response_handling(self, mock_getenv, mock_post):
        mock_getenv.return_value = "fake_token"
        
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        # GitHub returns valid JSON but missing html_url
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response
        
        url = post_pr_comment("test/repo", 1, "Hello")
        self.assertEqual(url, "")

    @patch('app.services.github.httpx.post')
    @patch('app.services.github.os.getenv')
    def test_mock_integration(self, mock_getenv, mock_post):
        # 1. Mock final review
        mock_review = {
            "summary": "Integration test summary",
            "issues": [],
            "statistics": {"total": 0, "security": 0, "code_quality": 0, "testing": 0}
        }
        
        # 2. Markdown formatter
        md = format_review_as_markdown(mock_review)
        
        # 3. Mock GitHub API
        mock_getenv.return_value = "fake_token"
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"html_url": "https://github.com/integration"}
        mock_post.return_value = mock_response
        
        # 4. Comment created successfully
        url = post_pr_comment("owner/repo", 42, md)
        self.assertEqual(url, "https://github.com/integration")
        
if __name__ == '__main__':
    unittest.main()
