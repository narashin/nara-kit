# web-ui search box (placeholder repo for evals)

<!-- EVAL-FAKE-DO-NOT-USE: placeholder codebase description for nara-prototype evals. -->

Stack: React 18 + TypeScript + Vite, tests with Vitest. No lodash, no debounce library installed.
Ticket: PROJ-123 "Search box sends too many requests".

`src/search/useSearch.ts` calls `GET /api/search?q=<text>` on every keystroke. The search API is
owned by api-server and is not reachable from a local run.

Decision: leading-edge debounce (fire first keystroke, then wait 300ms) or trailing-edge debounce
(wait 300ms after the last keystroke)?

Criteria the team cares about:
1. Typing "acme" quickly sends at most 1 request.
2. The final typed text is always the one searched.
3. First results appear within 700ms of the last keystroke.

Nothing in the repo decides this yet: there is no debounce helper and no test covering request count.
