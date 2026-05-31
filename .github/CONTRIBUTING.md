# Contributing

This is a living framework. New patterns are welcome.

## Adding a Pattern

1. Copy `TEMPLATE.md` → `patterns/DP-NNN-your-pattern-name.md`
2. Fill all sections including Rationale
3. Add to `INDEX.md` under `patterns:` (YAML front matter)
4. Add a one-line row to the catalog table in `README.md`
5. Add a YouTube episode seed to `categories/12-youtube-episodes/episode-seeds.md`
6. Open a PR

## Pattern Lifecycle

- **proposed** — Invented but not yet validated across multiple sessions
- **active** — Validated by use in 2+ sessions, ideally backed by a hook, Constitution rule, or CI check
- **deprecated** — Superseded; kept for historical record with `supersedes:` pointing to replacement

## Code Style

- Python 3.11+
- No external dependencies in `generate-report.py`
- Markdown: ATX headings, 4-space code fences

## Questions

Open an issue — all discussion is welcome.
