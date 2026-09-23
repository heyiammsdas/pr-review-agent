import asyncio
import time
from app.services.github import get_pr_details, get_pr_diff
from app.agents.security_agent import run_security_review
from app.agents.quality_agent import run_quality_review
from app.agents.testing_agent import run_testing_review
from app.agents.aggregator_agent import run_aggregator_agent

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

async def process_pr_review(repository: str, pr_number: int) -> dict:
    """
    Core workflow to process a PR review. 
    Can be called by the manual endpoint or background webhook task.
    """
    pr_details = await asyncio.to_thread(get_pr_details, repository, pr_number)
    pr_diff = await asyncio.to_thread(get_pr_diff, repository, pr_number)
    
    print("---")
    print(f"Starting specialized agents concurrently for {repository} PR #{pr_number}...")
    total_start_time = time.time()
    
    security_task = run_agent_safe(run_security_review, pr_diff, "Security Agent")
    quality_task = run_agent_safe(run_quality_review, pr_diff, "Quality Agent")
    testing_task = run_agent_safe(run_testing_review, pr_diff, "Testing Agent")
    
    security_review, quality_review, testing_review = await asyncio.gather(
        security_task, quality_task, testing_task
    )
    
    specialized_duration = time.time() - total_start_time
    print(f"All specialized agents completed in {specialized_duration:.2f}s")
    
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
        "repository": repository,
        "pr_number": pr_number,
        "pr_details": pr_details,
        "pr_diff": pr_diff,
        "final_review": final_review
    }
