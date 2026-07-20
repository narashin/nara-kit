# nara-jira-drain — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Launch a chosen jira-triage queue ticket into a herdr worktree (space = repo@branch) running claude, and drive dev-mode/doc-mode to a PR — interactive ($0), human-triggered.

## 호출

- Claude Code: `/nara-jira-drain`
- Codex: `$nara-jira-drain`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "jira-drain", "큐 티켓 착수", "이 티켓 돌려", "/nara-jira-drain KEY".
- **DO NOT USE FOR:** 큐 생성·분류 (→ jira-triage), PR 리뷰 (→ review-queue), 큐 없이 직접 (→ /nara-wt + dev-mode).

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
