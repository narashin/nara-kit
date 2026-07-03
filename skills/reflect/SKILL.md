---
name: reflect
description: >-
  Route session learnings to the right durable surface — write memory/handoff directly, recommend a skill/hook/ADR/CLAUDE.md rule, or discard.
  USE FOR: "reflect", "세션 마무리", "오늘 배운 것", "결정 기록", "이거 어디 저장", "스킬로 만들까", "session end learnings".
  DO NOT USE FOR: code review, gap analysis, commit message generation.
---

# reflect — 세션 학습 라우터

세션에서 나온 학습을 분류해 **알맞은 durable surface로 라우팅**한다. memory·handoff는 직접 쓰고(preview), skill·hook·ADR·CLAUDE.md는 **추천 + 실행 명령만** 낸다 (실제 생성은 기존 스킬 담당). 저장 가치 없으면 discard.

> 트랜잭션·롤백 없음 — memory·handoff는 저위험·단일소유·되돌리기 쉬운(`memory-archive`) 파일. 안전장치 = preview + git. (고위험 공유 파일용 sha256/apply-plan은 nara 범위 밖)

## 1. 수집 (병렬)

1. **세션 히스토리**: 이번 대화의 결정·발견·시행착오 회고
2. **Git diff**: `git diff main...HEAD --stat` — 코드 변경 나열 X, 사고 흐름만
3. **gap.md 변화**: 있으면 점수 변화 확인
4. **`docs/implementation-notes.md` 흡수**: 존재 시 전 섹션 읽기
   - 4섹션 (Design decisions / Deviations / Tradeoffs / Open questions) → 학습 후보로 (구조적 Deviation은 ADR 타깃 + Why 보존, Open questions는 handoff)
   - `## Reconciliation Log`의 resolved entry (`Agreed Exception` / `Spec Revise Candidate`) → skip (중복 방지)
   - 흡수 후에도 파일 **삭제 금지** (PR 리뷰 참고용)

## 2. 분류 → 라우팅

각 학습 후보를 **정확히 하나의 타깃**으로 라우팅. 근거 못 대는 후보는 discard.

| 학습 모양 | 타깃 | reflect 동작 |
|---|---|---|
| 영속 지식 — 결정(+이유)·컨벤션·주의사항 | **auto-memory** | 직접 write (preview) |
| 미완 흐름 **또는** 미해결 질문 (In Progress 또는 Open Q — 하나라도) | **handoff.md** | 직접 write (preview) |
| 아키텍처 결정 (대안 비교·구조 변경·외부 제약) | **ADR** | 추천 → `/nara-kit:adr` |
| 반복 절차/루틴 (§skill 트리거) | **skill** | 추천 → `skill-development`(신규) · `/nara-kit:skill-forge`(개선) |
| lifecycle 자동화 ("매번 X 하면 Y") | **hook** | 추천 → `hook-development` |
| 이 repo 팀 durable rule | repo `CLAUDE.md` | 추천 (suggest-only, 직접 수정 X) |
| 모든 repo 개인 가이드 | user `CLAUDE.md` | 추천 (suggest-only) |
| 일회성·branch 한정·근거 없음·이미 코드/문서에 있음 | **discard** | 버림 + 사유 |

**write = memory·handoff 둘뿐.** 나머지는 추천 + 명령만 낸다 (surface 생성은 그 스킬이).

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

- **dedup 먼저** — 새로 만들기 전 memory dir + `MEMORY.md`를 slug/topic으로 grep. 겹치면 CREATE 대신 **기존 파일 UPDATE** (`verified_at` 갱신). 근사 중복 파일 금지.
  - memory dir / 타 repo `CLAUDE.md`를 **실제로 grep 못 하면** new-vs-UPDATE 단정 금지 — `duplicate_status: unknown`으로 표시하고 CREATE/UPDATE 결정을 사용자 확인으로 넘긴다.
- **evidence 필수** — 본문에 세션에서 실제 관찰한 근거(파일·커밋·사용자 발언) 명시. 못 대면 저장 X → discard.
- **canonical frontmatter (단일 스키마)** — `verified_at`/`ref_paths`는 `metadata:` 블록 **안**. user 글로벌 CLAUDE.md 스키마 + `memory-audit` 파서와 정확히 일치:

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
- write 전 **preview** — 무엇을 create/update 하는지 보여주고 진행.

### handoff.md

- In Progress **또는** Open Questions 중 **하나라도** 있으면 9섹션 스키마로 덮어쓰기 (OR 조건 — **둘 다 없을 때만** 파일 삭제). 단기 인계 계약.
- 9섹션 스키마: [references/handoff-schema.md](references/handoff-schema.md).

### gap.md (조건부)

- gap.md 존재 + Agreed Exceptions 변경 시에만 반영. 없으면 skip.

## 4. Memory Health Check

write 끝나면 `memory-audit` 호출 (`--log` = `.audit-log.jsonl` append). score>=2만 surface.

```bash
PROJECT_SLUG=$(echo "$PWD" | sed 's|/|-|g')
MEM=~/.claude/projects/$PROJECT_SLUG/memory
for f in "$MEM"/*.md; do
  [[ "$(basename "$f")" == "MEMORY.md" ]] && continue
  bash "${CLAUDE_PLUGIN_ROOT:-.}/skills/memory-audit/scripts/audit.sh" --log "$f"
done | jq -s 'sort_by(-.score) | map(select(.score >= 2))'
```

score>=2 발견 시 AskUserQuestion 4지선다: `update` / `keep` / `archive`(→ `memory-archive`) / `skip`. **자동 archive·삭제 금지 — 사용자 명시 승인.**

## 5. 출력 (receipt)

`## Session Reflect — {날짜}` 아래:

1. **라우팅 표** — `학습 | 타깃 | 동작(write/추천/discard) | 근거`
2. write된 memory/handoff 경로
3. 추천 항목의 **실행 명령** (예: `/nara-kit:adr`, `skill-development`)
4. Gap Status (이전→현재)
5. **Memory Health** — score>=2만 (없으면 생략)

- 모든 후보가 discard/no-op → **"특이사항 없음"** 한 줄로 종료
- 추천은 receipt 줄일 뿐 — **인터랙티브 게이트 없음** (보고 실행/무시)

> 외부 스킬(`skill-development`·`hook-development`) 없으면 수동 fallback 안내 (CLAUDE.md "When Adding a New Skill" 등). 의존 아님.
> nara-kit **스킬 자체**가 불편했다면 `/meta-feedback` (별개 — reflect는 프로젝트 지식, meta-feedback은 툴킷 friction).

## 규칙

- **write는 memory·handoff만.** skill/hook/ADR/CLAUDE.md는 추천만 — 직접 수정 금지
- 근거 못 대는 학습 **저장 금지** — discard가 기본 sink
- 같은 주제 메모리 새로 만들지 말고 **기존 UPDATE**
- skill 추천은 **절차형 + 반복 둘 다**일 때만 (per-session 프롬프트 금지)
- `git log`로 볼 수 있는 코드 변경 나열 금지 / 결정은 **이유** 필수
- Conventions는 프로젝트 전반 적용 가능한 것만 / Warnings는 코드만 봐선 모르는 것만
- In Progress는 코드·커밋으로 복원 불가한 흐름만 / Open Questions는 답 없이 남은 것만
- In Progress·Open Q 있으면 다음 세션 `/now`가 `docs/handoff.md` 우선 참조하도록 안내
