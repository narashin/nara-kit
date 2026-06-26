# deploy — Multica 셋업 (Stage 1 autopilot + Stage 2 agents)

Stage 1(jira-triage)은 autopilot 크론, Stage 2(착수)는 Dev/Planner agent다. autopilot은 *등록된 스킬 복사본*을 실행하므로, repo SKILL.md 수정 후엔 복사본 동기화 필수 (repo 변경만으론 autopilot 안 바뀜).

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

## Stage 2 — Dev / Planner agent

큐 이슈를 이 agent에 assign + status In Progress로 바꾸면 task가 enqueue된다. agent는 metadata `jira_key`/`repo`를 읽고 headless Claude Code로 shell out한다.

**전제 (case A):** agent 런타임 = **사용자 머신** (또는 repo·creds 갖춘 로컬 러너). `git` + `claude` CLI가 PATH에 있어야 함. Multica 백엔드 서버에서 돌면 repo/creds 없어 불가.

| agent | 담당 type | 실행 |
|-------|-----------|------|
| `Dev` | 구현 · 버그픽스 | `claude -p "/nara-kit:wt <KEY> → /nara-kit:prep <KEY> → dev-mode"` (repo worktree) |
| `Planner` | 기획 | `claude -p "/nara-kit:prep <KEY> → doc-mode"` |

**실행 규약 (Stage 2 agent skill에 박을 것):**
- 종료점 = **PR 생성까지. 머지 금지.**
- dev-mode 내부 게이트(gap<80, AC, code-review) 미달 → **강행 금지, 멈추고 이슈에 리포트**
- 완료 시 PR 링크를 이슈 코멘트로 남기고 done → Stage 3(review-reminder/review-queue) 인계
- agent에 git/jira MCP + 작업 repo 경로 주입

> Stage 2 executor 스킬은 별도 빌드 (jira-triage는 큐만 채움). 이 표는 그 계약.

## 동기화 체크리스트

- [ ] SKILL.md 변경 → `multica skill update` 재실행
- [ ] config(`~/.claude/jira-triage.md`) profiles에 신규 project 매핑 추가
- [ ] jira MCP 토큰 = 대상 assignee 본인
- [ ] Dev/Planner agent 런타임에 `git`·`claude` CLI + repo 경로 확인
