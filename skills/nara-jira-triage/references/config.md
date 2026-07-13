# config — project → repo 매핑·라우팅

티켓의 **Jira project key**가 repo를 결정한다. 사용자는 매핑을 손으로 외우지 않는다 — config가 들고 있고, 신규 project가 나타나면 키워간다.

## 위치

- 글로벌: `~/.claude/jira-triage.md` (어느 repo에서 돌리든 project key가 라우팅하므로 글로벌이 기본)
- repo override (선택): 소비 repo의 `.claude/overrides/jira-triage.md` 가 글로벌 위에 merge
- config에 비밀값 없음 — Jira 인증은 MCP 레이어가 담당

## 스키마 (YAML frontmatter)

```yaml
defaults:
  assignee: currentUser()
  mention: <SHINNARA_MEMBER_UUID>
  ready_statuses: [To Do, Selected for Development]
  misc_session_group: nara-kit        # 기타 타입 세션그룹
profiles:
  - jira_project: SVC
    pr_language: ko
    repos:
      default: { repo: your-org/svc, git_host: git.example.com, session_group: svc, local_path: "" }
  - jira_project: APP
    pr_language: en
    repos:
      fe: { repo: your-org/app-fe,         git_host: git.example.com, session_group: app-fe,         local_path: "" }
      be: { repo: your-org/app-be, git_host: git.example.com, session_group: app-be, local_path: "" }
```

## 라우팅

1. 티켓 key → project (`SVC-123` → `SVC`)
2. project profile 선택
3. **sub-repo 선택:**
   - SVC → `repos.default`
   - APP → FE/BE 분류로 `repos.fe` 또는 `repos.be` (분류 규칙은 SKILL.md classify)
4. 매칭된 `repo` / `session_group` / `git_host` / `pr_language` 를 이슈 본문·metadata에 기재
5. project 매핑 없음 → 큐 이슈 생성 + `[UNVERIFIED: project <KEY> repo 매핑 없음]`, session_group=`misc_session_group`

> `local_path` 는 사용자가 각 repo 체크아웃 경로로 채운다 (Stage 2 실행기가 cd할 위치). 빈 값이면 Stage 2가 경고.

## 학습 플로우 (신규 project 1회만)

1. 매핑 없는 project key 발견
2. notify-only 이슈로 발급하면서 본문에 매핑 요청 표기
3. 사용자가 `~/.claude/jira-triage.md` 의 `profiles` 에 `{jira_project, pr_language, repos}` append
4. 이후 같은 project 티켓은 dev/doc 런치킷으로 정상 라우팅

> autopilot은 무인 실행이므로 신규 project를 자동 학습하지 않는다 — notify-only로 떨어뜨려 사람이 매핑을 추가하게 한다 (잘못된 repo 추측 방지).

## 시드 매핑

| Jira project | 분류 | repo | session_group |
|--------------|------|------|---------------|
| SVC | (전체) | svc | svc |
| APP | FE | app-fe | app-fe |
| APP | BE | app-be | app-be |
| (기타) | — | — | nara-kit |
