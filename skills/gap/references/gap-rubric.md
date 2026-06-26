# Gap Rubric — 결함 판정 기준

LLM 자의 판단 방지용. 모든 gap 분석에서 이 룰을 기계적으로 적용.

## 1. Verbatim (exact match — 다르면 Missing 강제)

다음 항목은 의미 동등성과 무관하게 **문자 단위 정확 일치** 필요. 다르면 결함.

- `requirements.md` 안 따옴표(`"..."`, `'...'`), 백틱(`` `...` ``), 코드블록(``` ``` ```) 안 모든 텍스트
- UI 카피 (라벨, 버튼, 플레이스홀더, 에러 메시지, 토스트)
- 단위 표기 (괄호 단위 포함/누락 포함)
- API endpoint 경로, query param key
- env var name, config key, 상수 식별자
- 파일/디렉토리 경로

### 자동 강등 룰

| 상황 | 처리 |
|---|---|
| verbatim 텍스트가 코드 grep 결과 0건 | **Missing 강제** (LLM 판단 무시) |
| verbatim 텍스트와 코드 텍스트가 띄어쓰기/개행/특수문자 차이 | **Missing 강제** |
| verbatim 텍스트와 코드 텍스트가 단위/괄호 포함 차이 | **Missing 강제** |

## 2. Semantic (의미 동등 OK — Implemented 가능)

다음 항목은 표현 달라도 역할 동일하면 Implemented.

- 비즈니스 로직 흐름, 조건 분기 구조
- 함수/변수 이름 (역할 일치 시)
- 데이터 변환 순서
- 에러 처리 패턴

## 3. Evidence 강제 룰

| 상황 | 처리 |
|---|---|
| Implemented 주장에 `파일:라인` 없음 | **Partial 강등** |
| 요구사항 문장 ↔ 코드 라인 1:1 매핑 불가 | **Partial 강등** |
| Evidence 라인이 실제 요구사항 만족 입증 불가 | **Partial 강등** |

## 3-bis. Multi-surface & Security Evidence

요구사항이 여러 수면(서버 강제 / 클라이언트 게이팅 / 테스트)에 걸치면, 일부 수면만 구현돼도 Implemented 금지.

| 상황 | 처리 |
|---|---|
| 요구사항이 둘 이상의 수면(예: 서버 enforcement + 클라이언트 노출/게이팅)에 걸치는데 일부 수면만 구현 | **Partial 강등** + 누락 수면 명시 (예: "server O / client gating X") |
| 권한·보안·인증·데이터무결성 요구사항이 코드만 있고 테스트 증거 없음 | **Partial 강등** (guard 테스트 + 소비 계층 게이팅 테스트 둘 다 있어야 Implemented) |
| 권한·보안 요구의 동작이 수면 간 불일치 (한쪽 의미 ≠ 다른쪽) | **Missing 강제** (불일치는 미구현으로 취급) |

### --verify 재확인 강제

`--verify`는 권한·보안 항목에 대해 캐시된 gap.md 상태를 신뢰하지 말고 **실제 각 수면 코드 + 테스트를 재확인**. 재확인 없이 Implemented/complete 이월 금지. (다른 항목은 기존대로 Missing/Partial만 재검토.)

## 4. Forced Doubt Sampling

Implemented로 분류한 항목 중:

- 최소 2개 또는 전체의 20% (큰 쪽) 무조건 `Needs Confirm` 섹션에 표시
- user 확인 요청용. LLM 자가 확신 우회.
- 우선순위: verbatim 항목 > evidence 라인 짧은 항목 > 무작위

## 5. 비대상 (이 rubric 적용 안 함)

- `Agreed Exceptions` 항목
- `[UNVERIFIED]` 항목 (별도 처리)

## 5-bis. 항목 카운트 단위

- 기본 단위: requirements.md의 각 **체크리스트 bullet** (`- [ ] FR-1: ...` 등) = 1항목
- **AC 절 처리:**
  - AC가 다른 FR에 흡수 가능 (예: AC1의 "Then Slack과 Email 양쪽 발송" = FR-2 + FR-3) → 별도 ID 만들지 않음. FR ID에 통합
  - AC가 FR에 없는 단독 검증 항목 (예: "응답에 `notification_id` 포함", "401 + `TOKEN_EXPIRED`", dead-letter queue) → `AC<N>-<slug>` 형식 단독 ID로 카운트
- Total 카운트: FR 항목 수 + AC 단독 ID 수 + NFR 항목 수 + UX 항목 수 + API 항목 수
- Agreed Exceptions는 Total에 포함하되 분모에서 제외 (점수 산출 시)

## 6. Priority Classification (P0/P1/P2)

각 요구사항을 분류. **모든 항목 (Implemented / Partial / Missing) 분류 필수.** 분류 근거 1줄 출력 (trace).

### P0 — Critical (must, hard gate)

다음 중 **하나라도** 매칭되면 P0.

- spec 표현: `필수`, `MUST`, `반드시`, `required`, `core`, `필요`, `should not be missing`
- AC (Acceptance Criteria) 본문 항목 — 헤더 아래 bullet
- User Story `Given-When-Then`의 `Then` 절
- 데이터 무결성 / 권한 / 보안 / 인증
- API contract: request/response shape, HTTP status, endpoint 존재
- 사용자가 못 쓰면 기능 자체가 실패하는 항목 (golden path)
- 사용자가 명시적으로 보는 에러 경로 (error message text, error state UI)
- Verbatim 항목 (rubric §1) — UI 카피·API endpoint·env var 등 exact match 필요 항목은 기본 P0

### P1 — High (should)

- spec 표현: `should`, `권장`, `권고`, `recommended`
- UX 폴리시: loading state, empty state, toast, 보조 UI
- 보조 기능: 필터, 정렬, 페이지네이션 — spec에 있지만 core path 아님
- Edge case 처리 — 자주 안 가는 경로
- ARIA / 접근성 — 명시된 항목만

### P2 — Low (nice-to-have)

- spec 표현: `nice`, `future`, `차기`, `phase 2`, `추후`, `optional`
- 명시적 후순위 표기 항목
- 성능 마이크로 최적화 — spec 명시 없으면 P2 아님 (P1)

### 모호 시 (spec에 명시 없음)

| 항목 성격 | 분류 |
|---|---|
| user-facing 핵심 동작 | **P0** |
| user-facing 보조 동작 | P1 |
| 내부 구현 디테일만 영향 | P1 |
| 명시 없는 micro-opt | P2 |

**원칙: 의심되면 conservative — P0로.** 잘못 P0 분류 비용 < P0 누락 비용.

### Override

프로젝트 특화 P0 정의가 있으면 `.claude/overrides/gap.md`에 보강. base 분류를 격상만 가능. 강등 금지.

### Hard Gate

| 조건 | 결과 |
|---|---|
| P0 Missing **0건** AND score ≥ 80 | review-ready (commit + code-review 가능) |
| P0 Missing **≥ 1건** | 점수 무관 차단. P0 보완 1순위 |
| P0 Missing 0건 AND score < 80 | P1 보완 권장 (강제 X) |

**점수와 P0는 독립 신호.** score는 진행률, P0 missing은 게이트.

## 7. Notes Reconciliation (gap --verify 전용)

`docs/implementation-notes.md` 존재 시 매칭 룰. 분리된 산출물(gap = 관측, notes = 의도)을 통합.

### 매칭 룰

| notes 카테고리 | gap 항목 | 처리 |
|---|---|---|
| `Deviations` (DEV-*) | Missing 또는 Partial | **Agreed Exception 후보**. 사용자 확정 시 Agreed Exceptions로 이동. 점수 재산출 시 분모에서 제외 |
| `Design decisions` (DD-*) | Implemented | Evidence 보강. gap.md `Implemented` 표 `Why` 컬럼에 DD-ID 인용 |
| `Tradeoffs` (TO-*) | 모든 분류 | gap.md `Needs Confirm` 섹션에 reviewer 컨텍스트로 추가 (점수 영향 X) |
| `Open questions [Type: revise]` | (별도) | gap.md 새 섹션 `## Spec Revise Candidates`에 surface. 다음 `/prep` 재실행 후보 |
| `Open questions [Type: confirm]` | 모든 분류 | `Needs Confirm` 섹션에 합류 |

### 매칭 규칙

- **ID 기반 매칭 1차**: notes entry가 gap 항목 ID 명시 (예: "DEV-1 → FR-3") → 직접 매핑
- **키워드 매칭 2차**: notes entry 본문 ↔ gap 항목 Requirement 텍스트 의미 일치 (LLM 판단 + 사용자 확인)
- **매칭 실패**: notes entry는 reviewer 컨텍스트로만 보존, 점수 영향 X

### 사용자 확정 흐름

매칭 결과를 AskUserQuestion으로 일괄 제시:
```
다음 N개를 Agreed Exception으로 처리?
- FR-3 Email 발송 (DEV-1: 다음 phase로 미룸)
- AC2-DLQ (DEV-2: 초기 버전 범위 밖)
선택지: yes / select (개별 선택) / no
```

`yes` → 모두 Agreed Exception 이동
`select` → 개별 확인 모드
`no` → 매칭만 기록, 분류 유지

### 점수 영향

- Agreed Exception 이동된 항목 → 분모에서 제외 → 점수 ↑
- Reviewer 컨텍스트만 추가된 항목 → 점수 변화 X

### 충돌 처리

| 상황 | 처리 |
|---|---|
| notes에 Deviation 있는데 gap에 없음 | "notes는 deviation 주장하지만 gap이 못 발견함 — 코드 확인 필요" 경고. 사용자 결정 |
| gap에 Missing 있는데 notes에 매칭 entry 없음 | 정상 (의도되지 않은 갭). 보완 1순위 유지 |
| notes에 Deviation + Open Q [revise] 동시 있음 | spec revise 우선 고려 — 둘 다 surface |

### Reconciliation Log

`gap --verify`가 사용자 확정한 entry를 `implementation-notes.md`의 `## Reconciliation Log` 섹션에 append. notes 4섹션 원본은 보존(intent log) — Log만 추가.

#### 스키마

```markdown
## Reconciliation Log

> Written by `gap --verify`. Do not edit manually.

| Note ID | Mapped Gap Item | Resolution | Date | Source |
|---|---|---|---|---|
| DEV-1 | FR-3 Email 발송 | Agreed Exception | 2026-05-20 | gap --verify |
| OQ-1 | (none) | Spec Revise Candidate | 2026-05-20 | gap --verify |
| DD-2 | AC-1 Login 흐름 | Evidence (Implemented) | 2026-05-20 | gap --verify |
```

#### Resolution 값

| 값 | 의미 | reflect 동작 |
|---|---|---|
| `Agreed Exception` | Deviation/Open Q [confirm]이 Agreed Exceptions로 이동 | Warnings 승격 skip |
| `Spec Revise Candidate` | Open Q [revise]가 gap.md `Spec Revise Candidates`로 surface | handoff Open Questions skip |
| `Evidence (Implemented)` | Design decision이 Implemented evidence로 매핑 | 평소대로 처리 (메모리 승격 평가) |
| `Reviewer Context` | Tradeoff/매칭 실패 entry가 Needs Confirm으로만 추가 | 평소대로 처리 (ADR 후보 평가) |

#### 멱등성 규칙

- 같은 Note ID가 이미 Log에 있으면 verify가 **재처리 skip** — 중복 append 금지
- verify 여러 번 돌려도 Log 행은 1 Note ID당 최대 1개
- 4섹션 원본 entry는 절대 수정하지 않음 (PR 리뷰 시 intent log 보존)
