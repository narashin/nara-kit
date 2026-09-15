# 팀 요청 해석 + 리마인더 이슈 reconcile

`nara-review-reminder` 의 Step 0(reconcile)과 Step 1(팀 해석) 상세 절차.

## 왜 팀 확장이 필요한가

`gh pr list --json reviewRequests` 는 두 종류를 한 배열에 섞어 준다:

```json
{"__typename":"User","login":"shinnara"}
{"__typename":"Team","name":"Platform","slug":"acme-org/platform"}
```

팀 객체에는 `login` 필드가 **없다**. `reviewRequests[].login` 만 매칭하면 팀으로 걸린 요청은 100% 누락된다 — 티켓이 아예 안 만들어진다.

## 내 팀 slug 셋 만들기

```bash
GH_HOST=<host> gh api /user/teams --paginate
```

각 항목에서 `<organization.login>/<slug>` 를 조립한다 (예: `acme-org/platform`). PR JSON 쪽 `slug` 는 이미 `<org>/<team>` 합본이므로 이 형태로 맞춰야 비교가 성립한다. 비교는 대소문자 무시.

`--reviewer` 가 gh 실행 계정과 다르면 `/user/teams` 는 쓸 수 없다 — 그건 실행 계정의 팀 목록이다. 이 경우 팀 확장을 건너뛰고 개인 매칭만 수행하며 로그에 남긴다.

`read:org` 스코프가 없으면 팀 조회가 실패한다. 이때도 **중단하지 말고** 개인 매칭만으로 계속 진행하고, 누락 가능성을 로그에 남긴다.

## 내 차례 판정 (팀 경유 건)

팀 요청은 팀원 아무나 처리하면 되는 건이다. 팀원이 이미 리뷰했으면 내 차례가 아니다.

```bash
GH_HOST=<host> gh api /orgs/<ORG>/teams/<TEAM_SLUG>/members --paginate --jq '.[].login'
```

**팀원이 이미 리뷰함** = `reviews[].author.login` 중 위 멤버 목록에 있고 `<reviewer>` 가 아닌 사람이 존재.

> GitHub 이 "팀원 1명이 리뷰하면 팀 요청을 자동 해제"하는 동작에 **의존하지 말 것**. 실측에서 팀 요청이 남아 있는 PR이 다수 관측됐다(리뷰어가 해당 팀 비멤버인 케이스라 반증은 아니지만, 확증도 없다). 이 스킬은 해제 여부와 무관하게 위 계산을 직접 수행한다.

## Step 0 — reconcile 절차

새 이슈를 만들기 **전에** 이미 열려 있는 리마인더 이슈를 정리한다. 안 하면 끝난 PR의 이슈가 영구히 쌓인다.

```bash
multica issue list --output json --limit 100
```

대상 이슈:
- `metadata.tracker_type == "review"`, **또는** (`tracker_type` 부재 + `title` 이 `리뷰 필요:` 로 시작 — 레거시 이슈)
- `status` 가 `backlog|todo|in_progress|in_review|blocked` 중 하나

`tracker_type == "activity"` 이슈는 `pr-activity-reminder` 소유다. 둘 다 `pr_url` 을 갖고 있으므로 이 구분 없이는 남의 이슈를 닫게 된다 — 절대 건드리지 않는다. 그 종류는 더 만들어지지 않지만 이미 열린 것들이 PR 머지까지 남아 있다.

각 이슈의 `metadata.pr_url` 로 원격 상태를 조회한다 (host 는 URL 첫 세그먼트):

```bash
GH_HOST=<host> gh pr view <pr_url> --json state,reviews,reviewRequests
```

전환 규칙 — 위에서부터 먼저 맞는 것 **하나만** 적용:

| 조건 | 전환 |
|------|------|
| `state` 가 `MERGED` 또는 `CLOSED` | `multica issue status <id> done` |
| 팀 경유만인 건인데 내 팀원이 이미 리뷰함 | `multica issue status <id> cancelled` |
| 그 외 | 변경 없음 |

"팀 경유만" 여부는 `metadata.request_via == "team"` 으로 판정한다. 레거시 이슈라 이 키가 없으면 위 `gh pr view` 결과의 `reviewRequests` 로 재계산한다.

**내가 GitHub에 리뷰를 남긴 것은 종료 조건이 아니다.** 예전엔 `reviews[].author.login` 에 내가 있으면 닫았는데, 그게 하필 카드가 쓸모 있어지는 순간이었다. 이 repo들은 `dismiss_stale_reviews=False` 라서 내가 approve한 뒤 저자가 push해도 승인이 유지되고 재요청도 안 간다. 대댓글과 새 커밋은 정확히 그 다음부터 오는데 카드는 이미 닫혀 있었다. 실측으로 열린 PR 6건이 판정 카드는 `done`인 채 활동만 쌓이고 있었다.

이제 카드 하나가 리뷰 요청부터 머지까지 산다. `pr-activity-reminder` 가 대댓글·새 커밋을 이 카드에 코멘트로 적고 `last_comment_id`·`last_commit_sha` 를 여기 둔다. 판정이 어디까지 갔는지는 상태가 아니라 `reviewed` · `review_state` · `reviewed_sha` 가 말한다.

수명이 길어져도 중복 생성 위험은 없다. dedup은 `pr_url` 만 보고 상태를 안 본다(아래 참조). 드레인도 안 끌려간다 — `nara-review-queue` 조건이 `status todo` + `reviewed != true` 인데 판정 후엔 `reviewed=true` 다.

전환한 이슈에는 코멘트도 멘션도 달지 않는다 — 조용히 닫는다.
