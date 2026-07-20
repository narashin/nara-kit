# nara-design-pack-builder — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Extract a nara-design-studio DS pack (tokens + standalone component bundle + manifest) from a React design-system codebase, via a guided, verify-as-you-go protocol. React-first; flags non-React sources as manual.

## 호출

- Claude Code: `/nara-design-pack-builder`
- Codex: `$nara-design-pack-builder`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "build a design studio pack", "extract a DS pack", "make my design system work with design-studio", "pack-builder".
- **DO NOT USE FOR:** designing screens (use nara-design-studio), non-React design systems (manual pack), backend work.

## 설정

로컬 설정 파일(`*.local.md`)이 필요할 수 있음. 자세한 절차는 [SKILL.md](SKILL.md) 참고.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
