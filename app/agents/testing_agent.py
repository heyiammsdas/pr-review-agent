from app.services.llm import analyze_diff

def run_testing_review(pr_diff: str, retrieved_context: list = None) -> dict:
    """
    Analyzes the PR diff exclusively for testing-related concerns, using context.
    """
    if retrieved_context is None:
        retrieved_context = []
        
    context_text = "\n".join([f"File: {c['file']}\n{c['content']}\n---" for c in retrieved_context])
    
    system_prompt = (
        "You are an expert Testing Review Agent.\n"
        "Your ONLY responsibility is to identify testing-related concerns (missing tests, edge cases, regression risks) in the provided Pull Request diff.\n"
        "DO NOT report security vulnerabilities or general code-quality issues.\n\n"
        "IMPORTANT:\n"
        "The PR diff contains the proposed changes.\n"
        "The retrieved context contains related repository code that may help understand the changes.\n"
        "DO NOT treat retrieved context as a changed file unless it appears in the PR diff. Focus primarily on reviewing the actual PR changes."
    )
    
    combined_prompt = (
        f"--- PR DIFF ---\n{pr_diff}\n\n"
        f"--- RETRIEVED CONTEXT ---\n{context_text}\n"
    )
    
    return analyze_diff(combined_prompt, system_prompt)
