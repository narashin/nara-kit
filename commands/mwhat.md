# mwhat — 상황 판단 + 다음 행동 추천

세션 시작 또는 작업 재개 시, 현재 상황을 빠르게 파악하고 다음 행동을 추천한다.

## 수집 (병렬 실행)

1. **Git 상태**: `git branch --show-current`, `git status -s`, `git log --oneline -5`
2. **작업 문서 존재 여부**: `docs/requirements.md`, `docs/gap.md` 존재 확인. gap.md 있으면 `Score: N/100` 행에서 점수 추출
3. **프로젝트 메모리**: claude-mem observations 최근 항목 조회
4. **미완료 작업**: 기존 task 목록 확인 (판단에만 활용, 출력에는 포함 안 함)

## 판단 로직

수집 결과를 위에서 아래로 순서대로 평가. **첫 번째로 매칭되는 행이 주 추천**. 나머지 매칭은 부차 언급(최대 1개)으로만.

| 우선순위 | 상황 | 추천 |
|----------|------|------|
| 1 | main/master 브랜치 | "메인 브랜치. 새 작업이면 브랜치 생성 후 `/prep`" |
| 2 | 비-main 브랜치, requirements.md 없음 | "요구사항 미정리. `/prep`으로 요구사항 정리부터" |
| 3 | requirements.md 있음, gap.md 없음 | "요구사항 정리됨. `/gap`으로 갭 분석" |
| 4 | gap.md 있음, 점수 < 80 | gap.md Next Actions 분석 후 실행 방법 추천 (아래 실행 방법 판단 참조) |
| 5 | gap.md 있음, 점수 >= 80 | "거의 완료. 리뷰/마무리 단계" |

uncommitted changes는 별도 행 아님 — "현재 상황" 섹션에 항상 표기하되, 추천에는 영향 안 줌.

## 실행 방법 판단 (우선순위 4일 때)

gap.md Next Actions의 **상위 1~2개 항목**을 보고 판단:

| 조건 | 추천 실행 방법 |
|------|-------------|
| 항목이 1~2개 + 변경 파일 5개 이하 예상 + 요구사항 1~2줄 설명 가능 | `ultrawork` |
| 항목이 3개 이상 또는 새 도메인/기능 설계 필요 또는 API+UI+테스트 동시 | `SDD + harness` |
| 판단 불확실 | `ultrawork` 먼저 시도 추천 (에이전트가 복잡도 판단) |

추천 출력 예시:
- "FR-3 반려 다이얼로그 (파일 2~3개, 명확) → `ultrawork` 권장"
- "FR-5 알림 시스템 (신규 도메인, 설계 필요) → `SDD + harness` 권장"

## 예시

<example>
입력 상황: feature 브랜치, requirements.md 있음, gap.md 없음, uncommitted 2건

출력:
## 현재 상황
- 브랜치: feature/PROJ-456-approval-flow
- 변경사항: modified 2 (ApprovalForm.tsx, useApproval.ts)
- 작업 문서: requirements.md 있음 | gap.md 없음
- 최근 작업: PROJ-456 feat: Add approval form skeleton
- 메모: approval flow API endpoint TBD, frontend mock 사용 중

## 추천
요구사항 정리됨. `/gap`으로 갭 분석 진행.
</example>

<example>
입력 상황: main 브랜치, clean, 문서 없음

출력:
## 현재 상황
- 브랜치: main
- 변경사항: 없음 (clean)
- 작업 문서: requirements.md 없음 | gap.md 없음
- 최근 작업: NO-ISSUE chore: Update dependencies

## 추천
메인 브랜치 상태. 새 작업이면 feature 브랜치 생성 후 `/prep`으로 요구사항 정리부터.
</example>

## 출력 형식

```
## 현재 상황
- 브랜치: {branch}
- 변경사항: {modified/untracked 요약}
- 작업 문서: requirements.md {있음/없음} | gap.md {있음/없음 (없으면 점수 생략)} {있으면 (점수: N/100)}
- 최근 작업: {마지막 커밋 메시지}
- 메모: {claude-mem 최근 5건 중 관련 observation 요약. 없으면 생략}

## 추천
{위 판단 로직에 따른 구체적 다음 행동}
```

## 규칙

- 질문하지 않는다. 수집 가능한 정보로 판단하고 추천만 한다.
- 추천은 1-2개로 제한. 선택지 나열 금지.
- 토큰 절약: 코드 내용 출력 금지. 파일명과 상태만.
- context-mode ctx_batch_execute로 정보 수집하여 컨텍스트 윈도우 보호.

