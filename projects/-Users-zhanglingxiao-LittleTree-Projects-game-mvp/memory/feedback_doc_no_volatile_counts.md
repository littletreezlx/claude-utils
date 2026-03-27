---
name: feedback_doc_no_volatile_counts
description: Documentation should not include volatile counts (signal count, file count, test count) — they rot immediately and create false "inconsistencies"
type: feedback
---

Don't put exact counts of volatile things in documentation (e.g., "21 signals", "4 Resource scripts", "98 tests").

**Why:** These numbers change every time code is modified, creating a constant stream of false "inconsistencies" during doc reviews. The maintenance cost far exceeds the information value. Users consider count discrepancies unimportant — they are noise, not signal.

**How to apply:**
- When writing docs: describe *what* and *how*, not *how many*. E.g., "signals grouped by domain" instead of "21 signals, 7 domains"
- When reviewing docs: skip count discrepancies entirely — they are pseudo-problems
- When generating doc templates: avoid slots that invite volatile counts
- Exception: counts that are design constraints (e.g., "4×5 grid", "5-level cap") are fine — they don't change with implementation
