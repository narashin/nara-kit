# nara-jira-triage — 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Triage your ready (To Do / Selected) and In Progress Jira tickets into per-ticket Multica issues, classified by type and routed to a repo — ready ones queued as todo, In Progress mirrored as in_progress. A separate deterministic reconcile script mirrors Jira status onto existing issues (Done→done, In Progress→in_progress). Stage 1 never runs code.

## 호출

- Claude Code: `/nara-jira-triage`
- Codex: `$nara-jira-triage`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "jira triage", "지라 트리아지", "내 티켓 큐", "assignee 자동 분류", "완료 티켓 큐 정리", "진행중 티켓 반영", Multica Jira autopilot.
- **DO NOT USE FOR:** 티켓 생성 (→ slack-to-jira), 버그 원인 분석 (→ /nara-incident).

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
