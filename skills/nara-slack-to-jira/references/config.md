# config — profile 자동학습·라우팅

프로젝트 라우팅은 **링크에 박힌 channel_id**가 결정한다. 사용자는 channel_id를 손으로 쓰지 않는다 — 스킬이 링크에서 추출하고, 신규 채널이 나타날 때 config를 키워간다.

## 위치

- 글로벌: `~/.claude/slack-to-jira.md` (어느 repo에서 돌리든 링크가 라우팅하므로 글로벌이 기본)
- repo override (선택): 소비 repo의 `.claude/overrides/slack-to-jira.md`가 글로벌 위에 merge. 해당 repo에서만 profile 추가/덮어쓰기
- config에 비밀값 없음 — Jira/Slack 인증은 MCP 레이어가 담당

## 스키마 (YAML frontmatter)

```yaml
profiles:
  - channels: [C0123456789]        # 학습된 값, 손으로 안 씀
    jira_project: ABC
    issue_types: { bug: Bug, feature: Story }
    label_policy: classification   # label = classification (bug|feature). 정적 label 안 씀
    extra_labels: []               # 선택. classification 외 추가 정적 label (기본 없음)
    dedup_jql_base: "statusCategory != Done"   # 선택. project 필터에 AND로 붙음
```

## 라벨링

- label = **classification** → Bug 행은 `bug`, Feature 행은 `feature`. issue type이 아니라 분류값을 소문자 label로.
- `from-slack` 같은 출처 label은 **쓰지 않는다** — 티켓 label은 유형 식별용.
- 추가 정적 label이 필요하면 profile `extra_labels`에 append (기본 빈값). 최종 label = `[classification, ...extra_labels]`.

## 라우팅

1. 링크에서 `channel_id` 추출
2. `profiles[].channels`에 매칭되는 profile 선택
3. 매칭된 profile의 `jira_project` / `issue_types` / `label_policy` / `dedup_jql_base` 사용
4. 매칭 없음 → 학습 플로우

## 학습 플로우 (신규 채널 1회만)

1. 매칭 profile 없는 채널 발견
2. `jira_get_all_projects` + 생성 메타데이터로 후보 프로젝트·이슈타입 조회 → 사용자에게 제시
3. 사용자에게 한 번만 질문: 어느 Jira 프로젝트? / Bug·Feature 이슈타입명?  (label은 classification 자동 — 안 물음)
4. 답을 `~/.claude/slack-to-jira.md`의 `profiles`에 append → 계속 진행
5. 이후 같은 채널 링크는 질문 없이 그 profile로 라우팅

싱글 프로젝트 사용자는 첫 링크에서 한 번만 답하면 끝. 멀티 프로젝트는 새 채널이 처음 등장할 때마다 한 번씩 학습된다.
