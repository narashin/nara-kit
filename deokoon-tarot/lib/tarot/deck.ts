import type { Card, Suit } from "@/lib/types";

const MAJOR_ARCANA: { number: number; name_ko: string; name_en: string }[] = [
  { number: 0, name_ko: "바보", name_en: "The Fool" },
  { number: 1, name_ko: "마법사", name_en: "The Magician" },
  { number: 2, name_ko: "여사제", name_en: "The High Priestess" },
  { number: 3, name_ko: "여황제", name_en: "The Empress" },
  { number: 4, name_ko: "황제", name_en: "The Emperor" },
  { number: 5, name_ko: "교황", name_en: "The Hierophant" },
  { number: 6, name_ko: "연인", name_en: "The Lovers" },
  { number: 7, name_ko: "전차", name_en: "The Chariot" },
  { number: 8, name_ko: "힘", name_en: "Strength" },
  { number: 9, name_ko: "은둔자", name_en: "The Hermit" },
  { number: 10, name_ko: "운명의 수레바퀴", name_en: "Wheel of Fortune" },
  { number: 11, name_ko: "정의", name_en: "Justice" },
  { number: 12, name_ko: "매달린 사람", name_en: "The Hanged Man" },
  { number: 13, name_ko: "죽음", name_en: "Death" },
  { number: 14, name_ko: "절제", name_en: "Temperance" },
  { number: 15, name_ko: "악마", name_en: "The Devil" },
  { number: 16, name_ko: "탑", name_en: "The Tower" },
  { number: 17, name_ko: "별", name_en: "The Star" },
  { number: 18, name_ko: "달", name_en: "The Moon" },
  { number: 19, name_ko: "태양", name_en: "The Sun" },
  { number: 20, name_ko: "심판", name_en: "Judgement" },
  { number: 21, name_ko: "세계", name_en: "The World" },
];

const SUITS: { suit: Suit; name_ko: string; name_en: string }[] = [
  { suit: "wands", name_ko: "완드", name_en: "Wands" },
  { suit: "cups", name_ko: "컵", name_en: "Cups" },
  { suit: "swords", name_ko: "소드", name_en: "Swords" },
  { suit: "pentacles", name_ko: "펜타클", name_en: "Pentacles" },
];

const RANKS: { number: number; slug: string; name_ko: string; name_en: string }[] = [
  { number: 1, slug: "ace", name_ko: "에이스", name_en: "Ace" },
  { number: 2, slug: "2", name_ko: "2", name_en: "Two" },
  { number: 3, slug: "3", name_ko: "3", name_en: "Three" },
  { number: 4, slug: "4", name_ko: "4", name_en: "Four" },
  { number: 5, slug: "5", name_ko: "5", name_en: "Five" },
  { number: 6, slug: "6", name_ko: "6", name_en: "Six" },
  { number: 7, slug: "7", name_ko: "7", name_en: "Seven" },
  { number: 8, slug: "8", name_ko: "8", name_en: "Eight" },
  { number: 9, slug: "9", name_ko: "9", name_en: "Nine" },
  { number: 10, slug: "10", name_ko: "10", name_en: "Ten" },
  { number: 11, slug: "page", name_ko: "페이지", name_en: "Page" },
  { number: 12, slug: "knight", name_ko: "나이트", name_en: "Knight" },
  { number: 13, slug: "queen", name_ko: "퀸", name_en: "Queen" },
  { number: 14, slug: "king", name_ko: "킹", name_en: "King" },
];

const imagePath = (id: string): string => `/cards/rws-${id}.png`;

export const DECK: Card[] = [
  ...MAJOR_ARCANA.map((m): Card => {
    const id = `major-${m.number}`;
    return {
      id,
      name_ko: m.name_ko,
      name_en: m.name_en,
      arcana: "major",
      number: m.number,
      image: imagePath(id),
    };
  }),
  ...SUITS.flatMap((s) =>
    RANKS.map((r): Card => {
      const id = `${s.suit}-${r.slug}`;
      return {
        id,
        name_ko: `${s.name_ko} ${r.name_ko}`,
        name_en: `${r.name_en} of ${s.name_en}`,
        arcana: "minor",
        suit: s.suit,
        number: r.number,
        image: imagePath(id),
      };
    }),
  ),
];

export const DECK_BY_ID: Record<string, Card> = Object.fromEntries(
  DECK.map((c) => [c.id, c]),
);

export function getCard(id: string): Card | undefined {
  return DECK_BY_ID[id];
}
