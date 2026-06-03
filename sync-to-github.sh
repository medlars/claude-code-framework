#!/bin/bash
# Sync dedacted version of design-patterns registry to GitHub
# Run whenever new patterns are added: ./sync-to-github.sh
set -euo pipefail

REGISTRY="$HOME/Projects/shared/design-patterns"
CACHE_DIR="$HOME/.claude-code-framework-cache"
GITHUB_REPO="owner/claude-code-framework"
DATE=$(date +%Y-%m-%d)

# ── 1. Count patterns ────────────────────────────────────────────────────────
PATTERN_COUNT=$(ls "$REGISTRY/patterns/DP-"*.md 2>/dev/null | wc -l | tr -d ' ')
echo "==> Syncing $PATTERN_COUNT patterns to $GITHUB_REPO"

# ── 2. Clone or pull the GitHub repo ────────────────────────────────────────
if [ -d "$CACHE_DIR/.git" ]; then
  echo "==> Pulling existing cache at $CACHE_DIR"
  git -C "$CACHE_DIR" pull --ff-only origin main 2>&1 | tail -3
else
  echo "==> Cloning $GITHUB_REPO → $CACHE_DIR"
  git clone "https://github.com/$GITHUB_REPO.git" "$CACHE_DIR"
fi

# ── 3. Rsync files into clone (preserve .git/) ───────────────────────────────
echo "==> Rsyncing registry files..."
rsync -av --delete \
  --exclude='.git' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  "$REGISTRY/" "$CACHE_DIR/"

# ── 4. Apply dedaction substitutions ─────────────────────────────────────────
# Order matters: longest/most-specific patterns first.
echo "==> Applying dedaction..."

dedact_file() {
  local f="$1"
  # Personal identifiers
  sed -i '' \
    -e 's|medlars@gmail\.com|owner@example\.com|g' \
    -e 's|owner/|owner/|g' \
    -e 's|\bmedlars\b|owner|g' \
    -e 's|\beiman\b|owner|g' \
    -e 's|\bEiman\b|Owner|g' \
    -e 's|\bRahimi\b|Owner|g' \
    -e 's|Vohux Inc|Vohux Inc|g' \
    -e 's|rahimivip\.com|example\.com|g' \
    -e 's|rahimi\.vip|example\.com|g' \
    -e 's|epionepain\.com|clinic-example\.com|g' \
    -e 's|nynorth\.ca|clinic-north-example\.ca|g' \
    -e 's|\bP6R899T379\b|APPLE_TEAM_ID|g' \
    "$f"

  # Project-specific references → generic examples
  sed -i '' \
    -e 's|\bSickKids\b|<hospital>|g' \
    -e 's|saga-mail-imap-owner-gmail|saga-mail-imap-owner-gmail|g' \
    "$f"
}

# Dedact patterns, INDEX, README, generate-report.py, TEMPLATE
find "$CACHE_DIR" \
  \( -name "*.md" -o -name "*.py" -o -name "*.sh" -o -name "*.json" -o -name "*.toml" \) \
  -not -path "$CACHE_DIR/.git/*" \
  | while read -r f; do
    dedact_file "$f"
  done

# ── 5. Show diff stat ────────────────────────────────────────────────────────
echo "==> Changes:"
git -C "$CACHE_DIR" diff --stat HEAD 2>/dev/null || true
NEW_FILES=$(git -C "$CACHE_DIR" ls-files --others --exclude-standard | wc -l | tr -d ' ')
[ "$NEW_FILES" -gt 0 ] && echo "    $NEW_FILES new untracked file(s)"

# ── 6. Commit and push ───────────────────────────────────────────────────────
cd "$CACHE_DIR"
git add -A

if git diff --cached --quiet; then
  echo "==> Nothing changed — repo already up to date."
  exit 0
fi

COMMIT_MSG="Update: $DATE — $PATTERN_COUNT patterns, auto-sync"
git commit -m "$COMMIT_MSG"
git push origin main

echo "==> Pushed: $COMMIT_MSG"
