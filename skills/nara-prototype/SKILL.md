---
name: nara-prototype
description: >-
  Build and run a throwaway prototype (2 UI variants or a logic harness with realistic example I/O) to answer one decision question, then report a Pass | Fail | Blocked | Unverifiable verdict against measurable criteria.
  USE FOR: "프로토타입 만들어", "A안 B안 비교해 봐", "이 방식 되는지 빨리 확인", "prototype", "spike 돌려봐", "harness로 검증".
  DO NOT USE FOR: 구현자 핸드오프용 화면 디자인·시안 (→ nara-design-studio), 실제 기능 구현 (→ nara-implement), 실제 기능의 브라우저 AC 판정 (→ nara-browser-verify), 외부 접근법 조사 (→ nara-research).
---

# prototype: 결정 하나를 위한 일회성 프로토타입

> 출력 형식은 [nara-kit 출력 계약](../nara-now/references/output-contract.md)을 따른다. 이 본문이 다르게 정한 곳은 본문이 우선한다. 파일이 없으면(단독 설치) 이 줄은 건너뛴다.

질문 하나("어느 쪽이 나은가", "이 방식이 되는가")에 답하려고 버릴 프로토타입을 만들고 실행한다. 종류는 둘이다. **UI 변형**은 기본 2개이고, 3번째는 독립적인 가치를 더할 때만 만든다. **로직 harness**는 현실적인 예시 입력과 기대 출력으로 접근법을 돌려 본다. 화면을 설계해 넘기는 일은 `nara-design-studio`, 실제 구현은 `nara-implement`가 맡는다.

출처: tiger-kit `tk-prototype`(MTGVim/tiger-kit `5e35b6a`, MIT)에서 가설·기준 선행, 결정 차원만 바꾸기, fake/real 경계, 실행 영수증, 리포트 절 순서, 실패 표를 가져왔다. `.tigerkit/` 경로, 공용 HTML 테마 자산, 차트 가이드, 리소스 부하 단계, 게시용 evidence manifest는 뺐다. 경로는 `docs/`가 관례이고, 리포트는 markdown이면 충분하다.

## Core Rules

1. **가설과 기준이 먼저다**: 만들기 전에 아이디어를 가설 하나와 측정 가능한 기준으로 바꾼다. 기준은 관찰하거나 잴 수 있어야 한다. 감사받지 않은 미적 선호("더 깔끔해 보인다")는 기준이 아니다.
2. **저장소가 이미 답하면 만들지 않는다**: 코드·테스트·문서가 질문을 이미 가르면 프로토타입을 만들지 않고 첫 줄에 정확히 `프로토타입 불필요: 저장소 근거로 이미 결정됨`이라고 쓴 뒤 근거 파일과 라인을 인용한다. 이때 리포트 파일과 `## Tested`는 만들지 않는다.
3. **결정에 걸린 차원만 바꾼다**: 변형 사이에서 내용·데이터·상호작용 상태는 같게 두고, 질문이 묻는 차원만 다르게 한다. 색이 질문이면 색만, 흐름이 질문일 때만 흐름을 바꾼다.
4. **저장소 스택을 재사용한다**: 이미 설치된 런타임·UI 스택·컴포넌트·토큰으로 격리된 route나 harness를 만든다. manifest와 lockfile은 건드리지 않는다. 새 의존성이 필요하면 `→ ESCALATE:`로 이유와 대안을 적고 멈춘다.
5. **연동마다 fake | real을 선언한다**: API, DB, 인증, 외부 서비스마다 가짜인지 실제인지 적는다. 가짜 연동을 실제처럼 보고하지 않는다.
6. **실행 증거 없이는 Pass가 없다**: 모든 실행을 `## Tested`에 명령, cwd, exit code, 출력, 증거 경로로 남긴다. 명령을 요약하지 않고 실제로 실행한 값을 적는다.
7. **브라우저에 보이는 주장은 runtime 증거로 판정한다**: 화면 동작이나 시각 차이에 대한 주장은 [nara-browser-verify](../nara-browser-verify/SKILL.md)의 절차로 확인한다(같이 설치된 스킬 파일. 없으면 그 주장들을 `Unverifiable`로 표시하고 나머지만 판정한다).
8. **승격하지 않는다**: 프로토타입을 production-ready라고 부르지 않고, 실제 코드로 옮기거나 stage·commit하지 않는다. 범위가 실제 구현으로 넘어가면 `Blocked`로 멈추고 `nara-implement` 요청으로 분리한다.
9. **자기가 만든 것만 치운다**: 실행 전에 이미 있던 경로를 기록하고, 이번 실행이 만든 파일·프로세스만 정리한다. 기존 route, 의존성, production 소스는 보존한다.

## 인자 ($ARGUMENTS)

`nara-prototype <결정 질문 또는 아이디어> [--ref <스펙 | 티켓 | 스크린샷 | 코드 경로>] [--keep]`

`--keep`은 실행 후에도 변형 파일을 남긴다. 기본은 run-owned 변형·harness 코드를 지우고, 리포트와 리포트가 증거로 인용한 실행 출력은 남긴다.

## Procedure

1. **가설**: 질문, 가설, 측정 기준, 제외 범위를 적는다. 저장소를 읽어 이미 답이 있는지 본다. 있으면 Core Rule 2로 끝낸다.
2. **경계 조사**: 실행 명령, UI 스택, 컴포넌트, 토큰, 테스트 러너를 확인한다. 임시 경로 `docs/prototypes/<slug>/`가 무시되는지 저장소 루트에서 `git check-ignore -q docs/prototypes/<slug>/`로 확인한다. exit 0이면 진행하고, 그 외에는 `.gitignore`를 고치지 않고 `Blocked`로 멈춘다. 해당 경로에 이미 있는 파일 목록을 기록한다.
3. **체크포인트 (1회)**: 만들기 전에 사용자에게 한 번에 묻는다. 임시 경로, 연동별 fake/real 데이터, 검증 질문과 기준, 변형 수 또는 harness 형태. 이 질문 블록은 그 턴의 마지막 블록이다. 뒤에 "확인되면 만들겠다" 같은 문장을 붙이지 않는다. 이미 같은 범위를 승인받았으면 다시 묻지 않는다.
4. **만들기**: UI 변형은 넓은 화면에서 나란히, 좁은 화면에서 세로로 쌓는다. 동시 렌더가 비교를 해칠 때만 A/B 토글을 쓴다. 로직은 작은 순수 harness와 최소 adapter로 만든다. 저장소에 안전한 격리 route가 없으면 `docs/prototypes/<slug>/` 안에 정적 파일로 만든다.
5. **실행**: 변형과 harness를 실제로 돌리고 출력과 스크린샷을 남긴다. 반응형이 질문일 때만 넓은 폭과 좁은 폭을 둘 다 확인한다. 기준이 fake 값(API 지연, 데이터 크기, 동시 사용자 수)에 따라 갈리면 그 값을 한 점에 고정하지 말고 기준이 뒤집히는 경계까지 바꿔 가며 돌린다. 경계값이 곧 `## Production implication`에 적을 조건이다.
6. **비교와 리포트**: 증거를 기준에 매핑해 [report-format](references/report-format.md)의 골격으로 `docs/prototypes/<slug>/REPORT.md`를 쓴다. 관찰 안 된 차이는 `not observed`, 증거가 없는 칸은 `unverifiable`로 적는다.
7. **정리와 점검**: run-owned 파일과 프로세스를 정리하고 결과를 `## Variants or harness`에 `kept | removed`로 남긴다. 명령, 실제 출력, fake/real 경계, 미검증 범위 중 하나라도 비면 판정은 `Pass`가 될 수 없다.

## Output (receipt)

```
프로토타입 비교 완료 (recorded only).
- 질문: 검색창 debounce를 leading으로 할지 trailing으로 할지
- 판정: Pass · B안(trailing 300ms)이 기준 3개 중 3개 충족
- 실행 4회 (exit 0: 4) · fake 연동 1 (검색 API)
- artifact: `docs/prototypes/search-debounce/REPORT.md`
- next: 채택 여부 결정. 채택이면 `/nara-implement`로 실제 구현
```

## Trailing status (필수)

```
prototype: <REPORT.md 경로> | none (<사유>)
kind: ui-variants | logic-harness | none
runs: N (exit 0: a / nonzero: b)
fake: N 연동 (<이름 나열> | 없음)
verdict: Pass | Fail | Blocked | Unverifiable
```

`verdict:`는 넷 중 정확히 하나만 적는다. 리포트도 같은 `verdict:` 줄로 끝난다. 판정은 변형별이 아니라 **질문 전체**에 매긴다: `Pass` = 근거로 답이 났고 고른 안이 기준을 모두 넘음, `Fail` = 어느 안도 기준을 다 넘지 못함, `Blocked` = 환경이나 권한 때문에 실행 못 함, `Unverifiable` = 실행은 했으나 판정에 필요한 증거가 없음. 진 안이 기준을 못 넘은 것은 `Fail`이 아니라 비교 결과다. `runs:`는 `## Tested` 기록 수와 같게 센다.

## Error Handling (if-then)

| 조건 | 대응 | 판정 |
|---|---|---|
| 저장소 근거가 이미 질문을 가름 | `프로토타입 불필요: 저장소 근거로 이미 결정됨` + 근거 인용, 파일 안 만듦 | 없음 (`verdict:` 생략, `prototype: none`) |
| `docs/prototypes/`가 git에 무시되지 않음 | `.gitignore`를 고치지 않고 경로 문제를 보고 | `Blocked` |
| 새 의존성 없이는 실행 불가 | `→ ESCALATE:`로 패키지·이유·대안 제시 후 정지 | `Blocked` |
| 런타임·서버·harness가 환경 문제로 안 뜸 | 명령, exit code, 출력, 경계를 보존 | `Blocked` |
| 실행은 됐으나 출력·스크린샷 증거가 없음 | 같은 경계 안에서 한 번 더 캡처 | 여전히 없으면 `Unverifiable` |
| browser-verify 스킬이 없음 | 브라우저 주장만 `unverifiable` 칸으로 | 그 주장에 기댄 판정은 `Unverifiable` |
| 실행했고 기준을 못 넘음 | 어느 기준이 왜 실패했는지 기록 | `Fail` |
| 기존 경로·파일과 소유권 충돌 | 기존 것을 보존하고 다른 경로를 고른다 | 못 고르면 `Blocked` |
| 범위가 실제 구현·승격·커밋으로 커짐 | 프로토타입을 멈추고 구현 요청으로 분리 | `Blocked` |

## References

- [report-format.md](references/report-format.md): `REPORT.md` 골격, `## Tested` 영수증 필드, 판정 4종의 뜻, 짧은 예시
