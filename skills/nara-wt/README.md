# nara-wt — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Create a git worktree for a Jira ticket. Fetches the ticket summary, generates a kebab-case slug, asks the user for a git type prefix (never auto-mapped from Jira issue type), and invokes the shell `wt` helper to create the worktree at `../{repo}-{ticket}-{slug}`.

## 호출

- Claude Code: `/nara-wt`
- Codex: `$nara-wt`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "wt", "/nara-wt TICKET-ID", "worktree 만들어", "워크트리 생성", "create worktree from ticket".
- **DO NOT USE FOR:** switching worktrees (use `cd`), removing worktrees (use `git worktree remove`), creating branches without a ticket (use plain `wt <branch>` in shell), or PR creation (use `/nara-pr`).

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
