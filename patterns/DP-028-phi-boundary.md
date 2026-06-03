---
id: DP-028
name: PHI boundary enforcement (PHIPA/PIPEDA)
category: security
status: active
constitution-rules: [PHI-BND-001, PHI-LOG-001, PHI-EXT-API-001, PHI-SCAN-READ-001, PHI-TMP-001]
youtube-difficulty: advanced
youtube-episode-length: long
introduced: 2026-04
---

## What it is

A boundary contract for projects that touch Protected Health Information
(PHI): EpicVDI, SagaMail, Epione EMR Assistant, and any clinic-side
tools. PHI must never cross a trust boundary unencrypted, must never
appear in logs, must never be sent to external APIs (including LLM
providers), and must never land in `/tmp`. Enforced by PHIWatch.

## Rationale — Why We Adopted This Pattern

*The story of how this pattern came to exist and why it was chosen over alternatives.*

### The problem we kept hitting
The owner is a practicing physician. PHI (Protected Health Information)
leaks would end his career — PHIPA fines, CPSO action, loss of medical
license. Casual handling of even one identifier (DOB, MRN, name) in a
log file would be catastrophic.

### What we tried first (and why it didn't work)
- **"Just be careful"** — works for humans; AI doesn't know what PHI is.
- **A regex over 18 HIPAA identifiers** — over-matched (false positives
  on benign strings), under-matched on indirect identifiers.

### The insight that unlocked the solution
**Make PHI a *boundary* property, not a *content* property.** PHIWatch
rules: PHI never crosses a trust boundary unencrypted; PHI never goes to
an external LLM API; PHI access is always audit-logged; local Llama only
for PHI-touching LLM work.

### Why this approach, not the obvious one
*Why not just review every code change manually?* Because PHI handling
is too important to rely on review. Mechanical enforcement at the
boundary (cloud-API client refuses PHI-tagged data) is the only safe
floor.

### Evidence that it works
- 2026-05-09 EpicVDI audit found and fixed a "PHIPA rubber-stamp"
  pattern (audit logs that approved access without checking).
- Local Llama in place for all clinical analysis tasks; no PHI has
  reached the Anthropic API.

## Why we use it

Ontario PHIPA + Canadian PIPEDA: a single PHI leak triggers regulatory
reporting and patient harm. The owner is a physician; patient privacy is
non-negotiable. The boundary contract makes "did this leak PHI?" a
mechanical question, not a judgment call.

## How it works

**PHIWatch rule IDs:**
- `PHI-BND-001` — PHI must not cross trust boundary unencrypted
- `PHI-LOG-001` — PHI must not appear in log statements
- `PHI-EXT-API-001` — PHI must not be sent to external APIs (LLM, OCR)
- `PHI-SCAN-READ-001` — PHI scanners must be read-only
- `PHI-TMP-001` — PHI must not be written to /tmp

**Detection:**
- Static analysis: identifiers matching PHI patterns (name, DOB, MRN,
  OHIP number, address) appearing in `print()`, `log.*()`, external
  HTTP calls.
- Runtime: PHI-tainted variables tracked through call graph.

**De-identification pipeline** (EpicVDI):
- All PHI removed locally via 18-identifier check (HIPAA list adapted
  for PHIPA) before any operation crosses the boundary.
- Local LLM (Llama via Ollama) used; PHI never touches Anthropic API.

**Audit trail**: every PHI access logged to project-local audit DB,
never to syslog or cloud sinks.

**Threat model required** (annual review) for: EpicVDI, SagaMail,
CorpBooks, FinanceFlow, Verscout (financial-PHI adjacent). Use
`/threat-model` skill (STRIDE-lite).

## Example

Building EpicVDI's OCR pipeline:
```python
# Bad: sends image with PHI to cloud OCR
response = google_vision_api.recognize(image_bytes)  # PHI-EXT-API-001

# Good: local Tesseract, then de-identify
text = tesseract.image_to_string(image_bytes)
clean_text = deidentify(text, identifiers=ALL_18_PHIPA)
# Now safe to ship clean_text anywhere
```

```python
# Bad: PHI in log
logger.info(f"Processed patient {patient.name}, DOB {patient.dob}")  # PHI-LOG-001

# Good: opaque ID
logger.info(f"Processed patient {patient.audit_id}")
```

## Related patterns

- [DP-029] Secrets never in files (sibling: PHI never in logs)
- [DP-030] Add-then-remove migration
- [DP-038] Triple Review Protocol

## YouTube episode angle

- **Tech-savvy** (15-min): "Privacy by mechanical enforcement." Walk
  through PHIWatch's rule set, show a detection live, walk through
  de-identification pipeline. Compare to GDPR's role-based access vs.
  PHIPA's record-level audit.
- **Lay audience** (8-min): "Patient privacy without trusting humans."
  Use the analogy of a hospital where every chart access leaves a
  permanent log automatically — no nurse needs to remember.

## Known failure modes / lessons learned

- Cloud LLM APIs (Anthropic, OpenAI) are external; PHI in prompts
  violates PHI-EXT-API-001. Local models (Ollama) are the only safe
  LLM path for PHI.
- Screenshot cleanup: every screenshot taken on a PHI-touching app
  must be deleted within session, not left in `/tmp` or Desktop.
- LESSONS (EpicVDI session): PHIPA audit trail was rubber-stamped
  initially; cold-read found gaps fixed in 2026-05.
