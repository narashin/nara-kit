# nara-workflow-doc-mode — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Run documentation-first workflow producing specs, RFCs, design docs, or planning artifacts. Routes by requirement clarity: clear → nara-grill → nara-prep → spec, vague → nara-ac-draft → nara-prep → spec.

## 호출

- Claude Code: `/nara-workflow-doc-mode`
- Codex: `$nara-workflow-doc-mode`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "doc mode", "기획 모드", "spec 작성", "RFC", "설계 문서".
- **DO NOT USE FOR:** direct code implementation, bug fixes, test writing.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
