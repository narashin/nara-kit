# nara-incident — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Generate a structured incident analysis report with root cause hypotheses, evidence, and proposed fix.

## 호출

- Claude Code: `/nara-incident`
- Codex: `$nara-incident`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "incident", "/nara-incident TICKET", "장애 분석", "버그 원인 찾아", "root cause".
- **DO NOT USE FOR:** code modification (use /nara-incident-fix), general debugging, code review.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
