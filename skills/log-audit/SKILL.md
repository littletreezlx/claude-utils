---
name: log-audit
description: >
  Audit runtime log coverage across a project. Finds code paths where
  insufficient logging would prevent debugging from reconstructing what
  happened — streaming pipelines, state transitions, decision branches,
  and critical lifecycle paths. Produces a severity-ranked action list
  and can optionally apply fixes. Trigger when user says "log audit",
  "审日志", "查日志覆盖", "看下日志写得怎样", "日志补全", "log hygiene",
  or after a debugging incident exposed thin logging.
version: 2.0.0
---

# Log Audit — Runtime Log Coverage

## Role

Diagnose whether the project's runtime logs are sufficient to reconstruct
what happened when debugging. Produces a severity-ranked list of gaps and,
on request, applies fixes directly.

Single test for every finding: **could a future debugger, reading only the
logs, tell what the code did and why?** If no, it's a gap.

## In Scope

Four categories of code where log gaps break debuggability:

### A. Streaming / async / pipeline
Continuous data flow where "is it still alive?" matters.
Examples: WebSocket handlers, MQ consumers, media encoders, file watchers,
Stream/Flow/Observable pipelines, long-running workers.

### B. State machines / state transitions
Code whose correctness depends on transition order.
Examples: explicit `State` enums with `match`/`when`/`switch`, lifecycle
state fields (`Loading`/`Ready`/`Error`), game scene transitions, session
phases.

### C. Decision branches
Points where the code picks between non-trivial alternatives and the
choice matters for debugging.
Examples: AI behavior selection, algorithm dispatch, feature-flag gates,
retry/fallback logic, permission/auth branches.

### D. Critical lifecycle paths
Initialization, shutdown, or resource acquisition sequences where order
and success/failure of each step determines later behavior.
Examples: autoload/DI bootstrap, plugin registration, resource loaders,
connection setup, migration steps.

## Out of Scope

Skip these — they have their own conventions or add noise:

- One-shot request/response handlers (RPC single call, REST endpoints)
  whose response itself is the observability signal
- Pure UI render callbacks (frame draw, layout)
- Generated code (`*.pb.go`, `*.g.dart`, protobuf output)
- Test code
- Pure error logging (covered by error-handling conventions)
- Performance telemetry (covered by metrics pipelines)

## Detection Matrix

For each in-scope code block, check what's missing:

| Category | Required signals |
|----------|------------------|
| **A. Streaming** | (a1) lifecycle start/stop, (a2) first-data marker, (a3) periodic counter |
| **B. State machines** | (b1) transition log with `from → to` and trigger, (b2) entry/exit for long-lived states |
| **C. Decision branches** | (c1) chosen branch + key inputs that drove the choice |
| **D. Lifecycle paths** | (d1) per-step start, (d2) per-step outcome (ok/fail + reason) |

## Severity

Anchored on: **how badly is debugging blocked if this is missing?**

| Level | Condition |
|-------|-----------|
| 🔴 **Critical** | Debugger cannot tell whether the code ran at all, or cannot distinguish success from silent failure |
| 🟡 **Warning** | Debugger knows code ran but cannot reconstruct the path taken (which branch, which transition, when data arrived) |
| 🟢 **Minor** | Path is recoverable but requires cross-referencing multiple logs; one extra line would make it direct |
| ✅ **Healthy** | All required signals present for the category |

## Execution

### Step 1 — Scope

- Default: scan the entire CWD
- User-provided path (`/log-audit src/foo`) limits scope
- Skip: `node_modules`, `build`, `.gradle`, `vendor`, `target`, `dist`,
  and any generated-code directories

### Step 2 — Identify candidates

Use two complementary passes and merge results:

**Pass 1 — filename patterns** (Glob):
`*Stream*`, `*Capturer*`, `*Encoder*`, `*Decoder*`, `*Publisher*`,
`*Subscriber*`, `*Worker*`, `*Consumer*`, `*Producer*`, `*Handler*`,
`*Listener*`, `*Channel*`, `*Pipeline*`, `*State*`, `*Machine*`,
`*Loader*`, `*Bootstrap*`, `*Autoload*`

**Pass 2 — code patterns** (Grep):
- Streaming: `Flow<`, `Stream<`, `Observable<`, `Channel<`,
  `while\s*\((true|active|running)\)`, `setInterval`, `Timer.periodic`,
  `\.subscribe\(`, `\.collect\s*\{`, `addEventListener`
- State machines: `enum\s+\w*State`, `match\s+\w+\s*\{`,
  `when\s*\(state\)`, `switch\s*\(\w*[Ss]tate\)`
- Decision branches: functions whose body is dominated by `if/else if` or
  `switch` chains with ≥ 3 arms and non-trivial inputs
- Lifecycle: `_ready`, `init`, `setup`, `bootstrap`, `onStart`,
  `@PostConstruct`, top-level `main`-adjacent sequences

### Step 3 — Analyze each candidate

1. Read ± 30 lines around the candidate, not the full file
2. Identify its category (A/B/C/D). A single block can belong to multiple
3. Check the required signals from the matrix
4. Grade severity using the debugger-reconstruction test
5. Draft a concrete fix snippet in the file's language

### Step 4 — Output

Report structure (in-chat, no file writes unless oversized):

```markdown
## Log Audit — {date}

**Scope**: {path}
**Candidates**: {N} across A:{n} B:{n} C:{n} D:{n}
**Grades**: 🔴 {n} · 🟡 {n} · 🟢 {n} · ✅ {n}

---

### 🔴 Critical ({N})

- **{file}:{line}** `{symbol}` — {one-line purpose}
  - Category: {A|B|C|D}
  - Missing: {which signals}
  - Debug impact: {what you cannot tell from current logs}
  - Suggested fix:
    ```{lang}
    {concrete snippet}
    ```

### 🟡 Warning ({N})
{same shape}

### 🟢 Minor ({N})
{same shape}

### ✅ Healthy ({N})
- `{file}` `{symbol}` — all signals present
```

### Step 5 — Volume control

- Each grade: show top 10 inline
- Overflow → write full list to `_scratch/log-audit-{date}.md`
- Zero findings → output `Project passes log hygiene audit ✅` and stop
- Scan running > 60s → stop, suggest narrowing with a path argument

### Step 6 — Auto-apply (default behavior)

Skip the menu. After the report, immediately apply all findings:
- 🟡 and 🟢 — fix directly, no confirmation needed
- 🟢 too — these are quick wins, fix alongside 🟡

End with a one-line summary of what was changed.

**Rationale**: in this project's AI-Only workflow, the user always replies `1` or ignores the menu anyway. Eliminating the confirmation step closes the loop faster.

**Exception**: if the user explicitly says "diagnosis only" or invokes with `--diagnose`, skip all edits and output the report only.

## Constraints

1. **Fixes run through normal edit tools** — Read before Edit, run tests
   after a batch of edits, never touch unrelated code
2. **No scope creep** — do not audit error handling, performance metrics,
   or business audit logs; those have separate conventions
3. **Prefer false negatives** — when unsure whether a block is in scope,
   exclude it rather than pad the report
4. **In-chat output by default** — only write to `_scratch/` when volume
   forces it

## Relationship to other skills

- `feat-done` may call this when the delivery touches in-scope code
- `code-quality` may call this when the PR diff hits candidate patterns
- `comprehensive-health-check` includes this as a sub-node

## Triggers

| User says | Behavior |
|-----------|----------|
| `/log-audit` | Scan CWD, auto-apply all findings |
| `/log-audit <path>` | Scan that subtree, auto-apply |
| `/log-audit --fix` | Same as default — kept for backward compat |
| `/log-audit --diagnose` | Scan CWD, diagnosis only (no edits) |
| "审日志" / "查日志覆盖" | Scan CWD, auto-apply |
| "审日志并修复" | Same as default |

## Anti-ritual self-check

After the report, ask yourself:

> Would the fixes I just proposed actually help a future debugging
> session, or am I just demonstrating that I audited?

If three consecutive audits produce findings that are rejected or
ignored, the severity bar is too low or the fix suggestions are not
compelling. Report back to the user and recalibrate — do not keep
generating noise.

A clean audit (zero findings) is a correct outcome, not a failure.
