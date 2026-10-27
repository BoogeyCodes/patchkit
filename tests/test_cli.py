from __future__ import annotations

import io

from patchkit.cli import main

DIFF = """\
diff --git a/a.py b/a.py
--- a/a.py
+++ b/a.py
@@ -1,1 +1,2 @@
 x = 1
+y = 2
"""


def test_cli_summary_from_stdin(capsys, monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO(DIFF))
    assert main([]) == 0
    assert "1 file changed, 1 insertion(+), 0 deletions(-)" in capsys.readouterr().out


def test_cli_stat(capsys, monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO(DIFF))
    assert main(["--stat"]) == 0
    out = capsys.readouterr().out
    assert "a.py" in out and "+1 -0" in out


def test_cli_bad_diff(capsys, monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO("not a diff"))
    assert main([]) == 2
    assert "patchkit:" in capsys.readouterr().err


def test_cli_missing_file(capsys):
    assert main(["nope.diff"]) == 2
