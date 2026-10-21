"""patchkit: parse, summarise and apply unified diffs.

AI coding agents hand back their work as unified diffs. patchkit reads a diff into a structured
model, summarises what it touches (files, hunks, lines added/removed), and applies it to in-memory
file contents so the result can be checked — all with no dependencies.
"""

from patchkit.apply import ApplyError, apply_patch
from patchkit.model import FileChange, Hunk, Patch
from patchkit.parser import PatchError, parse_patch

__version__ = "0.1.0"
__all__ = [
    "parse_patch",
    "PatchError",
    "apply_patch",
    "ApplyError",
    "Patch",
    "FileChange",
    "Hunk",
]
