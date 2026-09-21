from app.services.llm import analyze_diff

def run_testing_review(pr_diff: str) -> dict:
    """
    Analyzes the PR diff exclusively for testing-related concerns.
    """
    system_prompt = (
        "You are an expert Testing Review Agent.\n"
        "Your ONLY responsibility is to identify testing-related concerns in the provided Pull Request diff.\n"
        "Check specifically for:\n"
        "- New functionality introduced without appropriate tests\n"
        "- Missing edge-case tests\n"
        "- Existing tests that may need to be updated because of the code changes\n"
        "- Possible regression risks\n"
        "- Important untested behavior\n\n"
        "DO NOT report security vulnerabilities.\n"
        "DO NOT report general code-quality, formatting, or readability issues.\n"
        "If there are no testing issues or missing tests, return an empty list of issues."
    )
    
    return analyze_diff(pr_diff, system_prompt)
