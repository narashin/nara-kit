# cleanup — 머지 후 space·워크트리 정리 (Stage 3 꼬리)

jira-drain이 띄운 herdr space는 PR 생성까지만 한다. PR이 **머지된 뒤**(사람이 Stage 3 리뷰 후 merge) 남는 space(워크트리+workspace)를 회수한다. 별도 크론 불요 — 머지 확인 시점에 사람이 1회 실행하거나, review-queue 드레인 끝에 붙인다.

## 트리거

연결 PR이 머지 상태 (`gh pr view <url> --json state -q .state` == `MERGED`).

## 단계

```bash
# 1) 브랜치로 space(workspace) 찾기 — launch가 만든 <prefix>/<KEY>-<slug>
WS=$(herdr worktree list --cwd "<local_path>" --json \
      | jq -r '.result.worktrees[] | select(.branch=="<prefix>/<KEY>-<slug>") | .open_workspace_id // empty')
# WS 비어 있으면 이미 정리됨 → 2) 스킵하고 3)으로

# 2) space + 워크트리 제거 (herdr가 git 브랜치는 남김)
herdr worktree remove --workspace "$WS" --force

# 3) (선택) 머지된 로컬 브랜치 삭제
git -C "<local_path>" branch -D "<prefix>/<KEY>-<slug>"

# 4) Multica 큐 이슈 종료
multica issue metadata set <id> --key drain_state --value done
multica issue status <id> done
```

## 규칙

- **space는 workspace_id로 개별 제거** — `worktree remove --workspace <WS> --force`. herdr엔 aoe식 orphaned 일괄 cleanup·dry-run 개념 없음. WS는 브랜치명으로 `worktree list --json` 매칭해 얻는다 (metadata에 저장 안 함).
- `worktree remove`는 워크트리 디렉토리 + herdr workspace만 제거하고 **git 브랜치는 남긴다** — 머지된 브랜치 삭제는 3) `git branch -D`로 별도(선택).
- 미머지 PR의 space는 건드리지 않는다 — 머지 확인 후 실행이 안전.
- 머지 판정은 PR 상태(`MERGED`)로만 — 로컬 브랜치 존재 여부로 추측 금지.
- `drain_state`: `working`(jira-drain 착수) → `done`(머지·정리 완료). [[jira-drain]] SKILL.md가 working write, 여기서 done.

## 오류 처리

| 상황 | 처리 |
|------|------|
| PR 미머지 | `정리 보류 — PR 아직 MERGED 아님 (<state>)` 후 스킵 |
| `worktree remove` 실패 | `→ ESCALATE: herdr worktree remove 실패 <stderr>` |
| WS 못 찾음(이미 정리) | 무시하고 이슈 종료 단계 진행 |
