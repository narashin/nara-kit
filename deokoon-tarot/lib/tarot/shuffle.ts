import type { DrawnCard } from "@/lib/types";
import { DECK } from "./deck";

type Rng = () => number;

function fisherYates<T>(arr: readonly T[], rng: Rng): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

// 정·역방향 모두 무작위. rng 주입 가능(셔플 시드 재현용), 기본은 Math.random.
export function drawCards(
  count: number,
  positions: readonly string[],
  rng: Rng = Math.random,
): DrawnCard[] {
  return fisherYates(DECK, rng)
    .slice(0, count)
    .map((card, i) => ({
      id: card.id,
      name: card.name_ko,
      reversed: rng() < 0.5,
      position: positions[i] ?? `위치 ${i + 1}`,
    }));
}
