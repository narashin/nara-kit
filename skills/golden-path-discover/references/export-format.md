# Golden-Path Export Format

The Playwright-ready export schema, coverage math, determinism contract, and SKIP/WARNING taxonomy. Default language is English (`lang=en`); the Korean variant (`lang=ko`) is given alongside each label.

## Document structure (fixed order)

1. `---`-fenced frontmatter (see below)
2. H1 title: `# {Feature} — Playwright-ready E2E Export ({env})`
3. `## Common Preconditions` / `## 공통 사전조건`
4. `## Scenario Index` / `## 시나리오 목록` — flat bullet list `- [E2E-{PREFIX}-NNN] {title}`, ascending ID
5. `## Dependency Chain` / `## 시나리오 의존 체인` — Serial blocks + independent list (only if any serial deps exist)
6. `## Scenarios` / `## 시나리오` — one H3 per scenario
7. `## Dropped S1 Paths` / `## 제외된 S1 경로` — REQUIRED final section; flat list of every dropped + deferred S1 candidate (see Coverage). This is the only allowed trailing section; nothing follows it.

## Frontmatter schema

`---`-fenced, 5 lines, `key: value`:

```
---
Document: {domain}({surface}) / {feature-slug} / {version}
Generated: {YYYY-MM-DD HH:mm} (KST)
Total scenarios: {N}
Atomic-path coverage: {ratio} (represented S1 {r} / total S1 candidates {r+d})
Crawl rung: {a live+auth | b live-public | c static} (MCP: {server or none})
---
```

(KO keys: `문서 / 생성 시각 / 총 시나리오 수 / 원자 단위 기준 시나리오 커버리지 / 크롤 등급`.)

- `Total scenarios` MUST equal the H3 count AND the index-bullet count (byte-identity gate).
- `Crawl rung` is the honesty gate (Hallucination Guards). Always present.

## Coverage math (pin ONE semantics)

```
coverage = represented / (represented + dropped)
```

- **numerator** = count of S1 atomic paths that an active scenario asserts.
- **denominator** = ALL enumerated S1 candidates = represented + dropped. Drops are ADDED to the denominator, never subtracted from the candidate count.
- Round to 3 decimals. Spell out numerator and denominator in the parenthetical (KO form: `대표된 S1 실행 path {r} / S1 후보+제외/drop {r+d}`).

**Recountability (G5 hard assert)**: every dropped path in the denominator MUST be listed in the `## Dropped S1 Paths` section, one line each. G5 asserts `(Dropped S1 Paths line count) == (denominator − numerator)`. The coverage number must be byte-recomputable from the document — a denominator containing drops that are not enumerated is malformed (this is the V6 failure mode: V6 claims 31/55 but enumerates none of its 24 drops; do not repeat it).

**Invariant** (G5 + eval grader): the parenthetical numerator MUST be ≤ the denominator, and denominator MUST equal `represented + dropped`. A parenthetical where numerator > the first denominator term is malformed.

**Partial / deferred exports (DEFERRED bucket)**: every S1 candidate is `represented`, `dropped` (a drop code applies), OR `deferred` (on-spine + UI-triggerable, but consciously not yet authored — no drop code fits). Deferred paths are NOT in the coverage denominator (they are coverable, just not done), but MUST be listed in `## Dropped S1 Paths` under a `Deferred (not in denominator):` subheading so nothing is silently omitted (Core Rule 3). A full export has zero deferred.

**Worked example**: 12 S1 paths enumerated; 9 represented, 3 dropped (1 `SECOND_IDENTITY_REQUIRED`, 1 `NO_UI_TRIGGER`, 1 `NON_SELF_CONTAINED`), 0 deferred. → `coverage = 9 / 12 = 0.750`, written `0.750 (represented S1 9 / total S1 candidates 12)`; the `## Dropped S1 Paths` section lists exactly 3 lines.

## Per-scenario block

```
### [E2E-{PREFIX}-NNN] {title — action + asserted focus}

**Entry path**: {1–2 sentences, from auth/session to the screen under test}

**Setup**:
- token prefix: `{PREFIX}-{YYYYMMDD}-{HHmm}-{worker}`
- seed/fixture: {named seed entity or fixture path, or "self-created only"}
- skip rule: {restate any SKIP_* / WARNING: that applies}
- dropped S1 here: {one-line rationale + drop code, if this scenario owns a dropped branch}
- guard: {e.g. "This scenario does not submit/create X" for inspection-only}

1. {action step}
2. Verify that {observable assertion}.
3. ...
```

Required fields: `Entry path`, `Setup`, numbered steps. (KO: `진입경로` / `시나리오 준비` / steps.)

## Step grammar (overrides test-discover conventions.md)

- Numbered **from 1** (NOT 0).
- Action steps: plain imperative ("Click `Create`", "Enter `{title}` in the `Title` field").
- Verify steps: assertion **inlined**, begin with "Verify that …" (KO: end with `…인지 확인한다`). NOT a separate `-> 확인:` / `-> Verify:` prefix line.
- UI strings in backticks, verbatim, target-UI language. Unobserved → `[UNVERIFIED: requires live crawl]`.
- Pre-arm download/new-page waits BEFORE the triggering click ("Start waiting for the download, then click `…`").
- Numbering is monotonic within a scenario. (Do NOT replicate the dual-numbering seen in some example exports where an inlined login block restarts at 1 and the outer counter resumes mid-sequence — that is a copy-paste defect, not a convention.)

## Determinism contract

- **Single fixed persona** per export; state it up front. Permission allow/deny branching is out of scope for the golden-path spine (removes role nondeterminism) — cover it as separate explicitly-dropped or separate-scenario items.
- **Data token** `{YYYYMMDD}-{HHmm}-{worker}` appended to every created title/search term/comment. `{worker}` = the parallel-safety variant guaranteeing distinct data per Playwright worker. Declared once in Common Preconditions; each scenario names its specific prefix in `Setup`.
- **Self-seed + exact re-query**: create own data, then locate it by the exact tokenized title (exact-row match, "the row whose title is exactly `…`"), never the top/live row.
- **Named seed constants** for any unavoidable shared entity; declare in Common Preconditions.
- **Exact-label selection** for autocomplete/search controls (single active item); fuzzy match is a determinism hazard → SKIP on failure.
- **Auth via storageState by NAME only** — never a literal credential (see SKILL Hallucination Guards, security delta).

## SKIP / WARNING taxonomy

Two marker classes, both terminal with "record then end/skip":

- **`SKIP_{REASON}`** (SCREAMING_SNAKE) — hard skip when a required fixture/precondition is unavailable. e.g. `SKIP_FIXTURE_{NAME}`, `SKIP_STORAGE_STATE`. Action: "record `SKIP_…` and end this scenario."
- **`WARNING: {free text}`** — soft data-availability issue; record and skip only the affected assertion, continue if safe. e.g. `WARNING: seed row not found — badge assertion skipped`.

Rules:
- A marker NEVER silently passes — it always records then ends/skips.
- `SKIP`/`WARNING` (data/fixture absence) are RIGOROUSLY separate from the **FAIL sentinel** (an error/interstitial page appearing = hard test failure, recorded as FAIL, never skipped/retried).
- Declare every applicable marker once in Common Preconditions AND restate it inline at the step that can trigger it.

## Fixture paths

`fixtures/{feature}/{images|bulk|upload}/...` — reference real fixture files by path; if absent, `SKIP_FIXTURE_{NAME}`. Never inline binary or invent a fixture.

## Common Preconditions block (template)

```
## Common Preconditions

- Persona: {single role}; permission allow/deny not verified here.
- Base URL: {env URL or [UNVERIFIED]}
- Auth: reuse storageState `{name}` (LINE SSO cookie captured out-of-band). No credentials in this document.
- Data token: append `{YYYYMMDD}-{HHmm}-{worker}` to every created title/search/comment.
- FAIL sentinel: if `{error/interstitial page text OR [UNVERIFIED: requires live crawl]}` appears in any scenario, record FAIL. (At rung b/c the sentinel string is unobserved → emit `[UNVERIFIED]`, never a guessed error string. A present-with-`[UNVERIFIED]` sentinel passes G5.)
- Crawl rung used: {a|b|c} (MCP: {server or none}). {If majority [UNVERIFIED], add the WARNING banner.}
- Seeds/fixtures: {named constants + fixture paths, or "self-created only"}
- Skip rules: {global SKIP_*/WARNING: definitions}
```

## Degraded-mode banner (when majority strings [UNVERIFIED])

Place immediately after the H1:

```
> ⚠️ This export was generated WITHOUT a live crawl (rung c, static read). Most selectors are [UNVERIFIED]
> and must be confirmed against the running UI before implementation.
```

## Dropped S1 Paths section (template)

REQUIRED final section. One line per dropped candidate; line count MUST equal `denominator − numerator`. Deferred paths go under their own subheading and are NOT counted toward that equality.

```
## Dropped S1 Paths

- {journey / atomic path} — `{DROP_CODE}` — {one-line rationale}
- approve a ticket I created — `SECOND_IDENTITY_REQUIRED` — approver ≠ creator; single test identity cannot self-approve
- SCHEDULED → IMPLEMENT transition — `NO_UI_TRIGGER` — no UI control; time/backend-driven

Deferred (not in denominator):
- {on-spine, UI-triggerable path consciously not yet authored}
```

