# nara-browser-verify — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Judge browser-visible acceptance criteria in a headless runtime, returning a per-axis verdict backed by runtime evidence (trusted input, network request/response, actually-inspected screenshots) — never a static guess.

## 호출

- Claude Code: `/nara-browser-verify`
- Codex: `$nara-browser-verify`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "브라우저 AC 검증", "이 화면 AC 통과했나", "런타임으로 확인해줘", "headless 검증", "browser-verify", dev-mode verify step for browser-visible AC.
- **DO NOT USE FOR:** env↔local 비교 (→ nara-ui-diff), 스샷 캡처 (→ nara-local-shot), 테스트 코드 작성 (→ nara-test-implement), 코드 AC 갭 분석 (→ nara-gap). E2E 시나리오 발굴은 → nara-golden-path-discover, 코드 diff 리뷰는 → nara-code-review.

## 이웃 스킬과의 차이

| 스킬 | 하는 일 | 결론 |
|---|---|---|
| `nara-browser-verify` | 승인된 criterion을 런타임에서 판정 | `Pass/Fail/Blocked/Unverifiable` |
| `nara-ui-diff` | 배포 baseline ↔ 로컬을 같은 조건으로 비교 | drift **후보** (판정은 사람) |
| `nara-local-shot` | 스크린샷 파일 생성 | 이미지 파일 |
| `nara-test-implement` | Playwright 테스트 **코드** 작성 | 커밋되는 테스트 |

## 설정

제품값(대상 URL·dev 서버 명령·로그인 경로)은 소비 repo가 소유한다. `.claude/ui-diff/env.md`가 있으면 재사용하고, 없으면 호출 시 인자 또는 `docs/plan.md`의 `검증` 필드에서 받는다. 증거는 `.claude/browser-verify/runs/<ts>/`에 남으며 gitignore 확인을 통과해야 한다.

서버 기동·auth bypass·드라이버 사다리는 같이 설치된 형제 스킬(`nara-local-shot`, `nara-ui-diff`)의 reference를 링크해 재사용한다 — 단독 설치 시 해당 링크는 스킵되고 repo 근거로 판단한다.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
