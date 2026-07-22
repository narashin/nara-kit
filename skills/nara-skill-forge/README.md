# nara-skill-forge — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

스킬 개선·강화·벤치마크: Waza 정적 분석 + eval grader + EPT subagent 실행 + working-tree regression ratchet.

## 호출

- Claude Code: `/nara-skill-forge`
- Codex: `$nara-skill-forge`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "skill 개선해줘", "스킬 개선해줘", "스킬 강화", "improve skill", "harden skill", "benchmark skill", "forge skill"
- **DO NOT USE FOR:** 툴킷 friction 리포트 (→ nara-meta-feedback), 스킬 아닌 프롬프트 튜닝 (→ nara-empirical-prompt-tuning), 신규 스킬 작성

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
