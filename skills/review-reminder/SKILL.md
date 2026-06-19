---
name: review-reminder
description: >-
  Find open PRs where you are a requested reviewer but have not yet reviewed, and create Multica reminder issues.
  USE FOR: "리뷰 안 한 PR", "review reminder", "PR 리뷰 미완료", "review-requested but not reviewed".
  DO NOT USE FOR: actually reviewing PRs (→ code-review), creating PRs (→ pr).
---

# review-reminder — 미리뷰 PR 리마인더

지정된 레포에서 리뷰 요청은 받았으나 아직 리뷰를 남기지 않은 PR을 찾아 Multica 이슈로 생성한다.

## 인자 (`$ARGUMENTS`)

```
review-reminder --host <GH_HOST> --repo <OWNER/REPO> --reviewer <USERNAME>
```

| 인자 | 예시 | 설명 |
|------|------|------|
| `--host` | `github.com` | GitHub 호스트 (기본: `github.com`) |
| `--repo` | `org/repo` | 대상 레포 (`OWNER/REPO`) |
| `--reviewer` | `alice` | 리뷰어 username |

인자 없으면 agent instructions에서 주입된 기본값 사용.

## 실행

```bash
GH_HOST=<host> gh pr list \
  --repo <OWNER/REPO> \
  --state open \
  --json number,title,url,reviewRequests,reviews \
  --limit 100
```

## 필터 조건

다음 조건을 **모두** 만족하는 PR만 대상:

1. `reviewRequests[].login` 에 `<reviewer>` 포함
2. `reviews[].author.login` 에 `<reviewer>` **없음**

## 출력 — 미리뷰 PR 없음

```
✅ 미리뷰 PR 없음 — 모든 리뷰 완료
```

## 출력 — 미리뷰 PR 있음

각 PR에 대해 Multica 이슈 생성:

```bash
multica issue create \
  --title "리뷰 필요: <PR 제목>" \
  --description "PR: <PR URL>\n\n리뷰 요청을 받았으나 아직 리뷰를 남기지 않은 PR입니다." \
  --priority medium \
  --output json
# → issue ID 추출 후 metadata 저장
multica issue metadata set <issue_id> --key pr_url --value "<PR URL>"
```

## Dedup 규칙

이슈 생성 전 `multica issue list` 로 기존 이슈 조회:
- title에 `리뷰 필요:` + PR URL 동일한 이슈 이미 존재 → 생성 스킵
- 존재하지 않으면 생성

## 규칙

- `GH_HOST` 환경변수로 gh CLI 라우팅 제어
- 인자 누락 시 agent instructions 기본값 사용. 그것도 없으면 오류 안내 후 중단
- `gh` CLI PATH에 존재해야 함
