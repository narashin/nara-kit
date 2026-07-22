---
name: nara-reflect
description: >-
  Route session learnings to the right durable surface — write memory/handoff directly, recommend a skill/hook/ADR/CLAUDE.md rule, or discard.
  USE FOR: "reflect", "세션 마무리", "오늘 배운 것", "결정 기록", "이거 어디 저장", "스킬로 만들까", "session end learnings".
  DO NOT USE FOR: code review, gap analysis, commit message generation.
---

# reflect — 세션 학습 라우터

세션에서 나온 학습을 분류해 **알맞은 durable surface로 라우팅**한다. memory·handoff는 직접 쓰고(preview), skill·hook·ADR·CLAUDE.md는 **추천 + 실행 명령만** 낸다 (실제 생성은 기존 스킬 담당). 저장 가치 없으면 discard.

> 트랜잭션·롤백 없음 — memory·handoff는 저위험·단일소유·되돌리기 쉬운 파일. 안전장치 = preview + git. (고위험 공유 파일용 sha256/apply-plan은 nara 범위 밖)

## 1. 수집 (병렬)

1. **세션 히스토리**: 이번 대화의 결정·발견·시행착오 회고
2. **Git diff**: `git diff main...HEAD --stat` — 코드 변경 나열 X, 사고 흐름만
3. **gap.md 변화**: 있으면 점수 변화 확인
4. **`docs/implementation-notes.md` 흡수**: 존재 시 전 섹션 읽기
   - 4섹션 (Design decisions / Deviations / Tradeoffs / Open questions) → 학습 후보로 (구조적 Deviation은 ADR 타깃 + Why 보존, Open questions는 handoff)
   - `## Reconciliation Log`의 resolved entry (`Agreed Exception` / `Spec Revise Candidate`) → skip (중복 방지)
   - 흡수 후에도 파일 **삭제 금지** (PR 리뷰 참고용)
5. **기존 `docs/handoff.md` 읽기** (존재 시): 이전 세션의 미해소 In Progress·Open Q를 **carry-forward 후보**로 확보. 이번 세션이 실제로 해소한 항목만 제거 대상 — 안 건드린 항목은 보존해야 함 (§3 merge 입력).

## 2. 분류 → 라우팅

각 학습 후보를 **정확히 하나의 타깃**으로 라우팅. 근거 못 대는 후보는 discard.

| 학습 모양 | 타깃 | reflect 동작 |
|---|---|---|
| 영속 지식 — 결정(+이유)·컨벤션·주의사항 | **auto-memory** | 직접 write (preview) |
| 미완 흐름 **또는** 미해결 질문 (In Progress 또는 Open Q — 하나라도) | **handoff.md** | 직접 write (preview) |
| 아키텍처 결정 (대안 비교·구조 변경·외부 제약) | **ADR** | 추천 → `/nara-adr` |
| 반복 절차/루틴 (§skill 트리거) | **skill** | 추천 → `skill-development`(신규) · `/nara-skill-forge`(개선) |
| lifecycle 자동화 ("매번 X 하면 Y") | **hook** | 추천 → `hook-development` |
| 이 repo 팀 durable rule | repo `CLAUDE.md` | 추천 (suggest-only, 직접 수정 X) |
| 모든 repo 개인 가이드 | user `CLAUDE.md` | 추천 (suggest-only) |
| 일회성·branch 한정·근거 없음·이미 코드/문서에 있음 | **discard** | 버림 + 사유 |

**write = memory·handoff 둘뿐.** 나머지는 추천 + 명령만 낸다 (surface 생성은 그 스킬이).

**타깃 충돌 tiebreaker** (한 학습이 2개 lane에 걸칠 때):
- **미래 세션/팀 동작을 지속적으로 규율하려는 rule·가이드라인** (강제 가능하든 — "gap<80이면 PR 차단" — 권고든 — "PR 본문은 한국어") → **CLAUDE.md suggest-only 우선** (repo=팀, user=개인). CLAUDE.md는 매 세션 context에 로드되고 repo는 git으로 공유됨 — recall-on-search인 memory보다 rule 전파에 맞음. 그 rule이 *왜* 생겼는지가 코드·rule 텍스트만으로 복원 불가할 때만 memory에도 이유 별도 write (2개 타깃 허용 예외).
  - **판별선**: 규범(prescriptive — "앞으로 X 해라") → CLAUDE.md. 서술(descriptive — "이 코드/시스템은 이렇게 동작한다"는 사실·주의사항) → auto-memory. 둘 다면 위 예외로 양쪽.
- 그 외 모든 충돌 (일회성 결정·발견 등) → 표의 **위쪽 행 우선** (auto-memory > handoff > ADR > skill > hook).

**추천 lane 표현 계약** (suggest-only 행 — skill/hook/ADR/CLAUDE.md):
- 금지어: "설치됨", "활성화됨", "자동 적용됨", "settings 갱신됨", "반영 완료" — reflect는 이 surface들을 **생성·적용하지 않는다**
- 필수어: "추천", "suggest-only", "실행 명령만" — 사용자가 해당 스킬을 직접 실행해야 함을 명시

### skill 추천 트리거 (고정밀 — 노이즈 방지)

매 세션 묻지 않는다. **아래 둘 다** 만족할 때만 skill 후보로 표면화:

1. **절차형** — 재실행 가능한 multi-step 루틴 (결정→ADR, 사실→memory, **절차→skill**)
2. **반복** — 이번 세션 2회+ 수동 반복 OR 관련 memory 이미 존재(재발)

아니면 침묵. (드물게·믿을 만하게 > 매번·무시됨. 무차별 추천은 안 눌린다.)

## 3. write 타깃 실행

### auto-memory

- **dedup 먼저** — 새로 만들기 전 memory dir + `MEMORY.md`를 slug/topic으로 grep. 겹치면 CREATE 대신 **기존 파일 UPDATE** (`verified_at` 갱신). 근사 중복 파일 금지. (grep 불가 시 → 실패 처리 표)
- **evidence 필수** — 본문에 세션에서 실제 관찰한 근거(파일·커밋·사용자 발언) 명시. 못 대면 저장 X → discard.
- **frontmatter** — memory 도구/디렉토리 컨벤션을 따른다. `verified_at`/`ref_paths`는 `metadata:` 블록 **안**. memory 도구가 별도 필드(예: `node_type`)를 붙이면 그 도구 스키마를 우선 — 아래는 최소 셋:

  ```yaml
  ---
  name: <short-kebab-case-slug>
  description: <one-line summary>
  metadata:
    type: user | feedback | project | reference
    verified_at: <YYYY-MM-DD>
    ref_paths: [<repo-relative path>, ...]   # 또는 []
  ---
  ```

- **ref_paths type-aware** — code-anchored(convention/reference)만 실제 repo-relative 경로. user/feedback은 `[]`. 절대경로(`/Users/...`)·worktree 경로·지어낸 경로 금지.
- 🔴 **CHECKPOINT — write 전 preview 필수**: memory/handoff에 실제 쓰기 직전, 무엇을 create/update 하는지 diff/전문으로 **먼저 보여준다**. preview 없이 write 금지 (silent memory 오염 방지). 비차단 — 보여준 뒤 바로 진행.

### handoff.md

- In Progress **또는** Open Questions 중 **하나라도** 있으면 9섹션 스키마로 write. 단기 인계 계약.
- **merge, 통째 덮어쓰기 금지** — §1에서 읽은 기존 handoff의 미해소 항목을 **carry-forward**하고, 이번 세션이 검증-해소한 항목만 제거한 뒤, 이번 세션 신규 항목을 합쳐 9섹션으로 재작성. (무관한 다음 세션이 이전 미완 작업을 지우는 교차세션 손실 방지)
- **삭제 조건**: carry-forward 후에도 In Progress·Open Q가 **둘 다 비었을 때만** 파일 삭제.
- 9섹션 스키마: [references/handoff-schema.md](references/handoff-schema.md).

### gap.md (조건부)

- gap.md 존재 + Agreed Exceptions 변경 시에만 반영. 없으면 skip.

## 4. 출력 (receipt)

`## Session Reflect — {날짜}` 아래:

1. **라우팅 표** — `학습 | 타깃 | 동작(write/추천/discard) | 근거`
2. write된 memory/handoff 경로
3. 추천 항목의 **실행 명령** (예: `/nara-adr`, `skill-development`)
4. Gap Status (이전→현재)

- 모든 후보가 discard/no-op → **"특이사항 없음"** 한 줄로 종료
- **게이트 구분**: 추천 lane(skill/hook/ADR/CLAUDE.md)은 인터랙티브 게이트 없음 (receipt에 명령만, 보고 실행/무시). write lane(memory/handoff)은 §3 🔴 CHECKPOINT의 preview 표시 의무 — 보여주는 것은 필수, 승인 대기는 아님(비차단).

> 외부 스킬 부재 시 fallback → 실패 처리 표. 의존 아님.
> nara-kit **스킬 자체**가 불편했다면 `/nara-meta-feedback` (별개 — reflect는 프로젝트 지식, meta-feedback은 툴킷 friction).

## 실패 처리 (if-then)

| 트리거 조건 | 일차 대응 | 여전히 실패 시 |
|---|---|---|
| memory dir / 타 repo `CLAUDE.md` grep 불가 | `duplicate_status: unknown` 표시 | CREATE/UPDATE 결정을 사용자 확인으로 위임 (단정 금지) |
| 학습에 세션 근거(파일·커밋·발언) 못 댐 | 해당 후보 discard | 사유를 라우팅 표 `근거` 열에 명시 |
| 외부 스킬(`skill-development`·`hook-development`) 부재 | 수동 fallback 안내 (CLAUDE.md "When Adding a New Skill") | 추천 lane 유지 — reflect가 대신 생성하지 않음 |
| carry-forward 후에도 In Progress·Open Q 둘 다 없음 | handoff.md 삭제 | 삭제 실패(파일 lock 등) 시 stale 경고만, 강제 삭제 금지 |
| implementation-notes.md resolved entry와 중복 | 해당 entry skip | 애매하면 후보로 올리되 근거에 "중복 의심" 표기 |

## 규칙

- **write는 memory·handoff만.** skill/hook/ADR/CLAUDE.md는 추천만 — 직접 수정 금지
- 근거 못 대는 학습 **저장 금지** — discard가 기본 sink
- 같은 주제 메모리 새로 만들지 말고 **기존 UPDATE**
- skill 추천은 **절차형 + 반복 둘 다**일 때만 (per-session 프롬프트 금지)
- `git log`로 볼 수 있는 코드 변경 나열 금지 / 결정은 **이유** 필수
- Conventions는 프로젝트 전반 적용 가능한 것만 / Warnings는 코드만 봐선 모르는 것만
- In Progress는 코드·커밋으로 복원 불가한 흐름만 / Open Questions는 답 없이 남은 것만
- In Progress·Open Q 있으면 다음 세션 `/nara-now`가 `docs/handoff.md` 우선 참조하도록 안내
