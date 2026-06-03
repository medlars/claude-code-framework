#!/bin/bash
# Quick health check for the design-patterns registry
# Run from CEO or manually: bash health-check.sh
set -uo pipefail

REGISTRY="$HOME/Projects/shared/design-patterns"
INDEX="$REGISTRY/INDEX.md"
PATTERNS_DIR="$REGISTRY/patterns"

# Count entries in INDEX.md (lines matching "  - id: DP-")
EXPECTED=$(grep -c "^  - id: DP-" "$INDEX" 2>/dev/null || echo 0)

# Count actual pattern files on disk
ACTUAL=$(ls "$PATTERNS_DIR"/DP-*.md 2>/dev/null | wc -l | tr -d ' ')

if [ "$EXPECTED" != "$ACTUAL" ]; then
  echo "WARN: INDEX.md has $EXPECTED entries but $ACTUAL pattern files exist"
  # Show which IDs are missing from INDEX
  for f in "$PATTERNS_DIR"/DP-*.md; do
    id=$(basename "$f" | sed 's/\(DP-[0-9]*\)-.*/\1/')
    if ! grep -q "^  - id: $id$" "$INDEX" 2>/dev/null; then
      echo "  Missing from INDEX: $id ($f)"
    fi
  done
  exit 1
fi

# Check README catalog count
README_COUNT=$(grep -c "^| DP-" "$REGISTRY/README.md" 2>/dev/null || echo 0)
if [ "$README_COUNT" != "$ACTUAL" ]; then
  echo "WARN: README.md catalog has $README_COUNT rows but $ACTUAL pattern files exist"
  exit 1
fi

echo "OK: $ACTUAL patterns, INDEX and README in sync"
