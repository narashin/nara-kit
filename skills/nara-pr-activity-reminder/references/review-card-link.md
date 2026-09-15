# 온디맨드 재리뷰

판정 카드를 `in_progress` 로 옮기면 재리뷰 요청이다. 실행은 디스패처(git 밖) 몫이고 이 스킬은 계약만 선언한다.

| 시점 | metadata |
|---|---|
| 착수 | `review_state=dispatched` · `review_worktree` · `review_worktree_sel` · `review_prompt_state=pending` |
| 수집 | `reviewed_sha` 기록 → `review_state` 를 판정값(`passed`/`changes_requested`)으로 · `review_worktree_sel`·`review_prompt_state` 삭제 → 상태 `in_review` |

착수 가드는 **실행 중**만 막는다 (`review_state ∈ {dispatched, blocked}`). 판정값은 `/post` 가 "게시할 판정이 있다"를 읽는 자리라 지우면 안 되고, 그걸 "바쁨"으로 읽으면 첫 판정이 영구히 굳어 재리뷰 드래그가 할 일이 없어진다.

`todo` 가 "리뷰해줘"로 읽히는 건 **아직 판정 안 난 판정 카드** 하나뿐이다. `reviewed` 가 이미 붙은 카드는 `in_progress` 드래그로만 돈다. 판정 범위는 PR 전체 재판정이고, `reviewed_sha` 는 나중에 증분 방식으로 갈 여지를 남겨둔 기록이다.

새 커밋 감지로 재리뷰가 자동 발동하는 일은 없다. 사람이 요청할 때만 돈다.

`review_state=dispatched` 인 카드는 종료 처리에서 건너뛴다. `done` 으로 넘기면 디스패처의 수집 대상 상태(todo/in_progress/in_review)에서 빠져 판정이 워크트리에 갇힌다.

## `reviewed` 는 판정 카드에만 쓴다

그 키는 `nara-review-reminder` dedup의 source of truth다. 다른 종류 카드에 쓰면 아무 동작도 없이 PR이 승인된 것처럼 읽힌다.

## 폐기된 것: 형제 카드 링크

예전엔 리뷰 요청 한 건에 카드가 둘 생겼다 — `tracker_type=review`(판정용)와 `tracker_type=activity`(판정 이후 감시용). 판정 결과는 앞쪽에만 달리므로 뒤쪽에서 앞쪽으로 가는 링크(`review_issue_key`)가 필요했다.

이제 카드가 하나다. 판정 카드가 리뷰 요청부터 PR 머지까지 살면서 판정과 활동을 모두 받는다. 링크할 형제가 없으므로 `review_issue_key` 도, 그걸 채우던 백필 패스도 없다. 기존 카드에 남아 있는 그 키는 읽히지 않는다.
