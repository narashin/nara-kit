# 판정 게시 제스처 — 라벨로 PR에 올린다

리뷰 파이프라인은 PR에 대해 read-only다. 판정은 카드 코멘트로만 남고, 아무도 손대지 않으면 PR에는 영원히 안 올라간다. 이 문서는 그 마지막 한 걸음의 계약이다.

## 제스처

카드에 라벨을 붙인다. 둘 중 하나만.

| 라벨 | 결과 |
|---|---|
| `post-comment` | 판정을 PR 리뷰 코멘트로 게시 (`gh pr review --comment`) |
| `post-approve` | approve + 코멘트 게시 (`gh pr review --approve`) |

**status 드래그가 아니라 라벨인 이유.** 남의 PR에 게시하는 것은 바깥으로 나가는 행동이고, 컬럼 이동이 암시할 성격이 아니다. 그리고 approve는 머지 신호다. `status: pass` 판정에서 자동 유도하면 안 되고, 사람이 approve를 명시한 것만이 근거다.

둘 다 붙어 있으면 아무것도 게시하지 않고 카드에 알린다. 추측하지 않는다.

판정이 없는 카드(`review_state`가 `passed`/`changes_requested` 아님)에 라벨이 붙으면 라벨을 떼고 알린다. 빈 리뷰를 남의 PR에 올리지 않는다.

## 왜 스크립트가 아니라 에이전트인가

판정문은 **보드용으로 쓰인 글**이다. `status:` / `blocking:` 같은 기계용 헤더, "PR에는 게시하지 않았다", "사람이 정한다" 같은 내부 문구, 워크트리·카드 언급이 섞여 있고 언어도 보드 기준이다. 그대로 내보내면 안 된다.

그래서 게시는 워크트리 세션에서 돈다. 하는 일은 다시 쓰기 하나다:

1. 내부 문구·기계 헤더 제거
2. 대상 repo의 언어 관행에 맞추기 (`nara-pr-review`의 게시 규칙과 동일)
3. 지적 내용·근거·심각도는 **변경 금지**. 없던 지적 추가 금지, 있는 지적 누락 금지
4. 코드 위치는 파일:줄로 유지

판정 자체를 다시 하지 않는다. approve 여부도 다시 판단하지 않는다 — 판정문이 수정을 요구하는데 `post-approve`가 붙어 있으면 게시를 거부하고 이유를 보고한다.

## 금지

- 코드 수정·커밋·push·머지. 이 실행은 게시 하나만 한다
- 인라인 코멘트를 개별로 흩뿌리기. 리뷰 하나로 게시한다
- 중복 게시. 성공 후 라벨이 제거되고 `post_state=posted`가 남는다

## metadata 계약

| 시점 | 상태 |
|---|---|
| 착수 | `post_state=dispatched` · `post_action=comment\|approve` · `post_worktree` · `post_worktree_sel` · `post_prompt_state=pending` |
| 성공 | 라벨 제거 → `post_state=posted` → 워크트리 제거 → 게시 본문을 카드 코멘트로 |
| 실패·거부 | 라벨 제거 → `post_state=failed\|refused` → **워크트리 유지**(원인 확인용). 다시 붙이려면 `post_state` 삭제 |

`post_*`는 `review_*`와 별개 키다. 판정과 게시는 다른 실행이고 재시도 조건도 다르다.

## status는 건드리지 않는다

게시가 성공하면 GitHub의 `reviews[].author.login`에 내가 들어간다. 그 시점부터 `nara-review-reminder`의 reconcile이 카드를 `done`으로 닫는다. 여기서 별도로 닫으면 reconcile 계약에 없는 종료 조건을 또 만드는 것이고, 그게 바로 판정을 `done`으로 찍어서 갚아야 할 리뷰를 보드에서 지웠던 결함이다.
