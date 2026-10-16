# git state (already captured; no repo in this run)

## git branch --show-current

```
feature/PROJ-111-retry-limit
```

## git diff --cached --stat

```
 src/api/session.ts      | 6 +++++-
 src/api/session.test.ts | 9 +++++++++
 2 files changed, 14 insertions(+), 1 deletion(-)
```

## git diff --cached

```diff
--- a/src/api/session.ts
+++ b/src/api/session.ts
@@ -18,7 +18,11 @@ export async function fetchWithSession(url: string): Promise<Response> {
   let res = await http.get(url, { headers: authHeaders() });
-  while (res.status === 401) {
+  let attempts = 0;
+  while (res.status === 401 && attempts < MAX_REFRESH) {
     await refreshToken();
     res = await http.get(url, { headers: authHeaders() });
+    attempts += 1;
   }
   return res;
 }
--- a/src/api/session.test.ts
+++ b/src/api/session.test.ts
@@ -40,3 +40,12 @@ describe("fetchWithSession", () => {
+  it("stops refreshing after MAX_REFRESH attempts", async () => {
+    mockHttp.always401();
+    const res = await fetchWithSession("/orders");
+    expect(res.status).toBe(401);
+    expect(refreshCalls()).toBe(MAX_REFRESH);
+  });
 });
```

## git log --oneline -5

```
3f0d8e1 PROJ-108 fix: Session 갱신 실패 시 로그인 화면으로 보낸다
2a91c4d PROJ-104 feat: Order 리포트에 월 합계를 더한다
```
