# nara-publish-spec — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Publish a local spec/plan markdown file to Confluence wiki via dry-run, confirm, and publish flow.

## 호출

- Claude Code: `/nara-publish-spec`
- Codex: `$nara-publish-spec`
- 자연어 트리거 없음. 원격에 쓰는 스킬이라 명시 호출만 받는다(Claude Code `disable-model-invocation`, Codex `agents/openai.yaml`). 아래 USE FOR는 언제 부를지에 대한 안내다

## 언제 쓰나

- **USE FOR:** "publish", "wiki에 올려", "confluence에 게시", "publish-spec", "스펙 게시".
- **DO NOT USE FOR:** creating specs from scratch (use nara-prep), editing existing Confluence pages directly.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
