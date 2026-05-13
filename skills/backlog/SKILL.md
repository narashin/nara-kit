---
name: backlog
description: >-
  Use when managing backlog tasks — decomposing features into implementable subtasks,
  updating task status, handling blocked items, or syncing from requirements.
  USE FOR: "backlog", "태스크 쪼개줘", "서브태스크", "decompose", "뭐가 막혔지",
  "blocked", "태스크 상태 변경", "task done", "이거 끝났어", "backlog 동기화"
  DO NOT USE FOR: "다음 뭐하지"(→now), "어디까지 했지"(→now), gap execution, code implementation
---

# backlog — Backlog.md Task Management

`backlog` CLI로 태스크 분해, 상태 관리, blocked 처리. `backlog/` 폴더 필수 — 없으면 안내 후 중단.

## Modes

| Arg | Action |
|-----|--------|
| (none) | `backlog task list` → status counts + in-progress details |
| `decompose TASK-ID` | Scoped gap → subtask creation. Load [references/decompose-flow.md](references/decompose-flow.md) |
| `done TASK-ID` | Complete task + auto-verify. Load [references/done-flow.md](references/done-flow.md) |
| `blocked TASK-ID "reason"` | `backlog task edit TASK-ID --ac "[BLOCKED: reason]"`. API/BE → suggest mock approach |
| `sync` | Diff requirements.md vs backlog → create/flag tasks (Level 1 only) |

## Routing

```
/prep complete     → "/backlog sync"
/backlog decompose → /gap --task TASK-ID (internal)
/backlog done      → auto-verify loop → code-review (on parent Done)
```

## Rules

- CLI only — never edit task .md directly
- 한국어 제목. Level 1 = 피처 단위, Level 2 = 1세션 구현 단위
- AC conventions: `[BLOCKED: reason in English]`, `[BLOCKS: TASK-ID]` — English for grep-ability
