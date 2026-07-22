# iris-ui — worked recipe

Concrete values for the iris-ui (LYRIS) frontend. Verified 2026-07-22 (LYRIS-502 approval-progress PR #84).

## Project facts

| Item | Value |
|---|---|
| Dev command | `pnpm dev` → `next dev -H lyris-local.linecorp-dev.com --experimental-https` |
| URL | `https://lyris-local.linecorp-dev.com:3000` |
| Session cookie | `irisToken` (`constants/common.ts` → `TOKEN_KEY`) |
| Route guard | `middleware.ts` — presence-only: `if (!isPrefetch && !token?.value) redirect(OAuthURL)` |
| Matcher | `["/((?!api|static|.*\\..*|_next).*)"]` → `/favicon.ico` bypasses |
| Pages router | preview pages under `pages/dev/<name>.tsx` |
| App providers | `pages/_app.tsx` wraps RecoilRoot + QueryClientProvider + TimezoneProvider — a bare page still gets timezone/query context |

## Full sequence

1. **New worktree needs deps**: `pnpm install` first (worktrees start without `node_modules`).
2. **Temp preview page** `pages/dev/<name>.tsx` — render the component with mock props, no API calls. For As-Is, reproduce the old markup:
   ```bash
   git show HEAD~1:components/changes/detail/BasicInformationTable.tsx   # copy the pre-change block
   ```
   Rebuild that block in the preview with mock data (don't swap the live file).
3. **Dev**: `cd <worktree> && (pnpm dev > /tmp/<slug>-dev.log 2>&1 &)`; wait ~12s; confirm `Ready` in the log.
4. **chrome-devtools bypass** (see `auth-bypass.md`):
   - `navigate_page` → `https://lyris-local.linecorp-dev.com:3000/favicon.ico`
   - `evaluate_script` → `document.cookie = "irisToken=dev-preview; path=/"`
   - `navigate_page` → `https://lyris-local.linecorp-dev.com:3000/dev/<name>`
   - `wait_for` a known string; re-navigate once if the first snapshot shows 404/redirect.
5. **Capture**: `resize_page` (e.g. 1200×1000) → `take_screenshot`. `filePath` must be inside the primary workspace root (chrome-devtools rejects sibling worktree paths):
   ```
   /Users/<me>/orca/workspaces/iris-ui/<primary-root>/<name>.png
   ```
   then `mv` to the worktree root beside the PR. Read each PNG back to verify the state rendered.
6. **Cleanup**: `rm pages/dev/<name>.tsx`; `rmdir pages/dev`; `lsof -ti:3000 | xargs kill`; confirm `git status` tracked-clean (screenshots + preview are untracked).

## PR handoff

iris-ui PRs on GHE (git.linecorp.com): the CLI cannot attach images. Name files `asis-*.png` / `tobe-*.png`, `open` the folder, and the human drags them into the PR editor's Visual comparison table to get `user-attachments` URLs. See memory `feedback-pr-visual-comparison`.

## Gotchas

- Components using `useTimezone`/`useCustomToast` etc. pull Recoil/context — the bare preview page still renders because `_app.tsx` provides them; but a child like `TimestampDisplay` needs the provider, so render inside the app (a `pages/` route), not a standalone React root.
- `MarkdownRenderer` bundles react-markdown (ESM) — fine in the browser/dev, but if screenshotting via jest-dom it must be mocked (irrelevant here; this is real-browser capture).
- Dev cwd resets between tool calls in some harnesses — prefix commands with the absolute worktree path rather than relying on persistent `cd`.
