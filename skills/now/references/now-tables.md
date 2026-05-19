# now — Judgment & Execution Tables

## 판단 로직

수집 결과를 위에서 아래로 순서대로 평가. **첫 번째로 매칭되는 행이 주 추천**. 나머지 매칭은 부차 언급(최대 1개)으로만.

| 우선순위 | 상황 | 추천 |
|----------|------|------|
| 1 | main/master 브랜치 | "메인 브랜치. 새 작업이면 브랜치 생성 후 `/prep`" |
| 2 | 비-main 브랜치, requirements.md 없음 | "요구사항 미정리. `/prep`으로 요구사항 정리부터" |
| 3 | requirements.md 있음, gap.md 없음 | "요구사항 정리됨. `/gap`으로 갭 분석" |
| 4 | gap.md 있음, **P0 Missing ≥ 1** | "P0 ({N}건) 보완 1순위 (점수 무관). gap.md Critical 섹션 참조" |
| 5 | gap.md 있음, P0 Missing 0건, 점수 < 80 | gap.md Next Actions 분석 후 실행 방법 추천 (아래 실행 방법 판단 참조) |
| 6 | gap.md 있음, P0 Missing 0건, 점수 ≥ 80 | "review-ready. commit + `/code-review`" |

**P0 hard gate 우선**: 점수 ≥ 80이어도 P0 Missing 있으면 우선순위 4. 점수만 보고 판단 금지.

gap.md에 `Gate: ✅/❌/⚠️` 필드가 있으면 그 신호 기준. 없으면 (legacy gap.md) 점수만 사용 + "/gap 재실행으로 P0 분류 권고" 우선 표면화.

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
- 작업 문서: requirements.md {있음/없음} | gap.md {있음/없음} {있으면 (점수: N/100, P0 Missing: {N}, Gate: ✅/❌/⚠️)}
- 최근 작업: {마지막 커밋 메시지}
- Backlog: {in-progress 태스크 ID + 제목} ({서브태스크 완료 N/M}). backlog/ 없으면 생략
- 메모: {claude-mem 최근 5건 중 관련 observation 요약. 없으면 생략}

## 추천
{위 판단 로직에 따른 구체적 다음 행동}
```
