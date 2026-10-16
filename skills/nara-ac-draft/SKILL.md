---
name: nara-ac-draft
description: >-
  Write docs/requirements.md, the requirements every later skill reads: localize an external source (Jira, Confluence, Figma, Linear, a URL or pasted text) keeping its AC verbatim, or turn a one-line intent into User Stories + Gherkin AC. Draft AC only where the source has none, and mark them as drafts.
  USE FOR: "요구사항 정리", "스펙 로컬화", Jira 티켓 ID·URL, Confluence URL, "한 줄 기획", "thin SoT", "US 뽑아", "AC 초안", "ac-draft".
  DO NOT USE FOR: 기능 기획 묶음·PRD (→ nara-planning), 테스트 시나리오 (→ nara-test-discover), 구현 (→ nara-implement), 요구사항 대비 진행률 (→ nara-gap).
---

# ac-draft: 요구사항 한 장

> 출력 형식은 [nara-kit 출력 계약](../nara-now/references/output-contract.md)을 따른다. 이 본문이 다르게 정한 곳은 본문이 우선한다. 파일이 없으면(단독 설치) 이 줄은 건너뛴다.

`docs/requirements.md` 하나를 쓴다. plan, gap, test-discover, browser-verify가 이 파일을 입력으로 읽는다. 입력에 따라 두 모드가 있고 산출물 경로와 `## Acceptance Criteria` 형식은 같다.

| 입력 | 모드 |
|---|---|
| 티켓 ID, Jira·Confluence·Figma·Linear URL, 기타 URL, 붙여 넣은 기획 본문 | **외부 원본**: 가져와서 옮긴다 ([external-source](references/external-source.md)) |
| 한 줄 의도, 원본 없음 | **초안**: US + Gherkin AC를 만든다 ([Pipeline](references/pipeline.md)) |

상세: [Template](references/template.md) · [Conventions](references/conventions.md) · [Examples](references/examples.md)

## 실행

0. **덮어쓰기 가드**: `docs/requirements.md`가 있으면 write 전에 사용자 확인. 기존 AC-ID는 로드해서 재사용한다(규칙 "AC-ID 안정").
1. **Context**:
   - 외부 원본이면 MCP나 WebFetch로 원문을 읽는다. 원문의 링크가 결정에 걸리면 그것도 읽는다. 못 읽으면 `❌ 실패:`로 멈추고 지어서 채우지 않는다.
   - 초안이면 intent를 그대로 받고 코드 scan으로 actor·domain을 찾는다. 못 찾으면 `[NOT FOUND]`.
   - 기획 묶음(`docs/product/<slug>/`)이 있으면 함께 읽는다([Pipeline](references/pipeline.md) Stage 1).
2. **외부 원본 옮기기**: FR·AC·결정사항·범위 밖을 원문 단어 그대로 옮긴다. 의역, 요약, 재정렬을 하지 않는다. 원문에 AC가 있으면 그것이 전부이고 3단계를 건너뛴다.
3. **AC 초안** (원본이 없거나 원본에 AC가 없을 때만): Who/What/Why 3축 → US 1.5~2.5배 과생성 → 0.4~0.6 선택 → Gherkin AC. Why가 없으면 US를 거부한다. 외부 원본 모드에서 만든 AC에는 `[draft]`를 붙여 원문 AC와 구분한다.
4. **태그와 저장**: AC마다 `browser-visible` 태그를 단다(아래 규칙). `Unknown / Needs Confirmation`을 채우고 write한다.

## 규칙

- **없는 걸 만들지 않는다.** 원문이나 코드에 근거 없는 구체값(API 경로, 필드명, 임계값, 에러코드)은 `[UNVERIFIED: <이유>]`. 원문 AC를 고치거나 보강하지 않는다. 원문 AC가 모호하면 Open Questions로 올린다.
- **원문과 초안을 섞지 않는다.** 원문에서 온 항목은 그대로, 이 스킬이 만든 AC는 `[draft]`. 사용자가 확정하면 `[draft]`를 떼고 frontmatter `confirmed_at`을 남긴다.
- Gherkin 단일 형식. 단, 원문 AC가 bullet이면 bullet 그대로 둔다.
- US "so that" 절 의무 (초안 모드).
- AC-ID 안정 (재실행 시 ID 유지).
- 기획 묶음을 읽었으면 frontmatter `product: docs/product/<slug>/`를 남긴다. 묶음의 결정 로그나 정책에 확정된 값은 `[UNVERIFIED]` 대신 그 결정·규칙 이름을 근거로 단다. 묶음과 다르게 쓰지 않는다.
- 구현 디테일 금지: observable behavior만.
- FR↔AC 1:1: US나 원문 문장을 그대로 재기술.
- **`browser-visible: yes|no|unknown`**: AC마다 필수. 판단은 그 AC가 **화면에서 관측되는 동작**(UI 요소 표시·화면 전이·표시 문구·입력 반응)을 말하는지로만. 서버 계산·데이터 정합·배치는 `no`. 근거 부족하면 `unknown` (추측 금지). 태그는 메타데이터라 AC 본문·ID·순서를 바꾸지 않는다. `yes` 항목의 런타임 검증은 `nara-browser-verify`가, 검증 경로 확정은 `nara-plan`이 소유한다.

## Examples

[Examples](references/examples.md): 타임존 walk-through + 환각 반례 (Error Handling 포함).

## Handoff

산출 후 `nara-plan` (설계 불안정하면 `nara-grill` 먼저). `test-discover`가 AC-ID로 매핑. `browser-visible: yes` AC는 plan의 `검증` 필드를 거쳐 `nara-browser-verify`로 간다. `[draft]` AC가 남아 있으면 receipt의 next에 확정 요청을 적는다. Standalone.
