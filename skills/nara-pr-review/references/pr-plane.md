# PR Collection & PR-Plane Lanes

## Collection

```bash
export GH_HOST=<PR URL의 hostname>   # 예: git.example.com. 첫 gh 호출 전에 반드시
gh pr view <n|url> --repo <owner/repo> --json title,body,state,baseRefName,headRefName,commits,files,additions,deletions,labels,reviewRequests
gh pr diff <n> --repo <owner/repo>
gh pr checks <n> --repo <owner/repo>
gh api repos/<owner>/<repo>/pulls/<n>/reviews
gh api repos/<owner>/<repo>/pulls/<n>/comments      # inline threads
gh pr view <n> --repo <owner/repo> --json comments  # conversation
```

- **`GH_HOST`는 환경에서 확인하는 게 아니라 PR URL에서 도출해 직접 export한다.**
  안 하면 `--repo <owner/repo>`가 엔터프라이즈 PR도 github.com에서 찾아
  `Could not resolve to a Repository with the name '<owner/repo>'`로 실패한다.
  gh에 두 호스트가 다 로그인돼 있어도 기본 호스트는 github.com이다.
  체크아웃하지 않는다. 로컬 워킹트리는 불변.
- 수집 실패(`GH_HOST` 미설정, 권한, 404)는 `❌ 실패:` 블록으로 즉시 중단한다.
  부분 데이터로 리뷰를 진행하지 않는다.
- 변경 파일의 전체 컨텍스트: `gh api repos/<o>/<r>/contents/<path>?ref=<headRef>`
  (base 비교 필요 시 `ref=<baseRef>`도).
- diff가 큰 경우(>~50 files) 리뷰 범위를 디렉터리 단위로 분할해 lane당 배분하고,
  분할 사실을 리포트에 명시한다 (silent cap 금지).

## Code-plane fallback lanes

`nara-code-review`가 설치돼 있으면 그쪽 references(agents/*.md)를 사용하고 이
섹션은 무시. 없을 때만 아래 4개 lane 요약으로 core 리뷰 수행:

- **behavior-state**: 비즈니스 로직·상태 전이·경계값·순서 의존성·이전 동작과의 차이
- **contracts-compatibility**: 타입·nullability·API/DTO/serialization 계약·하위 호환
- **resilience-data-integrity**: 예외·retry·timeout·transaction·idempotency·race
- **tests-regression**: 변경 동작 테스트 충분성·잘못된 assertion·누락 회귀 테스트

spec-fidelity(기획 충실도) 리뷰어는 PR이 가리키는 티켓이나 스펙 문서를 실제로
읽을 수 있을 때만 띄운다. PR 본문은 요구사항이 아니다. 본문과 diff의 정합은
description-alignment lane이 본다. 못 읽으면 리포트에 skipped로 남긴다.

finding 최소 필드: location(path+symbol) / invariant / preconditions /
failure_path / impact / counterevidence_checked.

## Dispatch (code-plane + PR-plane 공통)

리뷰어와 lane은 main 세션이 직접 순회하지 않는다. code-plane 리뷰어(설치 시
routing이 고른 것, 미설치 시 위 fallback 4개)와 PR-plane lane 4개를 **한 배치의
병렬 subagent**로 동시에 띄우고, main 세션은 취합만 한다. Judge도 별도
subagent다 (리뷰어 컨텍스트를 물려받지 않아야 독립이다).

- subagent는 전부 read-only. 코멘트 게시·approve·push를 하지 않는다. 게시는
  main 세션의 승인 게이트만 한다.
- code-plane 리뷰어 프롬프트에는 routing이 정한 구성(reviewer-contract + agents 파일 + manifest + diff)에 더해 Collection에서 받은 **변경 파일의 전체 본문**(`gh api contents` 결과)을 붙여 넣는다. 리뷰어가 스스로 조회하게 두지 않는다.
- lane 프롬프트에는 Collection 결과 중 그 lane이 쓰는 것을 붙여 넣는다
  (description-alignment: 본문+diff, commit-composition: commits+diff,
  ci-signal: checks+변경 파일 목록, discussion-coverage: reviews+threads+diff).
  경로만 넘기지 않는다.
- subagent의 shell은 main의 `export GH_HOST`를 물려받지 않는다. 추가 조회가
  필요하면 매 명령에 `GH_HOST=<host> gh ...`를 붙이라고 프롬프트에 host를 적는다.
- 모델은 code-plane 리뷰어와 같게 맞춘다 (nara-code-review 설치 시
  `$JUDGMENT_MODEL`). 미설치면 `model`을 생략하고 세션 모델을 쓴다.
- subagent를 띄울 수 없는 환경이면 main 세션이 lane을 순차 수행하고, trailing
  status의 `dispatch:`에 `inline (<사유>)`로 남긴다. 조용히 inline으로 내려가지 않는다.

## PR-plane lanes (항상 4개, 병렬 subagent)

Lane 산출물은 lane 요약(프로세스 평면)으로만 리포트에 실린다 — finding-schema로
변환하지 않으며 fingerprint dedup·Judge 대상이 아니다. lane이 코드 결함을
발견하면 직접 finding으로 보고하지 않고 code-plane으로 넘겨 finding화한 뒤,
lane 요약에서 해당 finding ID를 참조한다 (같은 사실의 이중 보고 금지).

리포트 파일 구성: code-plane finding 섹션(code-review report 형식 준용) +
PR-plane lane 요약 4개 + trailing status. Judge 절차는 nara-code-review
설치 시 adjudication.md 준용, 미설치 시 SKILL.md Step 4의 요약 규칙만.

**1. description-alignment**
- PR 본문이 주장하는 변경 vs 실제 diff: 미신고 변경(diff에 있는데 설명 없음),
  과장 주장(설명에 있는데 diff에 없음), 스코프 크리프(제목과 무관한 변경 혼입).
- Breaking change·마이그레이션 필요가 본문에 선언돼 있는가.

**2. commit-composition**
- 커밋이 논리 단위인가: 혼합 관심사(기능+포맷팅+리네임 한 커밋), fixup 잔재,
  되돌리기 쌍(add 후 remove), 거대 단일 커밋에 리뷰 불가 사유.
- 커밋 메시지가 repo 컨벤션을 따르는가 (강제 아님 — repo에 컨벤션 흔적이 있을 때만).

**3. ci-signal**
- 실패·스킵된 check와 그 의미. flaky 재시도 흔적 (동일 check 반복 실행).
- CI가 못 잡는 갭: 변경 영역에 테스트 job이 아예 없는 경우 지적.
- CI가 이미 실패로 잡은 항목은 finding 중복 생성 금지 — 요약만.

**4. discussion-coverage**
- 미해결 리뷰 스레드: 코드가 바뀌었는데 resolve 안 된 것 vs 답변 없이 방치된 것.
- 이전 리뷰어 지적이 실제로 반영됐는지 diff로 검증 (주장 아닌 hunk 확인).
- 반복 지적 패턴 (같은 이슈 여러 리뷰어) — severity 승격 후보.

## Posting rules

- 리뷰 완료 시 콘솔 응답은 output contract의 receipt (상세는 리포트 파일).
  초안 전체 표시는 사용자가 게시 의사를 밝힌 시점에 수행한다.
- 게시 전 초안 전체를 사용자에게 표시 → finding ID 단위 승인 → 승인분만
  `gh pr review --comment --body ...` 또는 inline (`gh api pulls/<n>/comments`).
- approve / request-changes는 절대 이 스킬이 실행하지 않는다.
- 게시 실패(권한 등)는 `❌ 실패:` 블록으로 보고, 리포트는 유지.
