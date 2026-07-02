---
name: jira-drain
description: >-
  Launch a chosen jira-triage queue ticket into a herdr worktree (space = repo@branch) running claude, and drive dev-mode/doc-mode to a PR — interactive ($0), human-triggered.
  USE FOR: "jira-drain", "큐 티켓 착수", "이 티켓 돌려", "/nara-kit:jira-drain KEY".
  DO NOT USE FOR: 큐 생성·분류 (→ jira-triage), PR 리뷰 (→ review-queue), 큐 없이 직접 (→ /nara-kit:wt + dev-mode).
---

# jira-drain — 큐 티켓 → herdr space 착수

사람이 고른 Multica 큐 티켓 1건을 받아, metadata 라우팅대로 herdr worktree(space)를 띄우고 그 안에서 claude가 워크플로를 PR까지 자율 실행한다. **인터랙티브 구독 = $0.**

herdr에서 **space = repo@branch** 단위다 (`worktree create` 한 방에 workspace + tab + pane 생성). 티켓 하나 = space 하나 — tab/group은 신경 쓰지 않는다.

## 인자

```
jira-drain <KEY|issue_id> [--dry-run]
```

## Step 0 — Pre-flight

`multica`, `herdr` PATH 확인. 없으면 `❌ 실패: <cmd> not found (PATH 확인)` 후 중단.

## 파이프라인

1. **resolve** — KEY/issue_id로 Multica 이슈를 찾고(`multica issue list --output json` → `jira_key` metadata 매칭 또는 직접 `multica issue get <id>`) metadata 읽음: `jira_key · triage_type · repo · pr_language · sub_repo`. `local_path`는 **로컬 config(`~/.claude/jira-triage.md`)** 에서 조회:
   - KEY 접두로 jira_project 도출 (`APP-425` → `APP`)
   - `profiles[].jira_project == jira_project` 인 profile 선택
   - `sub_repo` 값(`default|fe|be`)으로 `profile.repos.<sub_repo>.local_path` 읽음
   - `<summary>` 추출: 이슈 title에서 `[<KEY>] <타입>: ` 접두 제거 (`[APP-425] 구현: 편집 기능` → `편집 기능`). jira-triage가 세팅한 title 형식에 의존. `summary` metadata 키는 없음 — title에서만 파싱.
   - `default_branch` = repo 기본 브랜치 (`git -C <local_path> symbolic-ref --short refs/remotes/origin/HEAD` 실패 시 `main`)
   - `jira_key` 매칭이 여러 건이면 가장 최근 `created_at` 1건 선택, 나머지는 → `ESCALATE: <KEY> 중복 큐 이슈 N건`
   - **`session_group`은 읽지 않는다** — herdr엔 group 개념 없음(space=repo@branch가 그룹 역할). jira-triage가 넣은 `session_group` metadata는 무시.

2. **guard** — 다음 조건 중 하나라도 해당하면 중단:
   - Multica 이슈 없음 → `❌ 실패: <KEY> 큐 이슈 없음 (jira-triage 먼저)`
   - config에 jira_project profile 없음 → `❌ 실패: <KEY> project 매핑 없음 (~/.claude/jira-triage.md 보완)`
   - `local_path` 비어 있음 → `❌ 실패: <repo> local_path 미설정 (~/.claude/jira-triage.md 보완)`
   - `triage_type == 기타` → `수동 처리 — drain 안 함` 중단

3. **launch** — 브랜치명 `<prefix>/<KEY>-<slug>` (버그픽스→`fix/`, 구현→`feature/`, 기획→`docs/`; slug=summary kebab, 영숫자/하이픈, 소문자, ~50자; 비ASCII(한글 등)는 생략 — slug 비면 브랜치 = `<prefix>/<KEY>` trailing 하이픈 제거). **worktree create 한 방으로 space + claude pane 생성**, 프롬프트는 claude 초기 인자로 주입(§gate-as-stop):
   ```bash
   R=$(herdr worktree create --cwd "<local_path>" \
     --branch "<prefix>/<KEY>-<slug>" --base "<default_branch>" \
     --label "[<KEY>] <summary>" --no-focus --json)
   WS=$(echo "$R"   | jq -r '.result.workspace.workspace_id')   # 예: w5 — cleanup·receipt용
   PANE=$(echo "$R" | jq -r '.result.root_pane.pane_id')        # 예: w5:p1 — claude 실행처

   # claude 실행 + gate-as-stop 프롬프트를 초기 인자로 (pane run = text + Enter 한 방)
   herdr pane run "$PANE" "claude --permission-mode auto '<프롬프트>'"

   # folder trust 게이트 — 새 워크트리 첫 실행 시 "trust this folder?" 가 뜬다.
   # --permission-mode auto 로는 안 넘어가므로 "1"(Yes)을 보낸다. 통과 후 초기 프롬프트 인자가 자동 실행됨.
   # 새 워크트리는 항상 미신뢰라 항상 처리. 타이밍은 claude 로딩 대기 후(실사용 시 timeout 조정).
   herdr agent wait "$PANE" --status idle --timeout 90000 2>/dev/null || sleep 20
   herdr pane run "$PANE" "1"
   ```
   - `worktree create` 실패(브랜치/워크트리 이미 존재 등) → `ESCALATE: herdr worktree create 실패 <stderr>`
   - **프롬프트에 작은따옴표(`'`) 금지** — pane run 바깥 `"..."` 안 claude 인자 `'...'`로 감싸므로. gate-as-stop 프롬프트는 작은따옴표 없이 유지.
   - `--base`로 스택 지정 가능 (진행 중 PR 위 스택 필요 시 다른 브랜치).

4. **mark** — 이슈 metadata + 상태 전환:
   ```bash
   multica issue metadata set <id> --key drain_state --value working
   multica issue status <id> in_progress
   ```

5. **receipt** — 출력 계약 4요소 (실행한 herdr 커맨드 · space/workspace · side effects · next).

## gate-as-stop 프롬프트 (§launch claude 인자 본문)

### 구현 / 버그픽스 (dev-mode)

```
<KEY> 처리. /nara-kit:prep <KEY> 후 dev-mode를 PR 생성까지 자율 진행. 규칙: (1) 각 게이트(gap<80, AC 미비, code-review 미해결 결함, 테스트 실패)에서 사람 기다리지 말고 멈춰 — 사유를 한국어로 요약 출력하고 PR 만들지 마. (2) 모든 게이트 통과 시에만 PR 생성, 머지는 하지 마. (3) PR 본문 언어=<pr_language>, 템플릿: 요약/변경/검증/Jira. (4) 완료 시 PR URL 또는 정지 사유를 마지막 줄에 PR_RESULT: <url|STOPPED: 사유> 로 출력.
```

### 기획 (doc-mode)

```
<KEY> 처리. /nara-kit:prep <KEY> 후 doc-mode로 spec 초안까지 자율 진행. 규칙: (1) clarity/Readiness 게이트 미달 시 사람 기다리지 말고 멈춰 — 사유를 한국어로 요약 출력. (2) spec 초안까지만, publish/Confluence 게시는 하지 마. (3) spec 본문 언어=한국어. (4) 완료 시 산출물 경로 또는 정지 사유를 마지막 줄에 SPEC_RESULT: <path|STOPPED: 사유> 로 출력.
```

## 규칙

- **Stage 1 큐(jira-triage)가 만든 이슈만** drain. 큐 없으면 거부
- `local_path`는 로컬 config(`~/.claude/jira-triage.md`) `profiles[].repos.<sub_repo>.local_path`에서만 읽음 — 이슈 metadata에 없음
- local_path 미설정·project 매핑 없음·기타 타입 → 중단(§guard)
- **herdr space = repo@branch**. 티켓마다 새 space 하나 (`worktree create`). 기존 세션 재사용·tab rename 안 함 — space 자체가 티켓 단위
- 인터랙티브 herdr space = 구독 $0. 헤드리스(`claude --print`) 안 씀
- PR까지만. 머지·publish는 사람
- `--dry-run`이면 herdr/Multica 쓰기 없이 조립된 커맨드만 출력
- claude는 `--permission-mode auto`로 자율 실행 — gate-as-stop이 안전망. `--dangerously-skip-permissions`는 **쓰지 않는다**
- **folder trust 게이트**: 새 워크트리 첫 실행 시 "trust this folder?" 뜸 → `pane run "1"`(Yes)로 통과(§launch). `--permission-mode auto`론 안 넘어가며, 통과 후 초기 프롬프트 인자가 자동 실행됨 (검증됨)
- `triage_type` 값은 jira-triage classify 4종(구현/버그픽스/기획/기타)에 의존 — 변경 시 함께 갱신
- metadata 확장 — `drain_state: working`(착수) = jira-drain이 write, `done`(머지·정리 완료)은 [cleanup](references/cleanup.md)에서 write. (jira-triage 6키 외 추가 키)
- 머지 후 space·워크트리 정리 = [cleanup](references/cleanup.md) (PR `MERGED` 확인 후 `herdr worktree remove --workspace <WS> --force`)

## 오류 처리

| 상황 | 처리 |
|------|------|
| 이슈/metadata 없음 | `❌ 실패: <KEY> 큐 이슈 없음 (jira-triage 먼저)` |
| project 매핑 없음 | `❌ 실패: <KEY> project 매핑 없음 (~/.claude/jira-triage.md 보완)` |
| local_path 미설정 | `❌ 실패: <repo> local_path 미설정 (~/.claude/jira-triage.md 보완)` |
| triage_type=기타 | `수동 처리 — drain 안 함` 중단 |
| worktree create 실패 | `→ ESCALATE: herdr worktree create 실패 <stderr>` (브랜치/워크트리 중복 가능) |
| mark 실패 (space는 실행 중) | `→ ESCALATE: mark 실패 — 수동 상태 전환 필요` |

## Receipt

`--dry-run`이면 상태 라벨 = `recorded only`, side effects = "would: …".

```
jira-drain 착수 완료 (applied | recorded only — dry-run).
- space: "[<KEY>] <summary>" (workspace <WS>) · branch: <prefix>/<KEY>-<slug>
- local_path: <local_path>
- side effects:
  - multica: drain_state=working, status → in_progress (<id>)
  - herdr: 1 worktree(space) created + claude launched
- next: herdr space에서 PR_RESULT 확인 → /nara-kit:review-queue → 머지 후 cleanup
```
