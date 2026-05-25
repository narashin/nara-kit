# Implementation Notes — 덕운 (Deokoon)

> 실행 중 누적 기록. SoT는 `docs/plan.md`. Wave 진행/결정/편차를 여기 적는다.

## 환경 / 거주 (중요)

- 이 코드는 현재 **`narashin/nara-kit`의 feature 브랜치 `claude/tarot-fan-compatibility-app-snKno`** 안 `deokoon-tarot/` 하위폴더에 있다.
  - 이유: 클라우드 세션의 GitHub MCP가 nara-kit에만 접근 가능 → 신규 repo 생성 불가. push 가능한 유일한 곳이라 임시 거주.
  - **추출 방법** (독립 repo로 옮길 때):
    ```bash
    git clone -b claude/tarot-fan-compatibility-app-snKno \
      https://github.com/narashin/nara-kit.git /tmp/x
    cp -r /tmp/x/deokoon-tarot/ ./deokoon-tarot && cd deokoon-tarot
    rm -rf ../x && git init && git add -A && git commit -m "init: 덕운 Wave 0"
    ```
- 부모 nara-kit `.gitignore`가 `docs/`를 무시 → `deokoon-tarot/docs/`도 매칭됨. 이 폴더 커밋 시 `git add -f docs/` 필요.

## Wave 0 — 인프라 셋업 ✅ (2026-05-25)

| 항목 | 상태 | 비고 |
|---|---|---|
| `create-next-app` | ✅ | Next.js **16.2.6** + React 19.2.4 + TS + Tailwind v4 + ESLint, App Router, src 디렉토리 없음 |
| 디렉토리 구조 | ✅ | plan §3 구조대로 app/components/lib/data/scripts/public |
| `lib/types` | ✅ | Card/DrawnCard/Reading/UserProfile/Quota/Spread 등 (no `any`) |
| `lib/tarot/deck.ts` | ✅ | 78장 프로그래매틱 생성 (major-0..21, {suit}-{ace..king}) |
| `lib/tarot/shuffle.ts` | ✅ | Fisher-Yates + 정·역 무작위, rng 주입 가능 |
| `lib/tarot/spreads.ts` | ✅ | compat 6장(나3+최애3) / 나머지 7개 3장 + CATEGORY_LABELS |
| `lib/firebase/{client,admin,auth-server}.ts` | ✅ | client SDK + lazy admin(import-time throw 회피) + ID Token 검증 |
| `lib/openai/client.ts` | ✅ | lazy init, MODELS(default gpt-4o-mini / fallback gpt-4o) |
| `.env.local.example` | ✅ | Firebase client/admin + OpenAI + 앱 설정 |
| `data/card-meanings.json` | ✅ (스켈레톤) | 78장 전체 키, upright/reversed 빈 값. `scripts/gen-meanings.mjs`로 생성/재생성 |
| PWA manifest + 아이콘 | ⚠️ 부분 | `public/manifest.json` + SVG 아이콘(`icon.svg`/`icon-maskable.svg`). layout에 metadata.manifest + viewport.themeColor |
| 랜딩/로그인 페이지 | ✅ | `/` 브랜드 히어로 + 카테고리 칩, `/login` Wave 1 stub |
| dev 서버 검증 | ✅ | `/`,`/login`,`/manifest.json` 모두 200, Turbopack 454ms, 로그 클린 |

### Wave 0 편차 (plan 대비)

1. **GitHub repo 생성 스킵** — MCP 제약. nara-kit feature 브랜치 거주로 대체 (위 환경 섹션).
2. **PWA 아이콘 PNG → SVG** — 컨테이너에 이미지 생성 도구 없음. SVG 아이콘으로 대체(실동작). Lighthouse는 192/512 PNG 선호 → **Wave 5 폴리시에서 PNG 생성** (pwa-asset-generator 등).
3. **next-pwa 설치 스킵** — 클래식 next-pwa는 Next 16 App Router 미지원. Service Worker는 plan상 Wave 4 항목이므로, 그때 **Serwist(`@serwist/next`)**로 구현. Wave 0은 manifest+아이콘(설치 가능성 골격)까지만.
4. **Firebase/OpenAI/Vercel 실연동 보류** — 외부 계정·키 필요(사용자 몫). 코드·env 예시는 완비, placeholder로 빌드/부팅 검증.
5. **78장 카드 이미지 미수집** — Wikimedia 78개 다운로드는 repo 용량·시간 부담. deck.ts가 `/cards/rws-{id}.png` 경로를 가리키도록 준비만. 수집 스크립트/이미지는 Wave 1~2에서.

### 사용자가 직접 해야 할 외부 셋업 (Wave 1 전)

- [ ] Firebase 프로젝트 생성 → Authentication(Google) ON + Firestore 생성 → client config & service account 키 → `.env.local`
- [ ] OpenAI API 키 → `.env.local`
- [ ] (배포 시) Vercel 프로젝트 + 환경변수 등록, `npm i -g vercel`

## 다음 (Wave 1 — 인증 + 프로필 + 한도)

plan §6 Wave 1 참조. 선행: 위 Firebase/OpenAI 키 셋업.
