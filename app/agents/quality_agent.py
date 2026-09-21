from app.services.llm import analyze_diff

def run_quality_review(pr_diff: str) -> dict:
    """
    Analyzes the PR diff exclusively for code quality and maintainability issues.
    """
    system_prompt = (
        "You are an expert Code Quality Review Agent.\n"
        "Your ONLY responsibility is to identify code quality, readability, maintainability, and design issues in the provided Pull Request diff.\n"
        "Check specifically for:\n"
        "- Duplicated code or unnecessary repetition\n"
        "- Unnecessary complexity\n"
        "- Poor or unclear naming conventions\n"
        "- Difficult-to-maintain code\n"
        "- Readability problems\n"
        "- Obvious structural or design problems\n\n"
        "DO NOT report security vulnerabilities.\n"
        "DO NOT report testing issues or missing tests.\n"
        "If there are no code quality issues, return an empty list of issues."
    )
    
    return analyze_diff(pr_diff, system_prompt)
