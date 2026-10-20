---
name: nara-retro
description: >-
  Look back at how a session went or why a skill misbehaved: tie each lesson to observed evidence, separate confirmed causes from guesses, and route the smallest prevention to its owner — write memory directly (with preview), recommend a test/lint/script, CLAUDE.md rule, skill fix, hook or ADR, or conclude no change. A nara-kit skill failure becomes a redacted improvement proposal.
  USE FOR: "retro", "회고", "세션 회고", "오늘 배운 것", "이거 어디 저장", "왜 또 틀렸지", "재발 방지", "이 스킬 불편했어", "nara-kit 개선 피드백", "스킬로 만들까", "결정 기록할 거 있나".
  DO NOT USE FOR: 하다 만 일·열린 질문 인계 (→ nara-handoff), 기존 규칙·메모리 중복·충돌 감사 (→ nara-grooming), 스킬 개선 실행 (→ nara-skill-forge), 코드 리뷰 (→ nara-code-review), 아키텍처 결정 문서 작성 (→ nara-adr).
---

# retro: 무엇을 배웠고 무엇을 바꿔야 하나

> 출력 형식은 [nara-kit 출력 계약](../nara-now/references/output-contract.md)을 따른다. 이 본문이 다르게 정한 곳은 본문이 우선한다. 파일이 없으면(단독 설치) 이 줄은 건너뛴다.

코드 diff의 품질이 아니라 **일한 과정과 환경**을 돌아본다. 학습마다 근거를 붙이고, 가장 작은 예방책과 그 소유자를 정한다. 직접 쓰는 곳은 auto-memory 하나다. 나머지는 추천과 실행 명령만 낸다. 저장할 가치가 없으면 버리고, 바꿀 것이 없으면 `no change`가 정상 결론이다.

하다 만 일과 열린 질문은 이 스킬이 쓰지 않는다. 보이면 receipt 끝에서 `/nara-handoff`를 권한다.

## 모드

| 입력 | 모드 |
|---|---|
| 인자 없음, "회고", "배운 것" | **session**: 이번 세션 |
| 특정 스킬의 오동작을 설명함, `--skill <name>` | **skill-incident**: 그 스킬 하나의 장애 진단 + redacted 개선안 |
| PR·리뷰 스레드 링크를 근거로 줌 | session 모드에 [리뷰 근거 규칙](#리뷰-근거-규칙)을 더한다 |

다른 세션의 기록은 사용자가 가리킨 것만 읽는다. 보이지 않는 로그를 읽은 것처럼 쓰지 않는다.

## 1. 수집

1. **세션**: 결정, 발견, 시행착오, 사용자 교정, 재시도, 도구 낭비. 사용자의 지적은 사건의 실마리이지 원인의 증명이 아니다.
2. **Git**: `git diff <base>...HEAD --stat`. 코드 변경을 나열하지 않고 사고 흐름을 복원하는 데만 쓴다.
3. **`docs/implementation-notes.md`**: 있으면 Design decisions, Deviations, Tradeoffs를 학습 후보로 읽는다. 구조적 Deviation은 ADR 후보로 이유와 함께 보존한다. `## Reconciliation Log`에서 해소된 항목은 건너뛴다. 파일은 지우지 않는다.
4. **이미 있는 장치**: 후보를 처분하기 전에 그 실수를 막을 수 있었던 테스트·린트·스크립트·규칙·스킬이 이미 있는지 본다. 규칙이 이미 분명했는데 어겼다면 규칙을 하나 더 쓰지 말고 왜 어겼는지를 찾는다.

## 2. 학습마다 증거 사슬

실행 가능한 학습은 이 순서로 적는다.

```
관찰(출처) → 영향 → 원인: 확인됨 | 가설 | 불명 → 최소 예방 → 소유 층 → 판정 검사 → 보존할 동작
```

- 원인을 모르면 지어내지 않는다. 결정적 증거가 이번 세션 안에서 닿으면 먼저 가져온다. 끝내 못 가르면 남은 가설 모두에서 통하는 예방을 내거나, 무엇이 판정할지 적는다.
- 기계로 잡을 수 있는 실수는 프롬프트 규칙보다 가장 싼 결정적 검사(테스트, 린트, 스크립트, CI)를 먼저 제안한다. 지켜 온 동작을 깰 수 있는 규칙 삭제는 제안하지 않는다.
- 효율 주장("더 빨랐을 것")은 비교 기준이나 예산이 같이 있을 때만 쓴다.

## 3. 처분

각 후보를 **정확히 하나의 소유자**로 보낸다. 근거를 못 대면 discard.

| 학습 모양 | 소유자 | 동작 |
|---|---|---|
| 오래 남길 사실: 결정(+이유)·주의사항·외부 제약 | **auto-memory** | 직접 write (preview) |
| 기계로 잡을 수 있는 반복 실수 | 테스트·린트·스크립트·CI | 추천 + 넣을 자리 |
| 이 repo 팀이 앞으로 지킬 규범 | repo 지침 파일(`CLAUDE.md`·`AGENTS.md` 중 repo가 쓰는 쪽) | 추천 (suggest-only) |
| 모든 repo에 적용할 개인 규범 | user 지침 파일(`CLAUDE.md`·rules, Codex는 `~/.codex/AGENTS.md`) | 추천 (suggest-only) |
| 아키텍처 결정 (대안 비교·구조 변경·외부 제약) | ADR | 추천 → `/nara-adr` |
| 반복되는 절차 | skill | 추천 → `skill-development`(신규) · `/nara-skill-forge`(개선) |
| lifecycle 자동화 ("매번 X 하면 Y") | hook | 추천 → `hook-development` |
| 기존 규칙·메모리와 겹치거나 충돌 | 기존 항목 | 추천 → `/nara-grooming` |
| 하다 만 일, 답 없이 남은 질문 | handoff | 추천 → `/nara-handoff` |
| 이미 충분함, 일회성, 근거 없음, 코드·문서에 이미 있음 | **no change / discard** | 사유 한 줄 |

추천 행에는 "설치됨", "적용됨", "반영 완료" 같은 말을 쓰지 않는다. 이 스킬은 그 표면들을 만들지 않는다. "추천", "suggest-only", "실행 명령"으로 쓴다.

skill 추천은 **절차형이면서 반복**일 때만 낸다. 두 lane에 걸치는 후보, 규범과 서술의 판별선, 실패 처리 표는 [routing-rules](references/routing-rules.md).

## 4. auto-memory 쓰기

파일 층은 런타임의 memory dir(Claude Code `projects/<slug>/memory/`)이다. 없으면(Codex 등) 도구 층에만 쓰고, 도구도 없으면 지침 파일 추천으로 돌린다: `store: none (<사유>)`.

- **dedup 먼저, 층마다 따로.** 파일 층은 memory dir과 `MEMORY.md`를 slug와 주제로 grep. 도구 층(memory MCP)은 명사 키워드 1~3개로 검색한다. 0건은 부재가 아니다. 더 짧은 키워드로 다시 찾고, 특정 레코드는 ID로 확인한다. 겹치면 새로 만들지 않고 기존 것을 고친다.
- **dual-store**: 파일 층에 쓴 학습은 memory 도구에도 독립 레코드로 남긴다. 고칠 때도 양쪽을 같이 고친다. 도구가 없으면 건너뛰고 receipt에 `store: file-only (<사유>)`.
- **evidence 필수**: 본문에 세션에서 실제로 관찰한 근거(파일, 커밋, 사용자 발언)를 적는다.
- **frontmatter**: memory 도구·디렉터리 컨벤션을 따른다. 최소 셋은 `name`, `description`, `metadata.type`, `metadata.verified_at`, `metadata.ref_paths`. `ref_paths`는 코드에 묶인 항목만 repo 상대 경로로, user·feedback은 `[]`.
- 🔴 **CHECKPOINT: write 전 preview.** create·update할 전문이나 diff를 먼저 보여 준다. 승인 대기는 아니다.
- write 뒤 메모리 건강 점수만 읽는다(고치지 않는다). `nara-grooming`의 `scripts/audit.sh`가 있으면 돌려 `total | flagged`를 receipt에 적고, flagged가 있으면 `/nara-grooming`을 권한다. 스크립트가 없으면 그 줄을 생략한다.

## skill-incident 모드

nara-kit 스킬 하나가 잘못 동작한 사건을 진단하고, 소비 프로젝트의 정보를 빼낸 일반화 개선안을 낸다.

1. 사건과 대조군을 고정한다: 관찰한 프롬프트와 기대·실제 결과, 원인을 가를 가장 가까운 정상 동작, 보존해야 할 동작.
2. 증상을 실패 평면(선택, 로딩, 지시 해석, 계획, 실행, 형식, 평가, 호스트 호환, 로컬 override, 효율)에 대응시킨다. 문구 결함부터 가정하지 않는다. 평면 표와 재현 방법은 [incident-method](references/incident-method.md).
3. 행동 장애는 새 컨텍스트에서 한 번 재현하고 대조군을 한 번 돌린다. 문서 모순은 해당 구절과 인접 구절 대비로 충분하다. 재현이 안 되면 `no change`.
4. 처분은 소유 스킬·문서의 정확한 수정 제안이다. 개인 메모리 쓰기나 현재 repo 한정 우회는 공용 스킬 장애의 해법이 아니다. 독립적으로 증명된 소비자 override가 원인이면 `local-only`.
5. **redaction**: 출력은 공개 nara-kit repo로 갈 수 있다. 고유명, 경로, URL, 티켓, 인명, 사용자 원문을 placeholder로 바꾸고 출력 전체에 pre-flight 스캔을 돌린다. 하나라도 남으면 `cannot_generalize_safely`로 중단한다. 출력 템플릿과 규약: [redaction-rules](references/redaction-rules.md).
6. 기본은 채팅으로만 낸다. `--out <path>`면 같은 redacted 내용을 그 경로에 쓰고 저장 후 다시 스캔한다. 실행은 nara-kit repo에서 `/nara-skill-forge <name>`이 맡는다.

## 리뷰 근거 규칙

PR 리뷰 스레드를 근거로 쓸 때만 적용한다.

- 리뷰 지적은 결함의 주장이지 확인된 결함이 아니다. 구현, 검증 증거, 토론 결론과 대조해 `확정 | 기각·주관 | 미해결`로 가른다. resolved나 merged 상태만으로는 둘 다 증명하지 않는다.
- 댓글 수, 리뷰어 수, 표현 수가 아니라 **독립 사건 수**로 센다. 한 PR에서 한 수정을 두고 오간 말은 한 건이다.
- 같은 원인 메커니즘과 같은 예방 경계를 가질 때만 묶는다. 증상이 비슷해도 원인이 다르면 따로 둔다. 영향이 큰 확정 오류 하나는 반복이 없어도 예방 대상이 된다.

## 5. Receipt

```
회고 완료 (recorded only | applied).
- 학습 <n>: memory <a> · 추천 <b> · no change <c> · discard <d>
- memory: <파일 경로> / 도구 레코드 <id> | store: file-only (<사유>) | 없음
- 추천: `/nara-adr` <한 줄> · 린트 규칙 <한 줄> ...
- memory health: total <N> | flagged <M>   (스크립트 없으면 생략)
- next: <남은 사람 할 일 전부> | 없음
```

처분 표(`학습 | 소유자 | 동작 | 근거`)를 receipt 위에 둔다. 모든 후보가 no change·discard면 "특이사항 없음" 한 줄로 끝낸다. 하다 만 일이 보였으면 `- handoff 후보: <한 줄> → /nara-handoff`를 더한다.

## 규칙

- **write는 auto-memory뿐.** skill·hook·ADR·CLAUDE.md·테스트는 추천만 한다.
- 근거 없는 학습은 저장하지 않는다. discard가 기본이다.
- `git log`로 보이는 코드 변경을 나열하지 않는다. 결정에는 이유를 붙인다.
- 확인된 사실, 가설, 제안, 적용한 변경을 섞지 않는다.
- 빈 표, 억지 finding 수, 자동 개선 목록을 만들지 않는다.
