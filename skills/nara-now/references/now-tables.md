# now — Judgment & Execution Tables

## 판단 로직

수집 결과를 위에서 아래로 순서대로 평가. **첫 번째로 매칭되는 행이 주 추천**. 나머지 매칭은 부차 언급(최대 1개)으로만.

| 우선순위 | 상황 | 추천 |
|----------|------|------|
| 1 | main/master 브랜치 | "메인 브랜치. 새 작업이면 브랜치 생성 후 `/nara-prep`" |
| 2 | 비-main 브랜치, requirements.md 없음 | "요구사항 미정리. `/nara-prep`으로 요구사항 정리부터" |
| 3 | requirements.md 있음, plan.md 없음 | "요구사항 정리됨. `/nara-plan`으로 작업 단위 분할" |
| 3-bis | plan.md 있음, **미완료 유닛 존재** | "`{done}/{total}` 완료. 다음: `/nara-implement T-{다음번호}` — {유닛 제목}" |
| 3-ter | 구현 변경 있음, gap.md 없음 | "구현분 있음. `/nara-gap`으로 verify (코드 AC) + `browser-visible: yes` AC 있으면 `/nara-browser-verify`" |
| 4 | gap.md 있음, **P0 Missing ≥ 1** | "P0 ({N}건) 보완 1순위 (점수 무관). gap.md Critical 섹션 참조" |
| 5 | gap.md 있음, P0 Missing 0건, 점수 < 80 | gap.md Next Actions 분석 후 실행 방법 추천 (아래 실행 방법 판단 참조) |
| 6 | gap.md 있음, P0 Missing 0건, 점수 ≥ 80 | "review-ready. commit + `/nara-code-review`" |

**`gap.md` 부재는 결함이 아니다.** gap은 spine 맨 앞이 아니라 **verify 단계**에서 1회 생성된다 (ADR-0001). 구현 전에 없는 것이 정상이므로 3행에서 `/nara-gap`을 권고하지 않는다 — 구현 변경이 관측될 때(3-ter)부터 verify 대상이다. brownfield 인수인계처럼 "이 코드 얼마나 됐나"를 먼저 알아야 하는 경우에만 사용자가 `gap`을 직접 호출한다.

**P0 hard gate 우선**: 점수 ≥ 80이어도 P0 Missing 있으면 우선순위 4. 점수만 보고 판단 금지.

gap.md에 `Gate: ✅/❌/⚠️` 필드가 있으면 그 신호 기준. 없으면 (legacy gap.md) 점수만 사용 + "/nara-gap 재실행으로 P0 분류 권고" 우선 표면화.

uncommitted changes는 별도 행 아님 — "현재 상황" 섹션에 항상 표기하되, 추천에는 영향 안 줌.

## 실행 방법 판단 (우선순위 4일 때)

gap.md Next Actions의 **상위 1~2개 항목**을 보고 판단:

| 조건 | 추천 실행 방법 |
|------|-------------|
| 항목이 1~2개 + 변경 파일 5개 이하 예상 + 요구사항 1~2줄 설명 가능 | 직접 구현 |
| 항목이 3개 이상 또는 새 도메인/기능 설계 필요 또는 API+UI+테스트 동시 | subagent-driven-development |
| 판단 불확실 | 직접 구현 먼저 시도 추천 |

## 출력 형식

```
## 현재 상황
- 브랜치: {branch}
- 변경사항: {modified/untracked 요약}
- 작업 문서: requirements.md {있음/없음} | plan.md {있음/없음} | gap.md {있음/없음} {있으면 (점수: N/100, P0 Missing: {N}, Gate: ✅/❌/⚠️)}
- 진행: {plan.md 있으면 `T-{done}/{total} 완료 · 다음 T-{N} {제목}`. 없으면 생략}
- 최근 작업: {마지막 커밋 메시지}
- 메모: {memory 도구(engram 등) 최근 관련 observation 요약. 도구 없거나 결과 없으면 생략}

## 추천
{위 판단 로직에 따른 구체적 다음 행동}
```
