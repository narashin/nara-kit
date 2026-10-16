import * as exporters from "./export";

type Format = "Csv" | "Tsv";

export function runExport(format: Format, rows: string[][]): string {
  const fn = exporters[`export${format}`];
  return fn(rows);
}
