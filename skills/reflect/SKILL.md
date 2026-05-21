---
name: reflect
description: >-
  Capture session learnings — technical decisions, conventions, and warnings — and save to memory.
  USE FOR: "reflect", "세션 마무리", "오늘 배운 것", "결정 기록", "session end learnings".
  DO NOT USE FOR: code review, gap analysis, commit message generation.
---

# reflect — 세션 학습 캡처

세션에서 내린 결정, 발견한 컨벤션, 주의사항을 구조화하여 프로젝트 지식으로 저장한다.

## 수집 (병렬 실행)

1. **세션 히스토리**: 이번 대화에서 내린 기술 결정 회고
2. **Git diff**: `git diff main...HEAD --stat` 또는 최근 커밋 목록
3. **gap.md 변화**: gap.md 있으면 점수 변화 확인
4. **발견된 패턴**: 세션 중 발견한 코드 컨벤션이나 프로젝트 특이사항
5. **`docs/implementation-notes.md` 흡수**: 존재 시 5섹션 모두 읽기
   - 4섹션 (Design decisions / Deviations / Tradeoffs / Open questions) → 아래 분류로 매핑
   - 5섹션 (`## Reconciliation Log`) → resolved Note ID 추출 (`Resolution ∈ {Agreed Exception, Spec Revise Candidate}`)
   - resolved Note ID에 해당하는 4섹션 entry는 후속 처리에서 skip (중복 방지)

## 분류

- **Decisions**: 기술적/설계적 결정 + 이유 (← notes의 `Design decisions` + `Tradeoffs` 매핑)
- **Conventions**: 발견하거나 확립한 코드 컨벤션
- **Warnings**: 다음 세션 주의사항 (코드만 봐서 알 수 없는 것) (← notes의 `Deviations` 일부)
- **In Progress**: 미완료 작업의 현재 위치 + 다음에 이어서 할 일 (이번 세션에 끝나지 않은 것)
- **Open Questions**: 보류된 결정, 디버깅 가설, 검증 못 한 가정 (사용자/다음 세션에 답이 필요한 것) (← notes의 `Open questions` 그대로)

### implementation-notes 후속 액션

흡수 후 결정 (**Reconciliation Log에 resolved로 박힌 entry는 모두 skip**):
- `Deviations` 분류:
  - **Log에 `Agreed Exception`** → skip (gap.md Agreed Exceptions로 이미 영속화됨)
  - **구조적 변경** (새 패턴/모듈 도입, 디렉토리 배치 규약 변경 등) → Warnings + `/adr` 호출 권고
  - **정책 결정** (운영 표준에 맞춘 spec 누락 영역 보강) → Decisions (Why 보존). 후속 영향 (caller timeout 등)은 Warnings로 split
- `Open questions` 남은 채면 → `docs/handoff.md`에 박음 (다음 세션 `/now`가 surface)
  - **Log에 `Spec Revise Candidate`** → handoff 인계 skip (이미 `/spec-revision`으로 라우팅됨)
  - In Progress 없어도 (skip 제외 후) Open Questions 있으면 handoff.md 생성 (OR 조건)
- `Design decisions` / `Tradeoffs`는 Log 상태와 무관하게 평소대로 평가 (메모리 승격 vs ADR 후보는 독립 결정)
- 흡수 완료된 `docs/implementation-notes.md`는 **삭제 금지**, 그대로 보존 (PR 리뷰 참고용)

## 저장

1. **Auto-memory**: 다음 세션에도 유효한 Decisions/Warnings/Conventions → memory 저장
   - 새 메모리에는 반드시 `verified_at: <today>` + `ref_paths: [...]` (또는 `[]`) 박기 → `memory-audit` 호환
   - 기존 메모리 업데이트 시 `verified_at` 갱신
2. **docs/handoff.md**: In Progress + Open Questions 있으면 8섹션 정식 스키마로 덮어쓰기 (없으면 파일 삭제). 단기 인계 계약
3. **docs/learnings.md**: 팀 공유 필요 시, 파일 존재 시만 append
4. **gap.md**: Agreed Exceptions 변경 시 반영

## Memory Health Check

저장 끝나면 `memory-audit` 호출 (`--log` 모드 = `.audit-log.jsonl` append). score>=2 메모리만 surface.

```bash
PROJECT_SLUG=$(echo "$PWD" | sed 's|/|-|g')
MEM=~/.claude/projects/$PROJECT_SLUG/memory
for f in "$MEM"/*.md; do
  [[ "$(basename "$f")" == "MEMORY.md" ]] && continue
  bash skills/memory-audit/scripts/audit.sh --log "$f"
done | jq -s 'sort_by(-.score) | map(select(.score >= 2))'
```

**flag 결과 처리 (A1: flag 1회 → 즉시 archive 제안):**
- score>=2 메모리 발견 시 사용자에게 AskUserQuestion으로 4지선다 제시:
  1. `update` — 메모리 본문 수정 + `verified_at` 갱신
  2. `keep` — 무시 (다음 audit에서 또 surface됨)
  3. `archive` — `memory-archive` 스킬 호출 (move to `archive/` + MEMORY.md 정리)
  4. `skip` — 이번 세션 결정 보류

자동 archive/삭제 금지. **반드시 사용자 명시 승인**.

### docs/handoff.md 작성

9섹션 정식 스키마. Load [references/handoff-schema.md](references/handoff-schema.md) for full schema + writing rules.

## 출력

`## Session Reflect — {날짜}` 헤더 아래 Decisions, Conventions, Warnings, **In Progress, Open Questions**, Gap Status (이전→현재), Next Session 각 섹션 출력. 마지막에 **Memory Health** 섹션 — score>=2 메모리만 표 형태로 (없으면 생략).

## 규칙

- `git log`로 볼 수 있는 코드 변경 내역 나열 금지
- 결정의 **이유** 필수
- Conventions는 프로젝트 전반 적용 가능한 것만
- Warnings는 코드만 봐서 알 수 없는 것만
- **In Progress는 코드/커밋만 봐서 복원 불가능한 흐름만** — "X 파일 수정함"은 git이 보여줌. "X 함수 시그니처 A vs B 고민 중, A로 가다가 호환성 문제 발견" 같은 사고 흐름만
- **Open Questions는 답 없이 남은 것만** — 이미 결정된 건 Decisions로
- 모든 섹션 비면 "특이사항 없음" 출력 후 종료
- In Progress/Open Questions 있으면 다음 세션 `/now`가 `docs/handoff.md` 우선 참조하도록 안내
