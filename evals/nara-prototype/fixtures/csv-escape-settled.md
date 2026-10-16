# web-ui CSV export (placeholder repo for evals)

<!-- EVAL-FAKE-DO-NOT-USE: placeholder codebase description for nara-prototype evals. -->

Question from the team: should CSV cells be escaped by (A) wrapping every cell in double quotes, or
(B) quoting only cells that contain a comma, quote, or newline and doubling inner quotes?

The repo already contains this, merged under PROJ-123 and used by every export:

`src/export/csv.ts`
```ts
// RFC 4180: quote only when needed, double inner quotes.
export function escapeCell(value: string): string {
  if (/[",\r\n]/.test(value)) {
    return `"${value.replace(/"/g, '""')}"`;
  }
  return value;
}
```

`src/export/csv.test.ts`
```ts
import { escapeCell } from "./csv";
it("leaves plain cells unquoted", () => expect(escapeCell("acme")).toBe("acme"));
it("quotes and doubles inner quotes", () => expect(escapeCell('a"b')).toBe('"a""b"'));
it("quotes cells with commas", () => expect(escapeCell("a,b")).toBe('"a,b"'));
it("quotes cells with newlines", () => expect(escapeCell("a\nb")).toBe('"a\nb"'));
```

`docs/adr/0007-csv-escaping.md` records option B as accepted, citing the downstream importer of
acme-sre, which rejects quoted numeric cells.
