// data/card-meanings.json 스켈레톤 생성기.
// deck.ts의 id 스킴과 동일하게 78장 키를 만들어 upright/reversed 빈 값으로 채운다.
// 의미 본문은 Wave 2에서 채운다. 재실행 시 기존 비어있지 않은 값은 보존한다.
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUT = resolve(__dirname, "../data/card-meanings.json");

const suits = ["wands", "cups", "swords", "pentacles"];
const ranks = ["ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "page", "knight", "queen", "king"];

const ids = [];
for (let n = 0; n <= 21; n++) ids.push(`major-${n}`);
for (const s of suits) for (const r of ranks) ids.push(`${s}-${r}`);

const existing = existsSync(OUT) ? JSON.parse(readFileSync(OUT, "utf8")) : {};

const out = {};
for (const id of ids) {
  const prev = existing[id] ?? {};
  out[id] = {
    upright: prev.upright ?? "",
    reversed: prev.reversed ?? "",
  };
}

mkdirSync(dirname(OUT), { recursive: true });
writeFileSync(OUT, JSON.stringify(out, null, 2) + "\n", "utf8");
console.log(`wrote ${Object.keys(out).length} cards → ${OUT}`);
