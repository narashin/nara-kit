# issue-body — Multica 큐 이슈 본문 템플릿

티켓당 1개 이슈. **UNASSIGNED, status To Do** 로 생성. 본문은 사람이 읽고 착수 결정하는 데 쓰고, 착수 시 metadata(`jira_key`/`repo`)를 Stage 2 agent가 읽는다.

## dev 큐 이슈 (구현 / 버그픽스)

```markdown
**Jira:** <ticket url>
**타입:** 구현 | 버그픽스 · **repo:** <host>/<owner>/<repo>
**세션그룹:** <session_group> · **PR 언어:** <ko|en>

<summary 한 줄 + description 핵심 요약>

**접근법:**
- 버그픽스: 재현 → 실패 테스트(Red) → 수정 → 회귀 테스트 → verify
- 구현: prep(AC) → gap → plan → TDD → verify

**착수:** 판단 후 Stage 2 트리거 (aoe가 <session_group> 그룹·워크트리에서 실행)
(수동: `/nara-kit:wt <KEY>` → `/nara-kit:prep <KEY>` → dev-mode)
```

## doc 큐 이슈 (기획)

```markdown
**Jira:** <ticket url>
**타입:** 기획

<summary 한 줄 + description 핵심 요약>

**접근법:** 조사 → spec 초안 → 리뷰 (publish는 사람)
**착수:** Stage 2 트리거 또는 `/nara-kit:prep <KEY>` → doc-mode
```

## 기타 / repo 매핑 없음

```markdown
**Jira:** <ticket url>
**타입:** 기타 | [UNVERIFIED: <사유>]

<summary 한 줄>

---
**착수:** 역할 agent 없음 — 직접 처리. (repo 매핑 없으면 config 보완 후 재분류)
```

## metadata (모든 큐 이슈 공통)

| key | value | 용도 |
|-----|-------|------|
| `jira_key` | `<KEY>` | dedup + Stage 2 agent가 읽음 |
| `triage_type` | 구현/버그픽스/기획/기타 | 착수 agent 라우팅 힌트 |
| `repo` | `<host>/<owner>/<repo>` | Stage 2 agent가 작업할 repo |
| `session_group` | Sandy / iris-ui / iris-api-server / nara-kit | Stage 2 aoe 라우팅 |
| `pr_language` | ko / en | Stage 2 PR 작성 언어 |
| `sub_repo` | default / fe / be | LYRIS FE/BE 구분 |
