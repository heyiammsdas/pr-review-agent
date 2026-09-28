import os
import json
import unittest
from fastapi.testclient import TestClient

from tests.test_redis_pipeline import fake_redis
from app.main import app
from app.services.webhook import generate_test_signature

os.environ['GITHUB_WEBHOOK_SECRET'] = 'test_secret'
client = TestClient(app)

class TestWebhook(unittest.TestCase):
    def setUp(self):
        # Reset the fake redis state
        fake_redis.store = {}
        fake_redis.queue = []
        self.secret = 'test_secret'
        
    def test_valid_signature_opened_action(self):
        payload = {
            "action": "opened",
            "repository": {"full_name": "heyiammsdas/testing-pr-agent"},
            "pull_request": {"number": 1}
        }
        body = json.dumps(payload).encode('utf-8')
        signature = generate_test_signature(body, self.secret)
        
        response = client.post("/webhook/github", content=body, headers={"X-Hub-Signature-256": signature})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Webhook received")
        self.assertEqual(response.json()["status"], "queued")
        self.assertEqual(len(fake_redis.queue), 1)

    def test_invalid_signature(self):
        payload = {
            "action": "opened",
            "repository": {"full_name": "heyiammsdas/testing-pr-agent"},
            "pull_request": {"number": 1}
        }
        body = json.dumps(payload).encode('utf-8')
        
        # Pass a deliberately bad signature
        response = client.post("/webhook/github", content=body, headers={"X-Hub-Signature-256": "sha256=badsig"})
        
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Invalid GitHub webhook signature")
        self.assertEqual(len(fake_redis.queue), 0)

    def test_valid_signature_synchronize_action(self):
        payload = {
            "action": "synchronize",
            "repository": {"full_name": "heyiammsdas/testing-pr-agent"},
            "pull_request": {"number": 2}
        }
        body = json.dumps(payload).encode('utf-8')
        signature = generate_test_signature(body, self.secret)
        
        response = client.post("/webhook/github", content=body, headers={"X-Hub-Signature-256": signature})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(fake_redis.queue), 1)

    def test_valid_signature_reopened_action(self):
        payload = {
            "action": "reopened",
            "repository": {"full_name": "heyiammsdas/testing-pr-agent"},
            "pull_request": {"number": 3}
        }
        body = json.dumps(payload).encode('utf-8')
        signature = generate_test_signature(body, self.secret)
        
        response = client.post("/webhook/github", content=body, headers={"X-Hub-Signature-256": signature})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(fake_redis.queue), 1)

    def test_unsupported_action_ignored(self):
        payload = {
            "action": "closed",
            "repository": {"full_name": "heyiammsdas/testing-pr-agent"},
            "pull_request": {"number": 4}
        }
        body = json.dumps(payload).encode('utf-8')
        signature = generate_test_signature(body, self.secret)
        
        response = client.post("/webhook/github", content=body, headers={"X-Hub-Signature-256": signature})
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("Ignored: Unsupported action", response.json()["message"])
        self.assertEqual(len(fake_redis.queue), 0)

    def test_extraction_correct(self):
        payload = {
            "action": "opened",
            "repository": {"full_name": "owner/repo"},
            "pull_request": {"number": 42}
        }
        body = json.dumps(payload).encode('utf-8')
        signature = generate_test_signature(body, self.secret)
        
        response = client.post("/webhook/github", content=body, headers={"X-Hub-Signature-256": signature})
        
        self.assertEqual(response.status_code, 200)
        job_id = response.json()["job_id"]
        
        # Verify the job was pushed correctly to the fake redis store
        job_data = json.loads(fake_redis.get(f"job:{job_id}"))
        self.assertEqual(job_data["repository"], "owner/repo")
        self.assertEqual(job_data["pr_number"], 42)
        self.assertEqual(job_data["action"], "opened")

if __name__ == '__main__':
    unittest.main()
