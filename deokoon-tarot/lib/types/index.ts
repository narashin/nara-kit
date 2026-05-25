export type CategoryId =
  | "compat"
  | "encounter"
  | "evangelism"
  | "ticketing"
  | "stamina"
  | "comeback"
  | "onboarding"
  | "free";

export type Arcana = "major" | "minor";
export type Suit = "wands" | "cups" | "swords" | "pentacles";

export interface Card {
  id: string; // "major-0", "wands-ace", "cups-king"
  name_ko: string;
  name_en: string;
  arcana: Arcana;
  suit?: Suit; // minor only
  number?: number; // major 0-21 / minor 1-14 (11=page,12=knight,13=queen,14=king)
  image: string; // "/cards/rws-major-0.png"
}

export interface DrawnCard {
  id: string;
  name: string; // name_ko snapshot at draw time
  reversed: boolean;
  position: string; // spread position label
}

export interface CardMeaning {
  upright: string;
  reversed: string;
}

export type CardMeanings = Record<string, CardMeaning>;

export interface SpreadPosition {
  key: string;
  label: string;
}

export interface Spread {
  category: CategoryId;
  cardCount: number;
  positions: SpreadPosition[];
}

export type LlmStatus = "success" | "failed" | "pending_retry";

export interface Reading {
  id: string;
  category: CategoryId;
  questionText?: string; // free only
  mappedCategory?: CategoryId; // free → mapped category
  mappingConfidence?: number; // 0.0-1.0
  biasSnapshot: string; // 최애 at draw time
  extraInput?: string; // 영업 대상 / 공연명 / 입덕 후보 등
  cards: DrawnCard[];
  ruleBasedSummary: string; // offline fallback 본문
  llmInterpretation?: string | null; // null on failure
  llmStatus: LlmStatus;
  createdAt: number; // epoch ms
}

export interface UserProfile {
  googleId: string;
  displayName: string;
  email: string;
  bias: string; // 최애
  biasUpdatedAt: number;
  createdAt: number;
  lastSeenAt: number;
}

export interface QuotaDoc {
  count: number;
  lastUsedAt: number;
}

export interface QuotaStatus {
  used: number;
  limit: number;
  remaining: number;
  resetsAt: number; // epoch ms of next KST midnight
}
