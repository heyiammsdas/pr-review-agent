import asyncio
import time
import uuid
import json
from fastapi import FastAPI, HTTPException, Request, Header
from pydantic import BaseModel
from dotenv import load_dotenv

from app.services.job_queue import push_job_to_queue, get_job_status
from app.services.webhook import verify_github_signature

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
    return {"status": "ok"}

@app.post("/review")
async def create_review(request: ReviewRequest):
    # 1. Generate a unique job ID
    job_id = str(uuid.uuid4())
    
    # 2. Create the job data
    job_data = {
        "job_id": job_id,
        "repository": request.repository,
        "pr_number": request.pr_number,
        "status": "queued",
        "result": None
    }
    
    # 3. Push job and initial state to Redis queue
    push_job_to_queue(job_id, job_data)
    
    print(f"Job queued: {job_id}")
    
    # 4. Return immediately
    return {
        "job_id": job_id,
        "status": "queued"
    }

@app.get("/review/{job_id}")
async def get_review_status(job_id: str):
    # 1. Fetch job data from Redis
    job_data_str = get_job_status(job_id)
    
    if not job_data_str:
        raise HTTPException(status_code=404, detail="Job not found")
        
    # 2. Parse and return the current status (and result if completed)
    return json.loads(job_data_str)

@app.post("/webhook/github")
async def github_webhook(request: Request, x_hub_signature_256: str = Header(None)):
    # 1. Read raw body for signature verification
    payload_body = await request.body()
    
    # 2. Verify signature securely
    if not verify_github_signature(payload_body, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid GitHub webhook signature")
        
    # 3. Parse JSON payload
    try:
        payload = json.loads(payload_body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
    # 4. Extract action
    action = payload.get("action")
    if not action:
        return {"message": "Ignored: No action specified"}
        
    # 5. Support only specific PR actions safely
    supported_actions = ["opened", "synchronize", "reopened"]
    if action not in supported_actions:
        return {"message": f"Ignored: Unsupported action '{action}'"}
        
    # 6. Extract repository and PR number safely
    pr_data = payload.get("pull_request")
    repo_data = payload.get("repository")
    
    if not pr_data or not repo_data:
        return {"message": "Ignored: Missing pull_request or repository data"}
        
    pr_number = pr_data.get("number")
    repository = repo_data.get("full_name")
    
    if not pr_number or not repository:
        raise HTTPException(status_code=400, detail="Missing PR number or repository name")
        
    # 7. Generate Job ID and queue it reusing existing logic
    job_id = str(uuid.uuid4())
    job_data = {
        "job_id": job_id,
        "repository": repository,
        "pr_number": pr_number,
        "status": "queued",
        "result": None,
        "source": "webhook",
        "action": action
    }
    
    push_job_to_queue(job_id, job_data)
    print(f"Job queued: {job_id}")
    
    # 8. Return success response
    return {
        "message": "Webhook received",
        "job_id": job_id,
        "status": "queued"
    }
