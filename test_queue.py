import hmac
import hashlib
import httpx
import json
import os
import redis
import time
from dotenv import load_dotenv

load_dotenv()

SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "mysecret").encode()
URL = "http://127.0.0.1:8000/webhook/github"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

def get_signature(payload_dict):
    payload_bytes = json.dumps(payload_dict).encode('utf-8')
    return "sha256=" + hmac.new(SECRET, payload_bytes, hashlib.sha256).hexdigest(), payload_bytes

def run_tests():
    try:
        r = redis.from_url(REDIS_URL)
        r.ping()
        # Clear the queue before testing
        r.delete("pr_review_queue")
    except redis.RedisError:
        print("Cannot connect to Redis. Please ensure Redis is running via docker-compose.")
        return

    print("--- Test 1: Invalid webhook signature ---")
    payload = {"action": "opened", "pull_request": {"number": 1}, "repository": {"full_name": "heyiammsdas/testing-pr-agent"}}
    _, payload_bytes = get_signature(payload)
    headers = {"X-GitHub-Event": "pull_request", "X-Hub-Signature-256": "sha256=invalid", "Content-Type": "application/json"}
    res = httpx.post(URL, content=payload_bytes, headers=headers)
    print(f"Status: {res.status_code}, Response: {res.json()}")

    print("\n--- Test 2: Webhook successfully queueing a job ---")
    sig, payload_bytes = get_signature(payload)
    headers["X-Hub-Signature-256"] = sig
    res = httpx.post(URL, content=payload_bytes, headers=headers)
    print(f"Status: {res.status_code}, Response: {res.json()}")
    
    print("\n--- Test 3: Reading a review job from Redis (Worker check) ---")
    job = r.lpop("pr_review_queue")
    if job:
        print(f"Read job from Redis: {json.loads(job)}")
    else:
        print("No job found in Redis!")

    print("\n--- Test 4: Creating a direct malformed job ---")
    r.lpush("pr_review_queue", "invalid_json_string")
    r.lpush("pr_review_queue", json.dumps({"repository": "only_repo"}))
    print("Malformed jobs pushed to Redis (Worker will handle these gracefully).")

if __name__ == "__main__":
    run_tests()
