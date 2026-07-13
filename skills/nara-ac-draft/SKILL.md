---
name: nara-ac-draft
description: >-
  Generate User Stories + Gherkin AC from one-line intent when no external SoT exists. Sister of prep.
  USE FOR: "한 줄 기획", "thin SoT", "AC 비어 prep 막힘", "US 뽑아", "AC 초안", "ac-draft".
  DO NOT USE FOR: 외부 SoT→/nara-prep, 시나리오→nara-test-discover, 코드→nara-workflow-dev-mode.
---

# ac-draft

`prep`의 sister skill. 외부 SoT 부재 시 한 줄 의도 → User Story + AC. 산출 `docs/requirements.md`, frontmatter `sources: [internal-draft]`.

상세: [Pipeline](references/pipeline.md) · [Template](references/template.md) · [Conventions](references/conventions.md) · [Examples](references/examples.md)

## 실행

1. **Context** — intent verbatim. 코드 scan으로 actor/domain. 못 찾으면 `[NOT FOUND]`
2. **Decomposition** — Who/What/Why 3축. 불확실 `[NEEDS_CONFIRMATION]`. Why 없으면 US 거부
3. **S2 Discovery** — US 1.5~2.5x 과생성. Tag Happy/Sad/Edge. Gherkin AC 1~3. 근거 없는 구체값 `[UNVERIFIED]`
4. **S3 Selection** — ratio 0.4~0.6. AC-ID 확정. `Unknown` never empty

## 규칙

- Gherkin 단일 형식 (rule-list 혼용 금지)
- US "so that" 절 의무
- `[UNVERIFIED]` — intent/코드 근거 없는 모든 구체값
- AC-ID 안정 (재실행 시 ID 유지)
- 구현 디테일 금지 — observable behavior만
- FR↔AC 1:1 — US verbatim 재기술

## Examples

[Examples](references/examples.md) — 타임존 walk-through + 환각 반례 (Error Handling 포함).

## Handoff

산출 후 `nara-gap` or `superpowers:brainstorming`. prep 우회. `test-discover`가 AC-ID로 매핑. Standalone.
