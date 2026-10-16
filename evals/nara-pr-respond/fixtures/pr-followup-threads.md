# PR fixture: acme-sre/web-ui#57 "feat: refresh session token on 401"

GitHub is not reachable in this run. Each section below is the verbatim output the
named `gh` call returned. The PR branch is checked out; the diff below is its full change.

## gh pr view 57 --json number,url,headRefName,baseRefName,author,headRefOid

```json
{"number":57,"url":"https://github.com/acme-sre/web-ui/pull/57","headRefName":"feature/PROJ-41-token-refresh","baseRefName":"main","author":{"login":"dev"},"headRefOid":"9f3c2e1"}
```

## git diff main...HEAD

```diff
--- a/src/api/session.ts
+++ b/src/api/session.ts
@@ -18,8 +18,19 @@ import { http } from "./http";
 export async function fetchWithSession(url: string): Promise<Response> {
-  return http.get(url, { headers: authHeaders() });
+  let res = await http.get(url, { headers: authHeaders() });
+  while (res.status === 401) {
+    await refreshToken();
+    res = await http.get(url, { headers: authHeaders() });
+  }
+  return res;
 }
+
+async function refreshToken(): Promise<void> {
+  const r = await http.post("/auth/refresh");
+  const body = await r.json();
+  setToken(body.access_token);
+}
 
 function authHeaders() {
   const ttl = Number(process.env.SESSION_TTL);
   return { Authorization: `Bearer ${getToken()}`, "X-Session-TTL": String(ttl) };
 }
```

`authHeaders` and its `SESSION_TTL` line are unchanged context: `git blame` shows them
from commit `1a2b3c4` (2026-03-02), three months before this PR.

## gh api repos/acme-sre/web-ui/pulls/57/comments

```json
[
  {"id":9001,"user":{"login":"reviewer-a","type":"User"},"path":"src/api/session.ts","line":20,"side":"RIGHT","original_line":20,"position":4,"in_reply_to_id":null,
   "body":"401이 계속 오면 이 while이 끝나지 않아요. refresh 자체가 401이면 무한 루프입니다. 시도 횟수 상한이 필요해 보여요."},
  {"id":9002,"user":{"login":"reviewer-a","type":"User"},"path":"src/api/session.ts","line":34,"side":"RIGHT","original_line":34,"position":18,"in_reply_to_id":null,
   "body":"SESSION_TTL이 없으면 Number(undefined)라 NaN이 헤더로 나갑니다. 환경변수 검증을 넣어 주세요."},
  {"id":9003,"user":{"login":"reviewer-b","type":"User"},"path":"src/api/session.ts","line":28,"side":"RIGHT","original_line":28,"position":12,"in_reply_to_id":null,
   "body":"nit: `r`보다 `refreshRes`가 읽기 쉬울 것 같아요."}
]
```

## gh api repos/acme-sre/web-ui/pulls/57/reviews

```json
[
  {"id":501,"user":{"login":"reviewer-a"},"state":"CHANGES_REQUESTED","commit_id":"9f3c2e1","body":""},
  {"id":502,"user":{"login":"reviewer-b"},"state":"COMMENTED","commit_id":"9f3c2e1","body":""}
]
```

## gh api repos/acme-sre/web-ui/issues/57/comments

```json
[]
```

## gh api graphql (reviewThreads, first: 50)

```json
{"data":{"repository":{"pullRequest":{"reviewThreads":{"nodes":[
  {"id":"PRRT_kwA1","isResolved":false,"isOutdated":false,"comments":{"nodes":[{"databaseId":9001}]}},
  {"id":"PRRT_kwA2","isResolved":false,"isOutdated":false,"comments":{"nodes":[{"databaseId":9002}]}},
  {"id":"PRRT_kwA3","isResolved":false,"isOutdated":false,"comments":{"nodes":[{"databaseId":9003}]}}
],"pageInfo":{"hasNextPage":false}}}}}}
```

## gh pr view 57 --json reviewRequests

```json
{"reviewRequests":[]}
```
