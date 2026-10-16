# gh outputs for the current PR (GitHub not reachable in this run)

## gh pr view --json number,title,baseRefName,headRefName,headRefOid

```json
{"number":91,"title":"feat(report): CSV 내보내기 버튼 추가 (PROJ-77)","baseRefName":"main","headRefName":"feature/PROJ-77-export-csv","headRefOid":"9c1e2ab"}
```

## git merge-base main HEAD

```
3f0d8e1
```

## git diff 3f0d8e1...9c1e2ab

```diff
--- a/src/report/OrderReport.tsx
+++ b/src/report/OrderReport.tsx
@@ -12,6 +12,11 @@ export function OrderReport({ orders }: Props) {
   return (
     <section>
       <h2>주문 리포트</h2>
+      <button onClick={() => download(toCsv(orders), "orders.csv")}>CSV 내보내기</button>
       <OrderTable orders={orders} />
     </section>
   );
+}
+
+function toCsv(orders: Order[]): string {
+  return ["id,total", ...orders.map((o) => `${o.id},${o.total}`)].join("\n");
 }
```
