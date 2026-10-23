"""Apply a parsed patch to in-memory file contents."""

from __future__ import annotations

from patchkit.model import FileChange, Patch


class ApplyError(ValueError):
    """Raised when a hunk does not match the file it is applied to."""


def apply_patch(patch: Patch, files: dict[str, str]) -> dict[str, str]:
    """
    Apply ``patch`` to a mapping of ``path -> contents`` and return the new mapping. The input is not
    mutated. Raises :class:`ApplyError` if a hunk's context does not match the current file.
    """
    result = dict(files)
    for change in patch.files:
        if change.is_delete:
            result.pop(change.old_path, None)
            continue
        source = "" if change.is_new else result.get(change.old_path)
        if source is None:
            raise ApplyError(f"patch targets missing file {change.old_path!r}")
        new_content = _apply_to_file(change, source)
        if change.is_rename:
            result.pop(change.old_path, None)
        result[change.new_path] = new_content
    return result


def _apply_to_file(change: FileChange, source: str) -> str:
    original = source.splitlines()
    out: list[str] = []
    cursor = 0  # index into `original`, 0-based

    for hunk in change.hunks:
        start = hunk.old_start - 1 if hunk.old_start > 0 else 0
        if start < cursor:
            raise ApplyError(f"overlapping or out-of-order hunk in {change.path!r}")
        # Copy unchanged lines up to the hunk.
        out.extend(original[cursor:start])
        cursor = start

        for line in hunk.lines:
            marker, content = line[:1], line[1:]
            if marker == " ":
                _expect(change, original, cursor, content)
                out.append(content)
                cursor += 1
            elif marker == "-":
                _expect(change, original, cursor, content)
                cursor += 1  # drop the removed line
            elif marker == "+":
                out.append(content)

    out.extend(original[cursor:])
    text = "\n".join(out)
    # Preserve a trailing newline when the source had one.
    if source.endswith("\n") and not change.is_delete:
        text += "\n"
    return text


def _expect(change: FileChange, original: list[str], index: int, content: str) -> None:
    if index >= len(original) or original[index] != content:
        found = original[index] if index < len(original) else "<end of file>"
        raise ApplyError(
            f"context mismatch in {change.path!r} at line {index + 1}: expected {content!r}, found {found!r}"
        )
