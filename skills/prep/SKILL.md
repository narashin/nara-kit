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
- **Acceptance Criteria 처리:**
  - Jira "Acceptance Criteria" 필드, Confluence 본문의 "AC" / "수락 기준" / "Given-When-Then" 블록 발견 시 verbatim 보존 → `## Acceptance Criteria` 섹션에 박음
  - 외부 SoT에 AC 없음 → 빈 섹션 + `Open Questions`에 `[blocking] AC 누락. doc-mode AC Gate에서 작성 필요` 추가
  - **AC 추론·창작 금지.** raw에 없으면 만들지 않음. gap·test-discover가 정확도 잃는 게 spec 변조보다 나음
- **FR ↔ AC 중복 처리:**
  - 외부 SoT가 AC만 제공하고 FR 별도 명시 없음 (대부분의 Jira 케이스) → FR 섹션을 **비우지 않고**, AC 항목과 1:1 대응되는 FR을 raw 단어 그대로 옮김 (재구성/의역 없음). 결과적으로 FR과 AC가 유사하더라도 OK
  - 외부 SoT가 FR과 AC를 둘 다 명시 → 둘 다 그대로 보존. 중복 허용
  - 외부 SoT가 FR만 명시하고 AC 없음 → FR만 채우고 AC 비움 + blocking Open Question
  - 원칙: **raw에 있는 만큼만 채움. raw에 없는 걸 채우기 위해 derive 금지**
- 덮어쓰기 전 사용자 확인. `backlog/` 존재 시 "/backlog sync 가능" 안내
