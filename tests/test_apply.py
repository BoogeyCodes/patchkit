from __future__ import annotations

import pytest

from patchkit import apply_patch, parse_patch
from patchkit.apply import ApplyError

MODIFY = """\
--- a/greet.py
+++ b/greet.py
@@ -1,2 +1,2 @@
 def greet(name):
-    return "hi " + name
+    return "hello, " + name
"""


def test_applies_a_modification():
    files = {"greet.py": 'def greet(name):\n    return "hi " + name\n'}
    result = apply_patch(parse_patch(MODIFY), files)
    assert result["greet.py"] == 'def greet(name):\n    return "hello, " + name\n'
    # original mapping is untouched
    assert files["greet.py"].endswith('"hi " + name\n')


def test_creates_a_new_file():
    patch = parse_patch("--- /dev/null\n+++ b/new.txt\n@@ -0,0 +1,2 @@\n+a\n+b\n")
    result = apply_patch(patch, {})
    assert result["new.txt"] == "a\nb"


def test_deletes_a_file():
    patch = parse_patch("--- a/old.txt\n+++ /dev/null\n@@ -1,1 +0,0 @@\n-gone\n")
    result = apply_patch(patch, {"old.txt": "gone\n"})
    assert "old.txt" not in result


def test_context_mismatch_raises():
    files = {"greet.py": 'def greet(name):\n    return "DIFFERENT" + name\n'}
    with pytest.raises(ApplyError) as exc:
        apply_patch(parse_patch(MODIFY), files)
    assert "context mismatch" in str(exc.value)


def test_missing_target_raises():
    with pytest.raises(ApplyError):
        apply_patch(parse_patch(MODIFY), {})


def test_add_only_hunk_at_end():
    patch = parse_patch("--- a/f.txt\n+++ b/f.txt\n@@ -1,1 +1,2 @@\n a\n+b\n")
    result = apply_patch(patch, {"f.txt": "a\n"})
    assert result["f.txt"] == "a\nb\n"
