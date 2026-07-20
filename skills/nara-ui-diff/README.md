# nara-ui-diff — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Env-diff visual regression check: drive a QA/Prod baseline and a local target through the SAME screen at the SAME viewport/auth/context, measure computed-style + getBoundingClientRect on both, report ONLY the differing values as drift candidates (human decides regression vs intended). Depends on chrome-devtools/playwright MCP.

## 호출

- Claude Code: `/nara-ui-diff`
- Codex: `$nara-ui-diff`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "ui-diff", "env diff", "환경 비교", "QA랑 로컬 비교해줘", "마이그레이션 후 디자인 안 깨졌나", "리팩터 전후 스타일 비교", "visual regression check", "computed style diff", "prod vs local UI".
- **DO NOT USE FOR:** figma-diff / design-node vs runtime (OUT OF SCOPE — future ui-diff mode, not built), golden-path E2E scenario authoring (→ nara-golden-path-discover), running/writing Playwright test code (→ nara-test-implement), code diff review (→ nara-code-review), pixel-screenshot-only "looks similar" checks (screenshots are supporting evidence only here).

## 설정

로컬 설정 파일(`*.local.md`)이 필요할 수 있음. 자세한 절차는 [SKILL.md](SKILL.md) 참고.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
