---
name: prep
description: >-
  Localize external source-of-truth (Jira, Confluence, Figma, Linear, PRD) into docs/requirements.md.
  USE FOR: "prep", "/prep TICKET-ID", "요구사항 정리", "스펙 로컬화", Jira URL, Confluence URL.
  DO NOT USE FOR: gap analysis (→ /gap), code implementation (→ workflow-dev-mode), RFC writing (→ /rfc), verbal-only requirements with no external SoT (→ workflow-doc-mode brainstorming/interview first).
---

# prep — 외부 SoT 로컬화

이중 저장: `docs/sources/<id>.raw.md` (verbatim 원문) + `docs/requirements.md` (구조화 view).

참조: [Template](references/prep-template.md), [Gates](references/prep-gates.md) (trailing, stale, readiness, raw 규약)

## 실행

0. Stale (재실행 시): source ≤ 3일 + 새 인자 없음 → 종료
1. 소스 수집: 병렬 fetch. 참조 링크도 보조 추적
2. Raw 저장: verbatim. 기존은 hash diff
3. 구조화: 템플릿 변환. raw 추출/인용만
4. Write `docs/requirements.md`. frontmatter에 sources/fetched_at/raw_files/source_hashes
5. Readiness: 4기준 PASS 수 (functional / UNVERIFIED / blocking-Q / Goal — 임계값은 [Gates](references/prep-gates.md#readiness-판정))
6. 출력: 요약 + Readiness + trailing `[PREP]` 라인

## 규칙

- Raw verbatim — 의역 금지. 모든 항목 raw 추출/인용 가능해야
- 추론은 `[UNVERIFIED: <이유>]` 또는 Open Questions
- Figma: 화면/컴포넌트/인터랙션. Jira: description + AC + 결정사항
- 빈 섹션도 헤더 + "없음". `Agreed Exceptions` 필수 — gap false positive 방지
- 덮어쓰기 전 사용자 확인. `backlog/` 존재 시 "/backlog sync 가능" 안내
