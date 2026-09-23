import json
from app.services.redis_client import get_redis_connection

QUEUE_NAME = "pr_review_queue"

def push_job_to_queue(job_id: str, job_data: dict):
    """
    Pushes a job to the Redis queue and saves the initial state.
    """
    redis_client = get_redis_connection()
    # Save the state
    redis_client.set(f"job:{job_id}", json.dumps(job_data))
    # Push to queue
    redis_client.lpush(QUEUE_NAME, job_id)
    
def get_job_status(job_id: str) -> str:
    """
    Retrieves the job status from Redis.
    """
    redis_client = get_redis_connection()
    return redis_client.get(f"job:{job_id}")

def pop_job_from_queue(timeout=0):
    """
    Blocks until a job is available and returns (queue_name, job_id).
    """
    redis_client = get_redis_connection()
    return redis_client.brpop(QUEUE_NAME, timeout=timeout)

def update_job_status(job_id: str, job_data: dict):
    """
    Updates the job status in Redis.
    """
    redis_client = get_redis_connection()
    redis_client.set(f"job:{job_id}", json.dumps(job_data))