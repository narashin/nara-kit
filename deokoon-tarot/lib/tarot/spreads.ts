import type { CategoryId, Spread } from "@/lib/types";

const three = (
  category: CategoryId,
  labels: readonly [string, string, string],
): Spread => ({
  category,
  cardCount: 3,
  positions: labels.map((label, i) => ({ key: `p${i + 1}`, label })),
});

export const SPREADS: Record<CategoryId, Spread> = {
  // 나3 + 최애3 = 6장. 케미는 해석 단계에서 종합.
  compat: {
    category: "compat",
    cardCount: 6,
    positions: [
      { key: "me_heart", label: "나 — 마음" },
      { key: "me_attitude", label: "나 — 태도" },
      { key: "me_wish", label: "나 — 바람" },
      { key: "bias_heart", label: "최애 — 마음" },
      { key: "bias_attitude", label: "최애 — 태도" },
      { key: "bias_toward", label: "최애 — 너를 향해" },
    ],
  },
  encounter: three("encounter", ["계기", "흐름", "결과"]),
  evangelism: three("evangelism", ["대상의 마음", "접근법", "성공 가능성"]),
  ticketing: three("ticketing", ["운의 흐름", "변수", "결과"]),
  stamina: three("stamina", ["현재 체력", "주의점", "회복법"]),
  comeback: three("comeback", ["최애의 현재", "준비 과정", "다가올 소식"]),
  onboarding: three("onboarding", ["첫인상", "끌림의 이유", "입덕 후 흐름"]),
  free: three("free", ["과거", "현재", "미래"]),
};

export const CATEGORY_LABELS: Record<CategoryId, string> = {
  compat: "최애와의 케미",
  encounter: "만남운",
  evangelism: "영업운",
  ticketing: "티켓팅운",
  stamina: "덕질 체력",
  comeback: "컴백/근황",
  onboarding: "입덕운",
  free: "자유 질문",
};

export function getSpread(category: CategoryId): Spread {
  return SPREADS[category];
}
