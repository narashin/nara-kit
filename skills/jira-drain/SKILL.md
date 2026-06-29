---
name: jira-drain
description: >-
  Launch a chosen jira-triage queue ticket into an aoe session (right group + worktree) and drive dev-mode/doc-mode to a PR — interactive ($0), human-triggered.
  USE FOR: "jira-drain", "큐 티켓 착수", "이 티켓 돌려", "/nara-kit:jira-drain KEY".
  DO NOT USE FOR: 큐 생성·분류 (→ jira-triage), PR 리뷰 (→ review-queue), 큐 없이 직접 (→ /nara-kit:wt + dev-mode).
---

# jira-drain — 큐 티켓 → aoe 세션 착수

사람이 고른 Multica 큐 티켓 1건을 받아, metadata 라우팅대로 aoe 세션을 띄우고 워크플로를 PR까지 자율 실행한다. **인터랙티브 구독 = $0.**

## 인자

```
jira-drain <KEY|issue_id> [--dry-run]
```

## Step 0 — Pre-flight

`multica`, `aoe` PATH 확인. 없으면 `❌ 실패: <cmd> not found (PATH 확인)` 후 중단.

## 파이프라인

1. **resolve** — KEY/issue_id로 Multica 이슈를 찾고(`multica issue list --output json` → `jira_key` metadata 매칭 또는 직접 `multica issue get <id>`) metadata 읽음: `jira_key · triage_type · repo · session_group · pr_language · sub_repo`. `local_path`는 **로컬 config(`~/.claude/jira-triage.md`)** 에서 조회:
   - KEY 접두로 jira_project 도출 (`LYRIS-425` → `LYRIS`)
   - `profiles[].jira_project == jira_project` 인 profile 선택
   - `sub_repo` 값(`default|fe|be`)으로 `profile.repos.<sub_repo>.local_path` 읽음
   - `<summary>` 추출: 이슈 title에서 `[<KEY>] <타입>: ` 접두 제거 (`[LYRIS-425] 구현: 편집 기능` → `편집 기능`). jira-triage가 세팅한 title 형식에 의존. `summary` metadata 키는 없음 — title에서만 파싱.
   - `jira_key` 매칭이 여러 건이면 가장 최근 `created_at` 1건 선택, 나머지는 → `ESCALATE: <KEY> 중복 큐 이슈 N건`

2. **guard** — 다음 조건 중 하나라도 해당하면 중단:
   - Multica 이슈 없음 → `❌ 실패: <KEY> 큐 이슈 없음 (jira-triage 먼저)`
   - config에 jira_project profile 없음 → `❌ 실패: <KEY> project 매핑 없음 (~/.claude/jira-triage.md 보완)`
   - `local_path` 비어 있음 → `❌ 실패: <repo> local_path 미설정 (~/.claude/jira-triage.md 보완)`
   - `triage_type == 기타` → `수동 처리 — drain 안 함` 중단

3. **launch** — 브랜치명 `<prefix>/<KEY>-<slug>` (버그픽스→`fix/`, 구현→`feature/`, 기획→`docs/`; slug=summary kebab, 영숫자/하이픈, 소문자, ~50자; 비ASCII(한글 등)는 생략 — slug 비면 브랜치 = `<prefix>/<KEY>` trailing 하이픈 제거):
   - 먼저 존재 확인: `aoe session show "[<KEY>] <summary>"` 성공 → `aoe add` 생략하고 drive로 (send가 auto-revive). 실패(미존재) → `aoe add` 실행:
   ```bash
   aoe add "<local_path>" -t "[<KEY>] <summary>" -g "<session_group>" \
     -w "<prefix>/<KEY>-<slug>" -b -c claude -l -y
   ```
   `base = repo 기본 브랜치 (--base-branch 기본값). 진행 중 PR 위 스택 필요 시 --base-branch <branch> 추가.`

4. **drive** — triage_type에 따라 프롬프트 주입 (§gate-as-stop):
   ```bash
   aoe send "[<KEY>] <summary>" "<프롬프트>"
   ```
   identifier = launch에서 쓴 전체 title과 동일해야 함 (부분문자열 매칭 안 됨); 출력에 session id가 있으면 그 id를 써도 됨.

5. **mark** — 이슈 metadata + 상태 전환:
   ```bash
   multica issue metadata set <id> --key drain_state --value working
   multica issue status <id> in_progress
   ```

6. **receipt** — 출력 계약 4요소 (실행한 aoe 커맨드 · 세션 · side effects · next).

## gate-as-stop 프롬프트 (§drive aoe send 본문)

### 구현 / 버그픽스 (dev-mode)

```
<KEY> 처리. /nara-kit:prep <KEY> 후 dev-mode를 PR 생성까지 자율 진행.
규칙: (1) 각 게이트(gap<80, AC 미비, code-review 미해결 결함, 테스트 실패)에서 사람 기다리지 말고 멈춰 — 사유를 한국어로 요약 출력하고 PR 만들지 마. (2) 모든 게이트 통과 시에만 PR 생성, 머지는 하지 마. (3) PR 본문 언어=<pr_language>, 템플릿: 요약/변경/검증/Jira. (4) 완료 시 PR URL 또는 정지 사유를 마지막 줄에 PR_RESULT: <url|STOPPED: 사유> 로 출력.
```

### 기획 (doc-mode)

```
<KEY> 처리. /nara-kit:prep <KEY> 후 doc-mode로 spec 초안까지 자율 진행.
규칙: (1) clarity/Readiness 게이트 미달 시 사람 기다리지 말고 멈춰 — 사유를 한국어로 요약 출력. (2) spec 초안까지만, publish/Confluence 게시는 하지 마. (3) spec 본문 언어=한국어. (4) 완료 시 산출물 경로 또는 정지 사유를 마지막 줄에 SPEC_RESULT: <path|STOPPED: 사유> 로 출력.
```

## 규칙

- **Stage 1 큐(jira-triage)가 만든 이슈만** drain. 큐 없으면 거부
- `local_path`는 로컬 config(`~/.claude/jira-triage.md`) `profiles[].repos.<sub_repo>.local_path`에서만 읽음 — 이슈 metadata에 없음
- local_path 미설정·project 매핑 없음·기타 타입 → 중단(§guard)
- 인터랙티브 aoe 세션 = 구독 $0. 헤드리스(`claude --print`) 안 씀
- PR까지만. 머지·publish는 사람
- `--dry-run`이면 aoe/Multica 쓰기 없이 조립된 커맨드만 출력
- aoe 세션은 `-y`(yolo, 권한프롬프트 스킵)로 자율 실행 — gate-as-stop이 안전망
- `triage_type` 값은 jira-triage classify 4종(구현/버그픽스/기획/기타)에 의존 — 변경 시 함께 갱신
- metadata 확장 — `drain_state: working`(착수) = jira-drain이 write, `done`(머지·정리 완료)은 [cleanup](references/cleanup.md)에서 write. (jira-triage 6키 외 추가 키)
- 머지 후 세션·워크트리 정리 = [cleanup](references/cleanup.md) (PR `MERGED` 확인 후 `aoe worktree cleanup -f`)

## 오류 처리

| 상황 | 처리 |
|------|------|
| 이슈/metadata 없음 | `❌ 실패: <KEY> 큐 이슈 없음 (jira-triage 먼저)` |
| project 매핑 없음 | `❌ 실패: <KEY> project 매핑 없음 (~/.claude/jira-triage.md 보완)` |
| local_path 미설정 | `❌ 실패: <repo> local_path 미설정 (~/.claude/jira-triage.md 보완)` |
| triage_type=기타 | `수동 처리 — drain 안 함` 중단 |
| aoe add 실패 | `→ ESCALATE: aoe add 실패 <stderr>` |
| 세션 기존 존재 | `aoe send`로 재사용 (auto-revive) |
| mark 실패 (세션은 실행 중) | `→ ESCALATE: mark 실패 — 수동 상태 전환 필요` |

## Receipt

`--dry-run`이면 상태 라벨 = `recorded only`, side effects = "would: …".

```
jira-drain 착수 완료 (applied | recorded only — dry-run).
- session: "[<KEY>] <summary>" · group: <session_group>
- branch: <prefix>/<KEY>-<slug> · local_path: <local_path>
- side effects:
  - multica: drain_state=working, status → in_progress (<id>)
  - aoe: 1 session launched
- next: aoe 세션에서 PR_RESULT 확인 → /nara-kit:review-queue → 머지 후 cleanup
```
