# gap — 요구사항 vs 구현 갭 분석

`docs/requirements.md`와 현재 코드베이스를 비교하여 갭을 분석한다.
결과를 `docs/gap.md`에 저장하여, 이후 검증 시 SoT 재fetch 없이 이 문서만 참조한다.

## 모드

`$ARGUMENTS` 파싱:

| 인자 | 모드 | 동작 |
|------|------|------|
| (없음) | **생성** | 전체 갭 분석 + gap.md 생성 |
| `--verify` | **검증** | 기존 gap.md 기준으로 재검증 (경량) |
| `--score` | **점수만** | gap.md 읽고 현재 점수만 산출 |
| `--doc` | **문서 완성도** | 코드 분석 없이 requirements.md 자체 완성도 체크 |

## 생성 모드

### 전제조건
- `docs/requirements.md` 존재 필수. 없으면 → "/prep 먼저 실행" 안내 후 중단.

### 실행

1. **requirements.md 읽기**: 전체 요구사항 목록 파악
2. **코드베이스 분석**: 각 요구사항별 구현 상태 확인
   - Grep/Glob으로 관련 파일 탐색
   - 핵심 로직만 확인 (전체 코드 읽기 금지 — 토큰 절약)
3. **Agreed Exceptions 반영**: requirements.md의 `Agreed Exceptions`는 갭에서 제외
4. **[UNVERIFIED] 항목 처리**: requirements.md에서 `[UNVERIFIED]` 표기된 항목은 Agreed Exceptions로 분류. 이유: 스펙 미확정 항목은 구현 판단 불가. Reason 컬럼에 "스펙 미확정" 기재.
5. **gap.md 생성**: 아래 템플릿으로 Write

### 출력 템플릿 (`docs/gap.md`)

```markdown
# Gap Analysis

- Based on: docs/requirements.md
- Analyzed: {날짜}
- Score: {N}/100

## Summary
- Total requirements: {N}
- Implemented: {N}
- Partial: {N}
- Missing: {N}
- Agreed Exception: {N}

## Detail

### Implemented
| ID | Requirement | Evidence |
|----|-------------|----------|
| FR-1 | {요구사항} | {파일:라인 또는 근거} |

### Partial
| ID | Requirement | Done | Remaining |
|----|-------------|------|-----------|
| FR-3 | {요구사항} | {완료 부분} | {미완료 부분} |

### Missing
| ID | Requirement | Notes |
|----|-------------|-------|
| FR-5 | {요구사항} | {참고사항} |

### Agreed Exceptions (갭 아님)
| ID | Requirement | Reason |
|----|-------------|--------|
| API-2 | {요구사항} | TBD — API 미확정 |

## Next Actions
1. {우선순위 높은 미구현 항목}
2. {다음 작업 추천}
```

### 예시

<example>
requirements.md: FR-1(구현), FR-2(구현), FR-3(부분), FR-4(미구현), API-1([UNVERIFIED])
Agreed Exceptions: 다단계 결재선

계산:
- Total = 5, Agreed Exceptions = 2 (FR-4→미구현이 아님, API-1 UNVERIFIED + 다단계)
- Denominator = 5 - 2 = 3
- Score = (2 + 0.5×1) / 3 × 100 = 83점 → "리뷰 단계 진입 가능"
</example>

### 점수 산출
```
Score = (Implemented + Partial×0.5) / (Total - Agreed Exceptions) × 100
```

## 문서 완성도 모드 (`--doc`)

코드베이스 없이 기획문서 산출이 목표일 때 사용. 코드 Grep/Glob 일절 금지.

### 전제조건
- `docs/requirements.md` 존재 필수.

### 실행

1. **requirements.md 읽기**: 전체 요구사항 목록 파악
2. **문서 자체 완성도 체크** (코드 확인 없음):
   - **미정 항목**: `[UNVERIFIED]`, `TBD`, `미정`, `추후 결정` 등 표기된 항목
   - **모호한 요구사항**: 기준/조건이 불명확한 항목 (예: "빠르게", "적절히", "필요시")
   - **누락 케이스**: 명시된 요구사항에서 파생되는 edge case / 예외 처리가 없는 항목
   - **의존성 미정**: 다른 항목에 의존하나 해당 항목이 불완전한 경우
3. **gap.md 생성**: 아래 템플릿으로 Write

### 출력 템플릿 (`docs/gap.md`)

```markdown
# Gap Analysis (Doc Mode)

- Based on: docs/requirements.md
- Analyzed: {날짜}
- Completeness Score: {N}/100

## Summary
- Total requirements: {N}
- Complete: {N}
- Ambiguous: {N}
- Undefined (TBD): {N}
- Missing edge cases: {N}

## Detail

### Complete
| ID | Requirement | Notes |
|----|-------------|-------|

### Ambiguous (기준/조건 불명확)
| ID | Requirement | Issue |
|----|-------------|-------|

### Undefined — TBD/미정
| ID | Requirement | Blocker |
|----|-------------|---------|

### Missing Edge Cases
| ID | Parent Requirement | Missing Case |
|----|-------------------|--------------|

## Next Actions
1. {우선순위 높은 미정/모호 항목 해소}
2. {추가 명세 필요 항목}
```

### 점수 산출
```
Score = Complete / (Total - intentionally_deferred) × 100
```
- `intentionally_deferred`: 팀 합의로 다음 단계에서 결정하기로 한 항목 (Agreed Exceptions와 동일 처리)

## 검증 모드 (`--verify`)

기존 gap.md만 참조하여 경량 재검증:

1. **gap.md 읽기**: Missing/Partial 항목만 추출
2. **해당 항목만 코드에서 확인**: 구현되었는지 Grep/Glob
3. **gap.md 업데이트**: 상태 변경된 항목만 수정 + 점수 재산출
4. **결과 보고**: 변경된 항목 + 현재 점수

requirements.md 재읽기 불필요. SoT 재fetch 절대 불필요.

## 규칙

- Agreed Exceptions에 있는 항목은 절대 갭으로 보고하지 않는다.
- **확인 불가 시 표기**: 코드베이스에서 구현 여부를 확인할 수 없는 경우 Missing이 아닌 `Unknown (코드 접근 불가)` 으로 표기. 추측으로 ○/✗ 판정하지 않음.
- 점수 80 미만이면 "구현 계속 필요" 명시. 80 이상이면 "리뷰 단계 진입 가능" 명시.
- Evidence는 `파일경로:라인번호` 형식으로 구체적으로.
- 코드 내용 인라인 출력 금지. 파일 위치만 기재.
- 검증 모드는 기존 gap.md의 Missing/Partial만 체크. 전체 재분석 금지.

