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

**추천 lane 표현 계약** (suggest-only 행 — skill/hook/ADR/CLAUDE.md):
- 금지어: "설치됨", "활성화됨", "자동 적용됨", "settings 갱신됨", "반영 완료" — reflect는 이 surface들을 **생성·적용하지 않는다**
- 필수어: "추천", "suggest-only", "실행 명령만" — 사용자가 해당 스킬을 직접 실행해야 함을 명시

**skill 추천은 절차형 + 반복 둘 다**일 때만. 아니면 침묵 (매 세션 묻지 않는다).

타깃이 2개 lane에 걸치거나 skill 트리거 판정이 애매하면 → [references/routing-rules.md](references/routing-rules.md).

## 3. write 타깃 실행

### auto-memory

- **dedup 먼저 — 층마다 따로.** 겹치면 CREATE 대신 **기존 UPDATE** (`verified_at` 갱신). 근사 중복 금지.
  - *파일 층*: memory dir + `MEMORY.md`를 slug/topic으로 grep. (grep 불가 시 → 실패 처리 표)
  - *도구 층*: memory MCP 도구 검색은 **명사 키워드 1~3개**로. 문장형·패러프레이즈 쿼리 금지 — 부분 매칭으로 완만히 저하되지 않고 0건으로 떨어진다. **0건 ≠ 부재**: 더 짧은 키워드로 재시도, 특정 레코드 존재 확인은 ID 단위 조회로 확정. (여전히 0건 → 실패 처리 표)
- **dual-store** — 파일 층에 write한 학습은 memory MCP 도구에도 **독립 레코드**로 저장. 세션 요약 레코드에 담는 것으로 갈음 금지 (요약은 주제 단위 recall이 약하다). UPDATE도 양쪽 동시 — 한쪽만 고치면 divergence. 도구 미설치 환경이면 skip하고 receipt에 사유 명시.
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

### memory health (Tier 1 피기백, ~0 토큰)

write를 **끝낸 뒤** 파일 층 전체를 훑는다. reflect는 생산자, `/nara-memory-audit`은 청소부 — 여기선 **점수만 읽고 아무것도 고치지 않는다**.

```bash
MEM_DIR=~/.claude/projects/<slug>/memory
AUDIT=~/.claude/skills/nara-memory-audit/scripts/audit.sh   # Codex 등 설치 경로 다르면 그쪽
for f in "$MEM_DIR"/*.md; do [ "$(basename "$f")" = MEMORY.md ] || bash "$AUDIT" "$f"; done \
  | jq -s '{total: length, flagged: [.[] | select(.score >= 2) | {file, score, signals}]}'
```

- `$AUDIT` 없거나 `jq`/`git` 없으면 **skip** — receipt에서 그 줄 생략, 실패 아님 (의존 아님)
- `MEMORY.md` 포인터 수 ≠ memory 파일 수면 `index desync` 표시 (dedup grep에서 이미 본 데이터)
- `flagged > 0`이면 **추천만** → `/nara-memory-audit`. reflect가 Tier 2를 돌리거나 파일을 고치지 않는다

## 4. 출력 (receipt)

`## Session Reflect — {날짜}` 아래:

1. **라우팅 표** — `학습 | 타깃 | 동작(write/추천/discard) | 근거`
2. **write 산출물 — 층별로 분리** (한 줄에 뭉치지 않는다):
   - 파일 층: memory 파일 경로 + `MEMORY.md` 포인터, handoff 경로
   - 도구 층: 저장된 레코드 ID
   - 한쪽에만 있는 항목은 **`divergence`** 표시. 도구 미설치면 `store: file-only (<사유>)`
3. 추천 항목의 **실행 명령** (예: `/nara-adr`, `skill-development`)
4. Gap Status (이전→현재)
5. **memory health** — `total: N | flagged: M` (+ `index desync` 시 표기). `M>0`이면 `/nara-memory-audit` 추천. 스크립트 부재면 이 줄 생략

- 모든 후보가 discard/no-op → **"특이사항 없음"** 한 줄로 종료
- **게이트 구분**: 추천 lane(skill/hook/ADR/CLAUDE.md)은 인터랙티브 게이트 없음 (receipt에 명령만, 보고 실행/무시). write lane(memory/handoff)은 §3 🔴 CHECKPOINT의 preview 표시 의무 — 보여주는 것은 필수, 승인 대기는 아님(비차단).

> 외부 스킬 부재 시 fallback → 실패 처리 표. 의존 아님.
> nara-kit **스킬 자체**가 불편했다면 `/nara-meta-feedback` (별개 — reflect는 프로젝트 지식, meta-feedback은 툴킷 friction).

## 실패 처리

if-then 표 전체 → [references/routing-rules.md](references/routing-rules.md). 어떤 실패도 **단정 금지** — 모르면 `unknown` 표시 후 사용자 확인.

## 규칙

- **write는 memory·handoff만.** skill/hook/ADR/CLAUDE.md는 추천만 — 직접 수정 금지
- 근거 못 대는 학습 **저장 금지** — discard가 기본 sink
- `git log`로 볼 수 있는 코드 변경 나열 금지 / 결정은 **이유** 필수
- Conventions는 프로젝트 전반 적용 가능한 것만 / Warnings는 코드만 봐선 모르는 것만
- In Progress는 코드·커밋으로 복원 불가한 흐름만 / Open Questions는 답 없이 남은 것만
- In Progress·Open Q 있으면 다음 세션 `/nara-now`가 `docs/handoff.md` 우선 참조하도록 안내

**다음**: `/nara-pr` (또는 브랜치 정리). 구조 결정이 남았으면 `/nara-adr`.
