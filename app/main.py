from fastapi import FastAPI
from pydantic import BaseModel
from app.services.github import get_pr_details, get_pr_diff
from app.agents.security_agent import run_security_review
from app.agents.quality_agent import run_quality_review
from app.agents.testing_agent import run_testing_review

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
def create_review(request: ReviewRequest):
    # Fetch PR metadata
    pr_details = get_pr_details(request.repository, request.pr_number)
    
    # Fetch PR diff
    pr_diff = get_pr_diff(request.repository, request.pr_number)
    
    # Run Agents Sequentially
    security_review = run_security_review(pr_diff)
    quality_review = run_quality_review(pr_diff)
    testing_review = run_testing_review(pr_diff)
    
    return {
        "message": "Review request received",
        "repository": request.repository,
        "pr_number": request.pr_number,
        "pr_details": pr_details,
        "pr_diff": pr_diff,
        "security_review": security_review,
        "quality_review": quality_review,
        "testing_review": testing_review
    }
