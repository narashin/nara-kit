# Reference screen — Coupons (already shipped in the back office)
#
# Fixture: the baseline the request refers to. Two sources, both localized into the
# project before the skill runs: the Figma frame (via MCP) and the BO page component.
# Every label on the shipped screen is English. The user talks about it in Korean.

## Figma frame `BO / Coupons / List` (localized text layers, top to bottom)

- Nav item (selected): `Coupons`
- Page title: `Coupons`
- Primary button (top right): `Create coupon`
- Filter bar: `Status` select (`All` / `Active` / `Paused` / `Expired`), search placeholder `Search by code`
- Table header, left to right: `Code` · `Discount` · `Status` · `Valid until` · `Actions`
- Row actions: `Edit`, `Pause`
- Empty state: `No coupons yet`

## BO code `src/pages/coupons/CouponsPage.tsx` (excerpt)

```tsx
const columns = [
  { key: 'code',       header: 'Code' },
  { key: 'discount',   header: 'Discount' },
  { key: 'status',     header: 'Status' },      // Active | Paused | Expired
  { key: 'validUntil', header: 'Valid until' },
  { key: 'actions',    header: 'Actions' },     // Edit, Pause
];

export function CouponsPage() {
  return (
    <Page title="Coupons" primaryAction={{ label: 'Create coupon', to: '/coupons/new' }}>
      <FilterBar statusLabel="Status" searchPlaceholder="Search by code" />
      <Table columns={columns} emptyText="No coupons yet" onRowClick={openCouponDetail} />
    </Page>
  );
}
```
