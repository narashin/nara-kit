---
name: nara-publish-verify
description: >-
  Verify published GitHub PR assignee, attribution and selected AI commit metadata, read-only.
  USE FOR: "PR 게시 검증", "트레일러 확인", "PR 담당자 확인", "publish verify", post-publication metadata checks.
  DO NOT USE FOR: creating or editing PRs, Jira assignment, code review, merging or deployment.
---

# Publish Verify

> 출력 형식은 [nara-kit 출력 계약](../nara-now/references/output-contract.md)을 따른다. 이 본문이 다르게 정한 곳은 본문이 우선한다. 파일이 없으면(단독 설치) 이 줄은 건너뛴다.

Confirm the PR URL/host, expected assignee and exact trailer from trusted configuration, user/repository policy and the actual authoring agent. Ask for missing policy. Do not infer assignee from PR author or hardcode project identities.

Select full AI-assisted commit SHAs from run evidence or user input. Exclude human commits. Unknown AI scope cannot pass.

Run [the verifier](scripts/verify.py) after all approved PR body/image changes, using Python 3.10+ and authenticated `gh`:

```bash
python3 <skill-dir>/scripts/verify.py <pr-url> \
  --host <confirmed-host> --assignee <confirmed-login> \
  --trailer '<confirmed-Co-authored-by-line>' --commit <full-sha>
```

Repeat `--commit` for each selected commit. Never interpolate PR content into shell commands. The script reads PR metadata twice and every commit page. It checks the final PR trailer, assignee membership and selected commits' subject + blank line + one trailer without body. Require confirmed agreement with this commit policy; otherwise report unsupported policy.

Report `pass` (exit 0), `fail` (1), or `unverifiable` (2), PR URL/head, selected versus unchecked commits and discrepancies. Missing data, authentication failures, pagination limits or concurrent changes cannot pass. Verify metadata only, not code, review approval or deployment readiness. Never claim who assigned an existing assignee.

Keep this skill read-only: no metadata fixes, Jira assignment, commit rewrites, push, merge or deployment. Return discrepancies for separate authorization. Preserve commit hooks.

Run [fixture tests](scripts/test_verify.py) with unittest discovery when changing the verifier.
