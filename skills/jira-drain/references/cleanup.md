# cleanup — 머지 후 워크트리·세션 정리 (Stage 3 꼬리)

jira-drain이 띄운 세션은 PR 생성까지만 한다. PR이 **머지된 뒤**(사람이 Stage 3 리뷰 후 merge) 남는 aoe 세션과 워크트리를 회수한다. 별도 크론 불요 — 머지 확인 시점에 사람이 1회 실행하거나, review-queue 드레인 끝에 붙인다.

## 트리거

연결 PR이 머지 상태 (`gh pr view <url> --json state -q .state` == `MERGED`).

## 단계

```bash
# 1) tmux 세션 teardown (워크트리는 보존)
aoe session archive "[<KEY>] <summary>"      # 또는 session id

# 2) orphaned(머지 완료) 워크트리 미리보기 → 실제 제거
aoe worktree cleanup                          # 기본 dry-run — 제거 대상만 출력
aoe worktree cleanup -f                        # -f 로 실제 삭제

# 3) Multica 큐 이슈 종료
multica issue metadata set <id> --key drain_state --value done
multica issue status <id> done
```

## 규칙

- `aoe worktree cleanup` 은 **기본 dry-run** — 실제 삭제는 `-f/--force` 필수. 먼저 dry-run으로 대상 확인 후 `-f`.
- 미머지 PR의 워크트리는 건드리지 않는다 (cleanup은 orphaned만 대상이지만, 머지 확인 후 실행이 안전).
- 머지 판정은 PR 상태(`MERGED`)로만 — 로컬 브랜치 존재 여부로 추측 금지.
- `drain_state`: `working`(jira-drain 착수) → `done`(머지·정리 완료). [[jira-drain]] SKILL.md가 working write, 여기서 done.

## 오류 처리

| 상황 | 처리 |
|------|------|
| PR 미머지 | `정리 보류 — PR 아직 MERGED 아님 (<state>)` 후 스킵 |
| `aoe worktree cleanup` 실패 | `→ ESCALATE: worktree cleanup 실패 <stderr>` |
| 세션 이미 archive됨 | 무시하고 다음 단계 진행 |
