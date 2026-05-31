#!/usr/bin/env python3.14
"""Generate a narrative report of the [Your Company] Claude Code engineering system.

Reads INDEX.md and every patterns/DP-NNN-*.md file in this registry, then
emits a structured Markdown report tailored to the requested audience.

Usage:
  python3.14 generate-report.py --audience tech       # For developers
  python3.14 generate-report.py --audience lay        # For non-technical
  python3.14 generate-report.py --category governance # Just one category
  python3.14 generate-report.py --pattern DP-001      # Single pattern deep-dive
  python3.14 generate-report.py --youtube             # YouTube episode seeds
  python3.14 generate-report.py --full                # Complete report

Exit codes:
  0  report written to stdout
  1  invalid arguments
  2  missing or malformed pattern files
"""
from __future__ import annotations

import argparse
import logging
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

__all__ = [
    "Pattern",
    "discover_patterns",
    "render_full",
    "render_tech",
    "render_lay",
    "render_category",
    "render_pattern",
    "render_youtube",
    "main",
]

logger = logging.getLogger("design-patterns.report")

ROOT = Path(__file__).resolve().parent
PATTERNS_DIR = ROOT / "patterns"
INDEX_FILE = ROOT / "INDEX.md"
EPISODE_SEEDS = ROOT / "categories" / "12-youtube-episodes" / "episode-seeds.md"

VALID_AUDIENCES = ("tech", "lay")
VALID_CATEGORIES = (
    "governance", "detection", "execution", "enforcement", "quality",
    "data-management", "project-structure", "security", "workflow",
    "anti-pattern", "meta", "skills-agents-hooks",
)

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
SECTION_RE = re.compile(r"^## (.+?)$", re.MULTILINE)


@dataclass
class Pattern:
    """One DP-NNN pattern parsed from disk."""
    id: str
    name: str
    category: str
    status: str
    introduced: str
    youtube_difficulty: str
    youtube_length: str
    constitution_rules: list[str] = field(default_factory=list)
    path: Path = field(default_factory=Path)
    sections: dict[str, str] = field(default_factory=dict)

    @property
    def rationale(self) -> str:
        return self.sections.get("Rationale — Why We Adopted This Pattern", "").strip()

    @property
    def what_it_is(self) -> str:
        return self.sections.get("What it is", "").strip()

    @property
    def why(self) -> str:
        return self.sections.get("Why we use it", "").strip()

    @property
    def how(self) -> str:
        return self.sections.get("How it works", "").strip()

    @property
    def example(self) -> str:
        return self.sections.get("Example", "").strip()

    @property
    def youtube_angle(self) -> str:
        return self.sections.get("YouTube episode angle", "").strip()

    @property
    def lessons(self) -> str:
        return self.sections.get("Known failure modes / lessons learned", "").strip()


def _parse_frontmatter(text: str) -> dict[str, str | list[str]]:
    """Parse the YAML-like frontmatter block at the head of a pattern file."""
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError("missing frontmatter")
    block = match.group(1)
    out: dict[str, str | list[str]] = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            out[key] = [x.strip() for x in inner.split(",") if x.strip()] if inner else []
        else:
            out[key] = value
    return out


def _parse_sections(text: str) -> dict[str, str]:
    """Split a pattern body into {heading: body} pairs."""
    body = FRONTMATTER_RE.sub("", text, count=1)
    sections: dict[str, str] = {}
    matches = list(SECTION_RE.finditer(body))
    for i, m in enumerate(matches):
        heading = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        sections[heading] = body[start:end].strip("\n")
    return sections


def _load_one(path: Path) -> Pattern:
    text = path.read_text()
    fm = _parse_frontmatter(text)
    sections = _parse_sections(text)
    return Pattern(
        id=str(fm.get("id", "")),
        name=str(fm.get("name", "")),
        category=str(fm.get("category", "")),
        status=str(fm.get("status", "")),
        introduced=str(fm.get("introduced", "")),
        youtube_difficulty=str(fm.get("youtube-difficulty", "")),
        youtube_length=str(fm.get("youtube-episode-length", "")),
        constitution_rules=list(fm.get("constitution-rules", []) or []),
        path=path,
        sections=sections,
    )


def discover_patterns() -> list[Pattern]:
    """Load every DP-NNN-*.md file as a Pattern object, sorted by ID."""
    files = sorted(PATTERNS_DIR.glob("DP-*.md"))
    if not files:
        raise FileNotFoundError(f"no pattern files under {PATTERNS_DIR}")
    out: list[Pattern] = []
    for f in files:
        try:
            out.append(_load_one(f))
        except ValueError as exc:
            logger.error("skipped %s: %s", f.name, exc)
    out.sort(key=lambda p: p.id)
    return out


def _h(level: int, text: str) -> str:
    return "#" * level + " " + text + "\n\n"


def _group_by_category(patterns: list[Pattern]) -> dict[str, list[Pattern]]:
    out: dict[str, list[Pattern]] = {}
    for p in patterns:
        out.setdefault(p.category, []).append(p)
    return out


def render_pattern(p: Pattern, *, audience: str = "tech") -> str:
    """Render a single pattern as a Markdown block."""
    out: list[str] = []
    out.append(_h(2, f"{p.id}: {p.name}"))
    out.append(
        f"*Category: `{p.category}` · Status: `{p.status}` · Introduced: {p.introduced} · "
        f"YouTube: {p.youtube_difficulty} / {p.youtube_length}*\n\n"
    )
    if p.what_it_is:
        out.append(_h(3, "What it is"))
        out.append(p.what_it_is + "\n\n")
    if audience == "tech":
        if p.rationale:
            out.append(_h(3, "Rationale"))
            out.append(p.rationale + "\n\n")
        if p.how:
            out.append(_h(3, "How it works"))
            out.append(p.how + "\n\n")
        if p.example:
            out.append(_h(3, "Example"))
            out.append(p.example + "\n\n")
        if p.lessons:
            out.append(_h(3, "Known failure modes / lessons learned"))
            out.append(p.lessons + "\n\n")
    else:  # lay
        if p.why:
            out.append(_h(3, "Why this matters (in plain words)"))
            out.append(p.why + "\n\n")
        if p.youtube_angle:
            out.append(_h(3, "Story arc"))
            out.append(p.youtube_angle + "\n\n")
    return "".join(out)


def render_tech(patterns: list[Pattern]) -> str:
    """Full technical report for developers, grouped by category."""
    out: list[str] = []
    out.append(_h(1, "[Your Company] Engineering System — Technical Report"))
    out.append(
        f"*Generated from {len(patterns)} design patterns under "
        f"`{PATTERNS_DIR.relative_to(Path.home())}`.*\n\n"
    )
    groups = _group_by_category(patterns)
    for cat in sorted(groups):
        out.append(_h(2, f"Category: {cat}"))
        for p in groups[cat]:
            out.append(render_pattern(p, audience="tech"))
    return "".join(out)


def render_lay(patterns: list[Pattern]) -> str:
    """Plain-English report for non-technical readers."""
    out: list[str] = []
    out.append(_h(1, "[Your Company] Engineering System — Plain English"))
    out.append(
        "This report explains how one physician runs a software fleet with an "
        "AI coding assistant. Each section is a discipline or mechanism that "
        "took months to refine.\n\n"
    )
    for p in patterns:
        out.append(_h(2, f"{p.id}: {p.name}"))
        if p.why:
            out.append(p.why + "\n\n")
        if p.youtube_angle:
            out.append("**Storytelling angle**\n\n" + p.youtube_angle + "\n\n")
    return "".join(out)


def render_category(patterns: list[Pattern], category: str) -> str:
    """All patterns in a single category, technical view."""
    filtered = [p for p in patterns if p.category == category]
    if not filtered:
        raise ValueError(
            f"no patterns in category '{category}'. Valid: {', '.join(VALID_CATEGORIES)}"
        )
    out: list[str] = [_h(1, f"Category Report: {category}")]
    for p in filtered:
        out.append(render_pattern(p, audience="tech"))
    return "".join(out)


def render_youtube(patterns: list[Pattern]) -> str:
    """Production-ready YouTube episode list, derived from the seeds file."""
    out: list[str] = [_h(1, "YouTube Episode Seeds (production-ready)")]
    if EPISODE_SEEDS.exists():
        out.append(EPISODE_SEEDS.read_text())
        out.append("\n\n")
    out.append(_h(2, "Pattern → episode-angle cross reference"))
    out.append("| Pattern | Tech-savvy outline | Lay outline |\n")
    out.append("|---------|--------------------|-------------|\n")
    for p in patterns:
        tech_line = ""
        lay_line = ""
        for line in p.youtube_angle.splitlines():
            stripped = line.lstrip("- ").strip()
            if stripped.startswith("**Tech-savvy**"):
                tech_line = stripped.split(":", 1)[-1].strip()
            elif stripped.startswith("**Lay audience**"):
                lay_line = stripped.split(":", 1)[-1].strip()
        out.append(
            f"| `{p.id}` {p.name} | "
            f"{tech_line[:120].replace('|', '\\|')} | "
            f"{lay_line[:120].replace('|', '\\|')} |\n"
        )
    return "".join(out)


def render_full(patterns: list[Pattern]) -> str:
    """Everything in one document: tech report + lay report + youtube seeds."""
    parts: list[str] = []
    parts.append(_h(1, "[Your Company] Claude Code Engineering System — Full Report"))
    parts.append(
        f"*Sourced from {len(patterns)} design patterns + episode seeds. "
        "Suitable for sharing.*\n\n"
    )
    parts.append("---\n\n")
    parts.append(render_tech(patterns))
    parts.append("---\n\n")
    parts.append(render_lay(patterns))
    parts.append("---\n\n")
    parts.append(render_youtube(patterns))
    return "".join(parts)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--audience", choices=VALID_AUDIENCES, help="tech or lay")
    group.add_argument("--category", choices=VALID_CATEGORIES, help="single category")
    group.add_argument("--pattern", help="single DP-NNN ID")
    group.add_argument("--youtube", action="store_true", help="episode seed list")
    group.add_argument("--full", action="store_true", help="everything in one doc")
    p.add_argument("--verbose", "-v", action="store_true", help="debug logging")
    return p


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )
    try:
        patterns = discover_patterns()
    except FileNotFoundError as exc:
        logger.error("%s", exc)
        return 2

    if args.full:
        sys.stdout.write(render_full(patterns))
    elif args.youtube:
        sys.stdout.write(render_youtube(patterns))
    elif args.pattern:
        match = next((p for p in patterns if p.id == args.pattern), None)
        if match is None:
            logger.error("pattern %s not found", args.pattern)
            return 2
        sys.stdout.write(render_pattern(match, audience="tech"))
    elif args.category:
        try:
            sys.stdout.write(render_category(patterns, args.category))
        except ValueError as exc:
            logger.error("%s", exc)
            return 1
    elif args.audience == "tech":
        sys.stdout.write(render_tech(patterns))
    elif args.audience == "lay":
        sys.stdout.write(render_lay(patterns))
    else:
        parser.print_help(sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
