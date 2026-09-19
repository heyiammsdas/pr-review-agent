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

def generate_pr_review(pr_diff: str) -> dict:
    """
    Sends the PR diff to Gemini and returns a structured JSON review regarding bugs,
    security issues, and code quality.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured or is set to the default placeholder."
        )
        
    try:
        client = genai.Client(api_key=api_key)
        
        prompt = (
            "You are an expert software engineer and code reviewer.\n"
            "Review the following Pull Request diff for potential bugs, security problems, "
            "code quality issues, performance bottlenecks, and testing gaps.\n"
            "You must return the review STRICTLY in JSON format matching the schema.\n"
            "If no issues are found, return an empty list for 'issues'.\n\n"
            f"Here is the diff:\n\n{pr_diff}"
        )
        
        # Make the request to Gemini asking for structured JSON matching our Pydantic model
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ReviewResponse,
            ),
        )
        
        # Validate the response text strictly with Pydantic
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
        # We print to local logs for debugging but NEVER expose the key or stack trace to the client.
        print(f"LLM Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error generating AI review from Gemini"
        )
