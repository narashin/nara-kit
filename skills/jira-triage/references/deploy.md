# deploy — Multica 셋업 (Stage 1 autopilot + Stage 2 aoe)

Stage 1(jira-triage)은 autopilot 크론, Stage 2(착수)는 사람이 jira-drain으로 트리거하는 aoe 세션이다. autopilot은 *등록된 스킬 복사본*을 실행하므로, repo SKILL.md 수정 후엔 복사본 동기화 필수 (repo 변경만으론 autopilot 안 바뀜).

## Stage 1 — jira-triage autopilot

### 1) 스킬 복사본 등록/갱신

```bash
multica skill update <skill_id> --content-file skills/jira-triage/SKILL.md
```

## 2) agent에 jira MCP 주입

autopilot agent는 별도 프로세스 — 세션 MCP 접근 불가. Claude Desktop `claude_desktop_config.json` 의 jira mcpServers를 추출해 파일로 주입:

```bash
multica agent update <agent_id> --mcp-config-file <jira-mcp.json>
```

> secret(토큰) 포함 시 classifier가 인라인 `--mcp-config` 를 차단함 → `--mcp-config-file` + 사용자가 `!` 로 직접 실행해야 통과.
>
> jira MCP는 **본인(shinnara) 토큰**으로 인증되어야 `currentUser()` = 나. 아니면 `--assignee <ACCOUNT_ID>` 명시.

### 3) 크론 (Multica 백엔드)

예: 매시 정각. agent instructions에 기본값 주입:

```
assignee = currentUser()
mention  = <SHINNARA_MEMBER_UUID>
projects = SANDY,LYRIS
```

## Stage 2 — aoe 세션 (사람이 jira-drain으로 트리거)

큐 이슈를 사람이 판단 후 `/nara-kit:jira-drain <KEY>` 로 트리거한다. jira-drain이 metadata(`session_group`/`repo`/`local_path`/`pr_language`/`sub_repo`/`triage_type`)를 읽고 aoe로 인터랙티브 Claude Code 세션을 띄운다.

**전제:** 실행 머신에 `aoe`(tmux 세션매니저) + `claude` + `git` CLI가 PATH에 있고, 각 repo의 `local_path`가 config(`~/.claude/jira-triage.md`)에 채워져 있어야 한다.

```
aoe add [PATH] -t <title> -g <group> -w <branch> -b --base-branch <base> -c claude -l [-y]
aoe send <ID|title> "<message>"          # 세션에 프롬프트 주입 (auto-revive)
aoe session show|capture <ID>            # 상태·tmux pane 캡처(PR 링크 회수)
aoe session archive <ID>                 # tmux teardown (worktree 보존)
aoe group list|create|move               # 세션그룹
aoe worktree list|cleanup                # 머지 후 orphaned 워크트리 제거
```

**실행 규약 (jira-drain이 aoe send로 주입):**
- 종료점 = **PR 생성까지. 머지 금지.**
- dev-mode 내부 게이트(gap<80, AC, code-review 미해결) 미달 → **강행 금지, 멈추고 사유 리포트**
- 완료 시 PR 링크/정지 사유를 이슈 코멘트로 → Stage 3(review-queue) 인계
- 인터랙티브(구독) 실행 = $200 헤드리스 풀 안 씀

> Stage 2 런처 스킬 = `jira-drain` (별도). 이 절은 그 계약.

## 동기화 체크리스트

- [ ] SKILL.md 변경 → `multica skill update` 재실행
- [ ] config(`~/.claude/jira-triage.md`) profiles에 신규 project 매핑 추가
- [ ] jira MCP 토큰 = 대상 assignee 본인
- [ ] 실행 머신에 `aoe`·`claude`·`git` CLI + repo `local_path` 확인
