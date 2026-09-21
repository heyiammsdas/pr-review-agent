import os
import json
from typing import List, Literal
from pydantic import BaseModel, ValidationError
from google import genai
from google.genai import types
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
        
    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"{system_prompt}\n\nHere is the diff:\n\n{pr_diff}"
        
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ReviewResponse,
            ),
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
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"LLM Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error generating AI review from Gemini"
        )
