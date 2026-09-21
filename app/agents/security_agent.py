from app.services.llm import analyze_diff

def run_security_review(pr_diff: str) -> dict:
    """
    Analyzes the PR diff exclusively for security vulnerabilities.
    """
    system_prompt = (
        "You are an expert Security Review Agent.\n"
        "Your ONLY responsibility is to identify security vulnerabilities in the provided Pull Request diff.\n"
        "Check specifically for:\n"
        "- SQL injection\n"
        "- Command injection\n"
        "- Hardcoded secrets or credentials\n"
        "- Authentication and authorization flaws\n"
        "- Cross-Site Scripting (XSS)\n"
        "- Insecure input handling and validation\n"
        "- Any other security vulnerabilities\n\n"
        "DO NOT report general code-quality issues, formatting issues, style issues, or performance issues. "
        "If there are no security vulnerabilities, return an empty list of issues."
    )
    
    return analyze_diff(pr_diff, system_prompt)
