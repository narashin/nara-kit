# nara-adversarial-review — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

기존 리뷰 리포트를 공격적으로 검증: 오탐 격추(refuter) + 블라인드 누락 사냥(blind
hunter) + 리포트 무결성 감사(rigor auditor). 원 리포트에 append-only.
`/codex:adversarial-review`의 네이티브 대안 — codex 없이 동작, 겹쳐 돌려도 됨.

## 호출

- Claude Code: `/nara-adversarial-review [report-path]`
- Codex: `$nara-adversarial-review`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "리뷰 리포트 공격해", "이 리뷰 오탐 없나", "리뷰 빠진 거 찾아", "adversarial review", "리뷰 검증해줘", after a nara-code-review report.
- **DO NOT USE FOR:** 리뷰 자체 생성 (→ nara-code-review), 원격 PR 리뷰 (→ nara-pr-review), 코드 수정 (→ nara-implement), 설계 검증 (→ nara-grill).

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
