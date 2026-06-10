# Live Crawl: Verbatim Selector Harvest

How G2 harvests exact UI strings so the export's selectors are real, not guessed. The absolute rule: **an unobserved string is `[UNVERIFIED: requires live crawl]`, never an invented label.**

## MCP choice

- **Primary: Playwright MCP** (`mcp__playwright__*`). Rationale: `browser_snapshot` returns the accessibility tree as role + accessible-name pairs that map 1:1 to `getByRole`/`getByText`/`getByPlaceholder`, yielding directly-usable verbatim selector strings. It also reuses a captured `storageState` cleanly for cookie-gated SSO.
- **Fallback: chrome-devtools MCP** (`mcp__chrome-devtools__*`). Use only when an already-authenticated tab is open (reuse the live session via `take_snapshot`) or when network/console inspection is needed to confirm a toast actually fires. Its snapshot is DOM-oriented, not selector-oriented, so it is not the default.

If neither MCP is enabled at runtime → rung (c) static read (below). State the actual server (or `none`) in the export's `Crawl rung` frontmatter line.

## Harvest operation (rung a)

1. Navigate `baseURL` = the env UI URL (e.g. `env=dev`), reusing `storageState`.
2. For each golden screen, run `browser_snapshot`; extract accessible names for: buttons, links, headings (H1/tab labels), placeholders, toast text, dialog/confirm copy, table column headers.
3. Record each as a backticked verbatim string keyed to its locator role (e.g. `` button `Create` ``, `` placeholder `Search Employee ID or Name` ``).
4. Capture the **login readiness gate** text and the **FAIL sentinel** (error/interstitial page) string.
5. Capture **validation-message** copy — static reads often cannot confirm these (component libraries may render Modal/validation lazily; `validationMessage` is frequently not `getByText`-queryable), so live capture is the only reliable source.

## Graceful degradation (3-rung ladder)

| Rung | Condition | Behavior |
|------|-----------|----------|
| **(a) live + auth** | env URL + valid storageState + MCP | full crawl; harvested strings are CONFIRMED |
| **(b) live + public** | env URL + MCP, no auth | crawl only pre-auth/public screens; every gated string → `[UNVERIFIED: requires live crawl]` |
| **(c) static** | no env / no MCP / `crawl=off` | static read of source (below); all dynamic/validation/lib-internal strings → `[UNVERIFIED]` |

Across ALL rungs: an absent string becomes `[UNVERIFIED]`. No credential/token is ever written to the artifact — auth is referenced by `storageState` name only.

## Static read source (rung c)

Read **hardcoded JSX string literals in `components/**/*.tsx`** (and route files) — this is the real label source for codebases that keep UI text inline. Do NOT rely on i18n message files unless they are actually populated: many projects have near-empty `messages/*.json` stubs while real labels live in JSX. If a static source returns empty, emit `[UNVERIFIED]` — never synthesize a label to fill the gap.

Static read reliably yields: button/link/heading/tab/placeholder literals on the golden spine. It does NOT reliably yield: dynamically composed strings, component-library-internal copy, and validation messages → mark those `[UNVERIFIED]`.

## Honesty gate

- The export's `Crawl rung` frontmatter line + a Common Preconditions line MUST state the rung actually used and the MCP server available.
- If more than 50% of golden-screen strings are `[UNVERIFIED]`, prepend the degraded-mode WARNING banner (see export-format.md) — do not present a placeholder skeleton as full-fidelity. Below that threshold the `Crawl rung` frontmatter line + Common Preconditions disclosure carry the honesty load, so the absence of a banner is intentional, not an omission.
- G5 consistency pass FAILS if any selector string appears without crawl provenance or an `[UNVERIFIED]` marker.

## Language fidelity

Backticked strings MUST be in the TARGET UI's language exactly as observed. Never translate or normalize. If the example/reference exports are in a different language than the target UI, the target UI wins — a mismatch means you guessed, which is forbidden.

## Security

This skill intentionally DIVERGES from example exports that hardcode real test credentials. Never copy an account/password pattern into the artifact. Cookie-gated SSO auth is referenced by `storageState` name only; the capture (one-time manual login → save storageState) happens out-of-band and is never scripted with literal credentials in the export.
