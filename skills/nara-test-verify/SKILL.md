---
name: nara-test-verify
description: >-
  Verify test scenarios with one critic over fixed inputs (contract coverage + surviving bugs), tag each finding with where to fix it, and give a verdict. Read-only.
  USE FOR: "시나리오 검증해", "테스트 리뷰", "시나리오 빠진 거 없나", "review test scenarios", "verify scenarios".
  DO NOT USE FOR: discovering new scenarios (use nara-test-discover), implementing test code (use nara-test-implement).
---

# Test Scenario Verification

> 출력 형식은 [nara-kit 출력 계약](../nara-now/references/output-contract.md)을 따른다. 이 본문이 다르게 정한 곳은 본문이 우선한다. 파일이 없으면(단독 설치) 이 줄은 건너뛴다.

You are a test review coordinator: gather fixed inputs, dispatch one critic, report. You never edit scenarios or upstream documents.

**Input**: path to a scenarios file (auto-detected or manually specified). If none given, scan `docs/test-scenarios/` for the latest.
**Output**: `docs/test-scenarios/scenarios-review.md`

### Input schema detection (필수 — 두 producer가 서로 다른 스키마를 넘긴다)

이 스킬은 두 종류의 입력을 받는다. 먼저 스키마를 판정한 뒤 그에 맞는 인용 규칙(아래 Hallucination Guards)을 적용한다:

| 스키마 | 신호 | 인용 단위 |
|---|---|---|
| **discover** (`scenarios-detailed.md`) | S2/S3 scenario-ID 표기, `**진입경로**`/`**실행역할**` 필드 | scenario ID (S2/S3) |
| **golden-path** (`golden-paths.E2E.md`) | frontmatter + `Entry path`/`Setup` + 1부터 번호매긴 step + atomic-path coverage, S2/S3 ID 없음 | 시나리오 제목 + step 번호 + coverage denominator |

## Pipeline

1. 스키마를 판정하고 크리틱 입력 넷(시나리오 전문, 요구사항 AC·Edge Cases, plan 맥락, 코드 화이트리스트)을 모은다. 크리틱은 파일을 찾지 않는다. 목록과 규칙은 [agent-prompts.md](references/agent-prompts.md).
2. 크리틱 1회를 dispatch한다. `Input schema:` 줄을 판정한 스키마로 채운다. 서브에이전트를 쓸 수 없으면(도구 없음, 생성 거부) 같은 프롬프트를 메인 세션에서 한 번 돌리고 `dispatch: inline (no subagent tool)`를 적는다.
3. findings를 `F-N`으로 번호 매겨 리포트를 쓴다([output-format.md](references/output-format.md)).

## Verdict Rules

- PASS: 0 High findings, <=2 Medium
- NEEDS_WORK: 1-2 High OR 3+ Medium
- FAIL: 3+ High

**Remediation (verify는 read-only — 시나리오도 상류 문서도 고치지 않음):** `fix: scenario` finding은 **producer로 되돌린다**: discover → `nara-test-discover`, golden-path → `nara-golden-path-discover` 재실행. `fix: upstream:<doc>`은 Upstream Findings 표에 남기고 사용자가 정한다.

## Hallucination Guards

- The critic MUST cite the input's **native reference unit** (schema-aware): discover 스키마 → scenario ID; golden-path 스키마 → 시나리오 제목 + step 번호. Reject vague claims either way.
- Do not fabricate IDs / scenario titles / step numbers not present in the input file
- 커버리지: discover는 선택 비율을 보지 않고 AC↔시나리오 연결을 본다. golden-path는 export의 atomic-path **coverage(represented/(represented+dropped))**를 다시 셀 수 있는지와 dropped-branch 사유의 타당성을 본다.
- The survivor lens reports plausible surviving bugs only, not theoretical edge cases
- Flag files/URLs/endpoints not found in the inputs

## Standalone Mode

When invoked without nara-test-discover: scan for `*.md` in `docs/test-scenarios/` and common test directories. One file -> use it; multiple -> ask; none -> ask for path.

## Prior Review Handling

`scenarios-review.md`가 이미 있으면 재검증이다: 이전 `F-N`을 판정하고 그 뒤 바뀐 시나리오만 다시 본다. 절차는 [Re-check](references/agent-prompts.md#re-check-prompt).

## References

- [Critic prompt](references/agent-prompts.md)
- [Output template and example findings](references/output-format.md)
