"""The parsed-diff model and its summary statistics."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Hunk:
    """One @@ … @@ section of a file's diff."""

    old_start: int
    old_count: int
    new_start: int
    new_count: int
    # Each line keeps its leading marker: ' ' context, '+' added, '-' removed.
    lines: list[str] = field(default_factory=list)

    @property
    def added(self) -> int:
        return sum(1 for ln in self.lines if ln.startswith("+"))

    @property
    def removed(self) -> int:
        return sum(1 for ln in self.lines if ln.startswith("-"))


@dataclass
class FileChange:
    """All the hunks for a single file, plus its change type."""

    old_path: str
    new_path: str
    hunks: list[Hunk] = field(default_factory=list)
    is_new: bool = False
    is_delete: bool = False

    @property
    def path(self) -> str:
        """The path to show for this change (the new path, or the old one for a deletion)."""
        return self.old_path if self.is_delete else self.new_path

    @property
    def is_rename(self) -> bool:
        return not self.is_new and not self.is_delete and self.old_path != self.new_path

    @property
    def added(self) -> int:
        return sum(h.added for h in self.hunks)

    @property
    def removed(self) -> int:
        return sum(h.removed for h in self.hunks)


@dataclass
class Patch:
    files: list[FileChange] = field(default_factory=list)

    @property
    def added(self) -> int:
        return sum(f.added for f in self.files)

    @property
    def removed(self) -> int:
        return sum(f.removed for f in self.files)

    @property
    def net(self) -> int:
        """Net line change across the patch (insertions minus deletions)."""
        return self.added - self.removed

    def paths(self) -> list[str]:
        """The paths this patch touches, in order — handy for spotting overlap between runs."""
        return [f.path for f in self.files]

    def summary(self) -> str:
        """A git-style one-liner, e.g. ``3 files changed, 42 insertions(+), 9 deletions(-)``."""
        n = len(self.files)
        files = f"{n} file{'' if n == 1 else 's'} changed"
        ins = f"{self.added} insertion{'' if self.added == 1 else 's'}(+)"
        dels = f"{self.removed} deletion{'' if self.removed == 1 else 's'}(-)"
        return f"{files}, {ins}, {dels}"

    def stat(self) -> list[tuple[str, int, int]]:
        """Per-file (path, added, removed), like ``git diff --numstat``."""
        return [(f.path, f.added, f.removed) for f in self.files]
