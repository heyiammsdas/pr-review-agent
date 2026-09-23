import os
import json
import time
import asyncio
import redis
from dotenv import load_dotenv

load_dotenv()

from app.services.review import process_pr_review
from app.services.job_queue import get_redis_client

async def run_worker():
    print("Starting background worker...")
    try:
        r = get_redis_client()
        # Test connection
        r.ping()
        print("Connected to Redis. Waiting for jobs on 'pr_review_queue'...")
    except redis.RedisError as e:
        print(f"Worker failed to connect to Redis: {e}")
        return

    while True:
        try:
            # Block until a job is available (timeout of 5 seconds to gracefully handle interrupts)
            result = r.brpop("pr_review_queue", timeout=5)
            if result:
                _, job_data_bytes = result
                job_data = json.loads(job_data_bytes)
                print("\nWorker started job")
                print(f"Payload: {job_data}")
                
                repository = job_data.get("repository")
                pr_number = job_data.get("pr_number")
                
                if not repository or not pr_number:
                    print("Malformed job: missing repository or pr_number. Skipping.")
                    continue

                print(f"Processing review for {repository} PR #{pr_number}...")
                
                # Execute the existing review pipeline
                try:
                    await process_pr_review(repository, pr_number)
                    print("Job completed")
                except Exception as e:
                    print(f"Job failed during processing: {e}")
        except json.JSONDecodeError:
            print("Malformed job: invalid JSON. Skipping.")
        except redis.RedisError as e:
            print(f"Redis error during polling: {e}")
            time.sleep(5) # Backoff on connection lost
        except Exception as e:
            print(f"Unexpected worker error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(run_worker())
    except KeyboardInterrupt:
        print("\nWorker stopped.")
