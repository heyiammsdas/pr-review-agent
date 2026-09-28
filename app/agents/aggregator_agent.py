import json
from app.services.llm import analyze_diff, AggregatedReviewResponse

def run_aggregator_agent(security_review: dict, quality_review: dict, testing_review: dict, pr_diff: str = "") -> dict:
    """
    Aggregates findings from the specialized agents into a single cohesive structured response.
    Validates findings against the PR diff to ensure line numbers are accurate.
    """
    from app.services.diff_parser import parse_diff, validate_finding
    
    system_prompt = (
        "You are an expert Aggregator Agent.\n"
        "Your ONLY responsibility is to aggregate and organize findings from the Security, Quality, and Testing agents.\n"
        "Rules:\n"
        "- Combine findings from all three agents.\n"
        "- Remove obvious duplicate findings.\n"
        "- Preserve the original category and severity assigned by the specialized agents.\n"
        "- Organize findings in a clear order (e.g., Critical first, then High, etc.).\n"
        "- DO NOT invent new issues that were not identified by the specialized agents.\n"
        "- Produce a short summary of the review.\n"
        "- Generate accurate statistics based on the final issues list.\n"
        "Return the final review STRICTLY adhering to the schema."
    )
    
    # Combine the inputs into a single string to pass as the "input data" to analyze_diff
    combined_inputs = json.dumps({
        "security_findings": security_review,
        "quality_findings": quality_review,
        "testing_findings": testing_review
    }, indent=2)
    
    final_review = analyze_diff(combined_inputs, system_prompt, response_class=AggregatedReviewResponse)
    
    if pr_diff:
        parsed_diff = parse_diff(pr_diff)
        if "issues" in final_review:
            validated_issues = []
            for issue in final_review["issues"]:
                validated_issue = validate_finding(issue, parsed_diff)
                validated_issues.append(validated_issue)
            final_review["issues"] = validated_issues
            
    return final_review
