from __future__ import annotations

import pytest

from patchkit import parse_patch
from patchkit.parser import PatchError

MODIFY = """\
diff --git a/greet.py b/greet.py
index e69de29..a1b2c3d 100644
--- a/greet.py
+++ b/greet.py
@@ -1,3 +1,4 @@
 def greet(name):
-    return "hi " + name
+    # friendlier
+    return "hello, " + name
"""

NEW_FILE = """\
diff --git a/new.txt b/new.txt
new file mode 100644
--- /dev/null
+++ b/new.txt
@@ -0,0 +1,2 @@
+line one
+line two
"""

DELETE_FILE = """\
diff --git a/old.txt b/old.txt
deleted file mode 100644
--- a/old.txt
+++ /dev/null
@@ -1,2 +0,0 @@
-gone one
-gone two
"""


def test_parses_a_modification():
    patch = parse_patch(MODIFY)
    assert len(patch.files) == 1
    change = patch.files[0]
    assert change.path == "greet.py"
    assert change.added == 2
    assert change.removed == 1
    assert not change.is_new and not change.is_delete


def test_parses_a_new_file():
    change = parse_patch(NEW_FILE).files[0]
    assert change.is_new
    assert change.path == "new.txt"
    assert change.added == 2
    assert change.removed == 0


def test_parses_a_deletion():
    change = parse_patch(DELETE_FILE).files[0]
    assert change.is_delete
    assert change.path == "old.txt"
    assert change.removed == 2


def test_multi_file_summary_and_stat():
    patch = parse_patch(MODIFY + NEW_FILE)
    assert len(patch.files) == 2
    assert patch.added == 4
    assert patch.removed == 1
    assert patch.summary() == "2 files changed, 4 insertions(+), 1 deletion(-)"
    assert patch.stat() == [("greet.py", 2, 1), ("new.txt", 2, 0)]
    assert patch.net == 3  # 4 insertions - 1 deletion
    assert patch.paths() == ["greet.py", "new.txt"]


def test_hunk_counts():
    hunk = parse_patch(MODIFY).files[0].hunks[0]
    assert hunk.old_start == 1 and hunk.new_start == 1
    assert hunk.added == 2 and hunk.removed == 1


def test_singular_summary():
    assert parse_patch(MODIFY).summary().endswith("1 deletion(-)")


@pytest.mark.parametrize("text", ["", "not a diff at all", "random text\nmore text"])
def test_rejects_non_diff(text: str):
    with pytest.raises(PatchError):
        parse_patch(text)
