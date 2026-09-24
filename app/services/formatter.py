def format_review_as_markdown(final_review: dict) -> str:
    """
    Formats the JSON final_review output into a readable Markdown comment.
    """
    summary = final_review.get("summary", "No summary provided.")
    
    md = [
        "## 🤖 AI PR Review",
        "",
        "### Summary",
        summary,
        "",
        "### Issues Found"
    ]
    
    issues = final_review.get("issues", [])
    if not issues:
        md.append("\nNo critical issues found! 🎉\n")
    else:
        for issue in issues:
            severity = issue.get("severity", "Medium").title()
            category = issue.get("category", "General").title()
            file_path = issue.get("file", "N/A")
            line = issue.get("line", "N/A")
            description = issue.get("issue", issue.get("description", "Unknown issue"))
            suggestion = issue.get("suggestion", "")
            
            icon = "🔴" if severity == "High" else "🟡" if severity == "Medium" else "⚪"
            md.append(f"#### {icon} {severity}")
            md.append(f"- **{category}**")
            md.append(f"  - File: `{file_path}`")
            if line != "N/A":
                md.append(f"  - Line: {line}")
            md.append(f"  - Issue: {description}")
            if suggestion:
                md.append(f"  - Suggestion: {suggestion}")
            md.append("")
    
    md.append("### Review Statistics\n")
    md.append("| Category | Count |")
    md.append("|----------|-------|")
    
    stats = final_review.get("statistics", {})
    sec_count = stats.get("security", 0)
    qual_count = stats.get("code_quality", 0)
    test_count = stats.get("testing", 0)
    total = stats.get("total", sec_count + qual_count + test_count)
    
    md.append(f"| Security | {sec_count} |")
    md.append(f"| Code Quality | {qual_count} |")
    md.append(f"| Testing | {test_count} |")
    md.append(f"| Total | {total} |")
    
    return "\n".join(md)
