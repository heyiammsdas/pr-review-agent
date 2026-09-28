import re
from typing import Dict, List, Set, Optional

class ChangedFile:
    def __init__(self, new_path: str):
        self.new_path = new_path
        self.changed_new_lines: Set[int] = set()

def parse_diff(diff_text: str) -> Dict[str, ChangedFile]:
    """
    Parses a unified diff and returns a mapping of new file paths to ChangedFile objects.
    Tracks which new lines were added/modified.
    """
    files: Dict[str, ChangedFile] = {}
    current_file: Optional[ChangedFile] = None
    
    lines = diff_text.splitlines()
    
    new_path = ""
    new_line_num = 0
    
    for line in lines:
        if line.startswith("--- "):
            pass # We don't strictly need old_path for new line mapping
        elif line.startswith("+++ "):
            p = line[4:]
            if p.startswith("b/"):
                p = p[2:]
            elif p.startswith("a/"): # Sometimes it might not follow exactly, but usually b/
                p = p[2:]
            new_path = p
            # Skip /dev/null which means file was deleted
            if new_path != "/dev/null":
                current_file = ChangedFile(new_path)
                files[new_path] = current_file
            else:
                current_file = None
        elif line.startswith("@@ "):
            # parse hunk header
            # @@ -l,s +l,s @@
            match = re.search(r"@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
            if match:
                new_line_num = int(match.group(2))
        elif current_file is not None:
            if line.startswith("+") and not line.startswith("+++"):
                current_file.changed_new_lines.add(new_line_num)
                new_line_num += 1
            elif line.startswith("-") and not line.startswith("---"):
                pass # deletions don't advance the new line counter
            elif line.startswith(" ") or line == "":
                new_line_num += 1
            elif line == "\\ No newline at end of file":
                pass
                
    return files

def validate_finding(finding: dict, parsed_diff: Dict[str, ChangedFile]) -> dict:
    """
    Validates a finding against the parsed diff.
    - If the file is not in the diff, it's marked as contextual.
    - If the line is not in the changed lines, it's either snapped to null or marked contextual.
    
    Actually, the requirement says:
    7. When an AI agent reports a finding, validate that:
       - the file exists in the PR diff
       - the reported line belongs to a changed line/range when a line number is provided
    8. If an issue relates to repository context that is NOT changed in the PR, allow the finding to reference the related file but clearly mark that it is contextual rather than a direct change finding.
    9. Do not reject an otherwise useful review merely because an exact line cannot be determined.
    10. If an exact line cannot be determined, use: "line": null instead of inventing a line.
    """
    
    file_path = finding.get("file")
    line = finding.get("line")
    
    finding["is_contextual"] = False
    
    if not file_path:
        finding["line"] = None
        return finding
        
    if file_path not in parsed_diff:
        finding["is_contextual"] = True
        return finding
        
    changed_file = parsed_diff[file_path]
    
    if line is not None:
        if line not in changed_file.changed_new_lines:
            finding["line"] = None
            
    return finding
