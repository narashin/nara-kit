# nara-local-shot — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Capture screenshots of a locally-running web app — even auth/SSO-gated pages — for PR visual comparison or UI verification, then save the image files. Drives a local dev server + chrome-devtools MCP, bypassing SSO with a dummy session cookie when the target page needs no real backend.

## 호출

- Claude Code: `/nara-local-shot`
- Codex: `$nara-local-shot`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "스샷 찍어줘", "PR 스샷", "before/after 캡쳐", "visual comparison 이미지 만들어", "로컬 앱 스샷", "capture a screenshot of the local app", "as-is/to-be 스샷".
- **DO NOT USE FOR:** env-diff visual regression across QA/prod (use nara-ui-diff), figma-vs-runtime diff, writing/running Playwright test code (use nara-test-implement), 브라우저 AC 판정 (use nara-browser-verify).

## 이웃 스킬과의 차이

| 스킬 | 하는 일 | 결론 |
|---|---|---|
| `nara-local-shot` | 스크린샷 파일 생성 | 이미지 파일 |
| `nara-browser-verify` | 승인된 criterion을 런타임에서 판정 | `Pass/Fail/Blocked/Unverifiable` |
| `nara-ui-diff` | 배포 baseline ↔ 로컬을 같은 조건으로 비교 | drift 후보 (판정은 사람) |

## 알아둘 것

- 캡처는 **직접 저장까지** 한다 — PR 본문에 `_drag image here_` 자리표시자만 남기지 않는다. 사람은 마지막 드래그-드롭만.
- SSO 우회는 **더미 쿠키가 통하는 페이지에만** 유효하다(미들웨어가 값 유효성이 아니라 존재만 검사할 때). 실제 API를 호출하는 페이지는 진짜 `storageState`가 필요하다 — [references/auth-bypass.md](references/auth-bypass.md).
- Before/After는 **서로 다른 리비전의 렌더 2장**이다. 비싼 건 사진이 아니라 앱을 띄우는 과정이라, 두 패스를 미리 계획한다 — [references/comparison-passes.md](references/comparison-passes.md).

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
