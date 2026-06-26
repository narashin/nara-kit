# config — project → repo 매핑·라우팅

티켓의 **Jira project key**가 repo를 결정한다. 사용자는 매핑을 손으로 외우지 않는다 — config가 들고 있고, 신규 project가 나타나면 키워간다.

## 위치

- 글로벌: `~/.claude/jira-triage.md` (어느 repo에서 돌리든 project key가 라우팅하므로 글로벌이 기본)
- repo override (선택): 소비 repo의 `.claude/overrides/jira-triage.md` 가 글로벌 위에 merge
- config에 비밀값 없음 — Jira 인증은 MCP 레이어가 담당

## 스키마 (YAML frontmatter)

```yaml
defaults:
  assignee: currentUser()           # autopilot jira MCP 본인 인증 시
  mention: <SHINNARA_MEMBER_UUID>   # Multica member id (선택)
  ready_statuses:                   # 큐 대상 status (Backlog/In Progress 제외)
    - To Do
    - Selected for Development
profiles:
  - jira_project: SANDY
    git_host: git.linecorp.com
    repo: LINE-SRE/sandbox-dns
  - jira_project: LYRIS
    git_host: git.linecorp.com
    repo: LINE-SRE/iris-ui
```

## 라우팅

1. 티켓 key에서 project 추출 (`SANDY-123` → `SANDY`)
2. `profiles[].jira_project` 매칭 profile 선택
3. 매칭된 `git_host` / `repo` 를 dev 런치킷에 사용
4. 매칭 없음 → notify-only (repo 모르면 진입 커맨드 제안 불가) + `[UNVERIFIED: project <KEY> repo 매핑 없음]`

> **cross-repo 예외:** project→repo는 거의 항상 맞다 (LYRIS=iris-ui 등). 본문이 드물게 *다른* repo(예: lyris-ai-workbench)를 명시해도 **라우팅은 기본 매핑 유지** — 본문에 `[note: 본문이 <repo> 언급 — 확인]` caveat만 달고 넘어간다. 휴리스틱 오라우팅보다 일관성이 낫다.

## 학습 플로우 (신규 project 1회만)

1. 매핑 없는 project key 발견
2. notify-only 이슈로 발급하면서 본문에 매핑 요청 표기
3. 사용자가 `~/.claude/jira-triage.md` 의 `profiles` 에 `{jira_project, git_host, repo}` append
4. 이후 같은 project 티켓은 dev/doc 런치킷으로 정상 라우팅

> autopilot은 무인 실행이므로 신규 project를 자동 학습하지 않는다 — notify-only로 떨어뜨려 사람이 매핑을 추가하게 한다 (잘못된 repo 추측 방지).

## 시드 매핑

| Jira project | repo |
|--------------|------|
| `SANDY` | `git.linecorp.com/LINE-SRE/sandbox-dns` |
| `LYRIS` | `git.linecorp.com/LINE-SRE/iris-ui` |
