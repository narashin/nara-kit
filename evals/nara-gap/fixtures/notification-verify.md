# docs/requirements.md (excerpt)

- [ ] FR-1: A ticket transition MUST send a Slack notification to the assignee.
- [ ] FR-2: A ticket transition should also send an email notification.
- [ ] FR-3: The Slack message body must read `Ticket {id} moved to {state}`.

# docs/gap.md (existing — produced by a previous run)

```markdown
# Gap Analysis

- Based on: docs/requirements.md
- Analyzed: 2026-07-01
- Score: 33/100
- **Gate: ❌ blocked by P0 (2건)**

## Summary
- Total: 3 | Implemented: 1 | Partial: 0 | Missing: 2 | Agreed Exception: 0
- **P0 Missing (Critical): 2**
- Needs Confirm: 0 (forced sampling)

## Critical (P0) Missing — 보완 1순위
| ID | Requirement | Why P0 | Verbatim grep result |
|---|---|---|---|
| FR-2 | email notification | AC 본문 항목 | - |
| FR-3 | Slack body copy | verbatim UI 카피 | 0 |

## Detail

### Implemented
| ID | Priority | Requirement | Quote | Evidence (파일:라인) | Verbatim? |
|---|---|---|---|---|---|
| FR-1 | P0 | Slack notification | "Slack notification" | src/notify/slack.ts:22 | N |

### Missing
| ID | Priority | Requirement | Why P0 | Notes | Verbatim grep result |
|---|---|---|---|---|---|
| FR-2 | P0 | email notification | AC 본문 항목 | no mailer module | - |
| FR-3 | P0 | Slack body copy | verbatim UI 카피 | copy differs | 0 |
```

# Workspace state after the follow-up commit (raw command output)

```
$ git ls-files src/notify
src/notify/slack.ts
src/notify/api.ts
src/notify/email.ts
```

```
$ wc -l src/notify/slack.ts src/notify/email.ts
      66 src/notify/slack.ts
      41 src/notify/email.ts
     107 total
```

```
$ git grep -Fn "Ticket {id} moved to {state}" .
```

```
$ git grep -Fn "moved to" src/notify/slack.ts
src/notify/slack.ts:22:  const text = `Ticket ${id} moved to ${state}`
```

```
$ git grep -Fn "sendEmail" src/notify/email.ts
src/notify/email.ts:12:export async function sendEmail(to: string, body: string) {
```

No `docs/implementation-notes.md` in this workspace.
