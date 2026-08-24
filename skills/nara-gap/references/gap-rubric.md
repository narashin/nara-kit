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
| verbatim 텍스트의 grep을 이번 실행에 **돌리지 못함** | **Missing 강제 불성립.** 분류 유지 + `미재확인` 표기. 미실행은 0건 관측이 아니다 — 0건으로 읽으면 관측하지 않은 사실로 Missing을 강제한다 |

**0건과 미실행의 판별**: 관측에 그 grep **명령**이 있고 결과 라인이 없으면 **실행된 0건**이다(→ Missing 강제). 명령 자체가 관측에 없으면 **미실행**이다(→ `미재확인`). 둘은 화면상 모두 "출력 없음"으로 보이므로 명령의 존재로만 가른다.

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

### `--verify`에서의 적용 범위

이 절의 **내용 입증력 심사**는 재확인 대상(이월 Missing/Partial)과 §3-quater로 이동한 항목에만 적용한다. 좌표가 해석되는 이월 `Implemented`는 분류를 유지하고, 라인 내용이 약하다는 의심은 §4 표집으로 표면화한다.

이유: verify가 이월 Implemented의 내용까지 매번 재심사하면 생성 모드와 구별되지 않아 모드 분리가 무의미해지고, 같은 입력이 "§3으로 Partial 강등" 경로와 "§4로 Needs Confirm 이동" 경로로 갈려 점수가 흔들린다. 두 경로 중 하나를 고정해야 재현된다.

## 3-bis. Multi-surface & Security Evidence

요구사항이 여러 수면(서버 강제 / 클라이언트 게이팅 / 테스트)에 걸치면, 일부 수면만 구현돼도 Implemented 금지.

| 상황 | 처리 |
|---|---|
| 요구사항이 둘 이상의 수면(예: 서버 enforcement + 클라이언트 노출/게이팅)에 걸치는데 일부 수면만 구현 | **Partial 강등** + 누락 수면 명시 (예: "server O / client gating X") |
| 권한·보안·인증·데이터무결성 요구사항에 guard 테스트와 소비 계층 게이팅 테스트 중 **하나라도 없음** | **Partial 강등**. 둘 다 있어야 Implemented이므로 guard 테스트만 있는 중간 상태도 이 행에 걸린다 |
| 권한·보안 요구의 동작이 수면 간 불일치 (한쪽 의미 ≠ 다른쪽) | **Missing 강제** (불일치는 미구현으로 취급) |

### --verify 재확인 강제

`--verify`는 권한·보안 항목에 대해 캐시된 gap.md 상태를 신뢰하지 말고 **실제 각 수면 코드 + 테스트를 재확인**. 재확인 없이 Implemented/complete 이월 금지. (다른 항목은 기존대로 Missing/Partial만 재검토.)

## 3-ter. Producer-absence Evidence (거짓 Missing 방지)

"backend / API / serializer / DTO / 데이터 계층이 X를 제공·저장·노출하지 않는다"는 **부재 주장**은 producer-side 증거가 있어야 Missing 확정. 소비 계층에서 "안 보인다"는 producer 부재의 증거가 아니다 (가장 흔한 거짓 Missing 원인).

| 상황 | 처리 |
|---|---|
| producer 부재 주장에 producer-side 증거 (스키마 · 엔드포인트 응답 · serializer · 데이터 모델 · 백엔드 테스트) 있음 | Missing 확정 가능 |
| 부재 주장 근거가 consumer-side 단서뿐 (UI 형태 · fallback 분기 · empty state · mock · fixture · mapper · 호출부 부재) | **Needs Confirm 강등** — "missing producer evidence" 표기. Missing 확정 금지 |

producer 코드를 직접 확인하거나, 확인 불가면 사용자 판단(§4 Needs Confirm)으로 넘긴다.

## 3-quater. Evidence 좌표 감사 (`--verify` 필수)

`--verify`는 이월 후보 **전 항목**의 `파일:라인` 인용을 먼저 해석한다. 해석되지 않는 인용은 evidence가 아니므로, 그 인용에 기대고 있던 분류를 유지하지 않는다. 이 감사가 없으면 앞선 실행이 만든 위증 좌표가 캐시로 영구 이월된다.

| 상황 | 처리 |
|---|---|
| 인용 파일이 인덱스(`git ls-files`)에 없음 | **`Needs Confirm` 이동** — 사유 `unresolved evidence path` |
| 인용 라인 번호가 파일 행수(`wc -l`) 초과 | **`Needs Confirm` 이동** — 사유 `unresolved evidence path` |
| 인용이 `repo@sha:path:line` 형태이고 그 repo 또는 sha가 이 워크스페이스에서 해석되지 않음 | **`Needs Confirm` 이동** — 사유 `unresolved evidence path` |
| 인용이 해석됨 | 기존 분류 유지 (라인 **내용**의 입증력은 §3이 따로 본다) |

- 착지 버킷은 `Needs Confirm` **하나로 고정**한다. `Partial`은 Done/Remaining 분해를 전제하는데 해석 불가 인용에는 쓸 Done이 없고, `Missing`은 부재를 단정하는데 인용 결함은 부재의 증거가 아니다.
- 이번 실행의 관측에서 유효한 대체 좌표를 찾았더라도 **분류를 조용히 복구하지 않는다.** 대체 좌표는 `Needs Confirm` 행의 Evidence 칸에 적고 사용자 확인으로 넘긴다. 조용한 교체는 앞선 실행의 위증을 산출물에서 지운다.
- 감사 결과는 gap.md `## Evidence Audit` 표로 노출한다 (인용 / 해석 결과 / 판정 영향).
- 이 절의 이동은 §4 정족수 계산 **전에** 끝난다. 즉 §4의 `N`은 이 감사 후 카운트다.

## 3-quinquies. 강등 룰 서열

한 항목에 여러 강등 룰이 동시에 걸리면 **위에서 먼저 매칭된 룰의 버킷으로 확정**하고, 나머지는 그 행의 사유 칸에 부기만 한다. 서열 없이 적용하면 같은 입력이 실행마다 다른 버킷에 떨어진다.

| 순위 | 룰 | 버킷 | 왜 이 순위인가 |
|---|---|---|---|
| 0 | §1 verbatim grep **0건** (실행됨) | `Missing` | 문자열이 코드에 없다는 관측이므로 어떤 인용 상태보다 강하다. 인용이 해석되든 안 되든 카피 자체가 부재하다 |
| 1 | §3-quater 인용 좌표 해석 불가 | `Needs Confirm` | 좌표가 해석되지 않으면 그 인용으로는 하위 판정 자체가 불가능하다 |
| 2 | §3-bis 수면 간 의미 불일치 | `Missing` | 불일치는 **관측된 사실**이므로 미확인보다 강한 근거다 |
| 3 | §3-ter producer 부재 주장이 consumer 단서뿐 | `Needs Confirm` | 부재를 단정할 근거가 없다 |
| 4 | §3-bis 일부 수면만 구현 · 테스트 부재 | `Partial` | 구현된 수면이 관측되므로 부분 인정 |
| 5 | §3 evidence 부재 · 매핑 불가 | `Partial` | 가장 일반적인 강등이므로 최후순위 |

### §3-bis 수면 간 불일치의 판정 범위

불일치 판정은 **요구사항 원문이 지목한 주체**에 한정한다. 원문이 정의하지 않은 역할에서 발견된 불일치는 판정 근거로 쓰지 않고 별도 관측으로만 남긴다 — 요구가 그 역할을 다루지 않았다면 그것은 이탈이 아니라 **미정의**이고, 미정의는 갭이 아니라 질문이다.

## 4. Forced Doubt Sampling (정족수 판정)

`Needs Confirm`은 스킬이 단독으로 확정하지 않고 사용자 판단으로 넘기는 항목이다. 이 절은 그 표면이 최소 규모를 유지하는지 **검사**하는 규칙이며, 매 실행 새로 표집하라는 지시가 아니다. 기계적 재표집은 같은 의심을 두 번 세고, 코드가 그대로여도 점수를 단조 하락시킨다.

**적용 순서 (고정)**: §3 · §3-bis · §3-ter · §3-quater 강등을 §3-quinquies 서열로 **먼저 전부 확정**한 뒤 §4를 적용한다. §4의 `N`이 §3 계열 결과에 의존하므로, 순서를 뒤집으면 같은 입력이 다른 점수를 낸다. §3 계열로 이미 강등된 항목은 §4 표집 대상이 아니다.

```
N          = Implemented + Needs Confirm     # §3 계열 확정 후의 카운트
정족수     = floor(0.2 × N)                  # 주장의 5분의 1. 하한·상한 특례 없음
누적 의심  = 현재 Needs Confirm 건수 + Confirm Log 기록 건수
```

`N`이 4 이하면 정족수가 0이므로 강제 표집이 발생하지 않는다. 의도된 결과다 — 주장이 1건일 때 그 1건을 의심으로 돌리는 것은 "5분의 1"이 아니라 전량 보류이고, 코드가 전진한 실행에서 점수를 0으로 만들어 진행률 신호를 파괴한다. 소규모 spec에서는 §1·§3 계열 강등이 품질 방어를 맡고, §4는 주장이 5건 이상 쌓인 뒤에 작동한다.

| 상황 | 처리 |
|---|---|
| 누적 의심 ≥ 정족수 | **추가 표집 금지.** 분류를 그대로 둔다 |
| 누적 의심 < 정족수 | 부족분만 Implemented에서 뽑아 `Needs Confirm`으로 **이동**(병기 아님 — 분자에서 빠진다) |

표집 우선순위: verbatim 항목 > evidence 라인 짧은 항목 > 무작위. 동순위가 남으면 이번 실행에서 근거를 재확인하지 못한 항목을 먼저 뽑는다.

한 번 의심을 거쳐 사용자가 답한 항목은 `Confirm Log`에 남아 **영구히 누적 의심에 포함**된다. 그래서 전 항목이 구현·확인된 프로젝트는 score 100에 도달할 수 있다. 이 누적 규칙이 없으면 정족수가 매 실행 새 표본을 요구해 만점 상한이 구조적으로 80 아래에 갇힌다.

### 판정 기록 (`## Confirm Log`)

사용자가 답한 `Needs Confirm` 판정은 `docs/implementation-notes.md`의 `## Confirm Log` 절에 append한다. 파일이 없으면 이 절만 담아 생성한다. gap.md는 매 실행 덮어써지고 gap-history.md는 점수만 누적하므로, 이 절이 판정의 유일한 보존 면이다.

```markdown
## Confirm Log

> Written by `gap --verify`. Do not edit manually.

| Gap Item | Verdict | Resolved To | Date | Source |
|---|---|---|---|---|
| FR-9 | confirmed | Implemented | 2026-08-24 | gap --verify |
| FR-10 | rejected | Partial | 2026-08-24 | gap --verify |
```

- `Verdict`: `confirmed` | `rejected`
- `Resolved To`: 반영할 분류 (`Implemented` / `Partial` / `Missing`)
- 다음 실행은 이 절을 먼저 읽어 해당 항목을 `Resolved To` 분류로 이월한다. 기록이 **없으면** 미확인으로 보고 `Needs Confirm`에 유지한다 — "이전에 물었으니 해소됐다"는 추정 금지
- append-only. 같은 Gap Item ID가 이미 있으면 재기록하지 않는다 (§7 Reconciliation Log와 동일한 멱등성)
- 이 절은 gap이 쓰고 gap이 읽는다. notes의 4섹션 원본과 `## Reconciliation Log`는 건드리지 않는다
- 생성 모드도 이 절을 **읽어** 확정분을 이월한다. **쓰기**는 사용자 판정이 확정된 시점에만 발생하므로 모드와 무관하다 — 판정이 없는 실행은 행을 만들지 않는다

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

### 이월 분류 정정 (`--verify`)

`--verify`는 이월 gap.md의 우선순위를 이 절의 신호로 **재도출한다.** 앞선 실행의 분류가 근거 없이 붙어 있으면(예: 원문에 AC 절이 없는데 "AC 본문 항목"으로 P0) 캐시로 이월하지 않는다. 단 정정이 게이트를 움직이는 방향에 따라 처리가 갈린다.

| 상황 | 처리 |
|---|---|
| 정정 대상이 `Missing`이 **아님** | 즉시 적용. 게이트는 P0 **Missing** 카운트만 보므로 영향 없다 |
| `Missing` 항목을 **격상**(P1·P2 → P0) | 즉시 적용. P0 Missing이 늘어 게이트가 닫히는 방향이며, §6의 "의심되면 conservative" 원칙과 같은 쪽이다 |
| `Missing` 항목을 **강등**(P0 → P1·P2) | **자동 적용 금지.** 항목을 P0에 두고, 정정 제안을 `비판정 관측`에 근거와 함께 적어 사용자 확인으로 넘긴다 |

강등만 막는 이유: 그 방향은 규칙 정정이 조용히 리뷰 차단을 해제한다. 앞선 실행이 과하게 P0를 붙였다는 판단이 맞더라도, 그 판단 하나로 게이트가 열리면 정정이 곧 우회 수단이 된다. 확인을 받은 뒤 `Confirm Log`에 남기면 다음 실행이 이월한다.

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
| `Open questions [Type: revise]` | (별도) | gap.md 새 섹션 `## Spec Revise Candidates`에 surface. 다음 `/nara-prep` 재실행 후보 |
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
