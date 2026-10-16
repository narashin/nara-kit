export function exportCsv(rows: string[][]): string {
  return rows.map((r) => r.join(",")).join("\n");
}

export function exportTsv(rows: string[][]): string {
  return rows.map((r) => r.join("\t")).join("\n");
}
