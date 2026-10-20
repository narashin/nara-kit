---
name: nara-grooming
description: >-
  Audit persistent instructions — auto-memory, CLAUDE.md/AGENTS.md and rules files, installed or repo skills — for duplication, conflict, staleness, and stale overrides that explain a behavior the user just corrected. Report first; fix, archive or move only on per-tier approval, with a durable backup before touching files outside git.
  USE FOR: "grooming", "메모리 감사", "메모리 점검", "stale memory", "규칙 정리", "CLAUDE.md 중복", "규칙끼리 충돌", "왜 옛날 규칙대로 했지", "스킬 지침 낡았나", memory-audit, after a breaking rename / skill add-remove / migration.
  DO NOT USE FOR: 새 메모리 쓰기 (→ nara-retro), 세션 회고·재발 방지 (→ nara-retro), 스킬 개선 실행 (→ nara-skill-forge), 영구 삭제 (수동 rm), 일반 코드 정리.
---

# grooming: 오래 남는 지침을 감사한다

> 출력 형식은 [nara-kit 출력 계약](../nara-now/references/output-contract.md)을 따른다. 이 본문이 다르게 정한 곳은 본문이 우선한다. 파일이 없으면(단독 설치) 이 줄은 건너뛴다.

매 세션 실리거나 recall되는 지침이 서로 겹치거나, 충돌하거나, 현재 소유자보다 낡았는지 본다. 기본은 보고만 한다. 고치는 일은 위치 등급별 승인을 받은 뒤에만, 옮기지 지우지 않는다. 이 스킬은 의심 후보를 만드는 쪽이지 심사자가 아니다.

## 영역

요청이 가리키거나 사건이 연루한 영역만 본다. 기본값은 memory다.

| 영역 | 대상 | 절차 |
|---|---|---|
| **memory** | `<agent-config>/projects/<slug>/memory/*.md` (`MEMORY.md`, `archive/` 제외) + memory MCP 레코드. 파일 memory dir이 없는 런타임(Codex 등)은 MCP 레코드만 보고 파일 층은 `skipped (no memory dir)` | 아래 [memory 절차](#memory-절차) |
| **rules** | user·repo `CLAUDE.md`, `AGENTS.md`, `rules/*.md`, `@import`로 끌려오는 파일 | [context-audit](references/context-audit.md) |
| **skills** | repo `skills/`·`.claude/skills/`, 설치본 `~/.claude/skills`·`~/.codex/skills` | [context-audit](references/context-audit.md) |

경로는 지금 호스트에서 실제로 확인된 것만 쓴다. 다른 호스트의 경로 관례를 가져다 붙이지 않는다. 심링크는 실제 대상까지 풀고 링크 경로와 실제 경로를 둘 다 기록한다.

## 사용자 교정이 계기일 때

"왜 옛날 규칙대로 했지"처럼 사용자가 방금 동작을 바로잡았다면 이 사슬을 먼저 세운다.

```
교정된 동작 → 그 동작을 요구한 지속 지침(경로:줄) → 현재 소유자의 지침(경로:줄) → 충돌
```

사슬이 서야만 `stale override`로 분류한다. 파일이 있다는 것, 오래됐다는 것, 로드 순서는 증거가 아니다. 어떤 지속 지침에도 연결되지 않으면 지침을 그대로 두고 `/nara-retro`를 권한다. 현재 스킬 자체가 결함이면 그 스킬의 수정은 `/nara-retro` skill-incident 모드와 `/nara-skill-forge`의 몫이다.

## 분류

| 판정 | 뜻 |
|---|---|
| `duplicate` | 같은 뜻이 두 곳 이상에 있다 |
| `conflict` | 둘 다 현행인데 서로 다르게 요구한다 |
| `stale override` | 낡은 지침이 현재 소유자와 충돌하고, 관찰된 동작을 설명한다 |
| `stale` | 가리키는 경로·스킬·사실이 더는 없다 |
| `keep` / `keep (vendor)` | 결과를 바꾸는 문제가 증명되지 않았다 / 외부 설치본이다 |

처분 동작은 `keep | tighten | merge | split | move | archive | fix`다. `tighten`은 소유·범위·뜻을 바꾸지 않고 중복이나 모호함만 걷어 낼 때만 쓴다. 뜻이 바뀌는 `merge`·`split`·의미 재작성은 정확한 제안으로만 남긴다. 길지만 살아 있는 지침은 `keep`이다.

## 위치 등급과 승인

수정 대상마다 실제 경로를 풀고 등급을 매긴다.

| 등급 | 기준 | 판정 명령 |
|---|---|---|
| **T1** | 어느 git 저장소 밖 (memory dir 등) | `git -C <dir> rev-parse --show-toplevel` 실패 |
| **T2** | 저장소 안, 추적 안 됨 | `git ls-files --error-unmatch -- <rel>` exit 1. `git check-ignore -v`로 ignored 여부도 기록 |
| **T3** | 저장소 안, 추적됨 (dotfiles·nara-kit 소스 포함) | 같은 명령 exit 0 |

git 명령의 다른 오류, 깨진 링크, 없는 경로는 T1·T2가 아니라 증거 공백이다.

🔴 **CHECKPOINT**: 처분 표 전체를 한 번 보여 준 뒤, 비어 있지 않은 다음 등급 하나(T1 → T2 → T3)만 승인을 받는다. 앞 등급을 고치면 뒤 등급의 근거가 바뀔 수 있어 묶어서 묻지 않는다. T3는 기본이 정확한 패치 제안이다. 사용자가 그 변경을 요청했을 때만 고친다.

- **설치본은 소스에서 고친다.** `npx skills`나 플러그인으로 깔린 스킬은 `keep (vendor)`다. 그 소스 저장소가 사용자 것(예: nara-kit)이면 소스 경로를 T3 대상으로 제안한다.
- **T1·T2를 고치기 전 백업**: 실제 대상을 세션 임시 폴더가 아니고 자동 로드되지 않는 영속 위치에 복사한다(예: `~/.local/state/nara-grooming/<run-id>/`). 바이트 동일을 확인하고 절대 경로를 receipt에 적는다. 확인 못 하면 그 대상은 고치지 않는다.
- 규칙·memory의 삭제나 의미 재작성은 항목별 승인이 필요하다. memory는 지우지 않고 `memory/archive/`로 옮기고 `MEMORY.md` 줄을 뺀다.
- 고친 뒤에는 링크, 중복, frontmatter, 인덱스 동기(포인터 수 == 파일 수)를 다시 확인한다. 교정 계기였다면 원래 시나리오를 다시 돌려 낡은 동작이 사라졌는지 본다. 글자를 지운 것만으로는 증명이 아니다.

## memory 절차

memory 영역의 기계 검사와 의미 검증이다. 전체 알고리즘과 Tier 2 프롬프트: [scoring.md](references/scoring.md).

1. **Tier 1** (bash, 토큰 거의 0): 대상마다 `scripts/audit.sh`를 돌려 0~4점. 신호는 `age_days>=90`, `ref_validity<100%`, `code_drift>0`, `skill_ref_broken`. `0` 정상, `1` 관찰, **`2+` flagged**.
2. **Tier 2** (flagged만): 5~8개씩 묶어 병렬 서브에이전트로 파일마다 `FRESH | STALE | CONTRADICTION | UNVERIFIABLE` + 근거 + 최소 수정. 앵커 없는 원칙은 FRESH.
3. 처분 표에 합친다. 여기까지 아무것도 고치지 않는다.
4. 승인 뒤: 앵커 수정은 `Edit`(덧대지 말고 줄인다), 위험·반박된 것은 `memory/archive/`로 옮기고 `MEMORY.md` 줄을 뺀다.
5. **거울 제거**: `nara-retro`는 파일과 MCP 레코드에 이중 저장한다. 파일만 archive하면 살아 있는 쌍둥이가 계속 recall된다. 같은 승인 묶음에서 MCP 쪽도 supersede하거나 지운다. 도구가 없으면 건너뛰고 그렇게 적는다.

실행 위치는 그 memory가 다루는 저장소다(`CLAUDE_PROJECT_DIR`로 바꿀 수 있다). Tier 1은 macOS 전용(`stat -f`, `date -j`)이고 `jq`·`git`이 필요하다.

## 출력

`## Disposition` 표 하나를 먼저 낸다. ID는 처음 찾은 순서로 한 번만 매긴다.

| ID | 항목 | 등급 | 판정·동작 | 대상(실제 경로) | 근거 |
|---|---|---|---|---|---|

찾은 게 없으면 `— | 없음 | — | keep | — | no finding` 한 행. 증거 공백·소유 충돌·검증 실패가 있을 때만 `## Exceptions`, 고쳤을 때만 `## Applied`와 `## Verification`을 붙인다. 이어서 receipt:

```
status: audited | applied | partial
scope: memory <N> · rules <N> · skills <N>
flagged: duplicate <a> · conflict <b> · stale override <c> · stale <d>
applied: <n> fixed, <n> archived, <n> moved | none
backup: <absolute path> (byte-equal) | 해당 없음
mirror: <n> MCP records updated/superseded | skipped (<사유>)
next: <다음 등급 승인 질문 | 남은 사람 할 일 | 없음>
```

## 규칙

- **승인 전 변경 없음.** Tier 1·Tier 2와 rules·skills 대조는 읽기만 한다.
- **옮기지 지우지 않는다.** `rm`은 사용자가 직접 한다.
- 외부 시스템에 대한 주장은 `UNVERIFIABLE`. 추측하지 않는다.
- **전수 조사라고 주장하지 않는다.** Tier 1은 MCP 저장소를 못 읽는다. 백틱 안의 맨 스킬 이름은 Tier 2에서만 잡힌다. 툴킷 저장소 밖에서는 이름이 바뀌었지만 설치돼 있는 스킬을 `unknown`으로만 판정한다.
- **확인 못 한 것과 깨진 것은 다르다. 다만 어디에도 없는 것은 깨진 것이다.** `skill_ref_unknown`(0점)은 "스킬은 있는데 이 저장소에서 경로를 확인 못 함"일 뿐이다.
- **신호를 끄려고 진짜 앵커를 지우지 않는다.** 있는 파일에서 `ref_validity`가 실패하면 읽는 쪽이 틀린 것이다.
- 사용자가 이 대화나 지속 규칙에서 제외한 대상은 다시 묻지 않고 계속 제외한다. 제외 목록을 숨은 전역 상태로 저장하지 않는다.

## 문제 해결

- `❌ 실패: memory dir 없음 — <path>` → `<agent-config>/projects/<slug>/memory/` 확인. 런타임에 그런 디렉터리 규약 자체가 없으면(Codex) 실패가 아니라 위 `skipped`다.
- skill 참조가 `unknown`인데 판정이 필요하면 `CLAUDE_PROJECT_DIR`을 툴킷 저장소로 지정한다. `NARA_SKILLS_DIRS`는 루트 탐색 목록만 바꾼다.
- 실패 경로별 대응(소유 불명, 대상 표류, 백업 실패, 검증 실패): [context-audit](references/context-audit.md#실패-경로).
