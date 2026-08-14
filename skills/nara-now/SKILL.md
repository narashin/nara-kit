---
name: nara-now
description: >-
  Assess current session state — git branch, changes, docs, gap score — and recommend the next action.
  USE FOR: "now", "what should I do", "where were we", "세션 시작", "어디까지 했지", "다음 뭐해", "지금 뭐해".
  DO NOT USE FOR: code implementation, gap analysis execution, commit or PR creation.
---

# now — 상황 판단 + 다음 행동 추천

세션 시작/재개 시 현재 상황을 파악하고 다음 행동을 추천한다.

## 수집 (병렬 실행)

1. **Git 상태**: `git branch --show-current`, `git status -s`, `git log --oneline -5`
2. **작업 문서**: `docs/requirements.md`, `docs/plan.md`, `docs/gap.md` 존재 확인. gap.md 있으면 점수 추출. `docs/gap-history.md` 있으면 최근 점수 추이(직전→현재) 1줄 표면화. **gap.md 부재는 결함이 아님** — verify 단계 전에는 없는 게 정상 (ADR-0001)
2-bis. **진행 위치**: `docs/plan.md` 있으면 `grep -n '^## T-'`로 유닛과 `— ✅ done` 표식을 읽는다. 완료 수 / 전체 수, **다음 미완료 유닛의 T-N과 제목**을 뽑는다. 표식은 `nara-implement`가 검증 통과 시 붙인 것이므로 그대로 신뢰한다 — 커밋 로그나 파일 변경으로 완료를 **추측하지 않는다**. `docs/plan/` 아래 복수 plan이 있고 `docs/plan.md`가 없으면 가장 최근 수정본을 쓰되 경로를 함께 표기한다
3. **Requirements stale 검증**: `docs/requirements.md` 존재 시 frontmatter `sources[].fetched_at` 확인. 가장 오래된 source의 경과시간 측정
4. **Handoff**: `docs/handoff.md` 존재 확인. 있으면 9섹션 스키마로 파싱 — baseline SHA로 stale 검증, 현재 목표/In Progress/Open Questions/검증 상태/다음 안전 조치/먼저 읽을 파일 우선 표면화
5. **프로젝트 메모리**: 설치된 memory 도구로 최근 세션·관련 관찰 조회 (예: engram `mem_context` / `mem_search`). 도구 없으면 이 단계 skip — 없는 백엔드 호출 금지
6. **미완료 작업**: task 목록 확인 (판단용, 출력 안 함)

## Stale 판정

| 경과 | 판정 | 행동 |
|------|------|------|
| ≤ 3일 | fresh | 정상 진행 |
| 4-7일 | aging | 사용자에게 재fetch 권고 (선택) |
| > 7일 | stale | "requirements.md 7일 이상 경과. `/nara-prep` 재실행 권고" 우선 표면화 |

frontmatter에 `fetched_at` 없거나 `sources` 배열 누락 → `legacy prep` 표시 + 사용자에게 마이그레이션 안내.

## 판단 + 출력

수집 결과로 판단 후 추천. Load [references/now-tables.md](references/now-tables.md) for judgment tables and output format.

핵심 로직: main 브랜치 → `/nara-prep` | requirements 없음 → `/nara-prep` | **requirements stale (>7일) → `/nara-prep` 재실행 권고** | plan 없음 → `/nara-plan` | **plan에 미완료 유닛 있음 → `/nara-implement T-N`(다음 유닛 번호를 실제로 박아서)** | 전 유닛 done, gap 없음 → verify (`/nara-gap` + browser AC면 `/nara-browser-verify`) | **P0 Missing ≥ 1 → P0 보완 (점수 무관)** | P0 0 + gap < 80 → 실행 방법 판단 | P0 0 + gap ≥ 80 → 리뷰/마무리.

**추천은 실행 가능한 명령 형태로 낸다** — "구현하세요"가 아니라 `/nara-implement T-2`. 인자가 있는 스킬은 인자까지 채운다(`/nara-prep PRODUCT-431`, `/nara-browser-verify --url …`). 그대로 복사해 붙일 수 있어야 한다.

**Handoff 우선순위**: `docs/handoff.md` 존재하면 다른 추천보다 먼저 표면화. "이전 세션에서 X 작업 중단, Y 질문 미해결" 형태로 1-2줄 요약 후 그 다음 액션 추천.

## 규칙

- 질문하지 않는다. 수집 가능한 정보로 판단하고 추천만
- 추천은 1-2개로 제한. 선택지 나열 금지
- 토큰 절약: 코드 내용 출력 금지, 파일명과 상태만
- **"코드 내용 출력 금지" 정의:** 실제 코드 라인 (`function foo() {...}`, 다중 라인 코드 블록) 금지. gap.md / requirements.md / handoff.md의 **요약 1줄 인용**은 허용 (예: P0 항목 ID + Why P0 1줄). 파일명과 라인 번호만 가리키는 게 우선이지만, 액션 가능성을 위해 핵심 1~2줄은 인용 가능
