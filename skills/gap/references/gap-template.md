# gap.md Output Template

```markdown
# Gap Analysis

- Based on: docs/requirements.md
- Analyzed: {날짜}
- Score: {N}/100

## Summary
- Total: {N} | Implemented: {N} | Partial: {N} | Missing: {N} | Agreed Exception: {N}
- Verbatim 항목: {N} (pre-scan 적용)
- Needs Confirm: {N} (forced sampling)

## Detail

### Implemented
| ID | Requirement | Quote (req원문) | Evidence (파일:라인) | Verbatim? |

### Partial
| ID | Requirement | Done | Remaining | Evidence |

### Missing
| ID | Requirement | Notes | Verbatim grep result |

### Agreed Exceptions
| ID | Requirement | Reason |

### Needs Confirm (forced sampling — user 확인 요청)
| ID | Requirement | Why sampled | Evidence |

## Next Actions
1. {우선순위 높은 미구현 항목}
2. {Needs Confirm 항목 user 확인 요청}
```

## 컬럼 작성 룰

- **Quote**: requirements.md 원문 (따옴표/백틱 안 텍스트 또는 핵심 문장)
- **Evidence**: `파일:라인` 형식. 없으면 Partial 강등
- **Verbatim?**: Y/N. Y인 경우 Quote와 코드 텍스트 exact 일치 검증 필수
- **Why sampled**: `verbatim` | `short evidence` | `random` 중 하나
- **Verbatim grep result**: `git grep -F "..."` 결과 건수 (0이면 Missing 강제 사유)
