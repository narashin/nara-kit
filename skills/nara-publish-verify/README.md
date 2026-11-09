# nara-publish-verify

Verify published GitHub PR assignee, attribution and selected AI commit metadata, read-only.

Invoke `/nara-publish-verify <PR URL>` in Claude Code or `$nara-publish-verify <PR URL>` in Codex. Supply confirmed host, assignee, trailer and AI-assisted commit scope when they are not already known.

USE FOR: PR 게시 검증, 트레일러 확인, PR 담당자 확인, publish verify, post-publication metadata checks.

DO NOT USE FOR: creating or editing PRs, Jira assignment, code review, merging or deployment.

The verifier requires Python 3.10+ and authenticated `gh`. It makes GET requests only and never repairs remote state. A pass covers only observed metadata and explicitly selected commits.

[Skill instructions](SKILL.md) · [Catalog](../README.md)
