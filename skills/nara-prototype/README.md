# nara-prototype 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Build and run a throwaway prototype (2 UI variants or a logic harness with realistic example I/O) to answer one decision question, then report a Pass | Fail | Blocked | Unverifiable verdict against measurable criteria.

## 호출

- Claude Code: `/nara-prototype <결정 질문 또는 아이디어> [--ref <스펙 | 티켓 | 스크린샷 | 코드 경로>] [--keep]`
- Codex: `$nara-prototype ...`

## 언제 쓰나

- **USE FOR:** "프로토타입 만들어", "A안 B안 비교해 봐", "이 방식 되는지 빨리 확인", "prototype", "spike 돌려봐", "harness로 검증".
- **DO NOT USE FOR:** 구현자 핸드오프용 화면 디자인·시안 (→ nara-design-studio), 실제 기능 구현 (→ nara-implement), 실제 기능의 브라우저 AC 판정 (→ nara-browser-verify), 외부 접근법 조사 (→ nara-research).

## 왜 있나

"A안과 B안 중 뭐가 낫지", "이 방식이 되긴 하나"를 정할 때 대화로만 추측하거나, 반대로 실제 코드에 바로 짜 넣는 일이 많았다. 이 스킬은 그 사이에서 버릴 프로토타입을 만들어 실제로 돌리고, 기준 대비 결과를 리포트 한 장으로 남긴다. 기준은 만들기 전에 정하고, 실행마다 명령과 exit code를 남기고, 가짜 연동은 가짜라고 적는다.

저장소가 이미 답을 갖고 있으면 만들지 않는다. 프로토타입은 production 코드로 승격하지 않는다. 채택하면 `nara-implement`가 실제 구현을 맡는다.

## 산출물

`docs/prototypes/<slug>/REPORT.md`. 골격은 [references/report-format.md](references/report-format.md). `docs/`는 git에 무시되는 것이 전제이고, 아니면 `Blocked`로 멈춘다.

## 설계 메모

출발점은 MTGVim/tiger-kit의 `tk-prototype`(`5e35b6a`, MIT)이다. 가설과 기준 선행, 결정 차원만 바꾸는 변형, fake/real 경계, 실행 영수증, 리포트 절 순서, 실패 표를 가져왔고 본문은 새로 썼다. `.tigerkit/` 경로와 ignore 자동 설정, 공용 HTML 테마 자산과 차트 가이드, 호스트 리소스 부하 단계, PR 게시용 evidence manifest는 가져오지 않았다. nara-kit 산출물은 `docs/` markdown이 관례이고, 브라우저 증거는 `nara-browser-verify`가 이미 소유한다.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
