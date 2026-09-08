# 판정 카드 링크 + 온디맨드 재리뷰

리뷰 요청 한 건에 카드가 둘 생긴다. `tracker_type=review`(판정용, `nara-review-reminder`가 만든다)와 `tracker_type=activity`(판정 이후 대댓글·새 커밋 감시, 이 스킬이 만든다). 판정 결과는 앞쪽 카드에만 달리므로, 활동 추적 카드에서 그 카드로 가는 길이 없으면 리뷰가 안 돌아간 것처럼 보인다.

## 판정 카드 찾기

같은 `pr_url`을 가진 `tracker_type=review` 카드를 고른다. 조회는 **서버측 metadata 필터로** 한다. 판정 카드는 보통 이미 `done`이라 `issue list --limit N` 창에서 밀린다:

```bash
multica issue list --metadata "pr_url=<PR URL>" --output json
```

카드 URL은 `{app_url}/{workspace slug}/issues/{ident}`. `app_url`은 `~/.multica/config.json`, slug는 `multica workspace list`에서 읽는다 (config에는 `workspace_id`만 있어 id로 매칭해야 한다). 하드코딩하지 않는다.

판정 카드가 없으면(리뷰어로 지정된 적 없는 PR) 링크를 생략하고 `review_issue_key=none`으로 못 박아 매 실행 재조회를 막는다.

## 백필 — 링크 없는 기존 카드

`review_issue_key`가 없는 열린 활동 카드에 링크를 채운다. **PR 순회와 분리된 별도 패스로 돈다.** PR 순회는 login 단위 리뷰 요청이나 내가 GitHub에 남긴 리뷰가 있는 PR만 본다. 팀 단위로 요청됐고 판정을 GitHub에 게시하지 않은 PR은 둘 다 아니라서 그 추적 카드에 영원히 안 닿는다. 활동 감지에는 맞는 필터이고 카드 링크에는 틀린 필터다.

description은 이미 쓰여 있고 사람이 손댔을 수 있으니 고쳐 쓰지 않고 코멘트로 남긴다:

```bash
multica issue metadata set <issue_id> --key review_issue_key --value "<ident>"
multica issue comment add  <issue_id> --content "리뷰 판정 카드: <ident> (<카드 URL>)"
```

## 온디맨드 재리뷰

카드를 `in_progress`로 옮기면 재리뷰 요청이다. 실행은 디스패처(git 밖) 몫이고 이 스킬은 계약만 선언한다:

| 시점 | metadata |
|---|---|
| 착수 | `review_state=dispatched` · `review_worktree` · `review_worktree_sel` · `review_prompt_state=pending` |
| 수집 | `reviewed_sha` 기록 → `review_state`·`review_worktree_sel`·`review_prompt_state` 삭제 → 상태 `todo` 복귀 |

`reviewed`는 절대 쓰지 않는다. 그 키는 `nara-review-reminder` dedup의 source of truth로, 활동 카드에 쓰면 아무 동작도 없이 PR이 승인된 것처럼 읽힌다.

새 커밋 감지로 재리뷰가 자동 발동하는 일은 없다. 사람이 요청할 때만 돈다. 판정 범위는 PR 전체 재판정이고, `reviewed_sha`는 나중에 증분 방식으로 갈 여지를 남겨둔 기록이다.

`review_state=dispatched`인 카드는 PR 종료 처리(`close_finished`)에서 건너뛴다. `done`으로 넘기면 디스패처의 수집 대상 상태(todo/in_progress/in_review)에서 빠져 판정이 워크트리에 갇힌다. 수집 후 `todo`로 돌아오면 다음 패스가 정상적으로 닫는다.
