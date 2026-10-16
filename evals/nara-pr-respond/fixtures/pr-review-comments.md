# PR fixture: acme-sre/web-ui#58 "feat: show order totals on the dashboard"

GitHub is not reachable in this run. Each section below is the verbatim output the
named `gh` call returned. The PR branch is checked out; the diff below is its full change.

## gh pr view 58 --json number,url,headRefName,baseRefName,author,headRefOid

```json
{"number":58,"url":"https://github.com/acme-sre/web-ui/pull/58","headRefName":"feature/PROJ-63-order-totals","baseRefName":"main","author":{"login":"dev"},"headRefOid":"4b7d1a0"}
```

## git diff main...HEAD

```diff
--- a/src/dashboard/OrderTotals.tsx
+++ b/src/dashboard/OrderTotals.tsx
@@ -1,6 +1,18 @@
 import { useOrders } from "../api/orders";
+import { formatWon } from "../format";
 
 export function OrderTotals() {
-  return null;
+  const { data } = useOrders();
+  const sum = data.items.reduce((acc, o) => acc + o.total, 0);
+  const avg = sum / data.items.length;
+  return (
+    <section>
+      <h2>주문 합계</h2>
+      <p>{formatWon(sum)}</p>
+      <p>평균 {formatWon(avg)}</p>
+    </section>
+  );
 }
```

`useOrders()` returns `{ data: undefined }` until the first fetch resolves (src/api/orders.ts:12).
Other dashboard widgets read totals from `useDashboardSummary()`, which caches server-side aggregates.

## gh api repos/acme-sre/web-ui/pulls/58/comments (unresolved inline threads)

```json
[
  {"id":8101,"path":"src/dashboard/OrderTotals.tsx","line":7,"user":{"login":"reviewer-a"},
   "body":"`data` is undefined on first render, so `data.items` throws. This crashes the dashboard."},
  {"id":8102,"path":"src/dashboard/OrderTotals.tsx","line":8,"user":{"login":"reviewer-a"},
   "body":"nit: `sum` -> `totalWon` would read better next to `avg`."},
  {"id":8103,"path":"src/dashboard/OrderTotals.tsx","line":6,"user":{"login":"reviewer-b"},
   "body":"Should this compute totals client-side at all? Every other widget uses `useDashboardSummary()`. I'd rather not have two sources of truth for order totals, but it's a product call."}
]
```
