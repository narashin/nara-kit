export interface Item { id: string; category: string; score: number }
export interface History { viewed: string[]; purchased: string[] }

export function recommend(items: Item[], history: History, limit = 10): Item[] {
  if (limit <= 0) return [];
  const seen = new Set([...history.viewed, ...history.purchased]);
  const favorite = topCategory(items, history);
  return items
    .filter((i) => !seen.has(i.id))
    .map((i) => ({ ...i, score: i.category === favorite ? i.score * 1.5 : i.score }))
    .sort((a, b) => b.score - a.score || a.id.localeCompare(b.id))
    .slice(0, limit);
}

function topCategory(items: Item[], history: History): string | undefined {
  const counts = new Map<string, number>();
  for (const id of history.purchased) {
    const c = items.find((i) => i.id === id)?.category;
    if (c) counts.set(c, (counts.get(c) ?? 0) + 1);
  }
  return [...counts.entries()].sort((a, b) => b[1] - a[1])[0]?.[0];
}
