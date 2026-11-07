# Changelog

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- `Patch.net` — net line change (insertions minus deletions).
- `Patch.paths()` — the list of files a patch touches, which makes it easy to
  spot when two agent runs changed the same file.

## [0.1.0]

### Added
- Unified-diff parser with new-file, deletion and rename handling.
- `Patch` model with `summary()` and `stat()`.
- In-memory patch application with context checking.
- `patchkit` CLI to summarise a diff from a file or stdin.
