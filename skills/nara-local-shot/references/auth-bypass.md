# Auth bypass for local screenshots — mechanism & validity

chrome-devtools MCP drives a fresh browser with no cookies, so any SSO-gated route redirects to the identity provider before the page renders. This blocks automated screenshots. The bypass below makes a locally-running app render a page **without a real session**, valid only under specific conditions.

## When the dummy-cookie bypass is valid

All three must hold:

1. **The route guard checks cookie _presence_, not validity.** Typical Next.js middleware:
   ```ts
   const token = request.cookies.get(TOKEN_KEY)
   if (!isPrefetch && !token?.value) return NextResponse.redirect(OAuthURL)
   ```
   Any non-empty cookie value passes — the middleware never verifies the token server-side. A dummy string is enough.

2. **The target page makes no real API calls** (or none that block render). An isolated preview page rendering a component from mock props qualifies. A real data page does not — its fetches 401 against the dummy token, and a `credentials: "include"` client typically redirects to OAuth on 401.

3. **The session cookie is not httpOnly _in this browser_.** `document.cookie` cannot set or overwrite an httpOnly cookie. On a fresh automated browser there is no existing cookie, so JS can set a brand-new non-httpOnly cookie of the same name; the browser sends it on subsequent same-origin requests, which is all the middleware reads.

If any condition fails, use the real-session fallback below.

## The `.ico` origin trick

To set a cookie for the app origin, the browser must first be _on_ that origin — but navigating to any guarded route redirects away (to the external IdP) before any script runs. Solution: navigate to a **static-asset path containing a dot**.

Middleware matchers commonly exclude asset/framework paths:
```ts
export const config = { matcher: ["/((?!api|static|.*\\..*|_next).*)"] }
```
`.*\..*` excludes anything with a dot, so `/favicon.ico` (or any `*.ico`, `*.png`) is served directly, same-origin, with **no redirect**. That establishes the origin so `document.cookie` writes stick. Then navigate to the guarded preview URL.

## Steps (chrome-devtools MCP)

```
navigate_page  url=https://<host>:<port>/favicon.ico     # dotted path → no redirect, origin set
evaluate_script  () => { document.cookie = "<COOKIE>=dev; path=/"; return document.cookie }
navigate_page  url=https://<host>:<port>/dev/<preview>    # middleware sees cookie → passes
wait_for       text=["<some text on the page>"]           # confirm render (first nav may still 3xx briefly)
take_screenshot filePath=<inside workspace root> fullPage=true
```

Notes:
- The **first** navigate to the preview can transiently show a redirect/404 snapshot; re-navigate and `wait_for` real content. Trust the dev-server log's `GET /... 200` over a single early snapshot.
- Self-signed https (mkcert etc.) is usually accepted by the chrome-devtools browser; if a cert page blocks, the mkcert CA is likely already trusted from `pnpm dev` bootstrap.
- `take_screenshot` `filePath` must resolve **inside a configured workspace root**; saving elsewhere errors. Save to the primary root, then `mv`.

## Fallback: real session (API-dependent pages)

When the page genuinely needs authenticated backend data, the dummy cookie cannot work. Reuse the project's e2e `storageState` (real cookies captured once) with Playwright instead of chrome-devtools' fresh browser. For iris-ui this is the SSO storageState pattern already documented for e2e — the dummy-cookie route is only for isolated, API-free preview pages.
