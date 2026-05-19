# gap.md Output Template

```markdown
# Gap Analysis

- Based on: docs/requirements.md
- Analyzed: {날짜}
- Score: {N}/100
- **Gate: ✅ review-ready** | ❌ blocked by P0 | ⚠️ score < 80

## Summary
- Total: {N} | Implemented: {N} | Partial: {N} | Missing: {N} | Agreed Exception: {N}
- **P0 Missing (Critical): {N}**  ← hard gate
- P1 Missing (High): {N}
- P2 Missing (Low): {N}
- Verbatim 항목: {N} (rubric §1 처리 대상 항목 수 — pre-scan에 의해 exact match 검증된 항목)
- Needs Confirm: {N} (forced sampling)

## Critical (P0) Missing — 보완 1순위
| ID | Requirement | Why P0 | Verbatim grep result |

## Detail

### Implemented
| ID | Priority | Requirement | Quote (req원문) | Evidence (파일:라인) | Verbatim? |

### Partial
| ID | Priority | Requirement | Done | Remaining | Evidence |

### Missing
| ID | Priority | Requirement | Why P{0/1/2} | Notes | Verbatim grep result |

### Agreed Exceptions
| ID | Requirement | Reason |

### Needs Confirm (forced sampling — user 확인 요청)
| ID | Priority | Requirement | Why sampled | Evidence |

## Next Actions
1. {P0 미구현 우선}
2. {P1 미구현}
3. {Needs Confirm 항목 user 확인 요청}
```

## 컬럼 작성 룰

- **Priority**: `P0` | `P1` | `P2`. rubric §6 기준 분류. 모든 항목 분류 필수
- **Why P{0/1/2}**: rubric §6 신호 중 매칭된 것 1줄 (예: "AC 본문 항목", "verbatim UI 카피", "edge case 처리")
- **Quote**: requirements.md 원문 (따옴표/백틱 안 텍스트 또는 핵심 문장)
- **Evidence**: `파일:라인` 형식. 없으면 Partial 강등
- **Verbatim?**: Y/N. Y인 경우 Quote와 코드 텍스트 exact 일치 검증 필수
- **Why sampled**: `verbatim` | `short evidence` | `random` 중 하나
- **Verbatim grep result**: `git grep -F "..."` 결과 건수 (0이면 Missing 강제 사유)

## Gate 출력 룰

`Gate:` 필드는 hard rule:
- P0 Missing = 0 AND score ≥ 80 → `✅ review-ready`
- P0 Missing ≥ 1 → `❌ blocked by P0 ({N}건)`
- P0 Missing = 0 AND score < 80 → `⚠️ score {N} (P1 보완 권장)`

`Critical (P0) Missing` 섹션은 P0 Missing 0건이어도 헤더 출력 (`(없음)` 표기). 가시성 유지.
