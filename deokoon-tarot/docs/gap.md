# Gap Analysis

- Based on: docs/requirements.md
- Analyzed: 2026-05-24
- Score: **0/100**
- **Gate: ❌ blocked by P0 (13건)**

> **Greenfield 프로젝트**. 현 워킹 디렉토리는 `nara-kit` (Claude Code 플러그인 repo)로, 타로 앱 관련 코드 0건. 모든 FR/AC Missing. 본 gap.md는 **MVP 백로그 + P0/P1 우선순위**로 기능.

## Summary
- Total: 16 | Implemented: 0 | Partial: 0 | Missing: 16 | Agreed Exception: 0
- **P0 Missing (Critical): 13** ← hard gate
- P1 Missing (High): 3
- P2 Missing (Low): 0
- Verbatim 항목: 6 (UI 카피 — pre-scan에서 모두 0 hits, Missing 강제)
- Needs Confirm: 0 (Implemented 0건 → Forced Doubt Sampling 비대상)

## Critical (P0) Missing — 보완 1순위

| ID | Requirement | Why P0 | Verbatim grep |
|---|---|---|---|
| FR-1 | 최애 자유 텍스트 입력 + 프로필 저장 | golden path onboarding, AC-1 본문 | "최애" 0 hits |
| FR-2 | 카드 셔플·뽑기 인터랙션 | golden path UX, AC-3 본문 | — |
| FR-3 | 룰베이스 의미 + LLM 톤 종합 해석 | core value, AC-4/5 본문 | "온라인 복구 시 해석 업데이트" 0 hits |
| FR-7 | 궁합(compat) 카테고리 결과 | category golden path, AC-10 본문 | — |
| FR-8 | 마주침(encounter) 카테고리 + 실존/가상 톤 분기 | category golden path + 핵심 UX, AC-11 본문 | — |
| FR-9 | 영업(evangelism) 카테고리 + 영업 대상 입력 | category golden path, AC-12 본문 | — |
| FR-10 | 티켓팅(ticketing) 카테고리 + 공연명 입력 | category golden path, AC-13 본문 | — |
| FR-11 | 덕질 지속력(stamina) 카테고리 | category golden path, AC-14 본문 | — |
| FR-12 | 컴백/활동운(comeback) 카테고리 — 주어가 최애 | category golden path + 톤 규칙, AC-15 본문 | — |
| FR-13 | 입덕 적기(onboarding) 카테고리 + 후보 입력 | category golden path, AC-16 본문 | — |
| FR-14 | 자유 질문 → 카테고리 매핑 + fallback | category golden path + LLM 매핑 로직, AC-17/18 본문 | "일반 스프레드로 해석" 0 hits |
| FR-15 | Google OAuth 로그인 + 멀티디바이스 동기화 | 인증·데이터 무결성 (rubric §6 P0), AC-19/20 본문 | — |
| FR-16 | 일 5회 한도 + 초과 안내 + KST 0시 리셋 | 비용 폭증 방지 + business rule (P0), AC-21/22 본문 | "오늘 5회 모두 사용", "내일 다시 만나요" 0 hits |

## Detail

### Implemented
(없음)

### Partial
(없음)

### Missing

| ID | Priority | Requirement | Why P{0/1/2} | Notes |
|---|---|---|---|---|
| FR-1 | P0 | 최애 자유 텍스트 입력 + Firestore 프로필 저장 | golden path onboarding | 인증 후 첫 폼 |
| FR-2 | P0 | 카드 셔플·뽑기 인터랙션 (정·역방향 무작위) | golden path UX | 정·역 처리 정책은 Unknown |
| FR-3 | P0 | 룰베이스 카드 의미 + LLM 톤 종합 해석 | core value, AC-4/5 본문 | OpenAI API 연동 + 78장 의미 DB |
| FR-4 | P1 | PWA 홈화면 설치 + standalone 모드 | 보조 기능 (browser fallback 가능) | manifest.json + service worker |
| FR-5 | P1 | 오프라인 룰베이스 fallback + 안내 표시 | edge case (오프라인 자주 안 가는 경로) | service worker 캐싱 전략 |
| FR-6 | P1 | 결과 히스토리 시간역순 리스트 + 빈 상태 | 보조 기능 (첫 사용 블로킹 X) | Firestore 컬렉션 |
| FR-7 | P0 | 궁합(compat) — 나 3 + 최애 3 스프레드 | category golden path | 카드 수 [UNVERIFIED] |
| FR-8 | P0 | 마주침(encounter) — 시기/장소/가능성 + 실존/가상 톤 분기 | category golden path + 핵심 UX | LLM이 비실존 판단 시 톤 자동 조정 |
| FR-9 | P0 | 영업(evangelism) — 대상 수용성/매력 노출/성공 | category golden path | 영업 대상 자유 텍스트 추가 입력 |
| FR-10 | P0 | 티켓팅(ticketing) — 예매일/좌석/성공 | category golden path | 공연명 선택 입력 |
| FR-11 | P0 | 덕질 지속력(stamina) — 열정/권태기/극복 | category golden path | — |
| FR-12 | P0 | 컴백(comeback) — 활동성격/팬덤반응/응원 | category golden path + 주어 규칙 | 해석 주어 = 최애 (사용자 본인 X) |
| FR-13 | P0 | 입덕(onboarding) — 적기/양립성/만족도 | category golden path | 입덕 후보 자유 텍스트 추가 입력 |
| FR-14 | P0 | 자유 질문 → 8 카테고리 매핑 + 매핑 라벨 + fallback 3장 | category golden path + LLM 분류 로직 | 매핑 신뢰도 임계값 [UNVERIFIED] |
| FR-15 | P0 | Google OAuth + 멀티디바이스 동기화 + 거부 시 재시도 | 인증·데이터 무결성 | Firebase Auth |
| FR-16 | P0 | 일 5회 한도 + 초과 시 "내일 다시 만나요" + KST 0시 리셋 | 비용 + business rule | Firestore 카운터 (사용자/날짜) |

### Agreed Exceptions
(없음)

### Needs Confirm
(없음 — Implemented 0건이라 Forced Doubt Sampling 비대상)

## Next Actions

1. **P0 13건 전부 미구현** — `plan` 단계에서 시퀀싱 필요. 추천 순서:
   - **Wave 1 (인프라)**: FR-15 (Auth) → FR-1 (프로필) → FR-16 (한도 카운터)
   - **Wave 2 (코어 루프 1개)**: FR-2 (셔플) + FR-3 (해석) + FR-7 (궁합) — 1개 카테고리로 end-to-end 검증
   - **Wave 3 (카테고리 확장)**: FR-8 → FR-9 → FR-10 → FR-11 → FR-12 → FR-13 → FR-14 (매핑은 8개 다 있은 후)
   - **Wave 4 (P1)**: FR-6 (히스토리) → FR-4 (PWA 설치) → FR-5 (오프라인)
2. **plan 진입 전 결정 필요** (Unknown / Needs Confirmation 중 P0 영향):
   - 프론트엔드 스택 (Next.js / Vite+React / SvelteKit)
   - 스프레드 카드 수 (각 카테고리별 권장값)
   - 정·역방향 처리 정책
   - 자유 질문 매핑 임계값
3. **plan 단계에서 따로 결정**: 코드 거주 위치 (별도 repo 신규 생성 vs nara-kit 서브디렉토리 vs 다른 형태)
