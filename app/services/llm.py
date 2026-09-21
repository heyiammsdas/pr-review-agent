import os
import json
import time
from typing import List, Literal
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
    line: int
    issue: str
    explanation: str
    suggestion: str

class ReviewResponse(BaseModel):
    issues: List[ReviewIssue]

def analyze_diff(pr_diff: str, system_prompt: str) -> dict:
    """
    Sends the PR diff and a custom system prompt to Gemini, 
    returning a structured JSON review based on ReviewResponse schema.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured or is set to the default placeholder."
        )
        
    client = genai.Client(api_key=api_key)
    prompt = f"{system_prompt}\n\nHere is the diff:\n\n{pr_diff}"
    
    max_retries = 3
    base_delay = 2
    
    for attempt in range(max_retries + 1):
        try:
            response = client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ReviewResponse,
                ),
            )
            break
        except errors.APIError as e:
            # Check for 503 Service Unavailable or 529 Resource Exhausted
            if e.code in (503, 529):
                if attempt < max_retries:
                    delay = base_delay * (2 ** attempt)
                    print(f"Gemini API {e.code} Error. Retrying in {delay} seconds (Attempt {attempt+1}/{max_retries})...")
                    time.sleep(delay)
                    continue
                else:
                    print(f"Gemini API {e.code} Error: Max retries exceeded.")
                    raise HTTPException(
                        status_code=503,
                        detail="Gemini service is temporarily unavailable due to high demand. Please try again later."
                    )
            else:
                # E.g. 400 Bad Request, 403 Forbidden
                print(f"LLM API Error: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail="Error generating AI review from Gemini"
                )
        except Exception as e:
            print(f"LLM General Error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error generating AI review from Gemini"
            )

    try:
        parsed_data = json.loads(response.text)
        validated_review = ReviewResponse(**parsed_data)
        return validated_review.model_dump()
    except (json.JSONDecodeError, ValidationError) as parse_err:
        print(f"LLM Parsing Error: {str(parse_err)}")
        raise HTTPException(
            status_code=500,
            detail="Received invalid or malformed output from Gemini."
        )
