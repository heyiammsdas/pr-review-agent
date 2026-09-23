import hmac
import hashlib
import os
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, Header
from pydantic import BaseModel
from dotenv import load_dotenv
from app.services.review import process_pr_review

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
    result = await process_pr_review(request.repository, request.pr_number)
    return {
        "message": "Review request received",
        **result
    }

async def run_background_review(repository: str, pr_number: int):
    try:
        await process_pr_review(repository, pr_number)
        print(f"Background review for {repository} PR #{pr_number} completed.")
    except Exception as e:
        print(f"Background review for {repository} PR #{pr_number} failed: {e}")

@app.post("/webhook/github")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: str = Header(None)
):
    webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET")
    
    if not webhook_secret:
        raise HTTPException(status_code=500, detail="Webhook secret not configured")
        
    if not x_hub_signature_256:
        raise HTTPException(status_code=401, detail="Missing signature")
        
    payload_body = await request.body()
    
    # Verify signature
    signature = "sha256=" + hmac.new(
        webhook_secret.encode(),
        payload_body,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")
        
    payload = await request.json()
    
    event_type = request.headers.get("X-GitHub-Event")
    if event_type == "ping":
        return {"message": "pong"}
        
    if event_type != "pull_request":
        return {"message": f"Ignored event: {event_type}"}
        
    action = payload.get("action")
    if action not in ["opened", "synchronize", "reopened"]:
        return {"message": f"Ignored PR action: {action}"}
        
    pr = payload.get("pull_request", {})
    repo = payload.get("repository", {})
    
    pr_number = pr.get("number")
    repository = repo.get("full_name")
    
    if not pr_number or not repository:
        raise HTTPException(status_code=400, detail="Missing PR number or repository in payload")
        
    print(f"Received GitHub webhook")
    print(f"Event: {event_type}")
    print(f"Action: {action}")
    print(f"Repository: {repository}")
    print(f"PR: #{pr_number}")
    print(f"Starting review in background...")
    
    # Schedule the review to run in the background so GitHub gets a quick 200 response
    background_tasks.add_task(run_background_review, repository, pr_number)
    
    return {"message": "Webhook accepted, review started"}
