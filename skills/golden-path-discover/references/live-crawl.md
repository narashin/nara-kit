# Live Crawl: Verbatim Selector Harvest

How G2 harvests exact UI strings so the export's selectors are real, not guessed. The absolute rule: **an unobserved string is `[UNVERIFIED: requires live crawl]`, never an invented label.**

## Crawl tool choice

- **Primary: Playwright Agent CLI** (`playwright-cli`, the `@playwright/cli` package — "run playwright mcp commands from terminal"). Token-efficient (concise CLI output, no large tool schema loaded into context) and the best fit for agent-driven crawl. Key commands: `open <url> [--headed]`, `goto`, `snapshot [element]` (returns the accessibility tree with element `ref`s — role + accessible-name pairs that map 1:1 to `getByRole`/`getByText`/`getByPlaceholder`), `state-save <file>` / `state-load <file>` (native storageState for cookie-gated SSO), `cookie-set` (direct token injection), `-s=<session>` for isolated sessions. Invoked via Bash.
- **Alternative: Playwright MCP** (`mcp__playwright__*`). Same capability set via MCP; use when already wired in-session and no CLI is installed. Higher token cost (verbose output + schema) than the Agent CLI.
- **Fallback: chrome-devtools MCP** (`mcp__chrome-devtools__*`). Use only when an already-authenticated tab is open (reuse the live session via `take_snapshot`) or when network/console inspection is needed to confirm a toast fires. DOM-oriented snapshot, not selector-oriented.

If no crawl tool is available at runtime → rung (c) static read (below). State the actual tool used (or `none`) in the export's `Crawl rung` frontmatter line.

## Auth capture (one-time, human step)

Cookie-gated SSO cannot be scripted (the IdP login screen — Okta/SAML/OIDC — is outside the app). The login is a one-time HUMAN action; the agent only reuses the result:

1. `playwright-cli open <env URL> --headed` → the app redirects to the IdP login.
2. The USER completes SSO in that visible browser (their hands, their credentials — never typed to the agent, never written to any file/artifact).
3. `playwright-cli state-save <auth file>` → persists cookies + localStorage (the session) to a gitignored local file.
4. Subsequent crawls: `playwright-cli state-load <auth file>` then `goto` — already authenticated.

(Alt: if the user already has a live session, `cookie-set <token-name> <value>` injects it — but prefer state-save so the raw token never passes through chat.) State files expire with the IdP/token TTL → re-capture on 401.

## Harvest operation (rung a)

1. `state-load <auth file>` then `goto` each golden screen at the env UI URL.
2. For each golden screen, run `snapshot` (Agent CLI) / `browser_snapshot` (MCP); extract accessible names for: buttons, links, headings (H1/tab labels), placeholders, toast text, dialog/confirm copy, table column headers.
3. Record each as a backticked verbatim string keyed to its locator role (e.g. `` button `Create` ``, `` placeholder `Search Employee ID or Name` ``).
4. Capture the **login readiness gate** text and the **FAIL sentinel** (error/interstitial page) string.
5. Capture **validation-message** copy — static reads often cannot confirm these (component libraries may render Modal/validation lazily; `validationMessage` is frequently not `getByText`-queryable), so live capture is the only reliable source.

## Label harvest vs behavioral claims (CRITICAL)

A single snapshot is reliable for **labels** (static text in the accessibility tree) but NOT for **behavioral claims**. Two different trust levels:

- **Labels** (button/heading/placeholder/column text) — one `snapshot` is authoritative. Tag freely.
- **Behavioral claims** — "clicking X opens a modal", "submit redirects to URL Y", "no dialog appears", "toast Z shows". A single post-action snapshot is UNRELIABLE for these: stale element `ref`s, animation/redirect timing, and toasts with short `duration` routinely produce a WRONG observation (e.g. snapshot taken after a redirect already completed shows "no modal" when the modal did open). **Never tag a behavioral claim `[LIVE-CONFIRMED]` from a single snapshot.**

To assert a behavioral claim, do ONE of:
1. **Step-through**: snapshot immediately after the click (catch the modal), THEN act on it (confirm/cancel), THEN snapshot again (catch the redirect) — confirm each transition explicitly, never infer the chain from one frame.
2. **Source cross-check**: read the handler in `components/**/*.tsx` (e.g. does `onClick` call `setModalOpen(true)` vs submit directly? does success do `router.push(ROUTE.X)` — bare or with query?). Source is authoritative over a flaky frame; when a snapshot and the source disagree, the source wins and the claim is re-crawled.
3. Otherwise mark the behavioral claim `[UNVERIFIED]` with the specific reason.

This is a hard rule: a behavioral `[LIVE-CONFIRMED]` requires either an explicit per-transition step-through OR a source cross-check, not a lone snapshot. G5 treats a behavioral claim contradicted by source as a FAIL.

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
