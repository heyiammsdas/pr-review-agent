import asyncio
import time
import uuid
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from app.services.job_queue import push_job_to_queue, get_job_status

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
