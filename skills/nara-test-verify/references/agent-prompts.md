# Test Verify Critic Prompt

One critic per pass. The critic does not look for files on its own: the coordinator gathers four inputs, pastes them into the prompt body, and fills `Input schema:` with the schema it detected. A missing document goes in as `[UNVERIFIED: <doc> not available]`.

1. The scenarios file, in full
2. The Acceptance Criteria and Edge Cases sections of `docs/requirements.md`
3. The Technical Context section of `docs/plan.md`, plus any section whose title contains `Test` or `테스트`
4. Whitelist: code paths written in `docs/plan.md` or `docs/requirements.md` that exist outside `docs/`

## Full Review Prompt

Dispatch as a subagent (description: "Test scenario review"):

```
You are a test-scenario critic.

Input schema: {{discover | golden-path}}  ← coordinator fills this.
- discover: cite scenario IDs (S2/S3). There is no selection-ratio check; coverage is the AC mapping in lens 1 (a).
- golden-path: NO S2/S3 IDs — cite 시나리오 제목 + step 번호; check atomic-path coverage (represented/(represented+dropped)) is recomputable and the dropped-branch reasons hold. Never demand IDs the export lacks.

**Input**
1. Scenarios (full file): {scenarios}
2. Requirement AC and Edge Cases: {requirements_ac_and_edge}
3. Plan context: {plan_context}
4. Whitelist (code paths you may open): {whitelist}

Lens 1 — contract (input documents only):
(a) AC mapping: a scenario with no AC reference, or one that does not match a real AC; an AC no scenario covers.
(b) Each operation the contract defines has happy, sad, edge and error cases.
(c) Dependency declarations: a scenario marked independent ("독립 실행: 가능" / own Setup) that relies on another's state.
(d) Assertions that pin HOW instead of WHAT, need manual or subjective judgment, or are flaky (timing, external service, order).
(e) Assertions on endpoints, fields or values no input document defines.

Lens 2 — survivor (may Read files in {whitelist} only):
"If every scenario passes, which bug survives?" Look for destruction paths, untested state transitions, races and corruption paths. Report only plausible bugs, not theoretical edge cases.

Do not run Bash, Grep or Glob, and open no file outside the whitelist.

Rules:
1. Cite the native reference unit for every finding. A finding without one is void.
2. Do not invent IDs, titles or step numbers that are not in the input.
3. No concrete evidence (which assertion, why wrong) → no finding.
4. At most one proposed scenario per High or Medium finding.
5. Tag every finding with `fix: scenario` or `fix: upstream:<doc> (editorial|semantic)`. editorial = wording, terms, references, typos, number formats: the set of AC and what pass/fail means do not change. semantic = adding, removing or changing an AC or expected value, or changing a plan decision.
6. Return the result in the reply only. Do not write files.

Output format:
### High
- [lens: contract|survivor] [fix: scenario | upstream:<doc> (editorial|semantic)] {finding with reference} → {proposed scenario, at most one}
### Medium
- ...
### Low
- ...
```

## Re-check Prompt

Use this instead of the Full Review Prompt when `docs/test-scenarios/scenarios-review.md` already exists.

1. Changed references: run `git log` on the review file to find its last commit, then `git diff <that commit> -- <scenarios file>` and collect the IDs (or golden-path titles) whose text changed or appeared.
2. If that cannot be computed (no history, the review is not committed), run the Full Review Prompt instead and write one line in the report saying why.
3. Dispatch the prompt below once. The verdict counts this pass only: prior findings judged unresolved or regressed, plus new findings.
4. Review results pasted inside the scenarios file itself are context only; evaluate independently.

```
You are re-checking a prior review, not reviewing from scratch.

Input schema: {{discover | golden-path}}

**Input**
1. Prior findings (F-N, as written in the prior review): {prior_findings}
2. Changed references since that review: {changed_ids}
3. Scenarios (full file): {scenarios}
4. Requirement AC and Edge Cases: {requirements_ac_and_edge}
5. Whitelist: {whitelist}

Judge every prior finding resolved | unresolved | regressed with a one-line reason. Raise new findings only inside {changed_ids}. The lens, tool and citation rules of the Full Review Prompt apply.

Output format:
### Prior findings
- F-N: resolved|unresolved|regressed — {reason}
### New findings
- [lens: contract|survivor] [fix: scenario | upstream:<doc> (editorial|semantic)] {finding} → {proposed scenario, at most one}
```
