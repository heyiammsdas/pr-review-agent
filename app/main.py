import asyncio
import time
from fastapi import FastAPI
from pydantic import BaseModel
from app.services.github import get_pr_details, get_pr_diff
from app.agents.security_agent import run_security_review
from app.agents.quality_agent import run_quality_review
from app.agents.testing_agent import run_testing_review
from app.agents.aggregator_agent import run_aggregator_agent

app = FastAPI()

class ReviewRequest(BaseModel):
    repository: str
    pr_number: int

@app.get("/")
def read_root():
    return {"message": "AI PR Review Agent is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

async def run_agent_safe(agent_func, pr_diff: str, agent_name: str) -> dict:
    start_time = time.time()
    print(f"[{agent_name}] Starting...")
    try:
        # Run synchronous LLM call in a thread pool to avoid blocking the event loop
        result = await asyncio.to_thread(agent_func, pr_diff)
        duration = time.time() - start_time
        print(f"[{agent_name}] Finished successfully in {duration:.2f}s")
        return result
    except Exception as e:
        duration = time.time() - start_time
        print(f"[{agent_name}] Failed in {duration:.2f}s: {e}")
        # Return empty/error structure so aggregator doesn't crash
        return {"issues": []}

@app.post("/review")
async def create_review(request: ReviewRequest):
    # Fetch PR metadata and diff in a thread pool so it doesn't block
    pr_details = await asyncio.to_thread(get_pr_details, request.repository, request.pr_number)
    pr_diff = await asyncio.to_thread(get_pr_diff, request.repository, request.pr_number)
    
    print("---")
    print("Starting specialized agents concurrently...")
    total_start_time = time.time()
    
    # Run Agents Concurrently
    security_task = run_agent_safe(run_security_review, pr_diff, "Security Agent")
    quality_task = run_agent_safe(run_quality_review, pr_diff, "Quality Agent")
    testing_task = run_agent_safe(run_testing_review, pr_diff, "Testing Agent")
    
    security_review, quality_review, testing_review = await asyncio.gather(
        security_task, quality_task, testing_task
    )
    
    specialized_duration = time.time() - total_start_time
    print(f"All specialized agents completed in {specialized_duration:.2f}s")
    
    # Run Aggregator Agent
    print("[Aggregator Agent] Starting...")
    agg_start_time = time.time()
    try:
        final_review = await asyncio.to_thread(
            run_aggregator_agent, security_review, quality_review, testing_review
        )
        agg_duration = time.time() - agg_start_time
        print(f"[Aggregator Agent] Finished successfully in {agg_duration:.2f}s")
    except Exception as e:
        print(f"[Aggregator Agent] Failed: {e}")
        final_review = {
            "summary": "Aggregation failed due to API error.", 
            "issues": [], 
            "statistics": {"total": 0, "security": 0, "code_quality": 0, "testing": 0}
        }
    print("---")
    
    return {
        "message": "Review request received",
        "repository": request.repository,
        "pr_number": request.pr_number,
        "pr_details": pr_details,
        "pr_diff": pr_diff,
        "final_review": final_review
    }
