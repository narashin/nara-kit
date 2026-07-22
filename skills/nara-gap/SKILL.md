---
name: nara-gap
description: >-
  Analyze gap between docs/requirements.md and codebase, producing docs/gap.md with a score (0-100).
  USE FOR: "gap", "gap 분석", "구현 얼마나 됐어", "요구사항 대비 진행률", "--verify".
  DO NOT USE FOR: writing requirements (use /nara-prep), code implementation, code review.
---

# gap — 요구사항 vs 구현 갭 분석

`docs/requirements.md`와 현재 코드베이스를 비교하여 갭을 분석한다.

## 모드 (`$ARGUMENTS`)

- (없음) → 전체 갭 분석 + gap.md 생성
- `--verify` → 기존 gap.md 기준 재검증 (경량)
- `--score` → gap.md에서 점수만 산출

## 생성 모드

전제: `docs/requirements.md` 존재 필수. 없으면 "/nara-prep 먼저 실행" 안내 후 중단.

판정 룰은 [references/gap-rubric.md](references/gap-rubric.md) 기계 적용. LLM 자의 판단 금지.

1. requirements.md 읽기
2. **Verbatim pre-scan** (자동):
   - requirements.md에서 따옴표/백틱/코드블록 안 모든 텍스트 추출
   - 각 텍스트에 대해 `git grep -F` 실행 → 0건이면 rubric §1에 따라 **Missing 강제**
   - LLM 판단 거치지 않음
3. 각 요구사항별 코드베이스 구현 상태 확인 (Grep/Glob, 핵심 로직만)
4. rubric §3 Evidence 강제 룰 적용 → Implemented 주장 중 매핑 불가 항목 Partial 강등
4-bis. rubric §3-bis 적용 → 다수면 요구사항 중 일부 수면만 구현·권한/보안 테스트 부재 항목 Partial 강등, 수면 간 불일치는 Missing 강제
4-ter. rubric §3-ter 적용 → producer(backend/API/serializer/DTO) 부재 주장이 consumer-side 단서뿐이면 Missing 확정 금지, `Needs Confirm` "missing producer evidence"로 강등
5. Agreed Exceptions 반영 (갭에서 제외)
6. `[UNVERIFIED]` 항목 → Agreed Exceptions로 분류
7. rubric §4 Forced Doubt Sampling → Implemented 중 20% (최소 2개) `Needs Confirm` 표시
8. **Priority Classification** (rubric §6): 모든 항목을 P0/P1/P2로 분류. 근거 1줄 trace 출력 필수. `.claude/overrides/gap.md` 존재 시 격상만 적용
9. **Gate 판정**: P0 Missing 카운트 + score로 `✅ review-ready` / `❌ blocked by P0` / `⚠️ score < 80` 결정
10. gap.md 생성. Follow template in [references/gap-template.md](references/gap-template.md).
11. **Score history append** (`docs/gap-history.md`): 이번 실행 결과 1행 append (파일 없으면 헤더 + 생성). gap.md는 매 실행 덮어써지므로 점수 추이는 이 파일에 누적 (§Score History).

### 점수 산출
```
Scoreable = Total - Agreed Exceptions          # 평가 대상 요구사항
Score     = (Implemented + Partial*0.5) / Scoreable * 100
```

- **분모 가드**: `Scoreable == 0` (전 항목이 Agreed Exception) → 점수 `N/A ("평가할 요구사항 없음")` 출력, div-by-zero 금지. Gate만 보고.
- **분자 구성 명시** (silent deflation 금지): `Needs Confirm`·`Unknown`은 Implemented로 안 세므로 분모엔 남고 분자엔 안 들어가 점수를 낮춘다 — 이는 **의도된 conservative 처리** (미확인 = 미구현 취급). gap.md에 `Scoreable / Implemented / Partial / Needs Confirm / Unknown` 카운트를 나열해 점수 근거를 투명하게 보인다.

**점수는 진행률 신호. P0 게이트와 독립.** 가중 점수 X — 단일 점수 + 카테고리 분리.

### Score History (`docs/gap-history.md`)

gap.md는 현재 스냅샷(매 실행 덮어쓰기). 점수 추이는 append-only `docs/gap-history.md`에 보존 — `/nara-now`가 추세 파악, `--verify` 반복 시 직전 점수 소실 방지.

```markdown
# Gap Score History

| Date | Mode | Score | P0 Missing | Note |
|---|---|---|---|---|
| 2026-07-03 | gen | 72 | 2 | initial |
| 2026-07-03 | verify | 85 | 0 | P0 resolved |
```

- append-only — 기존 행 수정/삭제 금지
- `Mode`: `gen`(전체 분석) / `verify`(--verify 재검증)
- `Date`: 실행일 YYYY-MM-DD

## 검증 모드 (`--verify`)

기존 gap.md의 Missing/Partial 항목만 추출 → 코드 확인 → gap.md 업데이트 + 점수 재산출.
Verbatim pre-scan + Evidence 강등 + Doubt sampling 모두 동일 적용.
점수 재산출 후 `docs/gap-history.md`에 `verify` 행 append (§Score History) — 재검증마다 추이 누적.
**예외 — 권한·보안 항목**: rubric §3-bis에 따라 이전 Implemented여도 실제 각 수면(서버·클라이언트·테스트) 재확인. gap.md 캐시 상태로 complete 이월 금지.

### Notes Reconciliation (필수)

`docs/implementation-notes.md` 존재 시:

1. **읽기**: 5섹션 모두 추출
   - 4섹션 (Design decisions / Deviations / Tradeoffs / Open questions) → 매칭 대상
   - `## Reconciliation Log` (5섹션, 없으면 빈 표) → 이미 박힌 Note ID 목록 추출
   - Log에 이미 있는 Note ID는 매칭 대상에서 **skip** (멱등성)
2. **매칭**: 미처리 entry를 gap.md의 Missing/Partial/Implemented 항목과 매핑
   - Deviations entry ↔ Missing/Partial 항목 (의도된 갭 후보)
   - Design decisions entry ↔ Implemented 항목 (evidence 보강)
   - Open questions [revise] entry → gap.md `## Spec Revise Candidates` 섹션에 surface
3. **사용자 확인**: 매칭된 항목을 AskUserQuestion으로 일괄 제시
   - "이 N개를 `Agreed Exceptions`로 처리?" — 응답 YES/SELECT/NO
4. **반영**: 확정된 항목 `Agreed Exceptions`로 이동. 점수 재산출
5. **Notes log 갱신** (필수): 확정된 entry를 `implementation-notes.md` `## Reconciliation Log` 표에 append (섹션 없으면 생성). 컬럼: Note ID / Mapped Gap Item / Resolution / Date / Source. 4섹션 원본은 **수정 금지** — Log만 append
6. **rubric §7 Notes Reconciliation** 룰 따름

자세한 매칭 룰: [references/gap-rubric.md](references/gap-rubric.md) §7.

implementation-notes.md 없으면 이 단계 skip.

## 규칙

- Agreed Exceptions 항목은 갭으로 보고하지 않음
- 구현 여부 확인 불가 시 `Unknown (코드 접근 불가)` 표기
- **Gate는 P0 Missing 기반.** 점수만 보고 분기 금지:
  - P0 Missing 0 AND score ≥ 80: "리뷰 단계 진입 가능"
  - P0 Missing ≥ 1: "P0 보완 1순위 (점수 무관)"
  - P0 Missing 0 AND score < 80: "P1 보완 권장"
  - score `N/A` (Scoreable 0 — 전 항목 Agreed Exception): P0 Missing 0이 자명 → "리뷰 단계 진입 가능 (평가 대상 요구사항 없음)"
- Evidence는 `파일경로:라인번호` 형식. 코드 내용 인라인 출력 금지
- 모든 판정은 [references/gap-rubric.md](references/gap-rubric.md) 기준 따름. "비슷하다" 식 자의 판단 금지
- Verbatim 항목(따옴표/백틱/코드블록 안 텍스트)은 의미 무관 exact match. grep 0건이면 Missing 강제
- Implemented 판정에 evidence 없으면 자동 Partial 강등
- **모든 항목 P0/P1/P2 분류 필수.** 모호 시 conservative — P0로. rubric §6 신호 기반, 근거 1줄 trace
