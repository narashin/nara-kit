# nara-gap — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Analyze gap between docs/requirements.md and codebase, producing docs/gap.md with a score (0-100).

## 호출

- Claude Code: `/nara-gap`
- Codex: `$nara-gap`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "gap", "gap 분석", "구현 얼마나 됐어", "요구사항 대비 진행률", "--verify".
- **DO NOT USE FOR:** writing requirements (use /nara-prep), code implementation, code review.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
