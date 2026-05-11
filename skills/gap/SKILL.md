---
name: gap
description: Analyze gap between docs/requirements.md and current codebase implementation. Produces docs/gap.md with score (0-100). Use when requirements exist but need to measure implementation completeness. Supports --verify (lightweight re-check), --score (score only), --doc (doc completeness without code check). Triggers on "gap", "gap 분석", "구현 얼마나 됐어", "요구사항 대비 진행률".
version: 0.1.0
---

# gap — 요구사항 vs 구현 갭 분석

`docs/requirements.md`와 현재 코드베이스를 비교하여 갭을 분석한다.

## 모드

`$ARGUMENTS` 파싱:

| 인자 | 모드 |
|------|------|
| (없음) | **생성** — 전체 갭 분석 + gap.md 생성 |
| `--verify` | **검증** — 기존 gap.md 기준으로 재검증 (경량) |
| `--score` | **점수만** — gap.md 읽고 현재 점수만 산출 |
| `--doc` | **문서 완성도** — 코드 분석 없이 requirements.md 자체 완성도 체크 |

## 생성 모드

### 전제조건
- `docs/requirements.md` 존재 필수. 없으면 → "/prep 먼저 실행" 안내 후 중단.

### 실행
1. requirements.md 읽기
2. 각 요구사항별 코드베이스 구현 상태 확인 (Grep/Glob, 핵심 로직만)
3. Agreed Exceptions 반영 (갭에서 제외)
4. `[UNVERIFIED]` 항목 → Agreed Exceptions로 분류 (스펙 미확정)
5. gap.md 생성

### 점수 산출
```
Score = (Implemented + Partial×0.5) / (Total - Agreed Exceptions) × 100
```

### 출력 템플릿 (`docs/gap.md`)

```markdown
# Gap Analysis

- Based on: docs/requirements.md
- Analyzed: {날짜}
- Score: {N}/100

## Summary
- Total: {N} | Implemented: {N} | Partial: {N} | Missing: {N} | Agreed Exception: {N}

## Detail

### Implemented
| ID | Requirement | Evidence |

### Partial
| ID | Requirement | Done | Remaining |

### Missing
| ID | Requirement | Notes |

### Agreed Exceptions
| ID | Requirement | Reason |

## Next Actions
1. {우선순위 높은 미구현 항목}
```

## 검증 모드 (`--verify`)

기존 gap.md만 참조하여 경량 재검증:
1. gap.md의 Missing/Partial 항목만 추출
2. 해당 항목만 코드에서 확인
3. gap.md 업데이트 + 점수 재산출

requirements.md 재읽기 불필요.

## 규칙

- Agreed Exceptions 항목은 절대 갭으로 보고하지 않음.
- 구현 여부 확인 불가 시 Missing 아닌 `Unknown (코드 접근 불가)` 표기.
- 점수 80 미만: "구현 계속 필요" 명시. 80 이상: "리뷰 단계 진입 가능" 명시.
- Evidence는 `파일경로:라인번호` 형식.
- 코드 내용 인라인 출력 금지. 파일 위치만.
