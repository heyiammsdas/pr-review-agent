import json
import asyncio
from app.services.job_queue import pop_job_from_queue, get_job_status, update_job_status
from app.graph.review_graph import review_graph
from app.services.formatter import format_review_as_markdown
from app.services.github import post_pr_comment

async def process_job(job_id: str):
    """
    Retrieves the job from Redis, runs the LangGraph review pipeline,
    and updates the job status back in Redis.
    """
    # 1. Fetch job info
    job_data_str = get_job_status(job_id)
    if not job_data_str:
        print(f"Job {job_id} data not found in Redis!")
        return
    
    job_data = json.loads(job_data_str)
    
    # 2. Update status to 'processing'
    job_data["status"] = "processing"
    update_job_status(job_id, job_data)
    print(f"Job started: {job_id}")
    
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
        final_review = final_state.get("final_review", {})
        
        # 4. Mark completed and store the result
        job_data["status"] = "completed"
        job_data["result"] = final_review
        print(f"Job completed: {job_id}")
        
        # 5. Post GitHub Comment if successful
        if "summary" in final_review and "failed" not in final_review["summary"].lower():
            comment_md = format_review_as_markdown(final_review)
            # Post to GitHub synchronously (since httpx in our wrapper is sync right now)
            comment_url = post_pr_comment(job_data["repository"], job_data["pr_number"], comment_md)
            if comment_url:
                job_data["comment_url"] = comment_url
                print(f"Posted PR comment: {comment_url}")
        
    except Exception as e:
        # Mark failed on error
        job_data["status"] = "failed"
        # Store a safe error message, not exposing secrets
        job_data["error"] = "An internal error occurred during review processing."
        print(f"Job failed: {job_id}")
    
    # Save final status back to Redis
    update_job_status(job_id, job_data)

def run_worker():
    """
    Simple worker daemon that blocks on the Redis queue, popping jobs as they arrive.
    """
    print("Worker is waiting for jobs on Redis queue...")
    while True:
        try:
            # brpop blocks until a job is available in the queue
            result = pop_job_from_queue(timeout=0)
            if result:
                _, job_id = result
                # Run the async job processing natively
                asyncio.run(process_job(job_id))
        except Exception as e:
            print(f"Worker encountered a fatal Redis connection error: {e}")
            break

if __name__ == "__main__":
    run_worker()
