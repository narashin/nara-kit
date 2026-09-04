# nara-wip-sweep

"In Progress"가 실제 진행을 뜻하지 않게 된 Jira 티켓을 한 번에 쓸어내 분류하고, 정리 후보를 보고한다. 티켓을 전이시키지는 않는다.

## 호출

- Claude Code: `/nara-wip-sweep`
- Codex: `$nara-wip-sweep`

인자는 선택이다: `--project <KEY>`, `--limit <N>`.

## USE FOR

- "In Progress 정리", "진행 중인데 안 하는 티켓", "wip 쓸어내"
- "티켓 상태 정리", "내 In Progress 몇 개야"
- 상태 부채가 쌓여 브리핑이 "오늘 무엇부터"를 못 답할 때

## DO NOT USE FOR

- 큐 채우기 → [nara-jira-triage](../nara-jira-triage/SKILL.md)
- 보드 상태 미러 → `jira-reconcile.sh` (git 밖 크론 스크립트)
- 요구사항 로컬화 → [nara-prep](../nara-prep/SKILL.md)
- 구현 → [nara-implement](../nara-implement/SKILL.md)

## 왜 전이하지 않나

팀이 보는 Jira에서 상태를 바꾸는 것은 "이 일을 안 한다"는 선언이다. 이 스킬은 증거와 분류만 내놓고 판정은 사람이 한다. 자동 전이가 필요하면 그건 별개 결정이고 `jira-reconcile.sh`의 `JIRA_SYNC` 게이트가 그 자리다.

## 산출물

실행한 디렉터리의 `wip-sweep.md` — 분류별 표(사실상 종료 / 리뷰 대기 / 컨테이너 / 착수 불가 / 방치 / 진행 중), 티켓당 근거와 제안 행동. 여러 프로젝트를 걸치는 내 상태 보고서라 어느 repo의 `docs/`에도 넣지 않는다.

---

- 스킬 카탈로그: [../README.md](../README.md)
- 실행 계약: [SKILL.md](SKILL.md)
