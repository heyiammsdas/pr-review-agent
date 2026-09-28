import os
import json
import time
from typing import List, Literal, Optional
from pydantic import BaseModel, ValidationError
from google import genai
from google.genai import types
from google.genai import errors
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

class ReviewIssue(BaseModel):
    severity: Literal["critical", "high", "medium", "low"]
    category: Literal["security", "bug", "code_quality", "performance", "testing"]
    file: str
    line: Optional[int] = None
    title: str
    description: str
    suggestion: str
    is_contextual: Optional[bool] = False

class ReviewResponse(BaseModel):
    issues: List[ReviewIssue]

class AggregatedStatistics(BaseModel):
    total: int
    security: int
    code_quality: int
    testing: int

class AggregatedReviewResponse(BaseModel):
    summary: str
    issues: List[ReviewIssue]
    statistics: AggregatedStatistics

def analyze_diff(pr_diff: str, system_prompt: str, response_class=ReviewResponse) -> dict:
    """
    Sends the PR diff and a custom system prompt to Gemini, 
    returning a structured JSON review based on the provided schema.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured or is set to the default placeholder."
        )
        
    client = genai.Client(api_key=api_key)
    prompt = f"{system_prompt}\n\nHere is the input data:\n\n{pr_diff}"
    
    max_retries = 5
    base_delay = 5
    
    for attempt in range(max_retries + 1):
        try:
            response = client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=response_class,
                ),
            )
            break
        except errors.APIError as e:
            # Check for 429 Too Many Requests, 503 Service Unavailable or 529 Resource Exhausted
            if e.code in (429, 503, 529):
                if attempt < max_retries:
                    error_msg = getattr(e, 'message', str(e))
                    
                    import re
                    import random
                    
                    # Look for explicit retry delay in the error message (e.g. "Please retry in 17.574s.")
                    match = re.search(r"retry in (\d+(?:\.\d+)?)s", error_msg)
                    if match:
                        delay = float(match.group(1)) + random.uniform(0.5, 2.0)
                    else:
                        delay = base_delay * (2 ** attempt) + random.uniform(1.0, 5.0)
                        
                    print(f"Gemini API {e.code} Error: {error_msg}. Retrying in {delay:.2f} seconds (Attempt {attempt+1}/{max_retries})...", flush=True)
                    time.sleep(delay)
                    continue
                else:
                    error_msg = getattr(e, 'message', str(e))
                    print(f"Gemini API {e.code} Error: Max retries exceeded. Details: {error_msg}", flush=True)
                    raise HTTPException(
                        status_code=503,
                        detail="Gemini service is temporarily unavailable due to high demand. Please try again later."
                    )
            else:
                error_msg = getattr(e, 'message', str(e))
                print(f"LLM API Error: {error_msg}", flush=True)
                raise HTTPException(
                    status_code=500,
                    detail="Error generating AI review from Gemini"
                )
        except Exception as e:
            print(f"LLM General Error: {type(e).__name__} - {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error generating AI review from Gemini"
            )

    try:
        parsed_data = json.loads(response.text)
        validated_review = response_class(**parsed_data)
        return validated_review.model_dump()
    except (json.JSONDecodeError, ValidationError) as parse_err:
        print(f"LLM Parsing Error: {str(parse_err)}")
        raise HTTPException(
            status_code=500,
            detail="Received invalid or malformed output from Gemini."
        )
