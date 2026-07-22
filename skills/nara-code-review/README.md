# nara-code-review — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Multi-agent parallel code review + auto-fix for local commits.

Evidence-based 구조: 직교 리뷰어(코어 4: behavior-state / contracts-compatibility /
resilience-data-integrity / tests-regression + 조건부 6: security-privacy /
performance-resources / architecture-reuse / frontend-ux-a11y / database-migration /
operations-config) → blind Judge → 중앙 Fixer(위험등급 R0–R3, 기본 `--fix=safe`) →
issue 단위 Verifier(hash/hunk + validation proof).

## 호출

- Claude Code: `/nara-code-review`
- Codex: `$nara-code-review`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "리뷰해줘", "코드 검수", "버그 찾아줘", "review code", "check for bugs", "audit code", "cleanup", or before committing.
- **DO NOT USE FOR:** PR review on remote (→ nara-pr-review), production incident root-cause (→ nara-incident), refactoring, or documentation-only changes.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
