import OpenAI from "openai";

let client: OpenAI | null = null;

export function getOpenAI(): OpenAI {
  if (client) return client;
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) throw new Error("OPENAI_API_KEY가 없습니다");
  client = new OpenAI({ apiKey });
  return client;
}

export const MODELS = {
  default: "gpt-4o-mini", // 기본
  fallback: "gpt-4o", // 매핑 어려운 free question 등
} as const;
