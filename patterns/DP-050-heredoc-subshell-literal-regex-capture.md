---
id: DP-050
name: Heredoc in subshell captured as literal string in regex extr
category: anti-pattern
status: proposed
constitution-rules: []
youtube-difficulty: intermediate
youtube-episode-length: short
introduced: 2026-06
---

## What it is

When a shell script uses regex to extract the argument following a `-m` flag from a raw command string, and the caller passes a commit message via the `$(cat <<'EOF'...EOF)` heredoc-in-subshell idiom, the regex sees the subshell expression as an opaque literal. The pattern captures `$(cat <<'EOF'` as the message text rather than expanding it, corrupting every downstream operation that depends on the extracted message content.

## Rationale

### The problem

Commit quality gate scripts commonly parse the invoking `git commit` command by scanning `$*` or a reconstructed argument string for a `-m` flag and capturing what follows. A typical extraction pattern looks like:

```
message=$(echo "$*" | sed -n "s/.*-m[[:space:]]\+'\([^']*\)'.*/\1/p")
```

This works for simple quoted strings. It breaks silently when the caller writes:

```
git commit -m "$(cat <<'EOF'
feat: add retry logic

Implements exponential backoff on transient failures.
EOF
)"
```

By the time the quality gate sees `$*`, the shell has not evaluated the subshell; it is still a literal token sequence. The regex matches `-m` followed by `$(cat <<'EOF'` and stops at the first structural character it was not designed to handle. The captured subject line becomes `$(cat <<'EOF'` and the body detection predicate `has_body` sees a single-line message, causing it to report false negatives on messages that are structurally valid.

### The insight

Regex extraction against a reconstructed argument string cannot safely handle shell metacharacters embedded in argument values. The correct fix is two-stage: first detect that the captured value begins with the heredoc-in-subshell prefix `$(cat <<`, then re-extract the actual message body from between the heredoc delimiters in the original captured token. This is a post-extraction sanitisation step rather than a change to the primary extraction regex, making it backwards compatible with callers who pass plain `-m "message"` forms.

### Evidence

The failure surfaced in `commit-message-quality-gate.sh` when a developer switched to the heredoc style to author a multi-paragraph commit body. The gate accepted the commit without triggering the body-length check because `has_body` received the one-line string `$(cat <<'EOF'` and evaluated it as a bodyless message. The bug was silent: no error was raised, the gate passed, and the structural violation reached the repository undetected.

## Why we use it

Documenting this as an anti-pattern establishes a registry entry that:

- warns future authors of argument-parsing scripts to treat any `-m` capture as potentially containing shell metacharacter prefixes rather than plain text;
- mandates the post-extraction sanitisation step so the pattern is applied consistently across all quality gate scripts in the monorepo;
- prevents the silent false-negative class of failures where a gate reports success on structurally invalid input rather than raising an error.

## How it works

1. **Primary extraction** — apply the existing `-m` regex to the argument string and capture the raw value into `raw_message`.
2. **Prefix detection** — test whether `raw_message` matches `^\$\(cat <<` using a simple prefix check or anchored regex.
3. **Heredoc body re-extraction** — if the prefix is detected, locate the delimiter token (the word following `<<` or `<<'`), then extract the text between that delimiter's opening and closing occurrences in `raw_message` or in the full original argument block.
4. **Replacement** — overwrite `raw_message` with the extracted heredoc body before passing the value to any downstream check such as `has_body`, `check_subject_length`, or `check_imperative_mood`.
5. **Fallback** — if re-extraction fails (delimiter not found or empty body), emit a diagnostic error and exit non-zero rather than silently continuing with the corrupted value.

The detection step is intentionally separate from the primary extraction regex so that the common-case path is unchanged and the complexity of heredoc parsing is isolated to a single guarded branch.

## Example

**Broken behaviour (before fix)**

```
# $* contains: commit -m "$(cat <<'EOF'\nfeat: add retry\n\nBody text.\nEOF\n)"
raw_message=$(extract_m_flag "$*")
# raw_message == "$(cat <<'EOF'"
has_body "$raw_message"   # returns false — incorrect
```

**Fixed behaviour (after applying pattern)**

```
raw_message=$(extract_m_flag "$*")

if [[ "$raw_message" =~ ^\$\(cat\ \<\< ]]; then
  raw_message=$(extract_heredoc_body "$raw_message")
  [[ -z "$raw_message" ]] && { echo "ERROR: heredoc re-extraction failed" >&2; exit 1; }
fi

has_body "$raw_message"   # returns true — correct
```

The `extract_heredoc_body` function identifies the delimiter token, strips the `$(cat <<'DELIM'` prefix and the closing `DELIM)` suffix, and returns the interior text with leading and trailing blank lines removed.

## Related patterns

- **DP-031 Argument string reconstruction hazard** — general class of failures arising from treating `$*` or `"$@"` as a parseable command string rather than an array of discrete values.
- **DP-044 Silent gate pass on malformed input** — pattern family covering quality gates that return success rather than error when input cannot be parsed.
- **DP-017 Post-capture sanitisation layer** — the complementary prescriptive pattern recommending a normalisation stage between raw extraction and semantic validation.

## Known failure modes

**Nested subshells in the heredoc delimiter line.** If the caller uses a computed delimiter such as `$(cat <<$(echo EOF)`, the prefix detection regex matches but the delimiter extraction logic cannot identify the closing token reliably. Mitigation: restrict accepted delimiter forms to bare words and single-quoted words; reject others with a diagnostic error.

**Heredoc body itself contains the delimiter string.** Standard heredoc rules require the delimiter to appear alone on a line; if the body text happens to contain the delimiter mid-line the extraction is safe, but if a line consists solely of the delimiter string the extraction terminates early. Mitigation: document that quality gate scripts must not be used with heredocs whose body contains a line equal to the delimiter, and add a post-extraction sanity check that the captured body is non-empty.

**Windows-style line endings in the captured value.** If the argument string was assembled on a Windows host and passed through a non-normalising channel, `\r\n` line endings may prevent the closing delimiter from matching. Mitigation: normalise line endings in the raw capture before running heredoc re-extraction.

**Multiple `-m` flags on the same command.** Git concatenates multiple `-m` arguments; the primary extraction regex may capture only the first. If the first value happens to be a heredoc-in-subshell and the second is plain text, the re-extraction discards the second segment. Mitigation: the multi-`-m` case should be detected and either rejected or concatenated before the prefix detection step runs.