import os
import httpx
from fastapi import HTTPException

# Using dotenv in case a .env file is present locally
from dotenv import load_dotenv
load_dotenv()

def get_pr_details(repository: str, pr_number: int) -> dict:
    """
    Fetches Pull Request details from the GitHub REST API.
    """
    github_token = os.getenv("GITHUB_TOKEN")
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    
    # Only add authorization if the token is available
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    url = f"https://api.github.com/repos/{repository}/pulls/{pr_number}"

    try:
        response = httpx.get(url, headers=headers, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        
        return {
            "title": data.get("title"),
            "number": data.get("number"),
            "state": data.get("state"),
            "html_url": data.get("html_url")
        }
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code, 
            detail=f"GitHub API Error: {e.response.text}"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error connecting to GitHub API: {str(e)}"
        )
