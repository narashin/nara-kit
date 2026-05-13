---
name: prep
description: >-
  Localize external source-of-truth (Jira, Confluence, Figma, Linear, PRD) into docs/requirements.md.
  USE FOR: "prep", "/prep TICKET-ID", "요구사항 정리", "스펙 로컬화", Jira URL, Confluence URL.
  DO NOT USE FOR: gap analysis (use /gap), code implementation, RFC writing.
---

# prep — 외부 SoT를 로컬 요구사항 문서로 변환

외부 Source of Truth(Jira, Figma, PRD 등)를 `docs/requirements.md`로 로컬화한다.
이후 세션에서 원본 재fetch 없이 이 문서만 참조하여 토큰을 절약한다.

## 입력 + 출력 템플릿

Load [references/prep-template.md](references/prep-template.md) for input source table and output template.

## 실행

1. **소스 수집**: 외부 SoT 내용 가져오기 (병렬 가능). 1차 소스 내 참조 링크(wiki URL, Figma URL 등)도 자동 추적하여 보조 소스로 수집. 다중 소스 시 Source 필드에 각각 기재.
2. **구조화**: 템플릿으로 변환
3. **저장**: `docs/requirements.md`에 Write
4. **충분성 판정**: 아래 기준으로 Readiness 산출
5. **확인**: 요약 테이블 + Readiness 출력

## Readiness 판정

저장 후 requirements.md를 아래 4개 기준으로 판정:

| 기준 | PASS | FAIL |
|------|------|------|
| Functional Requirements 항목 수 | ≥ 1 | 0 |
| `[UNVERIFIED]` 비율 | < 50% | ≥ 50% |
| Blocking Open Questions 수 | ≤ 3 | > 3 |
| Goal 섹션 | 비어있지 않음 | 비어있음 |

**Readiness = 4개 중 PASS 수**:
- **4/4 READY** → "요구사항 충분. brainstorm → gap 진행 가능"
- **2-3/4 PARTIAL** → "부분적 부족. 보완 후 진행 또는 `ooo interview`로 명확화 추천"
- **0-1/4 INSUFFICIENT** → "`ooo interview` 필요. 요구사항 보완 후 `/prep` 재실행"

## 규칙

- **창작 금지**: 원본에 없는 요구사항 생성 금지. `[UNVERIFIED]`는 원본 언급은 있으나 세부 불명확한 경우만
- **확신 없으면 표기**: `[UNVERIFIED: <이유>]`. 억측 금지
- Figma: 화면명, 컴포넌트명, 인터랙션 흐름만. 시각 디테일 제외
- Jira: description + acceptance criteria + 기술 결정사항만
- 비어있는 섹션도 헤더 유지, "없음" 한 줄 기재
- `Agreed Exceptions` 섹션 필수 — gap 분석 false positive 방지
- `docs/requirements.md` 이미 존재하면 덮어쓰기 전 사용자 확인
- `backlog/` 존재 시 완료 후 "/backlog sync로 태스크 동기화 가능" 안내
