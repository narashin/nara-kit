# nara-merge-conflict — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Resolve merge/rebase conflicts by reconstructing ours-intent vs theirs-intent per hunk, surfacing both as candidates for human decision.

## 호출

- Claude Code: `/nara-merge-conflict`
- Codex: `$nara-merge-conflict`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "머지 충돌", "merge conflict", "rebase 충돌", "충돌 해결", "resolve conflict", "conflict marker".
- **DO NOT USE FOR:** conflict-free PR merge (use pr), branch teardown (native finish sequence — see Rules), general git ops.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
