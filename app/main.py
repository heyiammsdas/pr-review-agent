import asyncio
import time
import uuid
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from app.services.redis_client import get_redis_connection

load_dotenv()

app = FastAPI()
redis_client = get_redis_connection()
QUEUE_NAME = "pr_review_queue"

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
    # 1. Generate a unique job ID
    job_id = str(uuid.uuid4())
    
    # 2. Create the job data
    job_data = {
        "job_id": job_id,
        "repository": request.repository,
        "pr_number": request.pr_number,
        "status": "queued"
    }
    
    # 3. Save initial status to Redis
    redis_client.set(f"job:{job_id}", json.dumps(job_data))
    
    # 4. Push job to the processing queue
    redis_client.lpush(QUEUE_NAME, job_id)
    
    print(f"Job queued: {job_id} for {request.repository} PR #{request.pr_number}")
    
    # 5. Return immediately
    return {
        "message": "Review job queued",
        "job_id": job_id
    }

@app.get("/review/{job_id}")
async def get_review_status(job_id: str):
    # 1. Fetch job data from Redis
    job_data_str = redis_client.get(f"job:{job_id}")
    
    if not job_data_str:
        raise HTTPException(status_code=404, detail="Job not found")
        
    # 2. Parse and return the current status (and result if completed)
    return json.loads(job_data_str)
