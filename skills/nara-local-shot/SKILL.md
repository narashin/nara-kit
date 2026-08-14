---
name: nara-local-shot
description: Capture screenshots of a locally-running web app — even auth/SSO-gated pages — for PR visual comparison or UI verification, then save the image files. Drives a local dev server + chrome-devtools MCP, bypassing SSO with a dummy session cookie when the target page needs no real backend. USE FOR "스샷 찍어줘", "PR 스샷", "before/after 캡쳐", "visual comparison 이미지 만들어", "로컬 앱 스샷", "capture a screenshot of the local app", "as-is/to-be 스샷". DO NOT USE FOR env-diff visual regression across QA/prod (use nara-ui-diff), figma-vs-runtime diff, or writing/running Playwright test code (use nara-test-implement).
---

# nara-local-shot — capture local app screenshots (auth-gated ok)

Produce real screenshot files of a locally-running web app and save them to disk — for a PR's Before/After visual comparison, or to let a human eyeball a UI change. Handles the common blocker: the app is behind SSO and a fresh automated browser has no session.

Core insight: **capture the screenshots yourself and save the files** — never stop at leaving `_drag image here_` placeholders. The human only does the final drag-drop into the PR editor.

## When each capture strategy applies

- **Isolated preview page** (preferred for components): create a throwaway page that renders the target component with mock props and **no API calls**. Works with a dummy cookie, needs no real backend or data. Use for a single component (e.g. an approval widget) and for reproducing an **As-Is** (pre-change) render from old markup.
- **Real app page**: navigate a genuine route. Needs a real authenticated session (real backend data). Only when the screenshot must show live data end-to-end — heavier; prefer the isolated preview when the component is the subject.

## Workflow

### 1. Decide targets and passes
Settle first whether a comparison is wanted, or current-state only (single pass). A purely additive change has no prior render — capture To-Be only and say so, don't hunt for an As-Is.

For Before/After, list each shot: one **As-Is** + one-or-more **To-Be**, per state worth showing (e.g. in-progress vs rejected). That is **two renders from two revisions**; only To-Be comes from the current tree. Pick the As-Is source now — the cost is the launch sequence, not the picture:

- **Reconstruct in a preview page** (preferred): `git show HEAD~1:<file>` (or `origin/<base>:<file>`), rebuild the old markup in a temp preview page with mock data. Safer than swapping the live file, and both passes share one dev server.
- **Second server run**: for real app pages, or when the old render leaned on since-changed shared code. Needs its own base-revision worktree, dev server restart, and possibly refreshed deps/build/codegen state.

Fix a non-colliding naming scheme up front — `<state>-asis.png` / `<state>-tobe.png`. Full procedure: `references/comparison-passes.md`.

### 2. Temp preview page (isolated strategy)
Create `pages/dev/<name>.tsx` (Next.js pages router) or the framework's equivalent route. Render the component with representative mock props covering the states to capture. Mark the file clearly `TEMPORARY — DO NOT COMMIT`. Keep it API-free so a dummy session suffices.

### 3. Start the dev server
Run the project's dev command in the worktree (background). Note the host/port/protocol (often custom host + self-signed https). Confirm "Ready" in the log.

### 4. Auth bypass via chrome-devtools MCP
chrome-devtools MCP attaches to a **fresh** browser with no session, so an SSO-gated route 3xx-redirects to the login provider. Bypass when the target page needs no real API (see `references/auth-bypass.md` for the full mechanism and when it is/ isn't valid):
1. `navigate_page` to a **static-asset path with a dot** (e.g. `/favicon.ico`) — route-guard middleware matchers usually exclude `.*\..*`, so it loads same-origin with no redirect and establishes the origin.
2. `evaluate_script` to set the session cookie: `document.cookie = "<COOKIE_NAME>=dev; path=/"`. Works only if the cookie is not httpOnly on a fresh browser (no existing cookie to block it) AND the middleware checks **presence, not validity**.
3. `navigate_page` to the preview/target URL → middleware passes → renders.

If the page makes real API calls that 401 on a dummy token, the bypass fails — use a real `storageState` (Playwright) instead; see `references/auth-bypass.md`.

### 5. Capture + save
Use `take_screenshot` with `filePath`. Note: chrome-devtools **only writes inside a configured workspace root** — saving to a sibling worktree or `~/Downloads` errors with "not within workspace roots". Save to the primary workspace root, then `mv` the files to their destination (e.g. the worktree root next to the PR).
- Widen the viewport first (`resize_page`) for readable layout.
- `fullPage: true` for a whole page; scroll + viewport shots (`evaluate_script` `scrollIntoView`) for per-state crops.
- Verify each saved PNG by reading it back before handing off — confirm the intended state actually rendered.

### 6. Cleanup
Before tearing anything down, confirm every planned shot from step 1 exists on disk — a missing pass found after teardown costs the whole launch sequence again. Then delete the temp preview page(s), kill the dev server (`lsof -ti:<port> | xargs kill`), confirm the tracked tree is clean. Screenshots stay untracked (not committed).

### 7. Hand off
Report absolute file paths and open the folder (`open <dir>`). For GHE PRs, the human drags the files into the PR editor to get `user-attachments` URLs (CLI cannot attach): the `gh`/API path cannot upload PR-body image attachments, so hand the absolute paths back and let the user drop them into the web editor.

## Project specifics

Concrete per-project values (dev command, host/port, cookie name, middleware matcher) live in `references/`. webapp is worked end-to-end in `references/project-recipe.md`.

## Additional resources

- **`references/comparison-passes.md`** — planning both sides of a Before/After: when an As-Is exists at all, reconstruct-vs-two-server-runs, revision switching without disturbing the tree, stale generated state, naming so passes don't overwrite.
- **`references/auth-bypass.md`** — the dummy-cookie mechanism in detail: why presence-only middleware allows it, the `.ico` matcher trick, httpOnly caveat, and the real-`storageState` fallback for API-dependent pages.
- **`references/project-recipe.md`** — webapp worked example: `next dev -H local.example.com --experimental-https` on :3000, `appToken` cookie, `middleware.ts` presence-check, As-Is reproduction from `git show`.
