import asyncio
import time
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

from app.graph.review_graph import review_graph

load_dotenv()

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

@app.post("/review")
async def create_review(request: ReviewRequest):
    print("\n--- Graph started ---")
    start_time = time.time()
    
    # Initialize the starting state
    initial_state = {
        "repository": request.repository,
        "pr_number": request.pr_number,
        "pr_details": {},
        "pr_diff": "",
        "security_review": {},
        "quality_review": {},
        "testing_review": {},
        "final_review": {}
    }
    
    # Run the graph using native LangGraph ainvoke
    try:
        final_state = await review_graph.ainvoke(initial_state)
    except Exception as e:
        print(f"Graph execution failed: {e}")
        return {"message": "Review request failed"}
        
    duration = time.time() - start_time
    print(f"--- Graph finished in {duration:.2f}s ---")
    
    return {
        "message": "Review request received",
        "repository": request.repository,
        "pr_number": request.pr_number,
        "pr_details": final_state.get("pr_details", {}),
        "pr_diff": final_state.get("pr_diff", ""),
        "final_review": final_state.get("final_review", {})
    }
