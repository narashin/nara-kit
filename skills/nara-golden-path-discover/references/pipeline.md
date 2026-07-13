# Golden-Path Discovery Pipeline

Six stages. Each either CONSUMES nara-test-discover output or applies a golden-path-specific transform. The pipeline never re-derives what nara-test-discover already produces.

## Terminology: two different "S" vocabularies (disambiguated)

`nara-test-discover` uses **Stage-1 / Stage-2 / Stage-3** for its candidate→selection pipeline (Stage-2 = candidate set, Stage-3 = selected set). Those are *scenario-candidate* stages.

This skill uses **S1 atomic execution path** for a different, self-contained concept defined below. The bare token `S1` in this skill and in the export's coverage line ALWAYS means "atomic execution path", never nara-test-discover's stage number. Do not conflate them.

## S1 atomic execution path — definition (load-bearing)

An **S1 path** is one distinct, observable, top-level execution route through a golden journey that ends in a single asserted outcome. Granularity rules:

- One S1 path = one (entry state → action sequence → one observable outcome) triple. Different outcomes from the same screen = different S1 paths (e.g. "submit valid → success toast" and "submit empty → blocked" are two S1 paths).
- A branch caused by a distinct UI control value counts as a separate S1 path only if the outcome is observably different (enum/option value-parametrization → one S1 path per distinct observable outcome, not per value).
- Pure navigation with no asserted state change is NOT an S1 path (it is a step inside one).

Enumerate the S1 path candidates per journey explicitly. Each candidate is then classified in G3 as **represented** (an active scenario asserts it) or **dropped** (with a drop code). This enumeration is what makes the coverage number auditable — a reader can recount it from the document.

## G0 — Consume nara-test-discover (REUSE)

Invoke `nara-test-discover` on the target, or read `docs/test-scenarios/scenarios-detailed.md` if it already exists. Inherit, without re-deriving:

- screen tree (routes), interaction inventory, user journeys, permission×screen matrix, UI-observable state machine.

These journeys + the permission matrix ARE the golden-path candidate pool. Also reuse `../nara-test-discover/references/heuristics.md` for the E2E heuristic catalog (deep links, refresh, toast/modal, latency, acceptance invariant, cross-field corruption). Do not restate heuristics here.

## G1 — Journey filter + parallel-safety tagging

From the inherited pool, keep the **golden-path spine**: Happy + cross-screen `Scope=e2e` journeys. Admit a Sad/Edge step only if it is on the same journey AND browser-provable.

Tag every surviving candidate with three parallel-safety verdicts:

1. **self-seedable?** — can the scenario create its own data in-browser?
2. **single-identity?** — or does it need a second logged-in identity (e.g. creator ≠ approver)?
3. **UI-triggerable?** — or does the state transition require time/backend (no UI button)?

Candidates that fail are NOT deleted — route them to the coverage denominator with a drop code:

| Drop code | Meaning |
|-----------|---------|
| `NON_SELF_CONTAINED` | cannot create + locate its own data in-browser |
| `SECOND_IDENTITY_REQUIRED` | needs a different logged-in user (e.g. approve ≠ create); single test identity cannot cover |
| `NO_UI_TRIGGER` | the state transition has no UI control (time/backend-driven, e.g. SCHEDULED→IMPLEMENT) |
| `CONTROL_STATE_REQUIRED` | needs a precondition state not reproducible in a clean run |

These compose with nara-test-discover's existing exclusion codes (`LOWER_LAYER_BETTER`, `DUPLICATE`, `OUT_OF_SCOPE`, etc.) — use those for non-e2e-specific drops.

**Serial-block strategy**: when a journey legitimately needs an entity produced by an earlier step (and API setup is unavailable), chain the steps inside ONE scenario as a continuous numbered list (create → act → assert), OR declare a Serial block in the export's dependency section. Prefer single-scenario chaining for self-containment.

## G2 — Live crawl (verbatim selectors)

Harvest exact UI strings (labels, placeholders, toasts, dialog/confirm copy, column headers) + URL-contains asserts for each golden screen, so the export's selectors are verbatim and map 1:1 to Playwright `getByRole`/`getByText`/`getByPlaceholder`. Full operation, crawl-tool choice (Agent CLI `playwright-cli` primary / Playwright MCP / chrome-devtools fallback), one-time auth capture, and the 3-rung degradation ladder: [live-crawl.md](live-crawl.md).

## G3 — Atomic-path stratify + coverage

1. Decompose each kept journey into S1 path candidates (per the definition above). Write the enumerated list.
2. Classify each: **represented** or **dropped (code)**.
3. Coverage = `represented / (represented + dropped)`, rounded to 3 decimals. Spell out numerator and denominator in the frontmatter parenthetical. Every dropped S1 path MUST be enumerated in the REQUIRED `## Dropped S1 Paths` section (one line each) so the number is byte-recountable; the per-scenario `Setup` may also note a drop a surviving scenario owns, but the section is the canonical home for orphan drops (whole journeys dropped as `SECOND_IDENTITY_REQUIRED`/`NO_UI_TRIGGER`). On-spine-but-unauthored paths are `deferred` (not in the denominator) and listed under the section's Deferred subheading. Drops feed the denominator honestly — coverage is < 1.0 when real branches are not browser-coverable; never inflate by hiding drops. See export-format.md Coverage.

## G4 — Export detailing

Detail kept scenarios in batches of 5–10 using the export schema in [export-format.md](export-format.md): `Entry path` → `Setup` → numbered steps (from 1, inlined assertions). Clone the fixed resilience preamble into every scenario; stamp the token rule. Use stable append-only IDs `[E2E-{PREFIX}-NNN]`.

## G5 — Consistency pass + auto-chain

Scan and auto-fix:

- index ↔ H3 byte-identity; `Total scenarios` == H3 count == index-bullet count.
- IDs append-only, never renumbered. ID gaps from previously dropped/merged scenarios are EXPECTED — never renumber to close a gap. (This is distinct from step numbering, which is monotonic WITHIN a scenario.)
- frontmatter coverage recomputed against actual represented/dropped counts; assert `(Dropped S1 Paths line count, excluding Deferred) == (denominator − numerator)`.
- every UI string that maps to a selector has crawl provenance OR `[UNVERIFIED]` — **FAIL otherwise**. This gate covers selector strings AND the FAIL-sentinel string AND the login-readiness-gate string: at rung b/c each is either crawl-confirmed or `[UNVERIFIED]` (a present-with-`[UNVERIFIED]` sentinel/gate PASSES; a guessed one FAILS).
- every behavioral claim (`[LIVE-CONFIRMED]` modal opens / redirect target / navigation outcome / toast) is backed by an explicit step-through OR a source cross-check — NOT a lone snapshot (see live-crawl.md "Label harvest vs behavioral claims"). A behavioral claim contradicted by source is a **FAIL**.
- FAIL sentinel vs SKIP markers present and distinct.
- token-prefix consistency; pre-armed waits on download/new-page steps.

Then auto-invoke `nara-test-verify` on `docs/test-scenarios/golden-paths.E2E.md`.
