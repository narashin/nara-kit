---
name: now
description: >-
  Assess current session state — git branch, changes, docs, gap score — and recommend the next action.
  USE FOR: "now", "what should I do", "where were we", "세션 시작", "어디까지 했지", "다음 뭐해", "지금 뭐해".
  DO NOT USE FOR: code implementation, gap analysis execution, commit or PR creation.
---

# now — 상황 판단 + 다음 행동 추천

세션 시작/재개 시 현재 상황을 파악하고 다음 행동을 추천한다.

## 수집 (병렬 실행)

1. **Git 상태**: `git branch --show-current`, `git status -s`, `git log --oneline -5`
2. **작업 문서**: `docs/requirements.md`, `docs/gap.md` 존재 확인. gap.md 있으면 점수 추출
3. **프로젝트 메모리**: claude-mem observations 최근 항목 조회
4. **미완료 작업**: task 목록 확인 (판단용, 출력 안 함)

## 판단 + 출력

수집 결과로 판단 후 추천. Load [references/now-tables.md](references/now-tables.md) for judgment tables and output format.

핵심 로직: main 브랜치 → `/prep` | requirements 없음 → `/prep` | gap 없음 → `/gap` | gap < 80 → 실행 방법 판단 | gap >= 80 → 리뷰/마무리.

## 규칙

- 질문하지 않는다. 수집 가능한 정보로 판단하고 추천만
- 추천은 1-2개로 제한. 선택지 나열 금지
- 토큰 절약: 코드 내용 출력 금지, 파일명과 상태만
