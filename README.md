# patchkit

[![CI](https://github.com/BoogeyCodes/patchkit/actions/workflows/ci.yml/badge.svg)](https://github.com/BoogeyCodes/patchkit/actions/workflows/ci.yml)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB)
![No dependencies](https://img.shields.io/badge/dependencies-none-success)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

Parse, summarise and **apply unified diffs** — no dependencies. patchkit reads a diff into a
structured model, tells you what it touches (files, hunks, lines added/removed), and applies it to
file contents so you can check the result.

```python
from patchkit import parse_patch, apply_patch

patch = parse_patch(diff_text)
patch.summary()                      # "2 files changed, 42 insertions(+), 9 deletions(-)"
patch.stat()                         # [("src/app.py", 40, 9), ("README.md", 2, 0)]

result = apply_patch(patch, { "src/app.py": current_contents })  # -> new contents
```

```bash
patchkit change.diff --stat          # per-file breakdown + summary
git diff | patchkit                  # read a diff from stdin
```

## Why

AI coding agents hand their work back as a unified diff. To evaluate a run you need to know what the
diff actually does — which files it changes, how big the change is, whether it even applies cleanly to
the given code. patchkit is that small, dependency-free toolkit: a parser, a summariser and an
in-memory apply, so a patch can be inspected and verified without shelling out to `git apply`.

## What it does

- **Parse** a unified diff (git-style, with `diff --git`, `---`/`+++`, `@@` hunks, and `/dev/null`
  for new/deleted files) into a `Patch` of `FileChange`s and `Hunk`s.
- **Summarise**: `patch.summary()` gives the git-style one-liner; `patch.stat()` gives per-file
  `(path, added, removed)`; `patch.added` / `patch.removed` give totals.
- **Classify** each file: new, deleted, renamed, or modified.
- **Apply** the patch to a `dict` of `path -> contents`, returning the new mapping without mutating
  the input. A hunk whose context does not match raises `ApplyError` with the exact mismatch, so you
  learn immediately that a patch does not fit the code it claims to.

## API

```python
from patchkit import parse_patch, apply_patch, Patch, FileChange, Hunk
from patchkit.parser import PatchError
from patchkit.apply import ApplyError

patch: Patch = parse_patch(text)              # raises PatchError on malformed input
new_files: dict[str, str] = apply_patch(patch, files)  # raises ApplyError on a context mismatch
```

- `FileChange`: `old_path`, `new_path`, `path`, `hunks`, `is_new`, `is_delete`, `is_rename`, `added`,
  `removed`.
- `Hunk`: `old_start`, `old_count`, `new_start`, `new_count`, `lines`, `added`, `removed`.

## Testing

```bash
pip install -e ".[dev]"
pytest
```

Nineteen tests covering parsing (modifications, new files, deletions, multi-file summaries, hunk
counts, singular/plural wording, non-diff rejection), applying (modify, create, delete, add-only
hunks, context mismatch, missing target, input immutability) and the CLI. CI runs on Python 3.10–3.13.

## Project layout

```
src/patchkit
├── model.py    Patch / FileChange / Hunk and the summary stats
├── parser.py   unified-diff text -> Patch
├── apply.py    apply a Patch to in-memory file contents
└── cli.py      summarise a diff from a file or stdin
tests/          pytest suite
```

## Where it fits

In an agent-evaluation workflow, patchkit turns an agent's diff into something you can measure (how
big, which files) and verify (does it apply to the repo state), feeding a rubric score or a test run.

## License

MIT
