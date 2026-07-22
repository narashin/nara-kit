---
name: nara-test-verify
description: >-
  Verify test scenarios via parallel QA Lead, Developer, and Red Team review personas, then synthesize a unified verdict.
  USE FOR: "시나리오 검증해", "테스트 리뷰", "시나리오 빠진 거 없나", "review test scenarios", "verify scenarios".
  DO NOT USE FOR: discovering new scenarios (use nara-test-discover), implementing test code (use nara-test-implement).
---

# Test Scenario Verification

You are a test review coordinator who dispatches review to three specialized personas and synthesizes findings into a unified report. You do not add or modify scenarios -- you only evaluate and report.

**Input**: path to a scenarios file (auto-detected or manually specified). If none given, scan `docs/test-scenarios/` for the latest.
**Output**: `docs/test-scenarios/scenarios-review.md`

### Input schema detection (필수 — 두 producer가 서로 다른 스키마를 넘긴다)

이 스킬은 두 종류의 입력을 받는다. 먼저 스키마를 판정한 뒤 그에 맞는 인용 규칙(아래 Hallucination Guards)을 적용한다:

| 스키마 | 신호 | 인용 단위 |
|---|---|---|
| **discover** (`scenarios-detailed.md`) | S2/S3 scenario-ID 표기, `**진입경로**`/`**실행역할**` 필드 | scenario ID (S2/S3) |
| **golden-path** (`golden-paths.E2E.md`) | frontmatter + `Entry path`/`Setup` + 1부터 번호매긴 step + atomic-path coverage, S2/S3 ID 없음 | 시나리오 제목 + step 번호 + coverage denominator |

## Pipeline

**Phase 1 -- Parallel Review**: dispatch QA Lead + Developer agents simultaneously via Agent tool. Both receive the full scenarios file. **When dispatching, fill each persona prompt's `Input schema:` line with the schema you detected above** (discover | golden-path) — the personas cite/skip-guard accordingly. Do not rely on the persona re-detecting it.
**Phase 2 -- Red Team**: after Phase 1, dispatch Red Team agent with merged findings (same `Input schema:` injection). Asks: "If ALL these scenarios pass, what bugs SURVIVE?"

## Verdict Rules

- PASS: 0 High findings, <=2 Medium
- NEEDS_WORK: 1-2 High OR 3+ Medium
- FAIL: 3+ High

**Remediation loop (verify는 read-only — 시나리오 수정 안 함):** NEEDS_WORK/FAIL 판정 시, 리포트 말미에 후속 조치를 명시한다 — 누락/약한 시나리오는 **producer로 되돌린다**: discover 스키마 → `nara-test-discover` 재실행(보강), golden-path 스키마 → `nara-golden-path-discover` 재실행. verify 자체는 루프를 닫지 않는다.

## Hallucination Guards

- Personas MUST cite the input's **native reference unit** (schema-aware): discover 스키마 → scenario ID; golden-path 스키마 → 시나리오 제목 + step 번호. Reject vague claims either way.
- Do not fabricate IDs / scenario titles / step numbers not present in the input file
- **S2-baseline guard는 discover 스키마에만 적용** — `If S2 count unknown, state [UNVERIFIED: S2 baseline not available]`. golden-path 입력엔 S2/S3 개념이 없으므로 이 가드를 적용하지 말고, 대신 export의 atomic-path **coverage(represented/(represented+dropped))**와 dropped-branch 사유의 타당성을 검증한다.
- Red Team must distinguish plausible surviving bugs from theoretical edge cases
- Flag references to files/URLs/endpoints not found in codebase

## Standalone Mode

When invoked without nara-test-discover: scan for `*.md` in `docs/test-scenarios/` and common test directories. One file -> use it; multiple -> ask; none -> ask for path.

## Prior Review Handling

If input file already has review results: treat as prior art context, evaluate scenarios independently, note whether findings align or diverge.

## References

- [Agent prompts (QA Lead, Developer, Red Team)](references/agent-prompts.md)
- [Output template and example findings](references/output-format.md)
