from app.services.llm import analyze_diff

def run_security_review(pr_diff: str, retrieved_context: list = None) -> dict:
    """
    Analyzes the PR diff exclusively for security vulnerabilities, using context.
    """
    if retrieved_context is None:
        retrieved_context = []
        
    context_text = "\n".join([f"File: {c['file']}\n{c['content']}\n---" for c in retrieved_context])
    
    system_prompt = (
        "You are an expert Security Review Agent.\n"
        "Your ONLY responsibility is to identify security vulnerabilities in the provided Pull Request diff.\n"
        "Check specifically for SQL injection, Command injection, Hardcoded secrets, Auth flaws, XSS, etc.\n\n"
        "DO NOT report general code-quality or formatting issues.\n\n"
        "IMPORTANT:\n"
        "The PR diff contains the proposed changes.\n"
        "The retrieved context contains related repository code that may help understand the changes.\n"
        "DO NOT treat retrieved context as a changed file unless it appears in the PR diff. Focus primarily on reviewing the actual PR changes.\n\n"
        "When reporting findings, you MUST identify the affected file and the line number of the NEW file if possible.\n"
        "If an exact line cannot be determined, use null for the line number rather than inventing one."
    )
    
    combined_prompt = (
        f"--- PR DIFF ---\n{pr_diff}\n\n"
        f"--- RETRIEVED CONTEXT ---\n{context_text}\n"
    )
    
    return analyze_diff(combined_prompt, system_prompt)
