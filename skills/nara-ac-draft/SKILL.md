---
name: nara-ac-draft
description: >-
  Generate User Stories + Gherkin AC from one-line intent when no external SoT exists. Sister of prep.
  USE FOR: "한 줄 기획", "thin SoT", "AC 비어 prep 막힘", "US 뽑아", "AC 초안", "ac-draft".
  DO NOT USE FOR: 외부 SoT→/nara-prep, 시나리오→nara-test-discover, 구현→/nara-implement.
---

# ac-draft

`prep`의 sister skill. 외부 SoT 부재 시 한 줄 의도 → User Story + AC. 산출 `docs/requirements.md`, frontmatter `sources: [internal-draft]`.

상세: [Pipeline](references/pipeline.md) · [Template](references/template.md) · [Conventions](references/conventions.md) · [Examples](references/examples.md)

## 실행

0. **덮어쓰기 가드** — `docs/requirements.md` 이미 존재하면 write 전 사용자 확인 필수. 특히 `sources:`가 `[internal-draft]`가 **아닌** 경우(= prep이 외부 SoT로 로컬화한 산출물) 무단 덮어쓰기 금지 — clobber 시 데이터 손실. 확인 없이 진행 금지. 자기 `[internal-draft]` 산출물 재생성이 승인되면 기존 파일의 AC-ID를 로드해 재사용한다 (규칙 "AC-ID 안정" 준수).
1. **Context** — intent verbatim. 코드 scan으로 actor/domain. 못 찾으면 `[NOT FOUND]`
2. **Decomposition** — Who/What/Why 3축. 불확실 `[NEEDS_CONFIRMATION]`. Why 없으면 US 거부
3. **S2 Discovery** — US 1.5~2.5x 과생성. Tag Happy/Sad/Edge. Gherkin AC 1~3. 근거 없는 구체값 `[UNVERIFIED]`
4. **S3 Selection** — ratio 0.4~0.6. AC-ID 확정. `Unknown` never empty. AC마다 `browser-visible` 태그 부여 (아래 규칙)

## 규칙

- Gherkin 단일 형식 (rule-list 혼용 금지)
- US "so that" 절 의무
- `[UNVERIFIED]` — intent/코드 근거 없는 모든 구체값
- AC-ID 안정 (재실행 시 ID 유지)
- 구현 디테일 금지 — observable behavior만
- FR↔AC 1:1 — US verbatim 재기술
- **`browser-visible: yes|no|unknown`** — AC마다 필수. 판단은 그 AC가 **화면에서 관측되는 동작**(UI 요소 표시·화면 전이·표시 문구·입력 반응)을 말하는지로만. 서버 계산·데이터 정합·배치는 `no`. 근거 부족하면 `unknown` (추측 금지). 태그는 메타데이터 — AC 본문·ID·순서를 바꾸지 않는다. `yes` 항목의 런타임 검증은 `nara-browser-verify`가, 검증 경로 확정은 `nara-plan`이 소유한다

## Examples

[Examples](references/examples.md) — 타임존 walk-through + 환각 반례 (Error Handling 포함).

## Handoff

산출 후 `nara-plan` (설계 불안정하면 `nara-grill` 먼저). prep 우회. `test-discover`가 AC-ID로 매핑. `browser-visible: yes` AC는 plan의 `검증` 필드를 거쳐 `nara-browser-verify`로 간다. Standalone.
