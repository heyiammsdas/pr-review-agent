import pytest
from app.services.diff_parser import parse_diff

def test_single_changed_line():
    diff = """--- a/file.py
+++ b/file.py
@@ -1,3 +1,3 @@
 def foo():
-    return False
+    return True
"""
    result = parse_diff(diff)
    assert "file.py" in result
    assert result["file.py"].changed_new_lines == {2}

def test_multiple_changed_lines():
    diff = """--- a/file.py
+++ b/file.py
@@ -10,3 +10,4 @@
 def bar():
-    pass
+    print("Hello")
+    return True
"""
    result = parse_diff(diff)
    assert "file.py" in result
    assert result["file.py"].changed_new_lines == {11, 12}

def test_multiple_changed_files():
    diff = """--- a/file1.py
+++ b/file1.py
@@ -1,1 +1,2 @@
+import os
--- a/file2.py
+++ b/file2.py
@@ -5,2 +5,2 @@
-x = 1
+x = 2
"""
    result = parse_diff(diff)
    assert "file1.py" in result
    assert result["file1.py"].changed_new_lines == {1}
    assert "file2.py" in result
    assert result["file2.py"].changed_new_lines == {5}

def test_added_lines():
    diff = """--- /dev/null
+++ b/new_file.py
@@ -0,0 +1,2 @@
+def init():
+    pass
"""
    result = parse_diff(diff)
    assert "new_file.py" in result
    assert result["new_file.py"].changed_new_lines == {1, 2}

def test_deleted_lines():
    diff = """--- a/old_file.py
+++ /dev/null
@@ -1,2 +0,0 @@
-def init():
-    pass
"""
    result = parse_diff(diff)
    # File is deleted, so we should not track new lines for it
    assert "/dev/null" not in result
    assert not result

def test_modified_lines():
    diff = """--- a/test.py
+++ b/test.py
@@ -1,3 +1,3 @@
 a = 1
-b = 2
+b = 3
 c = 4
"""
    result = parse_diff(diff)
    assert "test.py" in result
    assert result["test.py"].changed_new_lines == {2}

def test_invalid_unusual_diff():
    diff = "This is not a diff\nAnother line"
    result = parse_diff(diff)
    assert not result
    
    diff2 = """--- a/test.py
+++ b/test.py
@@ -1,3 +1,3 @@
 \\ No newline at end of file
"""
    result2 = parse_diff(diff2)
    assert "test.py" in result2
    assert not result2["test.py"].changed_new_lines
