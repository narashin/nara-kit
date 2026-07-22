# nara-empirical-prompt-tuning — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Iterate and improve agent-facing instructions by dispatching bias-free executors and evaluating two-sidedly until improvements plateau.

## 호출

- Claude Code: `/nara-empirical-prompt-tuning`
- Codex: `$nara-empirical-prompt-tuning`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "프롬프트 튜닝", "EPT", "prompt tuning", "improve prompt".
- **DO NOT USE FOR:** 스킬 개선/강화/벤치마크 (→ nara-skill-forge), one-off throwaway prompts, subjective style preferences, direct skill authoring (use skill-development).

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
