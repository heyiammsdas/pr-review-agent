import json
import asyncio
from app.services.redis_client import get_redis_connection
from app.graph.review_graph import review_graph

redis_client = get_redis_connection()
QUEUE_NAME = "pr_review_queue"

async def process_job(job_id: str):
    """
    Retrieves the job from Redis, runs the LangGraph review pipeline,
    and updates the job status back in Redis.
    """
    # 1. Fetch job info
    job_data_str = redis_client.get(f"job:{job_id}")
    if not job_data_str:
        print(f"Job {job_id} data not found in Redis!")
        return
    
    job_data = json.loads(job_data_str)
    
    # 2. Update status to 'processing'
    job_data["status"] = "processing"
    redis_client.set(f"job:{job_id}", json.dumps(job_data))
    print(f"\n[Worker] Job started: {job_id} for {job_data['repository']} PR #{job_data['pr_number']}")
    
    # Initialize the starting state for LangGraph
    initial_state = {
        "repository": job_data["repository"],
        "pr_number": job_data["pr_number"],
        "pr_details": {},
        "pr_diff": "",
        "security_review": {},
        "quality_review": {},
        "testing_review": {},
        "final_review": {}
    }
    
    # 3. Execute the LangGraph workflow
    try:
        final_state = await review_graph.ainvoke(initial_state)
        
        # 4. Mark completed and store the result
        job_data["status"] = "completed"
        job_data["result"] = final_state.get("final_review", {})
        print(f"[Worker] Job completed: {job_id}")
        
    except Exception as e:
        # Mark failed on error
        job_data["status"] = "failed"
        job_data["error"] = str(e)
        print(f"[Worker] Job failed: {job_id} - {e}")
    
    # Save final status back to Redis
    redis_client.set(f"job:{job_id}", json.dumps(job_data))

def run_worker():
    """
    Simple worker daemon that blocks on the Redis queue, popping jobs as they arrive.
    """
    print("Worker is waiting for jobs on Redis queue...")
    while True:
        try:
            # brpop blocks until a job is available in the queue
            # Returns a tuple: (queue_name, item)
            result = redis_client.brpop(QUEUE_NAME, timeout=0)
            if result:
                _, job_id = result
                # Run the async job processing natively
                asyncio.run(process_job(job_id))
        except Exception as e:
            print(f"Worker encountered a fatal Redis connection error: {e}")
            break

if __name__ == "__main__":
    run_worker()
