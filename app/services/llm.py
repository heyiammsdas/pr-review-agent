import os
import google.generativeai as genai
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

def generate_pr_review(pr_diff: str) -> str:
    """
    Sends the PR diff to Gemini and returns a review regarding bugs,
    security issues, and code quality.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured"
        )
        
    try:
        genai.configure(api_key=api_key)
        
        # We use gemini-2.5-flash as the fast, standard model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = (
            "You are an expert software engineer and code reviewer.\n"
            "Review the following Pull Request diff for:\n"
            "- Potential bugs\n"
            "- Security problems\n"
            "- Code quality issues\n\n"
            "Please explain each detected issue and why it matters clearly and concisely. "
            "If no issues are found, just say that the code looks good.\n\n"
            f"Here is the diff:\n\n{pr_diff}"
        )
        
        response = model.generate_content(prompt)
        
        return response.text
    except Exception as e:
        # Avoid exposing API keys in error logs
        print(f"LLM Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error generating AI review from Gemini"
        )
