import pytest
from app.services.diff_parser import parse_diff, validate_finding

@pytest.fixture
def sample_diff():
    diff_text = """--- a/src/main.py
+++ b/src/main.py
@@ -10,3 +10,4 @@
 def main():
-    print("old")
+    print("new")
+    return True
"""
    return parse_diff(diff_text)

def test_valid_changed_file_and_line(sample_diff):
    finding = {
        "file": "src/main.py",
        "line": 11,
        "title": "Test"
    }
    validated = validate_finding(finding, sample_diff)
    assert validated["file"] == "src/main.py"
    assert validated["line"] == 11
    assert not validated["is_contextual"]

def test_invalid_file(sample_diff):
    finding = {
        "file": "src/missing.py",
        "line": 10,
        "title": "Test"
    }
    validated = validate_finding(finding, sample_diff)
    assert validated["is_contextual"] is True
    # The line can remain as is, but it's contextual
    assert validated["line"] == 10

def test_line_outside_changed_range(sample_diff):
    finding = {
        "file": "src/main.py",
        "line": 50, # Not in changed lines
        "title": "Test"
    }
    validated = validate_finding(finding, sample_diff)
    assert validated["line"] is None
    assert not validated["is_contextual"]

def test_null_line(sample_diff):
    finding = {
        "file": "src/main.py",
        "line": None,
        "title": "Test"
    }
    validated = validate_finding(finding, sample_diff)
    assert validated["line"] is None
    assert not validated["is_contextual"]

def test_contextual_finding(sample_diff):
    finding = {
        "file": "src/other.py",
        "line": 10,
        "title": "Context issue"
    }
    validated = validate_finding(finding, sample_diff)
    assert validated["is_contextual"] is True
    
def test_no_file(sample_diff):
    finding = {
        "title": "Global issue"
    }
    validated = validate_finding(finding, sample_diff)
    assert validated.get("file") is None
    assert validated["line"] is None
    assert not validated["is_contextual"]
