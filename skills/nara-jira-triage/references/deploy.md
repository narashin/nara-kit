# deploy — Multica 셋업 (Stage 1 autopilot + Stage 2 herdr)

Stage 1(jira-triage)은 autopilot 크론, Stage 2(착수)는 사람이 jira-drain으로 트리거하는 herdr 세션이다. autopilot은 *등록된 스킬 복사본*을 실행하므로, repo SKILL.md 수정 후엔 복사본 동기화 필수 (repo 변경만으론 autopilot 안 바뀜).

## Stage 1 — jira-triage autopilot

### 1) 스킬 복사본 등록/갱신

```bash
multica skill update <skill_id> --content-file skills/nara-jira-triage/SKILL.md
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
projects = SVC,APP
```

## Stage 2 — herdr 세션 (사람이 jira-drain으로 트리거)

큐 이슈를 사람이 판단 후 `/nara-jira-drain <KEY>` 로 트리거한다. jira-drain이 metadata(`jira_key`/`triage_type`/`repo`/`pr_language`/`sub_repo`)를 읽고(`local_path`는 로컬 config에서 조회, `session_group`은 무시) herdr로 **space=repo@branch** 워크트리를 띄워 인터랙티브 Claude Code 세션을 실행한다. herdr 커맨드(`herdr worktree create`/`herdr pane run` 등) 상세는 `nara-jira-drain` 스킬이 소유한다 — 여기서 중복하지 않는다.

**전제:** 실행 머신에 `herdr` + `claude` + `git` CLI가 PATH에 있고, 각 repo의 `local_path`가 config(`~/.claude/jira-triage.md`)에 채워져 있어야 한다.

**실행 규약 (jira-drain이 herdr pane run으로 주입):**
- 종료점 = **PR 생성까지. 머지 금지.**
- dev-mode 내부 게이트(gap<80, AC, code-review 미해결) 미달 → **강행 금지, 멈추고 사유 리포트**
- 완료 시 PR 링크/정지 사유를 이슈 코멘트로 → Stage 3(review-queue) 인계
- 인터랙티브(구독) 실행 = $200 헤드리스 풀 안 씀

> Stage 2 런처 스킬 = `nara-jira-drain` (별도). 이 절은 그 계약.

## reconcile — out-of-band 결정론 스크립트 (LLM 아님)

reconcile(Jira Done → 큐 이슈 done)은 의미 판단이 없어 **오토파일럿(LLM)에 얹지 않는다** — 얹으면 빈 런마다 LLM 토큰 낭비. 대신 Jira REST(PAT) + `multica` CLI만 쓰는 셸 스크립트를 OS 크론으로 돌린다. Multica agent엔 precheck 프리미티브가 없으므로(빈 런 못 막음), 스크립트 자체가 게이트 역할(매칭 0 → no-op).

**전제:** 실행 머신에 `multica`·`jq`·`curl` + 셸에서 쓸 **Jira PAT** (Jira Data Center: `Authorization: Bearer <PAT>`).

```bash
# 1) PAT 저장 (0600). JIRA_PAT env 로 대체 가능
install -m 700 -d ~/.config/jira-reconcile
printf '%s' '<YOUR_JIRA_PAT>' > ~/.config/jira-reconcile/token && chmod 600 ~/.config/jira-reconcile/token

# 2) 스크립트 배치 (JIRA_BASE 기본값은 스크립트 상단 상수 — 사내 Jira 호스트로)
#    로직: multica issue list → jira_key 수집 → REST 'statusCategory=Done' 배치 → 매칭 done 전이
#    --dry-run 지원. 상세 로직은 SKILL.md reconcile 절.

# 3) 크론 (macOS launchd 예: 매시간). Linux면 crontab.
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/<label>.plist
launchctl kickstart -k gui/$(id -u)/<label>          # 즉시 1회
```

> 스크립트·PAT·크론 plist는 **각자 머신 로컬** — 이 repo(placeholder)엔 실 호스트/토큰 넣지 않는다.

## 동기화 체크리스트

- [ ] SKILL.md 변경 → `multica skill update` 재실행
- [ ] config(`~/.claude/jira-triage.md`) profiles에 신규 project 매핑 추가
- [ ] jira MCP 토큰 = 대상 assignee 본인
- [ ] 실행 머신에 `herdr`·`claude`·`git` CLI + repo `local_path` 확인
- [ ] reconcile: `multica`·`jq`·`curl` + Jira PAT(0600) + OS 크론(launchd/crontab) 등록. `--dry-run` 스모크 먼저
