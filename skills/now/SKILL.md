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
3. **Requirements stale 검증**: `docs/requirements.md` 존재 시 frontmatter `sources[].fetched_at` 확인. 가장 오래된 source의 경과시간 측정
4. **Handoff**: `docs/handoff.md` 존재 확인. 있으면 9섹션 스키마로 파싱 — baseline SHA로 stale 검증, 현재 목표/In Progress/Open Questions/다음 안전 조치/먼저 읽을 파일/최근 완료 태스크 컨텍스트 우선 표면화
5. **Backlog**: `backlog/` 존재 시 `backlog task list -s "In Progress"` 실행. 없으면 생략
6. **프로젝트 메모리**: claude-mem observations 최근 항목 조회
7. **미완료 작업**: task 목록 확인 (판단용, 출력 안 함)

## Stale 판정

| 경과 | 판정 | 행동 |
|------|------|------|
| ≤ 3일 | fresh | 정상 진행 |
| 4-7일 | aging | 사용자에게 재fetch 권고 (선택) |
| > 7일 | stale | "requirements.md 7일 이상 경과. `/prep` 재실행 권고" 우선 표면화 |

frontmatter에 `fetched_at` 없거나 `sources` 배열 누락 → `legacy prep` 표시 + 사용자에게 마이그레이션 안내.

## 판단 + 출력

수집 결과로 판단 후 추천. Load [references/now-tables.md](references/now-tables.md) for judgment tables and output format.

핵심 로직: main 브랜치 → `/prep` | requirements 없음 → `/prep` | **requirements stale (>7일) → `/prep` 재실행 권고** | gap 없음 → `/gap` | gap < 80 → 실행 방법 판단 | gap >= 80 → 리뷰/마무리.

**Handoff 우선순위**: `docs/handoff.md` 존재하면 다른 추천보다 먼저 표면화. "이전 세션에서 X 작업 중단, Y 질문 미해결" 형태로 1-2줄 요약 후 그 다음 액션 추천.

## 규칙

- 질문하지 않는다. 수집 가능한 정보로 판단하고 추천만
- 추천은 1-2개로 제한. 선택지 나열 금지
- 토큰 절약: 코드 내용 출력 금지, 파일명과 상태만
