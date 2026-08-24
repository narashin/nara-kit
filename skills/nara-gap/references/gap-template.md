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
- Needs Confirm: {N} (정족수 {N} — §4)

## Evidence Audit (`--verify` 전용 — rubric §3-quater)
| Cited Evidence | 해석 결과 | 판정 영향 |

생성 모드에서는 이 절을 **출력하지 않는다** (이월 인용이 없으므로 빈 표에 의미가 없다).

## 비판정 관측 (선택 — 점수·게이트 영향 없음)
| 관측 | 왜 판정에 쓰지 않았나 |

rubric §3-bis 판정 범위에 따라 요구사항 원문이 지목하지 않은 주체에서 발견된 불일치, 그 밖에 관측했으나 판정 근거로 쓰지 않은 사실을 여기 적는다. `Needs Confirm`에 넣으면 §4 정족수 카운트를 오염시킨다.

## Critical (P0) Missing — 보완 1순위
| ID | Requirement | Why P0 | Verbatim grep result |

## Detail

### Implemented
| ID | Priority | Requirement | Quote (req원문) | Evidence (파일:라인) | Verbatim? | Why (선택, DD-ID 인용) |

### Partial
| ID | Priority | Requirement | Done | Remaining | Evidence |

### Missing
| ID | Priority | Requirement | Why P{0/1/2} | Notes | Verbatim grep result |

### Agreed Exceptions
| ID | Requirement | Reason |

### Needs Confirm (forced sampling — user 확인 요청)
| ID | Priority | Requirement | Why sampled | Evidence |

reviewer context로 합류한 항목 (rubric §7 Tradeoffs/Open Q[confirm])은 Priority/Evidence 컬럼에 `-` 표기 허용. Why sampled 컬럼에 `tradeoff: TO-ID` 또는 `open-Q: OQ-ID` 명시.

### Spec Revise Candidates (선택 — gap --verify Notes Reconciliation 시만)
| ID | Topic | Type | Context | Source |

`Source` 형식: `implementation-notes.md OQ-<N>`. 다음 `/nara-prep` 재실행 후보 표시.

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
- **Why sampled**: `verbatim` | `short evidence` | `random` | `unresolved evidence path` | `missing producer evidence` 중 하나 (rubric §3-quinquies 서열로 확정된 사유 1개. 부수 사유는 같은 칸에 부기)
- **해석 결과**: `resolved` | `file absent` | `line out of range (N행 파일)` | `unresolved repo@sha`
- **Verbatim grep result**: `git grep -F "..."` 결과 건수 (0이면 Missing 강제 사유)

## Score History (`docs/gap-history.md`)

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

## Gate 출력 룰

`Gate:` 필드는 hard rule:
- P0 Missing = 0 AND score ≥ 80 → `✅ review-ready`
- P0 Missing ≥ 1 → `❌ blocked by P0 ({N}건)`
- P0 Missing = 0 AND score < 80 → `⚠️ score {N} — {사유}`. `{사유}`는 분자에 **온전히 들어가지 않은** 항목(`Needs Confirm`·`Unknown`은 전부, `Partial`은 남은 0.5) 중 최고 우선순위로 적는다: P0가 섞여 있으면 `P0 확인 필요`, P1뿐이면 `P1 보완 권장` — P0 항목이 `Needs Confirm`·`Partial`에 있으면 `P0 확인 필요`, P1뿐이면 `P1`. "P1 보완 권장"을 고정 출력하면 실제 블로커가 P0일 때 산출물이 사실과 어긋난다

`Critical (P0) Missing` 섹션은 P0 Missing 0건이어도 헤더 출력 (`(없음)` 표기). 가시성 유지.
