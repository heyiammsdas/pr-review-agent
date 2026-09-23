import json
import asyncio
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient

# 1. Create a Fake Redis Client that works in-memory
class FakeRedis:
    def __init__(self):
        self.store = {}
        self.queue = []
        
    def set(self, key, value):
        self.store[key] = value
        
    def get(self, key):
        return self.store.get(key)
        
    def lpush(self, queue_name, item):
        self.queue.insert(0, item)
        
    def brpop(self, queue_name, timeout=0):
        if self.queue:
            return (queue_name, self.queue.pop())
        return None

# Instantiate the global fake redis instance
fake_redis = FakeRedis()

def mock_get_redis_connection():
    return fake_redis

# 2. Patch get_redis_connection globally before importing the app
with patch('app.services.redis_client.get_redis_connection', side_effect=mock_get_redis_connection):
    from app.main import app
    from worker import process_job

client = TestClient(app)

class TestRedisPipeline(unittest.IsolatedAsyncioTestCase):

    @patch('app.graph.review_graph.get_pr_details')
    @patch('app.graph.review_graph.get_pr_diff')
    @patch('app.graph.review_graph.run_security_review')
    @patch('app.graph.review_graph.run_quality_review')
    @patch('app.graph.review_graph.run_testing_review')
    @patch('app.graph.review_graph.run_aggregator_agent')
    async def test_full_pipeline(
        self, 
        mock_aggregator, mock_testing, mock_quality, 
        mock_security, mock_diff, mock_details
    ):
        """
        Tests the entire lifecycle: POST /review -> Redis -> Worker -> LangGraph -> GET /review/{job_id}
        No external APIs (Gemini/GitHub) or native Redis servers are required!
        """
        # Mock the external API dependencies (GitHub & Gemini)
        mock_details.return_value = {"title": "Mock PR"}
        mock_diff.return_value = "diff --git a/test.py b/test.py"
        mock_security.return_value = {"issues": []}
        mock_quality.return_value = {"issues": []}
        mock_testing.return_value = {"issues": []}
        mock_aggregator.return_value = {"summary": "Mock success result", "issues": []}

        # Step 1: Hit POST /review endpoint
        response = client.post("/review", json={"repository": "mock/repo", "pr_number": 1})
        self.assertEqual(response.status_code, 200)
        
        response_data = response.json()
        self.assertIn("job_id", response_data)
        job_id = response_data["job_id"]
        
        # Step 2: Verify the job is initially 'queued' in Redis
        get_response = client.get(f"/review/{job_id}")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json()["status"], "queued")
        
        # Step 3: Simulate Worker polling and processing the job
        queue_result = fake_redis.brpop("pr_review_queue")
        self.assertIsNotNone(queue_result)
        
        _, popped_job_id = queue_result
        self.assertEqual(job_id, popped_job_id)
        
        # Explicitly run the async worker function (since we aren't using the while True loop)
        await process_job(popped_job_id)
        
        # Step 4: Verify the status is now 'completed' and contains the LLM result
        final_get_response = client.get(f"/review/{job_id}")
        self.assertEqual(final_get_response.status_code, 200)
        
        final_data = final_get_response.json()
        self.assertEqual(final_data["status"], "completed")
        self.assertEqual(final_data["result"]["summary"], "Mock success result")
        
        # Assert the external agents actually executed
        mock_diff.assert_called_once()
        mock_aggregator.assert_called_once()

if __name__ == '__main__':
    unittest.main()
