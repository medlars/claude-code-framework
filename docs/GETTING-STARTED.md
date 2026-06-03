# Getting Started with the Claude Code Engineering Framework

A step-by-step guide for adopting the 40-pattern framework in your projects.

---

## Prerequisites

- **Claude Code** installed — via [claude.ai/code](https://claude.ai/code) or the VS Code extension
- **Python 3.8+** — required for `generate-report.py`
- **Git** — for cloning and pattern contributions
- **GitHub CLI (`gh`)** — optional, for pattern publishing and PR submission

Verify your environment:

```bash
claude --version          # Claude Code CLI
python3 --version         # Must be >= 3.8
git --version
gh --version              # Optional
```

---

## Installation (3 steps)

```bash
# Step 1: Clone the framework
git clone https://github.com/owner/claude-code-framework
cd claude-code-framework

# Step 2: Generate your first report to understand what's here
python3 generate-report.py --audience tech > my-framework-report.md

# Step 3: Copy the CLAUDE.md snippet into your project
cat CLAUDE-SNIPPET.md >> your-project/CLAUDE.md
```

After step 2, open `my-framework-report.md` to see all 40 patterns explained for a technical audience. Use `--audience lay` if you want plain-English explanations for stakeholders.

---

## What to adopt first (tiered recommendation)

Do not adopt all 40 patterns at once. Start with Tier 1, prove value, then layer in Tier 2 and Tier 3.

### Tier 1 — Start here (no infrastructure needed)

These four patterns require no scripts, daemons, or registries. You can adopt them in 30 minutes.

| Pattern | Why first |
|---------|-----------|
| **DP-013: Hook-as-judiciary** | Write your first enforcement hook. Memory is advisory; hooks are law. |
| **DP-016: Immaculate code protocol** | Set your Definition of Done so "done" means the same thing every time. |
| **DP-018: Spec-driven development** | Write `spec.md` before coding. 60 minutes of planning saves 23+ hours of debugging. |
| **DP-019: Test-alongside discipline** | Tests land in the same session as the code they cover. No backfilling. |

### Tier 2 — Add governance (1-2 days setup)

Once Tier 1 is habit, add lightweight project governance.

| Pattern | What you get |
|---------|--------------|
| **DP-001: CEO/PM/CIS hierarchy** | Per-project monitoring script that owns build/test/deploy/lint/security. |
| **DP-002: Constitution** | A rule registry that survives across sessions and contributors. |
| **DP-006: 9-dimension audit** | Cold-read audit methodology — find issues a fresh reviewer would catch. |

### Tier 3 — Full fleet management (ongoing)

For users running 5+ projects in parallel.

| Pattern | What you get |
|---------|--------------|
| **DP-005: WatchTools detector-gap** | Automated detectors that catch fleet-wide drift before it lands. |
| **DP-007: Central Issue Store** | Single store for all findings across all projects. |
| **DP-009: Subagent-driven execution** | Parallel agents for security, performance, tests, docs. |

---

## Integrating with Claude Code

The most important step: add a `CLAUDE.md` snippet to your project so Claude loads the framework patterns automatically every session.

Create or edit `your-project/CLAUDE.md`:

```markdown
# Claude Code Engineering

This project follows the Claude Code Engineering Framework patterns.
Reference: ~/claude-code-framework/

## Active patterns
- DP-013: Hook-as-judiciary (memory advisory, hooks enforce)
- DP-016: Immaculate code (ruff + tests + PM green = done)
- DP-018: Spec-driven (write spec.md before coding)
- DP-019: Test-alongside (tests in same session as code)

## Enforcement
Hooks are in ~/.claude/hooks/. Never bypass without written rationale.

## Definition of Done
A feature is not done until: tests pass, linter clean, PM grade held.
```

Claude Code reads this file at session start. The patterns become part of the working context — no manual reminders required.

---

## Creating your first hook (DP-013 in practice)

Hooks are shell scripts wired into `~/.claude/settings.json` that fire on specific events (Stop, UserPromptSubmit, PostToolUse, etc.). They enforce rules that memory alone cannot.

Example: block commits that don't explain WHY.

```bash
cat > ~/.claude/hooks/commit-message-gate.sh << 'EOF'
#!/bin/bash
# Stop hook: block if commit message is too short or missing rationale
INPUT=$(cat)
MSG=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('command',''))" 2>/dev/null)
if echo "$MSG" | grep -q "git commit"; then
    echo '{"decision":"block","reason":"Write a commit message that explains WHY this change was needed, not just what changed."}'
fi
EOF
chmod +x ~/.claude/hooks/commit-message-gate.sh
```

Wire it in `~/.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [{"type": "command", "command": "~/.claude/hooks/commit-message-gate.sh"}]
      }
    ]
  }
}
```

The next time you ask Claude to commit, the hook intercepts. If the message is weak, Claude is told to rewrite — without you having to notice.

---

## Registering your own patterns

When you invent a new technique that works, contribute it back.

```bash
# Get next ID
NEXT_ID=$(grep "^  - id:" ~/claude-code-framework/INDEX.md | tail -1 | grep -oE '[0-9]+' | awk '{printf "DP-%03d", $1+1}')

# Create from template
cp ~/claude-code-framework/TEMPLATE.md ~/claude-code-framework/patterns/${NEXT_ID}-my-pattern.md

# Edit it, then add to INDEX.md
# Submit as a PR to contribute back!
```

A good pattern submission includes:

- **What it is** — one paragraph
- **Why it exists** — the real-world problem it solves
- **How it works** — the mechanism
- **Evidence** — at least one project where it has been in production
- **Trade-offs** — what it costs (setup time, ongoing maintenance, false positives)

---

## Generating reports

`generate-report.py` produces audience-tuned views of the framework.

```bash
# Full technical guide (for developers)
python3 generate-report.py --audience tech > report-tech.md

# Plain English (for stakeholders)
python3 generate-report.py --audience lay > report-lay.md

# Just one pattern
python3 generate-report.py --pattern DP-013

# All YouTube episode seeds
python3 generate-report.py --youtube

# Everything at once
python3 generate-report.py --full > complete-framework.md
```

Use `--audience lay` when sharing with non-engineers. Use `--audience tech` when onboarding a new engineer. Use `--pattern DP-NNN` to pull a single pattern into a code review or design doc.

---

## FAQ

**Q: Do I need to use ALL 40 patterns?**
A: No. Start with Tier 1 (4 patterns). Add more as your project grows. Most solo developers stay in Tier 1+2 indefinitely.

**Q: Does this work with Claude Code on any project type?**
A: Yes — Python, Swift, JavaScript, shell scripts, or mixed stacks. The patterns are language-agnostic. Examples in the framework cover all four.

**Q: Can I contribute new patterns?**
A: Yes. Open a PR against [github.com/owner/claude-code-framework](https://github.com/owner/claude-code-framework). New patterns must follow `TEMPLATE.md` and include a rationale grounded in real project experience.

**Q: Is this opinionated?**
A: Very. These patterns emerged from 80+ real projects across 500+ Claude Code sessions. The opinions are evidence-based, not speculative.

**Q: Do I need the full governance stack (CEO/PM/CIS)?**
A: Only for managing 5+ projects simultaneously. Single-project users: stick to Tier 1.

**Q: How do hooks differ from CLAUDE.md rules?**
A: Memory (CLAUDE.md) is advisory — Claude reads it but may forget mid-session. Hooks are enforcement — they fire deterministically and can block actions. See DP-013.

**Q: What if a hook blocks something I actually want to do?**
A: Hooks should have a documented bypass mechanism (e.g., an environment variable or sentinel file). Never silently weaken or remove a hook — log the bypass and the reason.

**Q: Can I use this with other AI coding tools (Cursor, Copilot)?**
A: Some patterns (spec-driven, immaculate code, test-alongside) transfer cleanly. Hook-based enforcement is Claude Code-specific. CLAUDE.md is Claude Code-specific; for Cursor/Copilot, use `AGENTS.md`.

**Q: Where do I file bugs or ask questions?**
A: GitHub Issues on the framework repo. For pattern-specific questions, tag the issue with the DP-NNN id.

---

## Next steps

1. Clone the repo and generate `--audience tech` report. Read DP-013, DP-016, DP-018, DP-019.
2. Add the `CLAUDE-SNIPPET.md` to your most active project.
3. Write your first hook (commit-message-gate is a safe starter).
4. After two weeks, run `python3 generate-report.py --full` and pick one Tier 2 pattern to add.
5. When you invent something that works, submit it as a PR.

The framework grows with your experience. The 40 patterns are not the ceiling — they are the floor.
