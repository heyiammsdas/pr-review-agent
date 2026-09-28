def format_review_as_markdown(final_review: dict) -> str:
    """
    Formats the JSON final_review output into a readable Markdown comment.
    """
    summary = final_review.get("summary", "No summary provided.")
    
    md = [
        "## 🤖 AI PR Review",
        "",
        "### Summary",
        "",
        summary,
        ""
    ]
    
    issues = final_review.get("issues", [])
    
    # Group issues by category
    categories = {
        "security": [],
        "code_quality": [],
        "testing": []
    }
    
    # Put other categories into the default mapped categories
    for issue in issues:
        cat = issue.get("category", "").lower()
        if cat in categories:
            categories[cat].append(issue)
        elif cat == "bug" or cat == "performance":
            categories["code_quality"].append(issue)
        else:
            categories["code_quality"].append(issue)
            
    # Format Security
    md.append("### 🔴 Security")
    md.append("")
    if not categories["security"]:
        md.append("No security issues found.")
        md.append("")
    else:
        for issue in categories["security"]:
            md.extend(_format_issue(issue))
            
    # Format Code Quality
    md.append("### 🟡 Code Quality")
    md.append("")
    if not categories["code_quality"]:
        md.append("No code quality issues found.")
        md.append("")
    else:
        for issue in categories["code_quality"]:
            md.extend(_format_issue(issue))

    # Format Testing
    md.append("### Testing")
    md.append("")
    if not categories["testing"]:
        md.append("No testing issues found.")
        md.append("")
    else:
        for issue in categories["testing"]:
            md.extend(_format_issue(issue))

    md.append("### Review Statistics")
    md.append("")
    md.append("| Category | Count |")
    md.append("|---|---:|")
    
    stats = final_review.get("statistics", {})
    sec_count = stats.get("security", len(categories["security"]))
    qual_count = stats.get("code_quality", len(categories["code_quality"]))
    test_count = stats.get("testing", len(categories["testing"]))
    total = stats.get("total", sec_count + qual_count + test_count)
    
    md.append(f"| Security | {sec_count} |")
    md.append(f"| Code Quality | {qual_count} |")
    md.append(f"| Testing | {test_count} |")
    md.append(f"| Total | {total} |")
    
    return "\n".join(md)

def _format_issue(issue: dict) -> list:
    md = []
    
    file_path = issue.get("file", "N/A")
    line = issue.get("line")
    is_contextual = issue.get("is_contextual", False)
    title = issue.get("title", issue.get("issue", "Issue"))
    description = issue.get("description", issue.get("explanation", ""))
    suggestion = issue.get("suggestion", "")
    
    file_display = f"`{file_path}`"
    if file_path != "N/A":
        if is_contextual:
            file_display = f"`{file_path}` (Contextual)"
        elif line is not None:
            file_display = f"`{file_path}:{line}`"
            
    md.append(f"**{file_display}**")
    md.append("")
    md.append(f"**{title}**")
    md.append("")
    if description:
        md.append(description)
        md.append("")
    if suggestion:
        md.append(f"**Suggestion:** {suggestion}")
        md.append("")
        
    return md
