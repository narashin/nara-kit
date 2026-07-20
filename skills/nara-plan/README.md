# nara-plan — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Split a spec or request into independently verifiable VERTICAL work units — each with its own goal, scope, acceptance criteria, and verification — written to docs/plan.md. This is the dev-mode plan step. Never implements code or posts to a remote tracker.

## 호출

- Claude Code: `/nara-plan`
- Codex: `$nara-plan`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "plan", "계획 짜줘", "작업 나눠", "수직 분할", "작업 단위로 쪼개", dev-mode plan step.
- **DO NOT USE FOR:** 스펙 작성 (→ nara-prep / doc-mode), 구현 (→ nara-implement), 원격 Jira 티켓 생성 (→ nara-slack-to-jira).

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
