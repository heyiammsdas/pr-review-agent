import os
import json
import redis
from fastapi import HTTPException

def get_redis_client():
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return redis.from_url(redis_url)

def enqueue_review_job(repository: str, pr_number: int, action: str):
    """
    Puts a review job into the Redis queue.
    """
    try:
        r = get_redis_client()
        job = {
            "repository": repository,
            "pr_number": pr_number,
            "action": action
        }
        r.lpush("pr_review_queue", json.dumps(job))
        print(f"Job queued for {repository} PR #{pr_number}")
    except redis.RedisError as e:
        print(f"Redis unavailable: {e}")
        raise HTTPException(status_code=500, detail="Failed to queue job, Redis unavailable")
