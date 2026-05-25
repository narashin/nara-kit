# Implementation Plan: 덕운 (Deokoon) — Fan Tarot PWA

- App name: **덕운 (Deokoon)** — 덕질 + 운(運)
- Repo: **`narashin/deokoon-tarot`** (Private)
- Based on: docs/requirements.md, docs/gap.md
- Generated: 2026-05-24 / Decisions finalized: 2026-05-25
- Stack confirmed: Next.js 16 App Router + Vercel + Firebase (Auth/Firestore) + OpenAI + Rider-Waite-Smith

## 1. 아키텍처 개요

```
[Browser PWA]
   ├─ Next.js 16 (App Router, RSC + Client Components)
   ├─ Tailwind CSS + shadcn/ui
   ├─ Firebase Auth (Google OAuth) — client SDK
   ├─ next-pwa (service worker + manifest)
   └─ IndexedDB (셔플 시드 / 오프라인 카드 의미 캐시)
                │
                ▼ (Firebase ID Token)
[Next.js API Routes — Vercel Edge/Node]
   ├─ Firebase Admin SDK (Firestore 서버 R/W, ID Token 검증)
   ├─ OpenAI SDK (서버 키 보관, 사용자 노출 X)
   ├─ Quota 카운터 로직 (KST 0시 리셋)
   └─ 룰베이스 78장 의미 DB (JSON) → LLM 톤 입히기 파이프라인
                │
                ▼
[Firestore] users/{uid}, /readings/{id}, /quota/{ymd}
[OpenAI]    gpt-4o-mini (기본) / gpt-4o (fallback)
```

**핵심 결정**: LLM 키는 서버에만. 클라이언트는 Firebase ID Token으로 Next.js API 호출 → 서버가 검증 후 OpenAI 호출. 키 유출 0.

## 2. 결정 요약 (Confirmed)

| 축 | 결정 | 근거 |
|---|---|---|
| 코드 거주 | 신규 repo `narashin/deokoon-tarot` (Private) | 사용자 선택 |
| 프론트 스택 | Next.js 16 App Router + TS + Tailwind + shadcn/ui | 사용자 + PWA·Firebase·Vercel 통합 우수 |
| 정·역방향 | 정·역 모두 무작위 | 추천 채택 — 해석 다양성 |
| 스프레드 | compat 6장 (나3+최애3) / 그 외 7개 카테고리 3장 / free fallback 3장 (과거·현재·미래) | 추천 채택 |
| LLM 모델 | gpt-4o-mini 기본 / 매핑 어려운 free question만 gpt-4o | 비용·정확도 균형 |
| 자유 질문 매핑 | 프롬프트에 confidence (0.0–1.0) 출력 요구, **0.6 미만 fallback** ([UNVERIFIED] — Wave 3 튜닝) | 합리적 기본값 |
| 톤 | 반말 + 따뜻함 + 이모지 절제(✨🔮 정도) ([UNVERIFIED] — Wave 5 튜닝) | fan 정서 친화 |
| 결과 본문 | 블록당 3-5문장 (300-500자) ([UNVERIFIED] — Wave 5) | 정성스러움 vs 읽기 부담 균형 |
| 카드 자산 | Wikimedia Commons의 Rider-Waite-Smith 1909 (Public Domain) PNG | 라이선스 0원 |
| 언어 | 한국어 only (MVP) — EN/JP는 차기 | 스코프 컷 |

## 3. 디렉토리 구조 (신규 repo)

```
deokoon-tarot/
├── app/
│   ├── layout.tsx              # 루트 (theme, PWA manifest link, AuthProvider)
│   ├── page.tsx                # 랜딩 (로그인 안 됐으면 /login redirect)
│   ├── login/page.tsx          # Google OAuth 진입
│   ├── onboarding/page.tsx     # 최애 입력 폼 (FR-1)
│   ├── home/page.tsx           # 8 카테고리 그리드 + 잔여 횟수 표시
│   ├── reading/
│   │   ├── [category]/page.tsx # 추가 입력(영업 대상 등) + 셔플 + 카드 뽑기
│   │   └── result/[id]/page.tsx
│   ├── history/page.tsx        # 히스토리 리스트
│   ├── settings/page.tsx       # 최애 변경, 로그아웃
│   └── api/
│       ├── reading/route.ts          # POST: 한도 체크 → 셔플 → 룰베이스 → LLM → 저장
│       ├── reading/[id]/route.ts     # GET: 단건 조회 (소유자 검증)
│       ├── history/route.ts          # GET: 페이지네이션
│       ├── quota/route.ts            # GET: 오늘 잔여 횟수
│       ├── free-question/route.ts    # POST: 자연어 → 카테고리 매핑
│       └── profile/route.ts          # PATCH: 최애 변경
├── components/
│   ├── ui/                     # shadcn/ui base (button, card, dialog…)
│   ├── tarot/
│   │   ├── ShuffleDeck.tsx     # 셔플 애니메이션 (스와이프/탭)
│   │   ├── CardReveal.tsx      # 카드 노출 + 정·역방향 회전
│   │   ├── SpreadLayout.tsx    # 3장/6장 레이아웃
│   │   └── ResultBlock.tsx     # "나 / 최애 / 케미" 등 3·6블록 표시
│   ├── auth/
│   │   ├── GoogleLoginButton.tsx
│   │   └── AuthGuard.tsx       # 미인증 → /login redirect
│   └── shared/QuotaBadge.tsx   # 잔여 횟수 + 리셋 시각
├── lib/
│   ├── firebase/
│   │   ├── client.ts           # initializeApp (client SDK)
│   │   ├── admin.ts            # initializeAdmin (server SDK, env 키)
│   │   └── auth-server.ts      # ID Token 검증 helper
│   ├── tarot/
│   │   ├── deck.ts             # 78장 카드 메타 (id, name_ko, name_en, suit, number)
│   │   ├── meanings.ts         # upright/reversed 의미 로더 (data/card-meanings.json)
│   │   ├── spreads.ts          # 카테고리 → 스프레드 정의 (cardCount, positions[])
│   │   ├── shuffle.ts          # Fisher-Yates + 정·역 무작위
│   │   └── interpret.ts        # 룰베이스 요약 → 카테고리별 LLM 프롬프트
│   ├── openai/
│   │   ├── client.ts           # SDK init
│   │   └── prompts/            # 카테고리별 프롬프트 템플릿
│   │       ├── compat.ts
│   │       ├── encounter.ts    # 실존/가상 톤 자동 분기 지시
│   │       ├── evangelism.ts
│   │       ├── ticketing.ts
│   │       ├── stamina.ts
│   │       ├── comeback.ts     # 주어가 최애임을 명시
│   │       ├── onboarding.ts
│   │       └── free-mapping.ts # 자유 질문 → 카테고리 분류 프롬프트
│   ├── quota/daily-limit.ts    # KST 0시 리셋 카운터 (Firestore 트랜잭션)
│   └── types/                  # TS types (Reading, User, Quota, Card, Spread…)
├── public/
│   ├── cards/                  # rws-{id}.png × 78 (정방향 원본, CSS로 회전)
│   ├── icons/                  # PWA 아이콘 (192/512/maskable)
│   └── manifest.json
├── data/
│   └── card-meanings.json      # 78장 한국어 의미 (upright/reversed)
├── firestore.rules
├── firestore.indexes.json
├── next.config.js              # next-pwa 설정
├── .env.local.example
└── README.md
```

## 4. Firestore 데이터 모델

```
users/{uid}
  googleId: string
  displayName: string
  email: string
  bias: string                    # 최애 (자유 텍스트, 1-50자)
  biasUpdatedAt: timestamp
  createdAt: timestamp
  lastSeenAt: timestamp

users/{uid}/readings/{readingId}
  category: "compat" | "encounter" | ... | "free"
  questionText: string?           # free 카테고리만
  mappedCategory: string?         # free → 매핑 결과 (AC-17)
  mappingConfidence: number?      # 0.0–1.0
  biasSnapshot: string            # 당시 최애 (AC-2 변경 대비)
  extraInput: string?             # 영업 대상/공연명/입덕 후보
  cards: [{ id, name, reversed, position }]
  ruleBasedSummary: string        # 카드별 의미 (오프라인 fallback용)
  llmInterpretation: string?      # 종합 해석 (실패 시 null)
  llmStatus: "success" | "failed" | "pending_retry"
  createdAt: timestamp

users/{uid}/quota/{ymd}           # 문서 ID = "20260524" (KST)
  count: number                   # 0-5
  lastUsedAt: timestamp
```

**Security Rules 요지**:
- `users/{uid}/**` — `request.auth.uid == uid` 만 R/W
- `quota` — 클라이언트 직접 쓰기 금지 (서버 API만), 클라이언트는 read만

## 5. API Surface

| Endpoint | Method | 동작 | AC |
|---|---|---|---|
| `/api/profile` | POST | 최초 최애 저장 (onboarding) | AC-1 |
| `/api/profile` | PATCH | 최애 변경 | AC-2 |
| `/api/reading` | POST | quota check → shuffle → meanings → LLM → save | AC-3, AC-4, AC-5, AC-10~17 |
| `/api/reading/[id]` | GET | 단건 조회 (소유자만) | AC-8 (상세 보기) |
| `/api/history` | GET | 시간역순 리스트 (cursor pagination) | AC-8, AC-9 |
| `/api/quota` | GET | 오늘 잔여 횟수 + 리셋 시각 | AC-21, AC-22 (UI 표시) |
| `/api/free-question` | POST | 자유 질문 → 카테고리 매핑 분석 | AC-17, AC-18 |

## 6. Task Waves (실행 순서)

### Wave 0 — 인프라 셋업 (반나절~1일)
- [ ] GitHub repo `narashin/deokoon-tarot` 생성 (Private, 라이선스 없음)
- [ ] `npx create-next-app@latest` (TS, Tailwind, App Router, ESLint)
- [ ] shadcn/ui init + 기본 컴포넌트 추가
- [ ] Firebase 프로젝트 생성 + Auth(Google) / Firestore 활성화
- [ ] OpenAI API 키 발급 + Vercel 프로젝트 환경변수 등록
- [ ] Vercel 연결 + 자동 배포 hello world 확인
- [ ] `next-pwa` 설치 + `manifest.json` + 아이콘
- [ ] Rider-Waite 78장 이미지 수집 (Wikimedia) → `public/cards/`
- [ ] `data/card-meanings.json` 스켈레톤 (78장 × upright/reversed 한국어 1-2줄)

### Wave 1 — 인증 + 프로필 + 한도 (1-2일) [FR-15, FR-1, FR-16]
- [ ] Firebase client/admin SDK 연결 + ID Token flow
- [ ] `GoogleLoginButton`, `AuthGuard`, `AuthProvider`
- [ ] `/onboarding` 최애 입력 폼 → `POST /api/profile`
- [ ] `/settings` 최애 변경 → `PATCH /api/profile`
- [ ] `lib/quota/daily-limit.ts` (KST 0시 리셋, Firestore 트랜잭션)
- [ ] `/api/quota` + `QuotaBadge` 컴포넌트
- [ ] Firestore Security Rules 1차 작성
- [ ] **검증**: AC-1, AC-2, AC-19, AC-20, AC-21, AC-22

### Wave 2 — 코어 루프 (compat 카테고리 E2E) (2-3일) [FR-2, FR-3, FR-7]
- [ ] `data/card-meanings.json` 컴팩트 완성 (78×2 한국어 의미)
- [ ] `lib/tarot/deck.ts` + `meanings.ts` + `shuffle.ts` (정·역 무작위)
- [ ] `lib/tarot/spreads.ts` — compat 6장 위치 정의
- [ ] `lib/openai/prompts/compat.ts` 프롬프트 v1
- [ ] `lib/tarot/interpret.ts` — 룰베이스 요약 → LLM 호출 파이프라인
- [ ] `POST /api/reading` (quota check → shuffle → meanings → LLM → save)
- [ ] `ShuffleDeck` + `CardReveal` + `SpreadLayout` + `ResultBlock`
- [ ] `/reading/compat` 페이지 + `/reading/result/[id]` 페이지
- [ ] LLM 실패 시 룰베이스 fallback + 배너 (AC-5)
- [ ] **검증**: AC-3, AC-4, AC-5, AC-10

### Wave 3 — 카테고리 확장 (3-5일) [FR-8 ~ FR-14]
- [ ] `encounter` (프롬프트에 "최애가 실존 인물인지 판단 후 톤 분기" 지시) — AC-11
- [ ] `evangelism` (영업 대상 자유 텍스트 추가 입력) — AC-12
- [ ] `ticketing` (공연명 선택 입력) — AC-13
- [ ] `stamina` — AC-14
- [ ] `comeback` (주어 = 최애, 사용자 본인 X 프롬프트 명시) — AC-15
- [ ] `onboarding` (입덕 후보 자유 텍스트) — AC-16
- [ ] `free` — `POST /api/free-question` 매핑 + confidence < 0.6 fallback 3장 — AC-17, AC-18
- [ ] 매핑 라벨 ("→ N 스프레드로 해석") UI

### Wave 4 — 보조 P1 (1-2일) [FR-4, FR-5, FR-6]
- [ ] `/history` 페이지 (cursor pagination + 빈 상태) — AC-8, AC-9
- [ ] PWA 설치 안내 배너 + standalone 모드 검증 (Chrome/Safari) — AC-6
- [ ] Service worker 캐싱 전략: `card-meanings.json` + 카드 이미지 + 룰베이스 fallback — AC-7
- [ ] 오프라인 시 LLM 호출 skip + 배너

### Wave 5 — 폴리시 + 배포 (1-2일)
- [ ] 톤 가이드 finalize (반말/이모지 정도, 결과 길이) — 실제 결과 5개 뽑아 검토
- [ ] 에러 핸들링 (rate limit, network, Firestore 권한 등) + 토스트
- [ ] Firestore Rules 정밀화 + 인덱스 등록
- [ ] `code-review` 실행 → fix
- [ ] `reflect` → ADR 후보 (LLM 비용 한도, 카드 정·역 정책 등 결정 기록)
- [ ] 프로덕션 배포 + 모바일 디바이스 실기 PWA 설치 테스트

**총 추정**: 8-13 영업일 (혼자, 디자인 외주 없이, 익숙도 보통 가정)

## 7. 위험 요소

| 위험 | 영향 | 완화 |
|---|---|---|
| OpenAI 비용 폭증 | $$$ | Wave 1에 quota 먼저 구현 (FR-16 P0 이유) |
| LLM 톤이 "정성스럽지 않음" | UX 핵심 가치 손상 | Wave 5 톤 가이드 finalize 단계에서 5개 결과 수동 검토, prompt 튜닝 반복 |
| 자유 질문 매핑 부정확 | AC-17/18 실패 | confidence threshold + fallback 3장 + UI에 매핑 라벨 노출로 사용자 기대 관리 |
| Next.js 16 RSC vs Firebase client SDK 충돌 | dev 지연 | Auth/Firestore client 호출은 Client Component로 격리. Server는 Admin SDK만 |
| 라이더-웨이트 이미지 품질 (Wikimedia 해상도) | 시각 quality 손상 | 1024px+ 버전 우선 수집, 부족하면 자체 트레이싱 (PD 원본 기반) |
| KST 0시 리셋 타임존 버그 | quota 잘못 동작 | UTC 저장 + 표시만 KST 변환, 문서 ID = KST YYYYMMDD |

## 8. Pre-execution Gate → 핸드오프 (Path A 확정)

**환경 제약**: 현 세션(nara-kit)의 GitHub MCP는 `narashin/nara-kit`에만 접근 가능 → 신규 repo 생성·푸시 불가. 따라서 새 세션으로 핸드오프하는 Path A로 진행.

**핸드오프 절차**:
1. 사용자: GitHub에서 Private repo `narashin/deokoon-tarot` 생성 (빈 repo — README/라이선스 자동생성 OFF 권장)
2. 사용자: 그 repo에서 새 Claude Code 세션 시작
3. 새 세션: 이 3개 spec 문서(requirements/gap/plan)를 가져옴 (아래 §10 방법)
4. 새 세션: Wave 0부터 진행 + `docs/implementation-notes.md` 자동 생성

## 9. 결정 사항 (Finalized 2026-05-25)

- [x] **앱 이름** — **덕운 (Deokoon)** = 덕질 + 운(運)
- [x] **repo 이름** — **`narashin/deokoon-tarot`**
- [x] **실행 방식** — Path A: 신규 repo + 새 세션 핸드오프
- [x] **라이선스** — Private repo, 라이선스 파일 없음 (비공개)

## 10. 새 세션에서 spec 문서 가져오는 법

이 3개 문서는 nara-kit의 feature 브랜치 `claude/tarot-fan-compatibility-app-snKno`의 `docs/`에 영속화돼 있음 (`git add -f`로 .gitignore 우회 커밋). 새 세션(deokoon-tarot repo)에서 가져오는 옵션:

- **수동 복사 (가장 단순)**: nara-kit 브랜치의 `docs/requirements.md`, `docs/gap.md`, `docs/plan.md`를 로컬에서 복사해 새 repo `docs/`에 붙여넣기
- **새 세션에게 위임**: 새 세션에 "nara-kit repo의 `claude/tarot-fan-compatibility-app-snKno` 브랜치 `docs/`에서 3개 문서를 가져와 이 repo `docs/`에 넣고 Wave 0부터 시작" 지시 (새 세션이 nara-kit 접근 권한을 가질 경우)
