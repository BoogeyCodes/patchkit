"""Parse unified-diff text into a :class:`Patch`."""

from __future__ import annotations

import re

from patchkit.model import FileChange, Hunk, Patch

_HUNK_HEADER = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
_DEV_NULL = "/dev/null"


class PatchError(ValueError):
    """Raised when the diff text cannot be parsed."""


def _strip_prefix(path: str) -> str:
    """Drop a leading ``a/`` or ``b/`` as git writes, and surrounding quotes/whitespace."""
    path = path.strip().strip('"')
    if path.startswith(("a/", "b/")):
        return path[2:]
    return path


def parse_patch(text: str) -> Patch:
    lines = text.splitlines()
    patch = Patch()
    current: FileChange | None = None
    hunk: Hunk | None = None
    i = 0

    while i < len(lines):
        line = lines[i]

        if line.startswith("diff --git "):
            current = _begin_file(line)
            patch.files.append(current)
            hunk = None
            i += 1
            continue

        if line.startswith("--- "):
            old = line[4:]
            new_line = lines[i + 1] if i + 1 < len(lines) and lines[i + 1].startswith("+++ ") else None
            if new_line is None:
                raise PatchError(f"'---' header without a following '+++' at line {i + 1}")
            new = new_line[4:]
            if current is None or current.hunks:
                current = FileChange(old_path="", new_path="")
                patch.files.append(current)
            current.is_new = old.strip() == _DEV_NULL
            current.is_delete = new.strip() == _DEV_NULL
            current.old_path = _strip_prefix(old) if not current.is_new else (current.old_path or _strip_prefix(new))
            current.new_path = _strip_prefix(new) if not current.is_delete else (current.new_path or _strip_prefix(old))
            hunk = None
            i += 2
            continue

        match = _HUNK_HEADER.match(line)
        if match:
            if current is None:
                raise PatchError(f"hunk header before any file header at line {i + 1}")
            hunk = Hunk(
                old_start=int(match.group(1)),
                old_count=int(match.group(2) or 1),
                new_start=int(match.group(3)),
                new_count=int(match.group(4) or 1),
            )
            current.hunks.append(hunk)
            i += 1
            continue

        if hunk is not None and line[:1] in (" ", "+", "-"):
            hunk.lines.append(line)
            i += 1
            continue

        if line == "\\ No newline at end of file":
            i += 1
            continue

        # Any other line (index …, mode …, blank, prose) is ignored between sections.
        i += 1

    if not patch.files:
        raise PatchError("no file diffs found")
    return patch


def _begin_file(diff_git_line: str) -> FileChange:
    # "diff --git a/old b/new"
    parts = diff_git_line.split()
    old = _strip_prefix(parts[2]) if len(parts) >= 4 else ""
    new = _strip_prefix(parts[3]) if len(parts) >= 4 else old
    return FileChange(old_path=old, new_path=new)
