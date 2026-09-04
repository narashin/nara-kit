# Changelog

nara-kit의 모든 주요 변경을 기록한다. 형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/),
버전은 [Semantic Versioning](https://semver.org/lang/ko/)을 따른다.

nara-kit은 매니페스트 없는 Agent Skills repo — `main` 브랜치가 곧 릴리즈이고 git tag가 immutable snapshot이다.
각 tag = 여기의 한 버전 섹션. tag가 없는 진행 중 변경은 `[Unreleased]`에 쌓인다.

호환성 규칙(major 판정): 스킬 이름 삭제·rename, invocation 방식 변경, 산출물 경로 변경은 consumer에게 breaking.
단 `0.x` 구간에서는 semver 관례대로 breaking을 minor로 올린다 — `1.0.0`은 API 안정 선언으로 읽히므로 표면이 굳은 뒤에 붙인다.

## [Unreleased]

### Fixed

- `nara-pr-activity-reminder`가 **`main`에 없었다** — `multica-agent` 브랜치에만 존재하고 머지된 적이 없어, `main`이 곧 릴리즈인 이 repo에서 소비자에게 배포되지 않았다. 실행 주체(`~/.local/bin/pr-activity-reminder.py`)는 git 밖이라 동작에는 영향이 없었고, 없어진 것은 계약 문서와 배포였다. 그 브랜치는 `main`보다 39커밋 뒤처져 통째 머지하면 `evals/` 전체가 삭제로 들어가므로 스킬 디렉터리만 꺼내왔다
- 스킬 카운트가 49에 멈춰 있었다 — 실제 54개(`nara-` 53 + `naranizer`). 스킬을 추가할 때 `README.md`·`CLAUDE.md`·`skills/README.md` 카운트 갱신이 반복적으로 빠진다
- 8-리뷰어 코드 리뷰 반영 — `nara-worklog`·`nara-release-watch`·`eval-fixture` 신규 Python 933 LOC 대상. raw 51건 → R0/R1 21건 적용, R2/R3 17건 이월. 리포트: `docs/review/260902-worklog-release-watch-eval-fixture.md`
  - **`fetch_versions`가 gh 실패를 "버전 없음"으로 오분류했다.** 판정이 `releases is None and tags is None`이라, 태그만 쓰는 repo(releases가 정상적으로 `[]`)에서 tags 호출만 실패하면 `unwatchable`로 낙인하고 `unwatchable_reported`를 영구 기록해 **그 repo가 영원히 조용해졌다**. 단계별 조기 반환으로 교체 — 부수적으로 실패 확정 후 두 번째 호출을 하지 않으므로 전 repo 실패 시 왕복이 절반이 된다
  - **`PRERELEASE_RE`에 단어 경계가 없어 정식 릴리즈가 사라졌다.** `v1.0.0-aarch64`(a**rc**h64), `-source`(sou**rc**e), `-devtools`, `-nextgen`이 prerelease로 오탐. 구분자 앵커(`(?:^|[-._+])`)로 교체하고 안정 태그 부정 케이스 6종을 테스트로 고정
  - **`--through`에 offset 없는 값이 들어가면 ledger가 영구 오염됐다.** naive watermark가 hook의 aware `ts`와 비교되며 `TypeError`를 내고, `list`는 디렉터리 전체를 훑으므로 **오염된 티켓 1개가 모든 티켓 조회를 죽였다.** `cmd_record`가 거부(exit 1, ledger 무변경)하고 `watermark()`는 디스크에 이미 있는 값을 승격한다
  - `gh_json`이 `OSError`·`SubprocessError`를 잡는다 — docstring이 "any failure"를 주장했지만 gh 미설치·hang은 예외를 전파해 repo 1개가 poll 전체를 죽였다
  - `argparse` 플래그를 서브커맨드 양쪽에서 사용 가능하게. **리뷰 중 자체 발견**: `parents=[common]`의 서브파서 default가 루트 파싱값을 clobber해서 `--state X list`가 X를 무시하고 **실제 state 파일**을 읽었다 — 원래 문제보다 나쁜 회귀였다. `argparse.SUPPRESS` + `apply_defaults()`로 해소
  - `total_seconds`를 날짜별 **내림값의 합**으로. Jira는 날짜당 1회 쓰이므로 raw 초 합계는 날짜별로 버린 잔여를 되살려 실제 게시량보다 크게 보고했다(하루 최대 59초 × 날짜 수). `unpostable_days` 필드 추가
  - hook의 `os.makedirs`를 티켓 매칭 판정 **앞으로** — 배선이 정상인데 디렉터리가 없어서 스킬이 "hook 미설치"로 오판하고 **거짓 재설치 루프**를 유발했다
  - `save_state`가 `abspath`로 정규화(bare 상대 파일명에서 `os.makedirs("")` 크래시), watchlist 후행 주석 분리를 `\s+--\s`로 제한(`some/repo--name` 절단), `MIN_POSTABLE_SECONDS` 상수화(임계 드리프트)
  - `eval-fixture.py`: `find("{")`의 -1을 슬라이스에 그대로 써서 `[-1:]`이 마지막 한 글자가 되어 의도한 진단 에러가 발화하지 않던 것, probe stale 재사용으로 거짓 green이 나던 것, 채점 0건에 성공을 반환하던 공허 통과, provenance 필드를 그레이더가 읽는다는 거짓 주석
  - 테스트 46 → **93건**. 변이 테스트가 드러낸 무보호 지점을 고정했다 — API `prerelease` 플래그 단독 케이스(`rel(prerelease=True)` 호출이 0건이었다), `jira_started` **배선**(함수 단위 테스트만 있어 상수 치환에도 통과했다), `fetch_versions`/`gh_json`(테스트 참조 0건). `test_stamp.py` 신설 14건 — 69 LOC 훅이 모든 세션의 모든 턴에서 도는데 테스트가 없었다. `run()` 헬퍼가 `--gap-minutes`를 명시 전달해 환경 의존 거짓 실패(`NARA_WORKLOG_GAP_MINUTES=10`에서 5건 실패)를 제거
  - **hook 인터프리터 배선 수정** (PRF-001, 이월 예정이었으나 즉시 적용) — bare `python3`가 pyenv shim으로 해석돼 순수 오버헤드를 지불했다. 실측 **438.8ms → 55.1ms**(8배), 턴당 2회 발동이므로 약 0.77초 절감. `nara-review-gate.py`도 같은 배선이었고 PreToolUse라 **모든 Bash 호출마다** 발생했다
    - 버전을 고정하지 않는 폴백 체인을 쓴다: `for P in /opt/homebrew/bin/python3 /usr/bin/python3; do [ -x "$P" ] && exec "$P" <hook>; done; exit 0`. pyenv 버전 경로가 제일 빠르지만(18.8ms) 업그레이드로 사라지면 exec 실패로 **모든 턴이 막힌다**. `exec`가 종료 코드를 보존하므로 exit 2 차단이 유지되고, `; exit 0`이 두 경로 부재 시 fail-open을 보장한다(그것 없이는 마지막 `[ -x ]` 실패가 exit 1이 된다) — 셋 다 실측 확인
    - 두 hook 모두 3.9에서 컴파일되므로 `/usr/bin/python3`(3.9.6) 폴백이 유효하다. 이 파일에 3.10+ 문법을 쓰면 폴백이 깨진다

- **eval 점수가 측정처럼 보이는 가짜였던 것을 막았다.** `waza run nara-gap`이 `4 passed / 4 failed`를 내놓고 있었는데, executor가 `mock`이라 스킬이 호출되지 않는다(`tool_call_count: 0`). mock의 출력은 `프롬프트 + 태스크명 + description + 픽스처 원문`을 그대로 이어붙인 것이라, 통과한 4건은 **단정 문자열이 자기 description에 이미 적혀 있어서** 통과한 동어반복이었다 — `Score`는 description의 `"produces docs/gap.md with a score (0-100)"`에 대소문자 무시로 매칭됐다
  - 원인은 2026-08-26 `f4dd7ac`의 `real_run` 그레이더 제거다. 사유("mock에서 절대 통과 못 하는 단정은 게이트가 아니다")는 **행동 게이트로는 맞고 출처(provenance) 게이트로는 틀렸다**. 제거 전엔 항상 0/8로 시끄럽게 고장났고, 제거 후엔 4/8로 조용히 그럴듯해졌다 — 나쁜 쪽으로 바뀐 거래다
  - `real_run`(`len(output) > 40`, `'Mock response for:' not in output`)을 **45개 스위트 전체**에 출처 게이트로 복원했다. mock 실행은 이제 8/8 실패하며 이유를 명시한다. 판별력은 그대로 — RIGHT 8/8 통과 / WRONG 0/8 통과 확인
  - CLAUDE.md의 실행 방법이 **없는 명령**(`waza eval <skill>`)이었다. 실제는 `waza run`이고, 어느 경로가 무엇을 재는지(정적 `check`·구조적 `coverage`·행동 `grade`) 표로 명시했다
- `tools/eval-fixture.py` 추가 — 그레이더 판별력 검증을 `validate <skill>` 한 명령으로. 2026-08-24에 만들어졌지만 **untracked `results/`에 방치돼 유실 직전이던** `make-validation.py`를 일반화한 것이다. 테이블은 `evals/<skill>/validation.yaml`로 이관해 추적한다(`right`/`wrong`, task id 키). `wrong`은 **실제 관측된 실패**를 재현해야 한다 — 지어낸 실패는 판별이 너무 쉬워서 아무것도 증명하지 못한다
  - 이관 과정에서 테이블이 픽스처와 어긋난 것도 잡혔다: `iris-api@a1b2c3d`(정화 전 사내 repo명)를 픽스처의 placeholder `billing-api@a1b2c3d`로 맞췄다. 식별자 게이트가 잡아준 건이다
  - executor 블로커는 그대로다 — `copilot-sdk`는 seat 미할당, `mock`은 스킬을 호출하지 않는다. 즉 지금 측정 가능한 것은 **그레이더의 판별력**이고 스킬 행동은 실제 실행 경로가 뚫려야 한다

### Changed

- `nara-code-review`에 판단 모델 선택을 도입 — 리뷰어·Judge·Fixer 3역이 `$JUDGMENT_MODEL` 하나를 공유하고, Verifier는 `sonnet` 고정. 세 역할은 열린 판단(무엇이 문제인가·유효한가·어떻게 고치는가)이라 모델 성능에 직접 좌우되지만, Verifier는 hash/hunk에 앵커된 확인 작업이라 같은 값을 치를 이유가 없다
  - 리뷰어 dispatch 직전 1회 질문(`opus` 기본 권장 | `fable`)으로 정하고 재리뷰 라운드에서 다시 묻지 않는다. `--model=opus|fable`로 질문을 건너뛴다
  - 미가용 시 **다른 모델로 대체하지 않는다** — `model`을 생략해 세션 모델을 상속하고 실제 사용 모델을 리포트 헤더에 기록한다. 조용한 강등이 리포트에 안 보이면 낮은 발견율을 모델 탓으로 돌릴 수 없다
  - 오케스트레이션 자체(Flow 0–3, 5, 9)는 세션 모델 고정이다. 스킬 안에서 자기 모델을 바꿀 수 없다. 같은 이유로 main 세션이 직접 Fixer로 뛰면 배정 모델을 지킬 수 없으므로, 세션 모델이 배정 모델보다 약하면 위임하도록 명시했다
  - Verifier의 3단계 중 **Resolved만은 관측 hunk만으로 결정되지 않는다**(`failure_path`가 더 이상 성립하지 않는지 판단해야 한다). 결정 불가일 때 Verifier 모델에서 판정하지 말고 그 항목만 리뷰어 모델로 재dispatch한다
  - override는 이 값을 재배정할 수 있다. 자원 노브이지 base check가 아니므로 Conflict rule 대상이 아니다

- `nara-release-watch` 2단계 분리 — **watch**(매일, 판정 없음)와 **digest**(사람 트리거, 증류 판정). 임계(`@minor`)가 알림과 판정을 동시에 죽여서 릴리즈 잦은 repo(stablyai/orca: minor 고정 + 일간 패치)를 감시할 수 없던 것이 동기
  - watch는 새 릴리즈를 `highlights[]`(기계 필터: fix/chore 등 conventional prefix, "Notable changes" 마케팅 섹션, first-contribution 보일러플레이트 제거 — orca 실측 주간 617줄 중 8할이 fix)와 함께 판정 없이 알리고 큐(`~/.claude/release-watch-queue.json`)에 적재한다
  - digest는 큐 누적분(여러 repo)을 한꺼번에 4분류 판정한다 — 누적이라 교차 repo 패턴 판정이 가능해졌다. 읽기와 드레인(`digest --drain`)을 분리해 판정·배달 실패 시 백로그를 잃지 않는다
  - 두 단계를 별도 autopilot으로 등록한다 (watch 매일 08:47 KST, digest 매주 월 09:23 KST). 에이전트도 분리했다 — watch 에이전트의 지시문이 "판정하지 말 것"이라 한 에이전트가 두 단계를 겸하면 그 계약이 흐려진다. 잡은 둘이지만 watchlist·폴러·큐를 공유하는 한 파이프라인이다
  - 단계 계약을 데이터로 강제한다: `poll` 출력에 `"stage": "watch"` / `"judgment": "forbidden"`, `digest` 출력에 `"digest"` / `"required"`. receipt 첫 줄에도 stage를 쓰게 해 판정이 섞이면 자기 모순이 드러나게 했다. 스킬이 증류 루브릭을 함께 싣고 있어 산문 금지만으로는 watch 알림이 판정으로 흐른다
  - suppressed는 큐에 들어가지 않는다 — digest는 "알린 것 중에서" 판정한다. 테스트 59 → 74건

- `evals/`를 추적 대상으로 전환 — 이전에는 `evals/*` ignore + 3개 스위트만 allowlist였다. 추적하지 않으면 **스킬 성능을 측정할 수 없고**, 측정하지 않는 스위트는 채점 대상 스킬에 대해 조용히 썩는다. 45개 스위트 / 205개 파일이 추적된다. `evals/**/results/`(실행 산출물)는 계속 ignore
  - allowlist가 막아주던 것은 실재하는 위험이었다. 전환 전 스캔에서 **5개 스위트에 사내 식별자 61건**이 나왔다 — Jira 프로젝트 키, 내부 repo명, `git.linecorp.com` 호스트, 조직명, 그리고 **Slack 채널 ID와 실제 메시지 타임스탬프**. 공개 repo에 사내 식별자가 올라가 history rewrite까지 갔던 전례가 있어 전환 **전에** 정화했다
  - 치환은 placeholder로: `PROJ`/`OPS`(티켓 키), `web-ui`/`api-server`(repo), `git.example.com`, `acme-sre`, `C0123456789`, Slack ts 무력화. `lyris-{fe,be}-classify.yaml`은 파일명까지 개명. **태스크가 검증하는 구분은 보존** — jira-triage 스위트가 FE→BE 라우팅을 채점하므로 두 placeholder repo명이 서로 반대편에 남아야 한다 (`output_not_contains` 대칭 유지 확인)
  - CLAUDE.md에 **eval 식별자 스캔 게이트** 추가 — `evals/`를 건드리는 커밋을 막는다. allowlist를 없앤 대신 스캔이 그 자리를 대신한다
  - 측정 공백 확인: eval이 없는 스킬 7개 (`eli5-note`, `local-shot`, `review-queue`, `review-reminder`, `spec-revision`, `trending-digest`, `wt`). 이번 전환의 목적이 측정이므로 기록해 둔다

### Added

- `nara-wip-sweep` 신설 — `In Progress`로 방치된 할당 티켓을 한 번에 쓸어내 분류한다. "In Progress 35건"은 작업량이 아니라 상태 부채이고, 그게 섞여 있으면 어떤 브리핑도 "오늘 무엇부터"를 답할 수 없다
  - 분류 근거는 **실측**이다: 단어 경계 매칭(`(^|[^A-Za-z0-9])KEY([^0-9]|$)`) PR 조회, subtask 보유(컨테이너), 본문 AC 유무, 마지막 갱신 경과일. `gh pr list --search`는 fuzzy해서 `PROJ-4` 질의에 `PROJ-40`이 온다
  - **티켓을 전이시키지 않는다.** 팀이 보는 Jira에서 상태 변경은 "이 일을 안 한다"는 선언이라 사람 판정이다. `metadata.pr_url` 같은 캐시된 링크도 근거로 쓰지 않는다 — 키 검증 없이 심어져 딴 티켓 PR이 붙은 사례가 있다
  - 산출물은 실행 디렉터리의 `wip-sweep.md`. 여러 프로젝트를 걸치는 상태 보고서라 어느 repo의 `docs/`에도 넣지 않는다
  - 첫 실행(35건)에서 사실상 종료 4건(머지 PR 보유), 착수 불가 3건(본문 없음), 컨테이너 3건, 방치 1건을 분리했다. `LYRIS-505`는 merged PR 19건이라 다수 규칙에 따라 모호로 남겼다

- `nara-worklog` subtask 전환 마커 — `worklog.py mark <SUBTASK>`가 ledger에 `ev: "switch"`를 append하고, 리듀서가 마커 이후 구간을 그 티켓에 귀속시킨다. 브랜치 하나로 여러 subtask를 오가는 실제 작업 방식을 위한 것 (worklog를 leaf에 다는 방향)
  - 마커는 **브랜치 티켓의 ledger**에 들어간다 — hook이 쓰는 그 파일이므로 subtask별 ledger가 새로 생기지 않는다. 마커 이전 구간은 브랜치 티켓(대개 부모)에 남고, 그건 `mark`를 잊었다는 신호다
  - 마커는 시간을 만들거나 없애지 않는다. span을 자를 뿐이라 귀속 합계 = 원본 합계 (테스트로 고정). 유휴 구간의 마커는 자기 시간 없이 다음 span의 소유자만 정한다
  - 출력이 `(날짜 × 티켓)` 버킷 구조로 바뀌어 Jira 쓰기가 버킷당 1건이 된다. 승인 게이트에 **부모 귀속 경고**(subtask 있는 티켓인데 마커 없이 부모로 잡힌 구간)와 **쓰기 전 `jira_get_worklog` 대조**를 추가 — watermark는 이 ledger 안에서만 유효해서 다른 경로로 올라간 기록을 모른다
  - **마커 없이 지난 시간은 사후 분리 불가.** hook은 브랜치명의 티켓 키만 안다. 추측으로 채우지 않는다
  - 3-리뷰어 집중 코드 리뷰 반영 (17건 → R0/R1 15건 적용, R2 2건 이월). 리포트: `docs/review/260903-worklog-marker-mode.md`
    - **시간이 창조되는 경로 2개**를 테스트로 막았다: `read_switches`의 `sorted()`를 제거하면 조각이 겹쳐 60분 입력이 100분으로 청구되고(subtask 2개 소실), `build_spans`의 `sorted()`를 제거하면 span이 -2h 20m가 된다. 둘 다 `attribute`의 `else: break`가 전제하는 정렬인데 테스트가 0건이었다
    - naive `ts` + 마커가 `TypeError`를 냈다 — `read_switches`는 승격하는데 `build_spans`는 안 했다. 마커가 방아쇠라 이 변경이 만든 새 크래시 경로다. `as_aware()` 헬퍼로 세 리더를 통일
    - 버킷 정렬 키가 ISO **문자열**이었다. 한 ledger에 offset이 섞이면(컨테이너 TZ=UTC + 호스트 KST) 문자열 순서 ≠ 시각 순서라 문서화된 오름차순 쓰기가 역전된다
    - `NARA_WORKLOG_GAP_MINUTES` 검증 추가 — 문서에 "1 이상의 정수"라 적어놓고 코드에 검사가 없었다. `0`은 조용히 모든 유휴를 분할해 읽기·검토 시간을 전부 빼먹는다
    - 승인 게이트 Example 표에 **티켓 열**을 넣었다. "단위는 (날짜×티켓) 버킷"이라 선언하면서 표는 티켓 열이 없어, 하루 2버킷이 한 행으로 접히고 사람이 일 합계만 승인하는 동안 쓰기는 서로 다른 issue_key에 2건 나갔다
    - 내가 추가한 `day_spans()` 테스트 헬퍼가 **정렬을 해서** `reversed(spans)` 회귀를 가렸다 — 실제로는 `jira_started`가 3h36m 어긋난다. 정렬 제거 + 버킷 1개가 span 2개를 갖는 픽스처로 pin. 리뷰 전 assertion은 이 변이를 잡았으므로 커버리지 순손실이었다
    - 테스트 54 → **69건**, 변이 재검증 **12/12 KILLED**(전부 이전엔 생존)
    - 이월 R2 2건은 같은 뿌리 — watermark가 아직 날짜 단위 가정이라 하루 안에서 귀속이 교차하면 부분실패 시 시간 소실/중복 게시가 가능하고, `day["time_spent"]`가 raw 합계를 한 번만 내려 승인값(`3h 59m`)과 실제 기록(`3h 56m`)이 어긋난다

### Changed

- `nara-worklog`가 **사람 시간과 agent 시간을 가른다.** 모든 이벤트에 `role`이 붙고 Jira worklog에는 `role: human`만 올라간다. dispatch된 codex 워커는 티켓 이름이 붙은 브랜치에서 돌아 사람과 똑같은 이벤트를 만들기 때문에, 구분이 없으면 무인 실행 한 시간이 팀 스프린트 리포트에 내 시간으로 들어간다
  - **역할 필터는 그룹화 전에 적용된다.** 나중에 걸러내면 워커의 턴이 사람의 유휴 간격을 메워 두 개의 별개 접속이 한 span으로 붙는다. 사람 10분 + agent 1시간 + 사람 10분이 `20m`이어야 하고 `2h 15m`이면 안 된다는 것을 테스트로 고정했다
  - `agent_seconds`/`agent_time_spent`로 따로 보고한다. 청구액이 아니라 자동화가 얼마나 걷어갔는지의 지표이고 `total_seconds`에 합산하지 않는다
  - 판별은 `NARA_WORKLOG_ROLE`(dispatcher가 워커에 심는다)이 1차, `~/orca/workspaces` 경로가 백스톱이다. 오타 같은 미지의 값은 `human`으로 떨어진다 — 인식 못 하는 역할을 만들면 사람 집계와 agent 집계 양쪽에서 사라진다
  - role 없는 기존 이벤트는 `human`으로 읽는다. ledger는 append-only이므로 과거 기록이 계속 세어져야 한다
- `nara-worklog` hook이 **harness에 의존하지 않는다.** 이벤트 이름을 `--event`로 받고 stdin 페이로드는 폴백이다. Claude Code와 Codex 둘 다 `UserPromptSubmit`/`Stop`을 노출하지만 두 페이로드 스키마가 계속 같다는 데 시계를 걸지 않는다 — 한쪽이 키를 바꾸면 조용히 멈춘다. Codex 배선 절차는 `references/hook-setup.md`에 추가
  - **손으로 JSON을 편집하다 두 번 틀렸다.** `UserPromptSubmit` 대신 `PostToolUse`에 넣어 턴 경계가 무의미해졌고(도구 호출마다 발동), 닫는 괄호를 빠뜨려 `~/.codex/hooks.json` 전체가 파싱 불가가 됐다. 후자는 worklog만 죽는 게 아니라 그 파일의 **모든** hook이 함께 죽는다. 문서는 이제 파서를 거치는 스크립트를 제시한다
  - **`-> str | None`을 추가했다가 3.9 폴백을 깨뜨렸다.** `TypeError`로 `exit=1`이고, 폴백이 발동하는 머신에서는 그게 모든 턴 차단이다. 첫 줄의 `from __future__ import annotations`가 그 방어이고, 문서에 실측 검증 한 줄을 넣었다
  - 테스트 69 → **78건**. role 3건(청구 제외·유휴 간격 비브리지·필드 없음=human)과 argv 이벤트 5건
- `nara-worklog` idle 임계 기본값 **30 → 90분**. 실측 하루에서 30분은 62분짜리 기획 검수 유휴와 55분 유휴를 청구에서 잘라냈다 — 생각·검수 시간도 작업 시간이라는 판단
  - "세션 시작~종료"를 그대로 쓰는 안은 실측으로 기각했다: 같은 ledger가 2h43m(30분 모델) vs **15h38m**(세션 모델)으로 갈렸고, 세션 하나가 18:34에 시작해 다음날 08:11까지 열려 있어 **707분 수면 구간이 청구**됐다. 문제는 세션 경계가 아니라 임계값이었다
  - 90분은 62·55·35분 유휴를 살리고 707분은 버리는 지점. 같은 날 값이 2h43m → 4h15m

- `nara-release-watch` 경로 감시 모드 — watchlist 항목을 `owner/repo:some/dir`로 쓰면 릴리즈가 아니라 **그 경로를 건드린 커밋**을 본다. repo 릴리즈가 특정 디렉터리의 변경을 대변하지 못할 때 필요하다
  - 실측 동기: `mattpocock/skills`는 릴리즈가 2026-08-06에 멈췄는데 `skills/productivity/grill-me`는 2026-08-15에 바뀌었고 repo 전체는 계속 활발했다. 릴리즈로 감시하면 그 변경을 영구히 못 보고, repo 전체 커밋으로 감시하면 하루 여러 건이라 노이즈다. 해당 경로 커밋은 2026-04 이후 6건 — 감시 대상으로 적정
  - state가 `repo` vs `repo:path`로 분리되므로 같은 repo를 repo 레벨과 여러 경로로 동시에 감시해도 충돌하지 않는다. watermark 단위는 태그 대신 커밋 SHA
  - `@minor`/`@major`와 prerelease 필터는 SHA에 무의미해 실질적으로 무시된다 — 16진수 SHA에는 prerelease 키워드가 나올 수 없다(모든 키워드가 비-16진수 문자를 포함). 특수 분기 없이 안전함을 테스트로 고정
  - 경로에 커밋이 0건이면 `unwatchable`로 1회 보고(거의 항상 오타), `..`가 든 경로는 파싱 단계에서 폐기
  - 판정 루브릭은 두 모드에 동일 적용 — 스킬 diff는 그 자체로 "증류할 게 있나"라는 질문이다

- `nara-release-watch` 신설 — watchlist repo의 신규 릴리즈를 폴링해 nara-kit에 증류할 값이 있는 것만 판정·보고한다. `nara-trending-digest`와 짝이지만 다른 일이다: trending은 **모르는 repo 발견**, 이건 **아는 repo 추적**. 배달 경로(Slack DM + Obsidian)만 공유
  - **2층 구조가 설계의 핵심.** "새 릴리즈 있나"는 GitHub API 한 방(LLM 0), "증류할 만한가"는 스킬 표면을 알아야 하는 판단이다. 분리하면 신규 0건인 날 모델을 아예 안 깨운다 — 기존 autopilot이 Claude 풀 절반을 쓰고 있어 실질적인 절약
  - **조용한 날엔 아무것도 보내지 않는다.** AI 툴링 repo 릴리즈는 버스티해서, 매일 "없음"을 보내면 6일치 무소식이 7일째 진짜 소식을 덮는다. 폴링은 매일, 알림은 있을 때만. 예외는 `needs_attention` — `gh` 인증 실패는 조용한 날과 구별이 안 되므로 조용함으로 접지 않고 매 실행 보고한다 (이게 없으면 토큰 만료 후 영구히 "평온"해 보인다)
  - 노이즈 통제는 실측으로 정했다. `openai/codex`가 `rust-v0.153.0-alpha.5`를 플래그 없는 정식 릴리즈로 올려서 **prerelease를 태그 문자열로도 판정**하고, `anthropics/claude-code`가 `v2.1.258`(패치 거의 매일)이라 watchlist 항목별 **`@minor`/`@major` 임계**를 뒀다. 억제된 릴리즈도 `last_seen`은 전진시킨다 — 안 그러면 같은 패치를 매 실행 재평가하고 수렴하지 않는다. 첫 관측은 baseline만 기록하고 침묵(첫날 히스토리를 쏟으면 쓸모 있는 말을 하기 전에 무시당한다). 버전을 파싱 못 하면 억제하지 않는다
  - 릴리즈·태그가 둘 다 없는 repo는 `unwatchable`로 **1회 보고 후 억제** — 조용히 감시하는 척 하지 않되 매일 조르지도 않는다 (실제로 `browserbase/skills`가 이 경로로 걸렸다)
  - 판정 루브릭 4분류(`이미 있음`/`의존`/`증류 후보`/`무시`)의 **기본값은 `의존`**. 이 잡은 구조상 흡수 루프라서 기본값이 `증류 후보`면 매일 "우리도 만들자" 후보만 쌓인다 — vendor-free는 배포 산출물 속성이고 nativize는 이식이 싸고 테제가 날카로울 때만. `이미 있음`은 겹치는 **스킬 이름을 대야** 쓸 수 있다 (인상으로 릴리즈를 버리면 진짜 새로운 것을 놓친다)
  - config는 `~/.claude/release-watch.md`(사람, 마크다운 산문 허용) + `~/.claude/release-watch-state.json`(기계, 원자적 재작성) 분리. 상태가 매번 덮어써지므로 사람이 편집하는 목록과 같은 파일에 둘 수 없다. 목록은 `watch.py seed`가 스타에서 후보만 제시하고 **자동 추가하지 않는다** — 스타는 다른 이유로도 누르니 노이즈다

- `nara-worklog` 신설 — 세션 타임스탬프를 날짜별 Jira worklog로 올린다. **수집(hook)과 쓰기(스킬)를 분리한 것이 설계의 핵심**: 시작 시각은 "기록해야 한다는 걸 알기 전"에 지나가므로 LLM 선언으로는 안 지켜지고(hook이 필요), 반대로 팀이 읽는 티켓에 확인 없이 숫자가 올라가면 안 되며 hook은 shell이라 MCP를 못 쓴다(스킬이 필요)
  - 수집: `assets/nara-worklog-stamp.py`를 `UserPromptSubmit` + `Stop`에 배선. 브랜치명의 `ABC-123`으로 티켓을 판정하고 `~/.claude/worklog/<TICKET>.jsonl`에 append. 티켓 키 없는 브랜치는 skip. stdout 무출력·항상 exit 0 계약 — `UserPromptSubmit` hook의 stdout은 모델 컨텍스트로 주입되고 non-zero는 턴을 막는다. 설치는 일회성 수동 작업 ([references/hook-setup.md](skills/nara-worklog/references/hook-setup.md)) — `~/.claude/hooks/`와 `settings.json`은 배포 대상이 아니다
  - 산정: `assets/worklog.py`(표준 라이브러리만)가 소유한다. LLM이 시각을 더하면 같은 ledger에서 매번 다른 숫자가 나오고 그 숫자는 스프린트 리포트에 들어간다. `prompt → turn_end` 구간은 길어도 자르지 않고(에이전트 실행 = 작업 시간), `turn_end → prompt`(자리 비움)와 `turn_end` 없는 `prompt → prompt`(턴 중간에 죽은 세션)만 idle 임계 30분으로 자른다. 자정 분할로 날짜별 1건 — 여러 날 걸린 티켓이 PR 날짜에 뭉치지 않는다. 한 티켓 워크트리 여러 개는 합집합 병합(세션별 합산이면 중복 계상). 분 단위 **내림** — 안 쓴 1분을 청구하지 않고, 정확히 30초일 때 banker's rounding도 피한다
  - 멱등성: `jira_add_worklog`가 멱등이 아니라서 ledger의 `logged` watermark가 유일한 중복 방지 장치다. 날짜 오름차순으로 쓰고 중간 실패 시 **성공한 날짜까지만** watermark를 올려 실패한 날이 다시 제안되게 한다. Jira 쓰기 0건이면 record하지 않는다
  - `nara-pr` 스텝 8 추가 — PR 생성 후 미기록 시간을 한 줄 알리기만 한다. 쓰기는 승인 게이트가 있는 `nara-worklog` 소관 (스크립트 없으면 스킵)

- `nara-eli5-note` 편입 — 로컬 전용 스킬(`~/.agents/skills`, 2026-08-24 신설)을 nara-kit으로 올림. 실무에서 막힌 것을 eli5 또는 실무 노트체로 풀어 Obsidian vault 관례(폴더 두 계열·frontmatter·노트 골격)에 맞춰 저장하고, 그림을 필수로 동반한다
  - **그림 매체는 HTML/SVG — ASCII 아트·mermaid 금지** (2026-08-26 유저 결정. 노트는 글, 그림은 렌더되는 파일). 그림 3개 이상·연결된 설명이면 노트 옆 `<slug>-그림.html`(HTML 뷰어 플러그인으로 열고, 절 번호를 노트와 1:1로 맞춤), 독립 그림 1~2개면 `_assets/` SVG 인라인 임베드
  - `references/diagram-patterns.md`가 패턴 8종의 판정 기준(before/after·생애주기·층 구조·트리·비율·대조·비유·상태 지도)을 매체 무관으로 유지하고, HTML 스타일 베이스 CSS + 의미 고정 색 팔레트(초록=해결·빨강=문제·파랑=강조·노랑=보류)를 제공 — 노트마다 그림 스타일을 재발명하지 않는다
  - 규율: 톤(eli5 vs 실무 노트체)을 추측하지 않고 묻는다 · `TL;DR`·`내가 틀렸던 것` 절 필수 · 비유는 하나만 · 개념어는 실제 식별자(필드명·파일명)와 1:1 대응
  - `references/vault-conventions.md`는 설치자 vault 실측 스냅샷 — 포크 시 자기 vault에 맞게 갱신해서 쓴다

## [0.22.0] - 2026-08-26

### Added

- `nara-ko-prose` 신설 — 공유 산출물(PR 본문·RFC·ADR·한국어 Confluence 본문)의 한국어 명확성 수리. 생략된 조사·어미·문장 성분을 되돌리고, 명사구로 끊긴 문장을 종결어미로 맺고, 엠대시를 치환한다
  - 규칙 출처는 [snflkd/fluent-korean](https://github.com/snflkd/fluent-korean) (MIT). **사본을 배포하지 않고** 설치된 원문을 실행 시점에 읽는다 — 원문 `## 상황과 목표` 절이 지침의 요약을 권장하지 않으므로 축약본도 두지 않으며, 원문 미발견 시 `Unverifiable`로 종료한다. nara-kit이 저작한 것은 호출 계약과 조항별 모드 배정뿐
  - 모드 2종. `repair`(기본, 산출물 스킬 post-pass 경로)는 결함 교정만 하고, `full`(사용자 직접 호출)은 전 조항을 적용한다. `repair`가 부분집합인 이유는 분량이 아니라 **`naranizer`와의 공존** — 원문 동작 범위 4항(사용자 어조 모방 금지)을 PR 본문에 적용하면 개인 말투 변환이 통째로 취소된다
  - `nara-humanizer`와 방향이 반대다. humanizer는 AI 마커를 **덜어내고**(쉼표 과다·유행어·번역투), ko-prose는 압축이 만든 결핍을 **채운다**. 한자어에서 정면으로 어긋나므로(humanizer는 "한자어 과다"를 검출, 원문 구 단위 2항은 적극 활용을 요구) `repair`는 그 조항을 적용하지 않는다
  - 적용 제외: 커밋 메시지·변수명·코드 주석·로그 문자열(원문 동작 범위 2항), 헤더·목록의 종결어미 요구(원문 문장 단위 2항이 스스로 제외), 코드 블록·인용, 영어 텍스트

### Changed

- `nara-pr`: Step 6에 `nara-ko-prose` repair post-pass 추가 (naranizer **다음**에 실행 — 어휘·말투를 건드리지 않아 앞 단계를 되돌리지 않는다). 기존 Step 6 → 7
- `nara-rfc`: Step 5에 `nara-ko-prose` repair post-pass 추가. 기존 Step 5 → 6
- `nara-adr`: Workflow Step 4에 `nara-ko-prose` repair post-pass 추가. 기존 Step 4 → 5
- `nara-publish-spec`: Language 규칙에 조건부 `nara-ko-prose` repair 추가 — 본문이 **한국어일 때만** Step 2 preview 전에 실행. 영어 본문은 대상 아님
- `nara-spec-revision`은 배선하지 않음 — 본문 규약이 영어 전용이므로 한국어 수리 대상이 없다
- `nara-reflect`: durable memory를 **두 층**(파일 기반 memory dir + memory MCP 도구)으로 인정하도록 §3·§4·실패 처리 표 개정
  - dedup을 층별로 분리 — 도구 층 검색은 명사 키워드 1~3개, 문장형 쿼리 금지, **0건을 부재로 단정 금지**(짧은 키워드 재시도 → ID 조회로 확정)
  - dual-store 스텝 신설 — 파일 층에 write한 학습은 도구 층에도 독립 레코드로. 세션 요약 레코드로 갈음 금지, UPDATE도 양쪽
  - receipt를 층별로 분리 표기 — 파일 경로 / 레코드 ID 나란히, 한쪽만 있으면 `divergence`, 도구 미설치면 `store: file-only (<사유>)`
- `nara-reflect`: `nara-memory-audit` **Tier 1 피기백** — write 후 `audit.sh`(bash, ~0 토큰)로 파일 층 점수만 읽어 receipt에 `memory health: total N | flagged M` 한 줄. `M>0`이면 `/nara-memory-audit` **추천만** (Tier 2·수정은 여전히 audit 스킬 소관). 스크립트/`jq`/`git` 부재 시 줄 생략 — 의존 아님
- `nara-reflect`: tiebreaker·skill 추천 트리거·실패 처리 표를 `references/routing-rules.md`로 분리 (조건부 발동 규칙만 이동 — 매 세션 발동 계약은 본문 유지). 3078 → 2737 토큰
- `nara-memory-audit`: dual-store 대칭 맞춤 — Apply에 step 6 **mirror the removal** 추가(파일 archive 시 MCP 쌍둥이 레코드도 같은 승인 배치에서 supersede/삭제, 도구 없으면 skip+명시). Rules에 커버리지 한계 선언 — Tier 1은 bash라 MCP 못 읽음, 파일 층은 프록시일 뿐 **MCP 전용 레코드는 감사 사각**
- `references/output-contract.md` §4: receipt 압축 축을 서드파티 플러그인 이름(`caveman lite/full/ultra`)에서 동작 기준 3단계(`full` / `compact` / `minimal`)로 교체. 배포되는 규약이 특정 스타일 플러그인의 설치를 전제하지 않게 됐다 — 세션에 걸린 어떤 출력 스타일이든 그 요구를 세 단계 중 하나로 매핑해 적용한다. "압축은 형식만 줄이고 §1의 4요소는 어느 수준에서도 빠지지 않는다"는 제약을 명문화
- `README.md`: My Setup 표에서 `caveman` 행 제거 (로컬에서 제거한 플러그인)

### Fixed

- `nara-memory-audit` Tier 1(`scripts/audit.sh`) 오탐 2건 — 값싼 선별기가 값비싼 Tier 2를 보호하는 대신 일거리를 만들어내고 있었다
  - **skill 존재 검사가 틀린 루트에서 해석됐다.** `$CLAUDE_PROJECT_DIR/skills/`만 뒤졌으므로, 스킬 문서가 지시하는 그대로 실행하면(감사 대상 메모리가 *설명하는* repo에서 실행 — 즉 `skills/` 트리가 없는 소비 애플리케이션 repo) 스킬을 언급한 **모든** 메모리가 broken으로 잡혔다. 최고 신뢰 신호로 문서화된 검사라 독자는 이를 신뢰하고, Tier 2는 서브에이전트 예산을 오탐 반증에 썼다
  - 이제 ref의 **형태별로** 해석하고, 형태별 식별자로 보고한다. `skills/<name>/`는 repo 상대 **경로** 주장이라 `skills/<name>`으로, `/nara-<name>`은 **설치된 스킬** 주장이라 `/<name>`으로. 판정이 어느 주장에서 나왔는지 항상 귀속되고, 같은 ref가 broken과 unknown에 동시에 오르는 일이 구조적으로 불가능하다
  - 루트 탐색 순서는 `$NARA_SKILLS_DIRS`(콜론 구분, 목록 전체를 대체) → `$CLAUDE_PROJECT_DIR/skills` → `${CLAUDE_CONFIG_DIR:-~/.claude}/skills` → `~/.codex/skills` → `~/.agents/skills`. 선언된 루트는 첫 번째만이 아니라 전부 탐색한다. 런타임 중립 — 어느 에이전트 디렉터리도 존재를 요구하지 않는다
  - **경로 주장은 repo 트리가 없을 때 "어디에도 없음"까지 판정한다.** 툴킷에서 제거된 스킬은 모든 루트에 없으므로 어느 repo에서 물어도 반박 가능하다 — 이를 unknown으로 내리면 제거된 스킬이 `healthy`로 읽히며 살아 있는 드리프트가 침묵한다. 반대로 어느 에이전트 루트엔 있는 경우엔 `unknown`에서 멈춘다: `nara-` 이전 맨이름(`code-review`, `commit`, `gap`, `jira-triage`)이 그 루트의 범용 이름 서드파티 스킬과 충돌하므로(`code-review`는 실제로 Codex skills 디렉터리에 존재한다) clear 처리하면 마이그레이션 드리프트 부류가 통과한다
  - **Form B 언급이 Form A 주장을 대신 해결하지 못한다.** 같은 스킬명이고 한쪽이 해석되니 넘어가고 싶어지지만, 그러면 위의 확대가 뒷문으로 들어온다 — 파일에 `/nara-x`를 한 줄 덧붙이면 바뀌지 않은 거짓 `skills/nara-x/` 주장의 판정이 지워진다
  - **해석 불가는 실패가 아니다.** 신설 `skill_ref_unknown`은 **0점**이며 "스킬은 존재하는데 이 repo가 경로를 확인할 수 없다"만 뜻한다. JSON `details`에 `skill_refs_unknown` 필드가 추가됐다. `signals[]`에는 새 값이 들어가므로, 배열 길이로 점수를 세던 코드는 과다 계산한다 — `score` 필드를 쓸 것
  - **`ref_paths` 정제기가 파일명의 일부를 지웠다.** YAML 인용부호를 떼려고 `[`, `]`, `"`, `'`, 공백을 문자 클래스로 일괄 삭제했으므로, 선언되지 않은 경로를 조회하게 됐다. 이제 항목별로 앞뒤 공백을 다듬고 인용부호 **한 쌍**만, 인라인 플로우 시퀀스는 외곽 `[ ]` **한 쌍만 쌍으로서** 떼어낸다. 값 안의 문자는 살아남는다
  - 보고된 증상은 브래킷(여러 주류 프레임워크의 동적 라우트 관례인 `app/[locale]/page.tsx`)이었지만, 실제 피해자는 **공백**이었다 — 외부 노트 볼트를 가리키는 절대경로의 `Mobile Documents`가 잘려, 메모리 2개가 선언한 경로 3개가 전부 영구히 missing으로 잡히고 있었다. 이 오탐이 독자를 미는 "해결책"은 `ref_paths`에서 앵커를 지우는 것이고, 그러면 실제 정보가 사라지고 신호 2·3이 영구 무장해제된다. 그래서 **앵커가 아니라 판독기를 고친다**는 규칙을 `SKILL.md` Rules에 명문화했다
  - 브래킷 앵커를 되살리자 신호 3에 **글롭 구멍**이 열렸다. git은 맨 pathspec을 wildmatch로 파싱하므로 `[locale]`이 문자 클래스가 되어 무관한 형제 경로(`app/l/`, `app/a/` …)의 커밋이 앵커에 귀속됐다 — 진짜 drift 0인데 `code_drift`가 발화. `:(literal)` 접두로 고정했다. 수정 전에는 브래킷이 잘려 앵커가 아예 해석되지 않았으므로 도달 불가였던 경로다
  - 같은 잘못된 루트 가정이 **Tier 2 서브에이전트 프롬프트에도** 있었다(`skills/<name>/SKILL.md`를 확인하라고 지시). 값비싼 층이 값싼 층의 오탐을 재확인할 구조였다. 이제 Tier 1과 같은 형태 구분을 따르고, 디렉터리 존재만 보는 Tier 1보다 엄격할 수 있는 유일한 경우(`SKILL.md` 없는 빈 디렉터리)를 근거에 명시하게 했다
  - `references/scoring.md`의 프론트매터 규약에서 절대경로를 일괄 "규약 위반"으로 규정한 문장을 완화했다 — repo 밖에 실제로 존재하는 앵커(외부 노트 볼트, 머신 로컬 설정)에는 절대경로가 정직한 형태다. 신호 2는 여전히 답하고 신호 3만 눈이 먼다
  - **실측** (이 repo의 메모리 48개, `HEAD` 대비). 소비 repo 기준(문서가 지시하는 대로 cwd = `CLAUDE_PROJECT_DIR` = 소비 repo) broken 판정 19건 → 3건: 3건은 0.21.0에서 제거된 스킬이라 계속 broken(폴백이 되살린 진짜 드리프트), 8건은 정직한 `unknown`, 나머지 9건은 실제 해석 성공. 판정 슬롯은 Form A 11 + Form B 9 = 20이므로 3+8+9로 맞는다 — 형태별 식별자 도입으로 수정 전 19와 단순 차감이 성립하지 않는다. flagged(2점 이상) 10 → 3. nara-kit repo 기준 broken 4 → 4로 마이그레이션 드리프트 탐지가 보존됐고, flagged는 6 → 4(공백 정제 수정분)
  - 하네스가 지키지 못하던 것 3건을 케이스로 메웠다 — **공백 경로**(CHANGELOG가 실제 피해자로 지목한 바로 그것인데 브래킷 케이스 4종이 전부 green인 채로 통과했다), 절대경로 as-given 폴백(외부 볼트 앵커 3개가 여기 달려 있다), `/nara-kit` 제외. 셋 다 해당 mutation을 재삽입하면 실패하는 것을 확인했다
  - `NARA_SKILLS_DIRS`는 **탐색 목록만** 대체한다. Form A의 권위 판정은 `$CLAUDE_PROJECT_DIR/skills`를 직접 보므로 이 변수로 우회되지 않는다 — 문서에 "목록 전체를 대체"라고만 적었던 것을 좁혔고, unknown 판정을 결정시키는 수단은 `CLAUDE_PROJECT_DIR`임을 Troubleshooting에 명시했다
  - 회귀 스위트 `evals/nara-memory-audit/` 추적 시작 (`.gitignore` opt-in). `regress.sh`는 케이스별로 임시 repo를 만드는 결정론적 하네스 18종·단정 42개로, bash 3.2·5.x 및 툴킷이 설치되지 않은 환경에서 동일하게 통과한다. 9종은 **가드**다 — 수정이 검사를 느슨하게 만드는 방향으로 "통과"하는 것을 막는다: 어디에도 없는 스킬 ref는 계속 broken인지, repo 내 마이그레이션 경로는 계속 broken인지, 진짜 없는 브래킷 경로는 계속 invalid인지, 에이전트 루트 이름 충돌이 낡은 경로를 지우지 않는지, `/nara-x` 언급이 거짓 경로 주장을 지우지 않는지, 브래킷 앵커의 **진짜** 변경은 여전히 drift로 잡히는지, 공백 경로가 계속 해석되는지, 절대경로 앵커가 계속 해석되는지, `/nara-kit`이 스킬로 오인되지 않는지
  - `eval.yaml`의 태스크 레이어는 `executor: mock`과 "mock 마커가 출력에 없어야 한다"는 단정이 정면 모순이어서 **구조적으로 0/4**였다(실행해 확인). mock은 프롬프트를 되돌려줄 뿐 스킬을 호출하지 않으므로 어떤 단정도 판별력이 없다 — eval 레벨 그레이더를 제거하고, 태스크는 실제 executor가 붙을 때까지 **기록된 시나리오**임을 명시했다. `output_contains` 문자열이 태스크 자기 이름에서 에코되어 통과하던 것도 이름을 바꿔 끊었다. 같은 모순이 있던 `evals/nara-gap/eval.yaml`도 함께 고쳤다

## [0.21.0] - 2026-08-14

> **BREAKING — 업그레이드 시 수동 조치 필요.** 스킬 4종이 제거됐다. `npx skills update`는 **삭제된 스킬을 지우지 않으므로** 설치본에 옛 사본이 그대로 남는다:
>
> ```bash
> rm -rf ~/.claude/skills/nara-workflow-orchestrator \
>        ~/.claude/skills/nara-workflow-dev-mode \
>        ~/.claude/skills/nara-workflow-doc-mode \
>        ~/.claude/skills/nara-workflow-viz
> npx skills update
> ls ~/.claude/skills | grep -c '^nara-'   # 47 (+ naranizer = 48)
> ```
>
> 옛 사본을 남겨두면 존재하지 않는 흐름을 가리키는 지침이 계속 로드된다. Codex 쪽 설치 경로도 동일하게 정리한다.
>
> **대체 경로**: `orchestrator`/`dev-mode`/`doc-mode` → 개별 스킬 직접 호출 + `nara-now`의 다음 행동 추천 · `viz` → 대체 없음(입력 `workflow.json`이 애초에 없어 실행 불가였다) · Implementation Notes Gate → `nara-implement`.

### Removed

- **워크플로 메타 스킬 4종 제거** — `nara-workflow-orchestrator`, `nara-workflow-dev-mode`, `nara-workflow-doc-mode`, `nara-workflow-viz`. **BREAKING**: 소비자 설치본에는 옛 스킬이 그대로 남으므로 수동 삭제가 필요하다 (`rm -rf ~/.claude/skills/nara-workflow-*` 후 `npx skills update`).
  - 근거는 취향이 아니라 실측이다. `~/.claude/projects/**/*.jsonl`에서 최근 60일 호출을 세면(사람의 슬래시 호출 `<command-name>`과 어시스턴트의 Skill 툴 호출 `"skill":` **양쪽**) 네 스킬 합계가 **1회**다 — `dev-mode` 1, 나머지 셋은 **각 0회**. 같은 기간 `nara-now` 74, `nara-reflect` 63, `nara-code-review` 23. 즉 흐름이 불필요한 게 아니라 **흐름을 스킬로 포장하면 아무도 부르지 않는다**. `viz`는 입력이어야 할 `workflow.json`이 저장소에 아예 없어 애초에 실행 불가였다.
  - 같은 날 `dev-mode` spine을 6→5단계로 고치며 3개 파일을 갱신했는데, 측정 결과 그 편집이 바꾼 실행 경로는 0이었다. 문서만 고친 셈이고, 그게 이 제거의 직접적 계기다.
  - **계약은 죽이지 않고 옮겼다** — Implementation Notes Gate(scope scaling·pre-flight·trailing `📝`·state gate·카테고리 4종 원문)는 `nara-implement/references/implementation-notes.md`로 이관. `docs/implementation-notes.md`의 **경로·섹션명·`Reconciliation Log` writer(`nara-gap --verify`)는 불변**이라 `nara-gap`·`nara-reflect` 연결이 그대로 산다.
  - 흐름 서술은 `skills/README.md`에 **"권장 순서이지 실행되는 스킬이 아니다"**로 남겼다. `CLAUDE.md`·전역 `rules/workflow.md`도 같은 방향으로 갱신. 다음 단계 안내는 `nara-now`(74회)가 맡는다 — 새 워크플로 스킬을 만들지 않는다는 것이 이 변경의 핵심 조건이다.
  - `nara-ac-draft`는 2회지만 **유지**한다. AC가 대개 외부 SoT에 이미 있고 `nara-prep`이 verbatim으로 옮기므로, AC 게이트가 우회되는 게 아니라 통과되는 것이다 — 낮은 호출수가 정상 동작이다.

### Changed
- **`nara-now`가 진행 위치를 추적한다** (제거된 워크플로 스킬의 대체재). 74회로 최다 호출되는 스킬이 "지금 어디고 다음이 뭔지"를 맡는다 — 흐름을 별도 스킬로 만들면 아무도 부르지 않는다는 게 측정의 결론이라, **새 워크플로 스킬을 만들지 않는 것이 이 설계의 조건이다.**
  - 추측하지 않기 위해 상태를 기록으로 남긴다: `nara-implement`가 유닛 검증 통과(`Pass`) 시 `docs/plan.md`의 **그 유닛 헤딩에만** `— ✅ done`을 붙이고, `nara-now`는 그 표식만 읽는다. 커밋 로그·파일 변경으로 완료를 유추하지 않는다. `Fail`·`Blocked`·`Unverifiable`엔 표식을 안 붙인다.
  - 추천이 **실행 가능한 명령 형태**로 나온다 — "구현하세요"가 아니라 `/nara-implement T-2`, 인자까지 채워서(`/nara-prep PROJ-123`). 그대로 복사해 붙일 수 있어야 한다.
  - 결정표에 진행 행 추가: plan에 미완료 유닛 있으면 `{done}/{total} 완료 · 다음 T-N {제목}`.
- **스킬 말미 handoff 표준화** — `nara-prep`·`nara-grill`·`nara-gap`·`nara-code-review`·`nara-reflect`에 `**다음**: /nara-<skill>` 한 줄. 다음 단계를 사람이 기억하지 않아도 화면에 남는다.
- **dev-mode core spine이 6→5단계** — `plan → execute → verify → code-review → reflect`. `nara-gap`이 spine 맨 앞에서 빠졌다: 구현 전 gap은 greenfield에서 score ~0의 무정보 산출물인데, 사용자 작업이 대부분 기획부터 시작하는 greenfield라 상시 발생했다. **축은 brownfield/greenfield가 아니라 타이밍이었다** — greenfield라도 구현 *후* 요구사항-vs-코드 대조는 유효하므로 gap을 verify 단계로 옮겨 생성+판정을 1회로 합쳤다. brownfield 인수인계처럼 "이 코드 얼마나 됐나"가 먼저 필요하면 entry에서 조건부 위성으로 호출한다.
  - **verify는 2-track** — 코드 AC는 `nara-gap`, `browser-visible: yes` AC는 `nara-browser-verify`. 초기 검토안이던 "gap 전면 조건부화"는 기각됐다: `gap --verify`가 기존 `gap.md`를 전제하므로(`nara-gap/SKILL.md`) 생성이 안 돌면 `docs/implementation-notes.md`의 `## Reconciliation Log` **유일한 writer**와 `nara-now` 라우팅이 함께 죽는다.
  - `nara-now` 결정표 재작성 — `gap.md` 부재가 더 이상 "gap 분석 필요" 신호가 아니다(verify 전엔 없는 게 정상). 3행이 `/nara-plan`, 3-bis가 `/nara-implement`, 3-ter가 verify로 갈린다.
  - 근거: `docs/adr/0001-verify-browser-ac-at-runtime.md` (repo-local).
- `nara-ac-draft`(주 소유) / `nara-prep`(외부 SoT 있을 때만) — AC마다 **`browser-visible: yes|no|unknown` 태그**. 검증 경로 자체는 `nara-plan`의 기존 `검증` 필드가 계속 소유하고, 상류엔 태그만 붙는다. prep의 **no-derive 원칙을 건드리지 않기 위한 선택** — 검증 경로는 raw SoT에 없는 순수 엔지니어링 판단이라 prep이 만들면 verbatim 보존이 무너지고, 그 원칙은 `nara-gap`의 verbatim pre-scan(`git grep -F`)과 맞물린 구조적 제약이다. greenfield엔 외부 SoT가 없어 prep이 아예 안 돌므로 주 소유자는 `ac-draft`다.
- `nara-plan` — `검증` 필드 계약 추가. `browser-visible: yes` AC를 포함한 단위는 대상 URL·viewport·auth·통과 조건과 실행 주체(`nara-browser-verify`)를 명시해야 하며, "UI 확인" 같은 문구로 대체하면 그 단위는 `Blocked`. 태그 없는 레거시 `requirements.md`는 `unknown`으로 취급해 중단 없이 진행한다.
- `CLAUDE.md` — **형제 스킬 링크 규약 성문화**. `../nara-<other>/references/*.md` 참조는 신규 패턴이 아니라 이미 4곳(`naranizer`, `nara-design-studio`, `nara-golden-path-discover` 2곳)에서 쓰이던 관행이었고, 저장소 루트 `references/`가 배포되지 않으므로 공용 파일로 빼는 선택지 자체가 없다. 이제 모든 형제 참조는 **대상 부재 시 동작을 명시**해야 한다(스킵 후 진행 / `Unverifiable`). `waza check`는 대상 존재 여부와 **무관하게** 동일한 `link escapes skill directory`를 내므로 깨짐 감지기가 아니다 — 릴리스 전 실행할 grep 기반 체크를 Release 절에 넣었다. 근거: `docs/adr/0002-link-sibling-skill-references.md`.

### Added
- `nara-claim-audit` (신규 스킬) — **기획문서의 수치 주장을 CSV 스냅샷과 대조**한다. 문제는 "몰라서 비워둔 수치"가 아니라 **자신 있게 틀린 수치**다 — 실제 12개인데 8개라고 쓰고 그 위에 기획이 쌓이면 정합성이 끝에 가서 깨진다. `[UNVERIFIED]` 규약은 이미 10개 스킬이 쓰지만 **쓰는 사람이 추측 중임을 자각할 때만** 붙으므로 이 실패를 원리적으로 못 잡는다. 실증 수요: 데이터 파일 20개 중 10개 이상에서 문서 수치 불일치.
  - **측정은 `assets/audit.py`(Python 표준 라이브러리만, 새 의존성 0)가 소유한다.** 사람이 못 세는 양이라 자동 교체가 기본값인데, LLM이 마커를 해석하면 같은 문서에서 매번 다른 값이 나와 자동 교체의 전제가 무너진다. 테스트 60개(`test_audit`/`test_apply`/`test_candidates`).
  - **마커는 제한된 mini-DSL** — `count rows` / `distinct|sum|avg|max|min <col>` + `where <col> <op> <값>`(AND만) + 단위 환산. 자연어·JOIN·서브쿼리·`or`는 **해석하지 않고 `syntax_error`로 거부**한다. "활성"이 `status=active`인지 `last_login` 기준인지를 추측하면 스킬이 병을 옮긴다.
  - **없는 것을 0으로 세지 않는다** — 컬럼·파일 부재, 데이터 행 0건 CSV는 전부 `mapping_failure`. 헤더만 남은 export를 0으로 보고하면 "관리자 0명"이라는 자신 있는 오답이 문서에 박힌다.
  - **자동 교체는 건별 승인 없이**(수백 건 전제) 하되 두 겹으로 막는다: 교체 전 **스냅샷**(gitignore 확인 실패 시 ESCALATE·진행 거부, receipt에 복구 명령) + **살균 게이트**(1/10 이하 붕괴·10배 폭증 차단, 10 미만 소수는 비율 검사 면제). 마커 없는 숫자(날짜·목차 번호·순번)는 절대 건드리지 않는다.
  - **`--bootstrap`** — 마커 없는 기존 문서용. 노이즈 필터 후 후보만 제시하고 **교체하지 않는다**(매핑이 추론이므로). 실측: `spec-naranizer.md` 숫자 토큰 71개 → 후보 22개, 실제 주장 재현율 100%.
  - **판정에 `ambiguous` 추가** — 마커 앞 구간에 숫자가 둘 이상이면 어느 것이 주장인지 확정 불가이므로 교체하지 않는다. 코드 리뷰가 실행으로 재현한 결함: `활성 사용자 10명 (전체 50명 중)`에서 **맞는 10은 두고 50을 10으로 바꿔** 무관한 사실을 조작했고, `월 1,200건`은 `1,1200건`이 됐다. 마커는 그 수치 **바로 뒤**에 두는 것이 규칙이며, 한 줄 다중 마커는 각자 직전 마커 이후 구간만 본다.
  - 리뷰에서 함께 닫은 것: 필터 결과 0행을 0으로 확정하던 문제(→ `mapping_failure`), 코드펜스 안 예시까지 교체하던 문제, 스냅샷이 재실행 시 원본을 덮어써 복구본을 파괴하던 문제(→ run별 디렉터리), `git check-ignore`가 엉뚱한 경로를 검사해 tracked 경로를 통과시키던 문제, 금칙어 부분문자열이 `joined_at`·`selected`를 오거부하던 문제, 숫자/문자열 비교를 행 단위로 결정해 `"1,200"`을 조용히 누락하던 문제, 부분 export(`5000→1000`)가 살균 게이트를 통과하던 문제(→ 절반 이상 이동은 전부 보류). 전체: `docs/review/260814-claim-audit.md`.
  - 진입 지점 2곳: `nara-publish-spec` 스텝 0 게이트(미확인 수치 남으면 게시 거부), `nara-grill` 사실 조사(수치 주장 + CSV 있을 때만 읽기 전용 대조 — 수치가 문서에 굳기 전에 잡는다). `nara-workflow-doc-mode` 스텝 추가는 실사용되지 않아 보류.
- `nara-browser-verify` (신규 스킬) — **브라우저 AC를 헤드리스 런타임에서 판정**한다. 지금까지 `verify` 슬롯은 `nara-gap --verify` 하나였고 그것은 `docs/requirements.md` 텍스트를 코드에 `git grep -F`로 대조하므로 **화면에 보이는 AC를 원리적으로 검증할 수 없었다** (전 스킬 SKILL.md에 `headless` 언급 0건이었음). `nara-test-implement`는 커밋되는 테스트 *코드*를 쓰는 다른 산출물이고, `nara-local-shot`은 캡처만, `nara-ui-diff`는 배포 baseline과의 *비교*라 greenfield엔 baseline 자체가 없다.
  - **판정 스킬이라 후보가 아니라 결론을 낸다** — `Pass | Fail | Blocked | Unverifiable` terminal token 하나. 정적 소스 분석으로 `Pass`를 낼 수 없고, MCP 드라이버가 없으면 `Unverifiable: requires live runtime`으로 끝난다.
  - **축별 필수 증거 매트릭스**(`references/evidence-matrix.md`) — geometry/typography/color는 computed 값이 primary, asset/imagery/전체 렌더는 **실제로 열어본 스크린샷** 필수(computed·DOM 대체 불가), behavior/mutation은 trusted input + network request·response, a11y focus는 trusted key + 표시된 focus 스크린샷. **한 축이라도 필수 증거가 없으면 그 축 `Unverifiable`이고 aggregate `Pass` 금지.** "검사 안 함"과 "Unverifiable"을 구분해 적는다.
  - **anti-cheat 실행 규율**(`references/anti-cheat.md`) — `element.click()`/`form.submit()`/`dispatchEvent()`는 상호작용 증거가 **아니다**(합성 이벤트는 hit-testing·기본 동작·이벤트 순서를 건너뛰어 가려진 버튼·`pointer-events:none`·비활성 상태를 전부 통과시킨다). `evaluate_script`는 관찰 전용. mutation 주장에는 request+response 필요 — toast·로컬 DOM 변화·응답만으로는 각각 불충분. 인용한 스크린샷은 존재+non-empty+**실제 inspect**. 직렬화는 primitive를 plain object로 직접 복사(안 하면 두 MCP 다 `{}`를 떨구는데 그걸 측정 성공으로 오인).
  - **소유권 기반 정리**(`references/session-lifecycle.md`) — run-owned만 종료, `killall`·broad `pkill` 금지, 강제 종료 전 PID+profile 대조. dev 서버는 프로세스 exit가 아니라 **HTTP/port readiness를 poll**. 증거 디렉터리는 `git check-ignore` 통과 필수(실패 시 ESCALATE·진행 거부).
  - 서버 기동·auth bypass·드라이버 사다리는 복제하지 않고 형제 스킬 reference를 링크한다(`../nara-local-shot/references/auth-bypass.md`, `../nara-ui-diff/references/drivers.md`) — 단독 설치 시 스킵하고 repo 근거로 판단. 근거: [ADR-0002](docs/adr/0002-link-sibling-skill-references.md).
  - 배경·대안 비교: [ADR-0001](docs/adr/0001-verify-browser-ac-at-runtime.md).
- `nara-design-studio` — **레이아웃 파리티 검사** `assets/runtime/layout-contract.js` + `check-layout.py`. 핸드오프의 일치 기준은 픽셀이 아니라 **레이아웃**(섹션 순서·테이블 컬럼 순서·필드 순서·액션이 어느 쪽에 붙는지)인데, 지금까지 스펙은 그것을 순서 있는 형태로 진술하지 않아 구현자가 PNG 보고 재유추했다. 추출기는 **하나**를 디자인 쪽(스튜디오)과 구현 쪽(실제 페이지 콘솔/브라우저 MCP) 양쪽에서 돌려 정규화 JSON을 만들고, `check-layout.py`가 diff한다(exit 1 = 드리프트). 섹션 이름은 양쪽이 다르므로(디자인은 라벨, 앱은 없음) **콘텐츠 겹침**으로 정렬한다. `Spec.md` 최상단에 계약이 실리고 Export 메뉴에 `Layout contract (JSON)` 추가. 라디오/체크박스 옵션 라벨은 필드가 아니므로 제외 — 옵션 문구 변경이 드리프트로 오탐되지 않는다. 테스트 13개(`test_check_layout.py`).
- `nara-design-studio` / `nara-design-pack-builder` — **팩 → 실제 prop 매핑** `components[].real`(`import`/`from`/`propMap`/`drop`/`notes`). 팩 컴포넌트는 **적응된 복제본**이다 — `adapt-guide.md` §1–§2가 store/router/context 결합을 plain prop으로, CSS-in-JS를 토큰 스타일로, i18n 훅을 문자열로 바꾸라고 **요구**하므로 divergence는 구조적으로 발생한다. 그런데 존재하지 않는 prop을 넘기면 React가 **조용히 무시**한다 — 타입 에러도, 린트도, 실패 테스트도 없이 화면만 틀어진다. pack-builder Step 4가 적응하는 그 순간에 기록하고(나중 역추적은 원본 DS 재독), 런타임이 `/_pack/_ds_manifest.json`을 읽어 **해당 후보가 실제로 렌더한** 컴포넌트 행만 `Spec.md`에 넣는다. `real` 없는 팩에는 명시적 경고 — "모름"과 "동일함"이 같게 읽히면 안 된다.
- `nara-design-studio` — **DESIGN.md → 팩 변환기** `assets/runtime/designmd_to_pack.py`. DESIGN.md(Stitch format) frontmatter는 color role set·typography scale·spacing·radii·컴포넌트 스타일 스펙을 이미 담고 있어 **번들 starter 팩(T1, 토큰 23개·컴포넌트 0)보다 토큰 표면이 넓다** — 산문으로 읽지 말고 팩으로 변환한다. `components:` 블록이 있으면 **T2**(각 항목이 마운트 가능한 standalone JSX + `_ds_bundle.js`), 없으면 T1.
  - **authored / derived 분리.** 엔진 크롬이 요구하지만 DESIGN.md가 정의하지 않는 토큰(`--ds-primary-hover`, ink 램프, `--ds-radius-200`, `--ds-shadow-popover` 등)은 `tokens.css`의 별도 주석 블록으로 emit + stdout 리포트. 매핑 가능한 role이 없으면 `MISSING` + exit 1 — 추론값이 authored 값과 섞이지 않는다.
  - **리터럴은 컴포넌트 스코프 토큰으로 승격.** DESIGN.md `components:`가 geometry를 리터럴로 적으므로(`padding: 12px 24px`) 그대로 인라인하면 팩 자신이 adherence 규칙을 위반한다 → `--ds-comp-<name>-<prop>`로 뽑고 JSX는 `var()`만 참조.
  - pyyaml 있으면 사용, 없으면 stdlib 파서로 폴백 — **새 의존성 0**.
- `nara-design-studio` — **emit-time adherence 게이트** `assets/runtime/check_adherence.py`. baseline 규칙 "tokens only — no hardcoded brand values"는 산문으로는 강제 불가(`padding: 16px`가 적힌 시점에 이미 위반)라 기계 검사로 전환. 기본 규칙 2개(raw hex / allowlist 밖 raw px, `1px` hairline은 허용)는 팩 협조 없이 동작, 위반 시 exit 1 + 라인 리포트. 인라인된 `:root { … }` 블록은 면제(`SKILL.md` §5가 portable single-file export에 토큰 블록 인라인을 지시하므로 그것은 정의부지 하드코딩이 아니다). 팩은 매니페스트 `adherenceConfig`로 규칙을 조일 수 있다.
- `nara-design-studio` — **그린필드 분기**(`SKILL.md` §2.1–2.2). 팩 tier는 "DS가 있나"만 답하고 "IA가 있나"는 아무도 묻지 않아, `startingPoints` 없는 팩에서 화면마다 nav·컬럼·상태값이 재발명되고 화면 2개째부터 일관성이 사라지던 문제. `manifest.startingPoints` 공백 여부로 **자동 판정**(유저에게 묻지 않음)하고, 보이는 IA(nav 형태·페이지 골격)는 기존 layout-direction candidate가 갈리는 축으로 흡수, 안 보이는 IA(상태 enum·정렬 기본·row 클릭 의미)는 후보 비교가 무의미하므로 기본값 통보 + 거부권. 확정된 화면은 팩 `startingPoints`로 **write back**해 다음 빌드부터 브라운필드로 수렴시킨다.

- `nara-jira-triage` — Step 7 `reconcile` 계약 명문화: 큐 이슈 상태를 **PR 실측**으로 되돌리는 전이 규약(strict KEY 경계 매칭 후 `MERGED`→`done`+`drain_state=done`, `OPEN`→`in_review`, 다건·미머지 close는 무변경+경고)과 증거 우선순위(PR 실측 > Jira 상태 > `pr_url` metadata — 후자는 KEY 검증 없이 심겨 오염 가능, 근거 아님)를 선언. `gh pr list --search`가 fuzzy라(`PROJ-40` 질의에 PROJ-39/29 혼입) 경계 매칭 `(^|[^A-Za-z0-9])<KEY>([^0-9]|$)` 필수.
  - **실행은 이 스킬이 하지 않는다** — 결정론(LLM 판단 0)이라 out-of-band 크론 스크립트 소유. 역할 분리 명문화: 오토파일럿=없는 것만 생성(classify에 LLM 필요) / 스크립트=있는 것만 상태 sync. Step 1~6 = 생성 전용.
  - 배경: 큐 `done` 전이가 jira-drain cleanup에만 있어 cleanup 미실행·큐 밖 손PR 건이 머지 후에도 `in_review`로 박제됨.

- `nara-review-reminder` — **팀 리뷰 요청 확장 + 리마인더 이슈 reconcile** (`references/teams-and-reconcile.md` 신규). 필터가 `reviewRequests[].login`만 봤는데 GitHub은 팀 요청을 `{"__typename":"Team","slug":"<org>/<team>"}`으로 주고 **`login` 필드가 없다** — 팀으로 걸린 요청은 100% 누락돼 티켓이 아예 생기지 않았다(실측: sandbox-dns#721의 한 팀, api-server 열린 PR 다수의 팀 요청 전건). `gh api /user/teams`로 `<organization.login>/<slug>`를 조립해 **동적으로** 해석한다 — 팀 slug 하드코딩은 팀 이동 시 조용히 썩고, 어차피 오탐 위험을 줄여주지도 않는다(그건 아래 별개 필터의 몫).
  - **"내 차례" 필터.** 팀 요청은 팀원 아무나 처리하면 되므로, 매칭된 팀의 멤버 중 리뷰를 이미 남긴 사람이 있으면 티켓을 만들지 않는다. GitHub이 "팀원 1명 리뷰 시 팀 요청 자동 해제"를 하는지에 **의존하지 않는다** — 해제되지 않은 채 남아 있는 PR이 관측됐고(해당 리뷰어들이 그 팀 비멤버라 반증은 아니나 확증도 없다) 어느 쪽이든 직접 계산이 맞다. 개인 지정이 함께 있으면 팀원 리뷰와 무관하게 대상 — 나를 콕 집은 요청이므로.
  - **Step 0 reconcile.** 리마인더 이슈를 닫는 주체가 아무도 없어 끝난 PR의 이슈가 영구히 쌓였다. 생성 루틴 **전에** 열린 이슈를 실측 대조해 머지·클로즈·내 리뷰 완료는 `done`, 팀원이 대신 처리한 건은 `cancelled`로 전환한다(전환 건에는 코멘트·멘션 없음 — 조용히 닫는다).
  - `tracker_type=review` metadata 신설. `pr-activity-reminder`의 `activity` 이슈도 `pr_url`을 갖고 있어, 이 구분 없이는 reconcile이 **남의 자동화 이슈를 닫는다**. `request_via`는 reconcile이 "팀 경유만" 여부를 재조회 없이 판정하게 한다.
  - `read:org` 스코프 부재 시 **중단하지 않고** 개인 매칭만으로 계속 진행 — 리마인더가 통째로 죽는 것보다 부분 동작이 낫다.
  - waza: 토큰 1200→1677(+477, 상세는 reference로 분리해 +1152에서 축소), 링크 이탈 advisory는 baseline과 동일한 `../README.md` 백링크 1건으로 불변.

- `nara-jira-triage` — Step 7 reconcile 계약에 **Pass C(Jira 역기록)** 추가. Pass A가 merged PR로 큐를 `done` 처리해도 Jira는 `In Progress`에 남아 두 트래커가 갈라졌다. Pass C는 A의 `MERGED` 1건 분기에서만, 그리고 **Jira assignee가 나인 티켓에만** 전이를 건다.
  - **기본 OFF**(`JIRA_SYNC=1` 명시 opt-in). 팀이 보는 트래커에 대한 유일한 외부 mutation이므로 자동 실행을 기본값으로 두지 않는다 — merged가 곧 종료인지는 팀 워크플로의 판단이다.
  - **종료 상태명은 프로젝트마다 다르다.** 전이 id 하드코딩 금지를 계약에 명문화 — 한 프로젝트는 `Resolved`/`Closed`를 노출하고 다른 프로젝트는 `Done` 하나뿐이라, 이름 하나로 고정하면 한쪽이 통째로 막힌다. `to.statusCategory.key == "done"`인 전이 중 `$JIRA_CLOSE_STATUSES` 순서로 첫 매칭을 고른다(카테고리 제약이 있어 동명의 비-done 상태를 잘못 집을 수 없다).
  - 실행 주체는 여전히 이 스킬이 아니라 out-of-band 크론 스크립트 — 스킬은 계약만 선언한다.
- `nara-local-shot` — Before/After 비교를 **두 revision·두 pass로 명시적 절차화** (Step 1 재작성 + `references/comparison-passes.md` 신규). 기존 Step 1은 As-Is 복원을 `git show`+preview page 한 경로로만 처방해서, subject가 **real app page**이거나 옛 렌더가 그 사이 바뀐 공유 코드에 기대던 경우(복원 시 drift) 필요한 두 번째 pass — 베이스 revision 워크트리 + dev server 재시작 + deps/build/codegen 산출물 갱신 — 를 아무도 언급하지 않았다. 그 비용은 앱을 띄우는 시퀀스이고 teardown 이후에 발견되므로 런치를 두 번 지불하게 되며, 비교표는 한 열만 채운 채 placeholder로 나간다.
  - **As-Is 존재 여부를 먼저 판정.** 순수 추가 변경은 선행 렌더가 없으므로 To-Be만 찍고 그 사실을 보고 — 없는 이전 상태를 뒤지지 않는다. 현재 상태 확인만 원하면 single pass.
  - **네이밍 스킴 선고정** `<state>-asis.png` / `<state>-tobe.png` — 두 pass가 같은 state를 쓰므로 무자격 이름은 충돌. Step 6에 teardown 전 계획된 shot 전수 존재 확인 추가(사후 발견 = 전체 재런치).
  - 트리 전환은 in-place `checkout`/`stash` 대신 별도 워크트리 — 미커밋 To-Be 작업 보존. revision 넘어온 stale 산출물이 비교의 반대편을 조용히 렌더하는 케이스 경고.
  - waza: advisory fail 집합 불변(baseline 4개 그대로, 신규 0), module-count 2→3(optimal 유지), 토큰 1318→1566(SKILL.md는 요약만, 절차는 reference로 분리).
- `nara-design-studio` — 부트스트랩 게이트를 **프로젝트 1회 결정** 모델로 재작성. 어떤 디자인 시스템 위에 짓는지는 프로젝트 고유 결정이므로 **상속되지 않는다** — 유저의 `defaultPackPath`나 공유 디렉터리에 팩이 있다는 이유로 신규 repo가 무관한 회사의 디자인 언어를 조용히 물려받는 것을 막는다. 결정을 확정할 수 있는 소스는 `.claude/overrides/nara-design-studio.md` 하나뿐이고(있으면 무질문 사용, 없으면 반드시 질문 후 여기에 기록), `settings.local.md`의 `defaultPackPath`(`packPath`는 alias)와 `~/.claude/design-packs/*/`(팀·사내 배포가 팩을 떨어뜨리는 자리)는 **질문의 기본 선택지로 강등** — 단독으로 이기지 않는다. 기존엔 단일 글로벌 `packPath`뿐이라 프로젝트마다 다른 팩을 쓰려면 매번 그 줄을 고쳐야 했다. 선택지에 **DESIGN.md 변환**을 추가하고 (a)의 소스 범위를 "design-system codebase"에서 설치된 npm 패키지·Storybook·배포 dist까지로 확장했다(UMD를 배포하는 DS는 컴포넌트별 adaptation이 아예 불필요한 경우가 많다).
- `nara-code-review` — trailing status 계약을 **증거 없이 쓸 수 있는 verdict가 하나도 없게** 만들고 실패 불가 테스트 카탈로그를 주입 (3커밋, forge EPT 검증):
  - `agents/tests-regression.md`에 **실측 vacuous 기전 10종** 열거(기존엔 `"Assertions that cannot fail"` 한 줄뿐). 실제 리뷰에서 mutation으로 증명된 사례 — `mockImplementationOnce`+React 동기 재시도 / 대상 상수로 기대값 계산 / `not.toBe` 방향 미고정 / 가드 없는 분기 / 소스가 안 읽는 필드로 `it.each` / 부재 단정 / React가 `null`을 렌더 안 함 / boundary 밖 chrome 단정 / 최상단 고정 mock / 키·상수 리터럴 복제.
  - `report.md` trailing status가 **명령 종료 상태와 파일 수를 인용**하도록 강화. `validation: pass`는 인용된 exit code로만, `scope-integrity`는 양측 카운트로만 성립.
  - **`scope-integrity`에 세 번째 상태 `expanded` 추가.** 성립 조건 3개(파일별 사유·수정 적용 **전** 공개·명시적 승인) 전부 충족해야 하고 하나라도 없으면 `MISMATCH`. 사후 승인은 MISMATCH를 되돌리지 않는다 — 먼저 공개하는 이유가 유저가 아직 거절할 수 있어야 한다는 것이므로. `expanded`는 `→ ESCALATE:`를 달지 않고 applied로 보고된다.
    - 배경: `match | MISMATCH` 2상태에서는 **사유를 적고 승인까지 받은 확장도 ESCALATE로 끝나** 통제된 실행이 escalate로 보이고 미공개 드리프트와 구분되지 않았다.
  - 템플릿이 산문과 어긋난 4슬롯 정합: `validation: pass`에 `baseline <base> → exit <code>` 슬롯(비-0 exit을 baseline 인용으로 강등하는 경로는 산문에만 있고 템플릿은 `exit 0`을 하드코딩했다) / `scope-integrity: match`·`fix-ledger: match`도 카운트 인용 / `overrides: none`은 확인 명령을 인용(`none`은 "찾아봤다"는 주장, `unverifiable`은 안 찾았다는 뜻) / `→ ESCALATE:`는 **블록 바로 아래** 고정(리포트 본문 유무와 무관하게 status와 함께 이동).
  - eval 신규 task 2 + fixture 2(승인된 확장 / baseline 인용된 비-0 exit). 기존 `validation-status-evidence-001`이 **반대 케이스 회귀 가드**로 작동 — 미baseline·미공개는 여전히 `fail`·`MISMATCH`이고 3라운드 전부 green.
  - 미해소(다음 테마): `→ ESCALATE:`가 MISMATCH에만 규정돼 `validation: fail`·`unverifiable`의 escalate 여부 미정 / `unverifiable`과 zero-fix 표(`match`+`0,0,0` 강제)의 상호작용 / SKILL.md가 500 하드리밋 대비 632토큰 초과(20 모듈 통합·examples 섹션 부재와 함께 별 테마).
- `nara-code-review` — 검증 단계의 **wall-clock 낭비와 조용한 오염 경로 2건**을 `verification.md`에서 차단 (실사용 세션 회고 기반, SKILL.md 무변경):
  - **뮤테이션 재검증 스코프 규칙 신설.** 스킬이 `tests-regression`에서 "살아남는 mutation을 지목하라"는 증거를 요구하면서 정작 **수정 후 재검증 범위는 규정하지 않아** 라운드마다 전량(10~20종 × 30초~4분) 재실행됐다 — 10분 툴 타임아웃에 두 번 걸린 실측 사례. 재실행 대상을 **이번 라운드가 바꾼 파일에 mutation site가 있거나 kill하는 테스트가 바뀐 mutant**로 한정(나머지는 이전 판정을 라운드 표기와 함께 재진술), 전량 스윕은 수렴 후 최대 1회, 배치당 ≤4 + 배치별 결과 즉시 영속화(타임아웃이 앞 배치 결과를 못 버리게).
  - **뮤테이션 잔존물 가드.** 배치 러너는 프로덕션 코드를 in-place로 변형하고 종료 시 되돌리므로, 타임아웃 kill은 **변형된 채로 남은 파일**을 만든다. 배치 전 pre-state(`git stash create` 또는 파일별 `git hash-object`)와 `git status --porcelain`을 기록해 배치 후 비교 — 불일치면 기록된 pre-state로 복원 후 STOP·escalate, 다음 배치를 dirty carry-over 위에서 시작 금지, 잔존물 검사가 실패한 실행은 verified로 보고 금지.
  - **writer 계열 validator의 경로 한정.** formatter·`--fix` linter·codemod는 매니페스트 파일을 명시 인자로만 실행하고 repo-wide 글롭(`npm run format` → `prettier --write .`)은 금지. 매니페스트 밖 재작성은 ledger가 설명할 수 없어 `changed-but-unclaimed`로 떠오르고 `scope-integrity`를 오염시키며 commit amend를 유발한다(실측: amend 2회). 경로 한정이 불가능한 도구는 check/dry-run으로만 실행.
  - eval 신규 task 2 + fixture 2(타임아웃 배치의 잔존물 / 글롭 formatter가 12개 무관 파일 재작성). 후자는 `scope-expansion-disclosed-001`의 대칭 케이스 — 사유·승인 없는 확장은 validator가 전부 green이어도 `MISMATCH`로 남는다. 설치된 waza(v0.31.0)에 `eval` 커맨드가 없어 러너 대신 **편향 없는 서브에이전트 프로브 2회**로 grader 문구를 실측했고, 초안 anchor 3개가 오탐으로 드러나 교정: (1) trailing status를 요구하지 않는 프롬프트에 대문자 `ESCALATE`를 요구한 건 계약 근거 없음(모델은 "에스컬레이션"·소문자 인용) → 제거, (2) **상태값 anti-anchor는 구조적으로 사용 불가** — 올바른 실행일수록 복구 후 목표 상태(`scope-integrity: match (scope 2 → touched 2)`)를 처방하므로 `output_not_contains`가 정답을 떨어뜨린다 → positive-only anchor로 전환. 미고정 구간은 task description에 명시(잔존물 task는 "batch 4를 시작하지 않는다"를 substring으로 붙들 수 없어, 복원·보고는 맞고 carry-over 위에서 재개하는 실행을 통과시킨다).
  - 채택 안 함: 리뷰어 수 축소(3→2). 리뷰어는 병렬이라 대기시간 = max(개별)이고 축소는 토큰만 줄이며 검출력을 깎는다.

## [0.20.0] - 2026-07-22

### Changed
- `nara-adversarial-review` — forge 하드닝 (EPT 프로브 검증):
  - code-review 계약 변경 sync: refuter에 non-runtime finding 재검증 규칙(사실 자체를 grep/read로), rigor auditor에 observability 루브릭 인지(suggestion의 E3-무실행경로는 위반 아님) + 신규 정상 status 값(`manual-only`, zero-fix `match`/`0,0,0`, empty-scope n/a) 등재.
  - 프로토콜 gap 규정화: refuted↔weakened 경계 규칙(path 불성립+실결함 → refuted+missed-found 재정식화·상호링크), missed-found 채택에 원 리포트 게이트 적용, `N missed-found`=채택분만 카운트, refuter 입력=confirmed+unadjudicated, manifest 부재 시 finding location 복원 허용, diff 미복원·rejected 섹션 부재 fallback.
  - 런타임 중립화("Agent tool" → "병렬 subagent") + SKILL↔protocol 모순 1건 해소(refuter 대상 범위).
- `nara-pr-review` — forge 하드닝 (EPT 프로브 검증):
  - PR-plane/code-plane 경계 규정: lane 산출물은 프로세스 평면 요약만(finding-schema 변환·dedup·Judge 비대상), lane 발견 코드 결함은 code-plane으로 이관 후 finding ID 참조(이중 보고 금지).
  - 리포트 구성 명문화(code-plane finding 섹션 + lane 요약 4 + trailing status), adjudication 준용 규칙(code-review 설치 시 adjudication.md), 수집 실패 시 부분 데이터 리뷰 금지(`❌ 실패:` 중단), receipt↔게시 초안 시점 분리, 재사용 목록에 routing 명시, ci 다중 실패 표기.
- `nara-code-review` — 리뷰 관점 15종 검토 후 14종을 기존 10 agent에 흡수(신규 agent 0 — 직교성 유지, 체크당 owner 1명):
  - 신규 섹션: deploy-window/시간축 호환(contracts, mixed-version·rollback deserialize) / business abuse(security, rate-limit·자원 독점) / failure aftermath(resilience, DLQ·재처리·수동 복구) / data lifecycle(resilience, cascade delete·soft-delete 누출) / i18n(frontend, 하드코딩 문자열·조사/복수형) / observability 심화(operations, 추적성·retry-vs-영구실패·alert actionability).
  - 라우팅 구멍 수리: 순수 코드의 신규 failure path(새 catch/외부 호출)도 operations-config 트리거.
  - context-map에 조건부 historical-context 단계(의문 guard/legacy 주석 → `git log -p`/`blame`).
  - P2 불릿: AC 완전성·temporal 경계(behavior), caller sweep 의무화(contracts), 과금 API(performance), mock fidelity(tests), add-without-delete·temp compat 기한(architecture), double-submit·dead-end 에러(frontend), 위험 기본값(operations).
- `nara-code-review` — skill-forge 5 iter (전부 kept):
  - 빈 스코프 정의: clean tree에서 base에 이미 머지된 커밋 재리뷰 방지(merge-base 가드) + fallback 순서 + n/a trailing status 규정.
  - `manual-only` 수렴 라벨 신설(confirmed 잔존이 전부 R2/R3) + fix 0건 시 trailing status 규칙(`match`/`0,0,0`, n/a는 `--fix=none` 전용).
  - description에 DO NOT redirect 추가: production incident root-cause → nara-incident (토큰 패리티 1097→1096).
  - routing.md 런타임 중립화("Agent tool" → "parallel subagents").
  - eval 수리: 구 5-agent 체계 잔재 assertion("High") 및 과광폭 not_contains("요구사항") 교정.
- `nara-code-review` — forge 2라운드 (iter 6–8, 전부 kept):
  - non-runtime finding 시맨틱 정립: 관측 가능한 불일치(rename leftover·중복 util·dead code)는 유효한 suggestion finding — E레벨을 "주장 사실의 관측가능성"으로 재해석(E3=repo 검증, E2=diff 도출), E2 게이트 동일 적용. suggestion의 failure_path는 비용 경로(drift·혼동)로 서술.
  - 부기 명확화: policy-excluded(suggestion·R3)는 auto-fix candidate 아님(Judge 스킵 근거), 통계표 `-(unadjudicated)` 표기 + fingerprint 병합 집계 규칙, zero-fix 런은 validation 실행 의무 없음(실행된 것만 보고).
  - `--staged` 스코프 옵션 신설(커밋 직전 staged만) + NL 매핑("staged만" 요청 시 플래그 없이 적용) + staged manifest 시맨틱(head=index) + 제외 dirty 파일 고지.

## [0.19.0] - 2026-07-22

### Fixed
- workflow-core 스킬 결함 일괄 수정 (darwin-skill 최적화 + 독립 adversarial 검증):
  - `nara-reflect` — handoff.md 통째 덮어쓰기 + 기존 handoff 미읽음으로 인한 **교차세션 데이터 손실** 수정 (§1 carry-forward + §3 merge). memory frontmatter의 phantom "글로벌 CLAUDE.md 스키마 일치" 주장 제거. 타깃 충돌 tiebreaker(prescriptive→CLAUDE.md / descriptive→memory) + preview CHECKPOINT.
  - `nara-gap` — score 공식 div-by-zero(전 항목 Agreed Exception) 가드 + `N/A` gate 분기 + Needs Confirm/Unknown deflation 명문화.
  - `nara-ac-draft` — `docs/requirements.md` 무가드 덮어쓰기(prep 산출물 clobber = 데이터 손실) 가드 추가 + self-rerun AC-ID 안정성.
  - `nara-rfc` — "Output ONLY RFC Markdown" 룰 ↔ interview/파일저장 스텝 모순 해소 (파일-내용 계약으로 rescope).
  - `nara-workflow-doc-mode` — clear-path frontmatter↔body 순서 모순 + prep-role mismatch(prep는 grill 산출 persist 불가) 수정, AC 기록 타깃 명시.
  - `nara-workflow-orchestrator` — "now" 트리거 `nara-now` 충돌 제거, scope dead-code 제거, 라우팅 표 중복 제거(SKILL.md=SoT).
  - `nara-workflow-dev-mode` — frontmatter spine ↔ body core spine drift 수정 (TDD를 execute 옵션으로 정정).

### Changed
- `nara-plan` — 수직 분할 6-step 절차 추가 (기존엔 계약+템플릿만 있고 분할 알고리즘 부재).
- `nara-adr` — Error Handling if-then 분기 추가 (context 부족/seq 충돌/supersede 누락/source 부재/routine 거부/중복).

### Fixed (non-core 스킬 defect batch — triage 후 real-defect 9건, 독립 adversarial 검증)
- `nara-now` — 버려진 `claude-mem` 참조를 memory 도구(engram 등)로 교체 (SKILL step5 + `now-tables.md`). 세션 진입 스킬의 메모리 arm이 조용히 죽어 있던 것 수정.
- `nara-pr-respond` — 동료 PR 스레드 답글 **무단 auto-post** 방지: preview-default(draft→show→confirm→post) 게이트를 SKILL + `references/procedure.md`(실행 절차) 양쪽에 강제.
- `nara-review-reminder` — Multica 이슈 description의 리터럴 `\n`(백슬래시-n 렌더) → `printf` 실개행. fire-and-forget 자동화 계약 명시.
- `nara-local-shot` — 배포 시 미해결되는 `[[wiki-link]]` Obsidian 참조를 인라인 설명으로 교체.
- `nara-design-studio` — USE FOR 과광범으로 전용 팩 스킬과 라우팅 충돌 → `DO NOT USE FOR` redirect(팩-agnostic 엔진 vs 전용 팩) 추가.
- `nara-test-verify` — `nara-test-discover`(S2/S3 ID)와 `nara-golden-path-discover`(제목+step, ID 없음) 이중 스키마 misfire 수정: 스키마 감지 + 페르소나 프롬프트(`agent-prompts.md`) fence 내 Input-schema 주입 + dispatch 배선. NEEDS_WORK/FAIL remediation loop 명시.
- `nara-jira-drain` — launch 후 metadata를 무조건 `working`으로 flip하던 것 수정: launch 커맨드 exit 성공 시에만 mark, `working=launched(실행 확정 아님)` 세만틱, 오발은 다운스트림 `PR_RESULT` 부재로 감지.
- `nara-trending-digest` — self-renew가 (a) 중복 cron 생성(`CronCreate` dedup 없음) → `CronList→Delete→Create`, (b) crawl 성공에 묶여 crawl 실패 시 스케줄 death → **Step 0**(crawl 전, ungated)로 이동. off-minute cron. fire-and-forget 계약.
- `nara-golden-path-discover` — 다운스트림 `nara-test-verify`가 golden-path 스키마를 파싱 못하던 문제 해결(test-verify 스키마 분기로; producer 측 변경 없음).

## [0.18.0] - 2026-07-22

### Added
- `nara-local-shot` — 로컬 실행 웹앱(SSO-gated 포함) 스크린샷 캡쳐+파일 저장 스킬. PR Before/After visual comparison·UI 검증용. 핵심: dev 서버 + chrome-devtools MCP로 직접 캡쳐(placeholder만 남기지 않음), 세션 없는 자동 브라우저는 더미 쿠키로 우회 — presence-only 미들웨어 + `.ico` matcher 트릭 + API-free 격리 프리뷰 전제. `references/auth-bypass.md`(메커니즘·httpOnly caveat·real-storageState fallback), `references/프로젝트별 레시피(구체값은 소비 repo 소유). nara-ui-diff(env-diff)와 스코프 구분.

- `nara-pr-review` — 원격 PR evidence-based 리뷰 (gh 기반, 체크아웃 없음). 코드 평면(nara-code-review 리뷰어 체계 재사용, 미설치 시 lane 요약 fallback) + PR 평면 4 lane(description↔diff 정합 / commit 구성 / CI 신호 / discussion 커버리지). 리포트 우선, 코멘트 게시는 finding 단위 승인 후에만 — approve/request-changes는 항상 사람.
- `nara-adversarial-review` — 기존 리뷰 리포트 공격 검증: refuter(finding 격추 시도) + blind hunter(리포트 미열람 재리뷰 후 대조) + rigor auditor(evidence level·proof·trailing status 무결성). 원 리포트에 append-only. `/codex:adversarial-review`의 네이티브 대안 (의존+fallback).

### Changed
- `nara-grill` — design-review 흡수: 설계 대상(구현 전 설계·대규모 리팩터링·API 설계·모듈 경계)일 때 `references/design-probes.md` 압박 축(경계·소유권 / API 계약 / 변경 비용·롤백 / 규모·실패 모드 / 코드베이스 정합) 사용. USE FOR에 "설계 리뷰"/"design review" 등 추가. 코드 diff 존재 시 code-review로 리다이렉트 명시.
- `nara-code-review` — **전면 재설계: 고정 5-agent → Evidence-based Reviewer→Judge→Fixer→Verifier 파이프라인.**
  - 리뷰어 직교화: 코어 4 (behavior-state / contracts-compatibility / resilience-data-integrity / tests-regression) + 조건부 6 (security-privacy / performance-resources / architecture-reuse / frontend-ux-a11y / database-migration / operations-config, 변경 내용 트리거 라우팅). security-performance 분리, cross-cutting 공통 체크리스트 해체(항목별 주 담당 agent 지정) — 공통 주입은 Universal Reviewer Contract만.
  - Evidence Level(E0–E3) 도입: 최종 finding 조건 = `evidence >= E2 AND confidence >= threshold`. E1 이하는 "미검토 리스크/확인 질문"으로 분리. confidence 구간 기준 명문화.
  - Finding 스키마 강제: invariant / preconditions / failure_path / counterevidence_checked / validation 필수, fingerprint = path+symbol+invariant (라인 넘버 아님).
  - 역할 분리: read-only Reviewer → blind Judge(원 confidence·proposed fix·중복발견 은닉, critical/major·보안·auto-fix 후보·충돌 필수 심사) → 중앙 단일 Fixer(ledger 순 직렬) → 별도 Verifier.
  - Auto-fix 위험 등급 R0–R3 + `--fix=none|safe|selected|all` (기본 safe = R0+검증가능 R1). suggestion·R3는 어떤 모드에서도 자동 수정 금지.
  - Claimed-vs-Observed를 파일 단위 → issue 단위로 강화: 라운드 시작 hash 스냅샷 + hunk·validation proof, mismatch 3분류(claimed-but-unchanged / changed-but-unclaimed / changed-but-unresolved). 수정 시 최종 baseline 전체 diff 재리뷰 필수.
  - Scope 보완: dirty→staged+unstaged+untracked, clean→HEAD~1, 시작 시 review manifest 고정(외부 변경 = scope mismatch). Context에 변경 의도(spec) 수집 단계 추가, 없으면 `specification: unavailable` 명시.
  - Override 보완: Accepted exceptions 테이블(`suppressed-by-project-exception`) + override 내 임의 shell command 자동 실행 금지(프로젝트 정의 validation script만).
  - references 재구성: agents.md/phases.md/fix-loop.md/cross-cutting.md 삭제 → scope/context-map/routing/reviewer-contract/finding-schema/adjudication/fix-policy/verification/report + agents/*.md 10개.
- `nara-skill-forge` — Darwin Skill 메커니즘 이식 + darwin 9-dim 평가 루프 하드닝(baseline 75.8 → 독립 judge 실측 ~87). **회귀 래칫**(fix→재채점→prior-passing grader 회귀 또는 토큰 증가 시 워킹트리 복원, no-auto-commit 각색) + **runtime-neutrality gate**(single-runtime lock grep 스캔, `references/ratchet.md`·`runtime-gate.md`). description `Triggers on:`→`USE FOR / DO NOT USE FOR`(런타임 중립 "agent skill"), 🔴 CHECKPOINT/🛑 Benchmark-only/🛑 최종 STOP 게이트. **Phase 2 결과 포맷 사실 오류 수정**(flat 리스트는 `waza grade` 거부 → `waza run` mock-probe 스키마, 적대적 subagent 실증), **Phase 1 no-Copilot 기본화**(waza 결정적 절반 의존, LLM 절반은 실행 에이전트가 대체 — task 직접 저작, `waza suggest`는 Copilot 옵션), **grader-validation**(정답+오답 주입으로 hollow grader 폐기), **waza-absent degraded path**(dry_run 마킹, 점수 날조 금지), task당 two-run 채점, Reporting/results-schema를 `references/reporting.md`로 progressive disclosure, Troubleshooting if-then 3열 표.
- `nara-empirical-prompt-tuning` — description USE FOR에서 "스킬 개선" 제거, DO NOT USE FOR에 "스킬 개선/강화/벤치마크 → nara-skill-forge" 리다이렉트 추가. skill-forge와의 라우팅 충돌("스킬 개선해줘" 코인플립) 해소. README.md 동기.

## [0.17.0] - 2026-07-16

### Added
- `nara-implement` — 검증 게이트 구현 스킬 (전략 승인 → TDD 옵션(red→green) → verify → staged 정지). **자동 커밋 없음** (글로벌 no-auto-commit 룰 준수 → `/nara-commit` 위임). dev-mode `execute` 단계.
- `nara-grill` — 사실 조사 후 한 번에 한 질문씩 설계 검증 (침묵≠동의). dev/doc 설계 탐색 satellite.
- `nara-plan` — 스펙을 독립 검증 가능한 수직 작업 단위로 분할 → `docs/plan.md`. dev-mode `plan` 단계.
- 세 스킬 모두 4-state verdict(`Pass | Fail | Blocked | Unverifiable`) + "미실행/미확인은 통과 보고 금지" 하네스 채택.

### Changed
- **superpowers 의존 전부 제거** — nara-kit이 이제 superpowers 없이 완결.
  - design exploration `superpowers:brainstorming` → `nara-grill`
  - plan `superpowers:writing-plans` → `nara-plan`
  - execution(SDD/TDD) `superpowers:subagent-driven-development` + `test-driven-development` + `executing-plans` → `nara-implement`
  - branch finish `superpowers:finishing-a-development-branch` → dev-mode 내 네이티브 git 시퀀스
  - `superpowers:receiving-code-review` 원칙 → `nara-pr-respond` 본문 인라인
  - 남은 외부 참조는 `codex:adversarial-review`(선택) 하나뿐.
- `nara-incident` — red-capable feedback-loop gate 추가 (재현 없이 가설 "유력" 금지, `Blocked`/`Unverifiable` 상태 도입).
- dev-mode/doc-mode/orchestrator 라우팅을 네이티브 스킬로 재배선. 스킬 수 41 → 44.

### 출처
- `github.com/MTGVim/tiger-kit` v19 (mattpocock/skills=superpowers 계보의 vendor-neutral fork)에서 `tk-implement`/`tk-grill-me`/`tk-to-tickets`/`tk-diagnosing-bugs` 패턴을 나라화해 흡수.

## [0.16.0] 및 이전

이 CHANGELOG 도입(위 Unreleased) 이전의 릴리즈 기록은 git tag와 커밋 로그에 있다:

```sh
git tag --sort=-creatordate      # v0.16.0 … v0.11.3
git log <prev-tag>..<tag> --oneline
```

주요 마일스톤: 플러그인 → Agent Skills 포맷 전환(`nara-` prefix, hooks 제거), naranizer/humanizer, release-prep/finalize, ui-diff, jira-triage/drain 등.
