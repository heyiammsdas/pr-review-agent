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
        error_msg = "GitHub API Error"
        try:
            error_msg = e.response.json().get("message", "GitHub API Error")
        except Exception:
            pass
            
        raise HTTPException(
            status_code=e.response.status_code, 
            detail=error_msg
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=500, 
            detail="Error connecting to GitHub API"
        )

def get_pr_diff(repository: str, pr_number: int) -> str:
    """
    Fetches the raw diff of a Pull Request from the GitHub REST API.
    """
    github_token = os.getenv("GITHUB_TOKEN")
    
    headers = {
        "Accept": "application/vnd.github.v3.diff",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    url = f"https://api.github.com/repos/{repository}/pulls/{pr_number}"

    try:
        response = httpx.get(url, headers=headers, timeout=10.0)
        response.raise_for_status()
        return response.text
    except httpx.HTTPStatusError as e:
        error_msg = "GitHub API Error fetching diff"
        try:
            error_msg = e.response.json().get("message", "GitHub API Error fetching diff")
        except Exception:
            pass
            
        raise HTTPException(
            status_code=e.response.status_code, 
            detail=error_msg
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=500, 
            detail="Error connecting to GitHub API for diff"
        )

def post_pr_comment(repository: str, pr_number: int, comment: str) -> str:
    """
    Posts a Markdown comment to the Pull Request.
    Returns the HTML URL of the created comment.
    """
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("[GitHub Service] GITHUB_TOKEN not found, skipping PR comment posting.")
        return ""

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"Bearer {github_token}"
    }

    url = f"https://api.github.com/repos/{repository}/issues/{pr_number}/comments"
    payload = {"body": comment}

    try:
        response = httpx.post(url, headers=headers, json=payload, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        return data.get("html_url", "")
    except httpx.HTTPStatusError as e:
        error_msg = f"GitHub API Error: {e.response.status_code}"
        try:
            error_msg = e.response.json().get("message", error_msg)
        except Exception:
            pass
        print(f"[GitHub Service] Failed to post comment: {error_msg}")
        return ""
    except httpx.RequestError as e:
        print("[GitHub Service] Error connecting to GitHub API to post comment.")
        return ""
