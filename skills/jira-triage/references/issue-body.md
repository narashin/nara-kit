# issue-body — Multica 큐 이슈 본문 템플릿

티켓당 1개 이슈. **UNASSIGNED, status To Do** 로 생성. 본문은 사람이 읽고 착수 결정하는 데 쓰고, 착수 시 metadata(`jira_key`/`repo`)를 Stage 2 agent가 읽는다.

## dev 큐 이슈 (구현 / 버그픽스)

```markdown
**Jira:** <ticket url>
**타입:** 구현 | 버그픽스 · **repo:** <host>/<owner>/<repo>

<summary 한 줄 + description 핵심 요약>

---
**착수:** 이 이슈를 **Dev agent** 에 assign + status In Progress
→ Dev agent가 repo에서 dev-mode 실행 (wt→prep→gap→TDD→verify) → PR 생성 후 인계
(Dev agent 미구축 단계에선 직접: `/nara-kit:wt <KEY>` → `/nara-kit:prep <KEY>` → dev-mode)
```

## doc 큐 이슈 (기획)

```markdown
**Jira:** <ticket url>
**타입:** 기획

<summary 한 줄 + description 핵심 요약>

---
**착수:** 이 이슈를 **Planner agent** 에 assign + status In Progress
→ Planner agent가 doc-mode 실행 (clarify→prep→spec→publish) → 산출물 인계
(Planner agent 미구축 단계에선 직접: `/nara-kit:prep <KEY>` → doc-mode)
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
