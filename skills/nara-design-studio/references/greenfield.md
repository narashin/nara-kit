# Greenfield builds — when the pack has no IA to inherit

A pack answers "which components and tokens exist". It does **not** answer "what does a screen in this
product look like" — that is the pack's `startingPoints`, and the contract makes it optional. A pack can
therefore be T2 or even T3 and still leave every structural decision open.

That gap is what makes a greenfield build drift. Nav shape, columns, and status values get re-invented per
build, so screen 2 silently contradicts screen 1 — not because the tokens differ, but because nothing
persists the structural decisions screen 1 made.

## 1. Detect it — do not ask

```
manifest.startingPoints non-empty  → brownfield. Adopt its real IA (SKILL.md §5); ignore the rest of this file.
manifest.startingPoints empty/absent → greenfield. Apply §2 and §3 below.
```

Say which one you detected in one line. Never put the question to the user — the manifest already answers it,
and "are you greenfield?" is a question about a word, not about their product.

## 2. Split IA by whether it is visible

Not every structural decision benefits from the same treatment. Sort each one by whether a person could tell
two options apart by looking at them side by side.

| IA decision | Visible? | How to settle it |
|---|---|---|
| Nav shape — sidebar vs. top tabs, one level vs. two | yes | a candidate axis (§2.1) |
| Page skeleton — where title, filters, pagination sit | yes | a candidate axis (§2.1) |
| Status enum + the color of each value | no | decide and state (§2.2) |
| Default sort, page size | no | decide and state (§2.2) |
| Row click — navigate vs. expand inline | no | decide and state (§2.2) |

### 2.1 Visible IA — reuse the candidate mechanism, add nothing

`SKILL.md` §3 already builds 2–5 **layout-direction** candidates the user compares and `Select`s. That *is* the
comparison mechanism for visible IA; it needs no counterpart. The only change in a greenfield build is what
the candidates differ on: make them diverge on nav shape and page skeleton **first**, before they diverge on
decoration. Three candidates that share one nav and differ in card padding waste the mechanism on the cheap
decision.

### 2.2 Non-visible IA — decide for the user, then let them overrule

Rendering three candidates that differ only in their default sort produces three identical-looking screens.
Comparison adds nothing, and asking costs the user a decision they usually have no opinion on yet.

So choose sensible values and state them compactly next to the candidates — one block, not an interview:

```
statuses : 대기 / 검토중 / 승인 / 반려   (반려 = negative, 승인 = positive, 나머지 = neutral)
row click: → detail
sort     : newest first
```

These are **not** Readiness Rubric blockers. An unanswered A/B/C item in `SKILL.md` §4 blocks the build because
no default is safe; an unanswered status palette has a defensible default, so it ships with one and the user
overrules it through the normal comment loop if they disagree.

## 3. Write the IA back — the step that stops this repeating

Everything above is per-build. Without persistence the next screen re-runs the same guesswork and lands
somewhere else, and the project never leaves greenfield.

When the user finalizes a handoff from a greenfield build, append that screen to the pack's `startingPoints`
(`{ path, name, note }`, see `pack-contract.md` §3.1) and record the §2.2 decisions in its `note`.

**Confirm before writing.** The pack may be shared — an internal distribution's pack, a teammate's, a
company-wide one. A pack the user does not own is theirs to change, not yours.

Once written, the next build's detection in §1 comes back *brownfield*, `SKILL.md` §5's "starting points = real
IA by default" rule applies normally, and the structural decisions stop being re-litigated. Convergence, not a
permanent greenfield mode.
