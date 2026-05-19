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

## 4. Forced Doubt Sampling

Implemented로 분류한 항목 중:

- 최소 2개 또는 전체의 20% (큰 쪽) 무조건 `Needs Confirm` 섹션에 표시
- user 확인 요청용. LLM 자가 확신 우회.
- 우선순위: verbatim 항목 > evidence 라인 짧은 항목 > 무작위

## 5. 비대상 (이 rubric 적용 안 함)

- `Agreed Exceptions` 항목
- `[UNVERIFIED]` 항목 (별도 처리)

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
