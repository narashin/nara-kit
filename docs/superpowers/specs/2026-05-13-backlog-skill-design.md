# /backlog Skill Design — Backlog.md 워크플로 통합

## Summary

Backlog.md CLI를 nara-kit 워크플로에 통합하는 `/backlog` 스킬 신설.
기존 스킬(`/now`, `/prep`, `/gap`, `workflow-dev-mode`)에 최소 변경으로 연결.

## Problem

1. gap 분석이 전체 코드베이스를 읽어 토큰을 소진 → 같은 세션에서 구현 품질 저하
2. 개별 태스크 상태(done/blocked/사유) 추적 수단 없음
3. 요구사항 분해 → 구현 사이 "알아서 함" 점프 발생

## Solution: 2-Level Task + Scoped Gap

### Level 1 태스크 (로드맵 단위)
- 입력: Confluence/requirements.md
- 기준: 사용자 관점 기능 단위
- 예: "F-13: URL 자동 추출"

### Level 2 태스크 (구현 단위)
- 입력: scoped gap 결과 + 코드 구조
- 기준: 1세션 구현 가능 단위
- 예: "F-13-1: URL 추출 유틸 함수"

---

## /backlog Skill Specification

### Description (Trigger Patterns)

```yaml
name: backlog
description: >-
  Manage backlog tasks — decompose into subtasks, update status,
  check blocked items, sync from requirements.
  USE FOR: "backlog", "태스크 쪼개줘", "서브태스크", "decompose",
  "뭐가 막혔지", "blocked", "태스크 상태 변경", "task done",
  "이거 끝났어", "backlog 동기화"
  DO NOT USE FOR: "다음 뭐하지"(→now), "어디까지 했지"(→now),
  gap analysis execution, code implementation
```

### Modes

| Command | Action |
|---------|--------|
| `/backlog` (no args) | Board summary: todo/in-progress/blocked/done counts + in-progress details |
| `/backlog decompose TASK-ID` | Scoped gap → Level 2 subtask creation |
| `/backlog done TASK-ID` | Complete task. Check all subtasks Done first |
| `/backlog blocked TASK-ID "reason"` | Tag [BLOCKED: reason] in AC |
| `/backlog sync` | Sync requirements.md changes → create/update tasks |

### decompose Flow (Detail)

```
1. Read TASK-ID from backlog (title, description, AC)
2. Run /gap --task TASK-ID (internal, scoped)
   - Read only code relevant to this task's AC
   - Produce scoped gap result
3. Based on gap result, generate Level 2 subtasks:
   - Each subtask = 1 session implementable unit
   - Include AC per subtask
   - Include dependency order
4. Create subtasks via `backlog task create`
5. Set parent TASK-ID to "In Progress"
6. Output: "N subtasks created. Start with brainstorm → plan → execute"
```

### done Flow (Detail)

```
1. If TASK-ID has subtasks:
   - Check all subtasks are Done
   - If not: "Remaining: TASK-29, TASK-30. Complete these first"
2. If TASK-ID is Level 2 (subtask):
   - Mark Done via `backlog task edit`
   - Check sibling subtasks
   - If all siblings Done → auto-trigger parent done
3. If TASK-ID is Level 1 (parent) and all subtasks Done:
   - Auto-trigger /gap --verify
   - Verify loop (max 3 iterations):
     a. Pass (80+) → Mark Done → "code-review recommended"
     b. Fail (small gap, 1-2 files) → auto-fix → re-verify
     c. Fail (large gap) → create new subtask → notify user
   - After 3 fails → report to user with remaining gaps
```

### blocked Flow (Detail)

```
1. Add [BLOCKED: reason] to task AC
2. If reason contains "API" or "BE":
   - Suggest mock implementation approach
   - "Mock으로 FE 구현 진행 가능. 나중에 API 나오면 교체"
3. Update task status metadata
```

---

## Existing Skill Modifications

### /now — Minimal Change (+3 lines)

Add to output template after "최근 작업":
```
- Backlog: {in-progress task ID + title} ({subtask completion N/M})
  (omit if no backlog/ directory)
```

Collection step: add `backlog task list -s "In Progress"` to parallel collection.

### /gap — Add --task Mode (+15 lines)

New mode: `/gap --task TASK-ID`

```
1. Read TASK-ID from backlog (description + AC)
2. Derive search scope from task description
   - Identify relevant directories/files from keywords
   - Grep/Glob only within that scope
3. Check each AC item against found code
4. Output: scoped gap result (same format as gap.md but smaller)
5. Do NOT write to gap.md (transient result for decompose)
```

### /prep — Add Sync Hint (+5 lines)

After Readiness assessment, add:
```
If backlog/ directory exists in project:
  → "Backlog project detected. Run /backlog sync to update tasks from requirements"
```

### workflow-dev-mode — Update Gate Sequence (+10 lines)

Current gates:
```
SoT → discovery → gap → plan → execute → verify → review
```

Updated gates:
```
SoT → discovery → /backlog decompose → plan per subtask → execute → /backlog done → auto-verify → review
```

Add to routing table:
```
| backlog/ exists + Level 1 task selected | /backlog decompose before plan |
| subtask completed | /backlog done (triggers verify chain) |
```

---

## Full Trigger Chain

```
Phase 0 — Roadmap Collection
  /prep complete → /backlog sync (hint)
  /backlog sync → Level 1 tasks created → "/now for next step"

Phase 1 — Task Selection
  /now → shows "Backlog: TASK-8 In Progress (2/4)"
  → recommends "/backlog decompose TASK-9"

Phase 2 — Task Decomposition
  /backlog decompose TASK-8
  → /gap --task TASK-8 (auto, internal)
  → subtasks created (TASK-28~31)
  → "brainstorm → plan → execute"

Phase 3 — Implementation (1 session per subtask)
  brainstorm → plan → execute → test
  → /backlog done TASK-28
  → "Next: TASK-29 (new session recommended)"

  If blocked:
  → /backlog blocked TASK-29 "API not ready"
  → mock implementation guidance

Phase 3→4 — Auto-Verify Loop
  Last subtask Done → /backlog done TASK-8 (parent)
  → /gap --verify (auto)
  → Pass (80+): TASK-8 Done → "code-review next"
  → Fail (small): auto-fix → re-verify (max 3x)
  → Fail (large): new subtask → notify user
  → 3x exceeded: report gaps → user decides

Phase 5 — Finish
  code-review → adr (if needed) → reflect → branch finish
  (unchanged)
```

---

## Token Budget Per Phase

| Phase | Token Usage | Why OK |
|-------|-------------|--------|
| 0 (roadmap) | High (Confluence read) | One-time |
| 1 (select) | Minimal (list only) | — |
| 2 (decompose) | Medium (scoped gap) | No implementation in same session |
| 3 (implement) | Focused (narrow scope) | 1 subtask = 1 session |
| 4 (verify) | Medium (full gap) | Separate session, no impl needed |
| 5 (finish) | Normal | Unchanged |

---

## Dependencies

- **Backlog.md CLI** (v1.45.1+): must be installed and `backlog init` done in target project
- **Existing skills**: /now, /prep, /gap, workflow-dev-mode — minimal modifications
- **No new npm packages** or external dependencies

## Out of Scope

- Backlog.md MCP server integration (future enhancement)
- Cross-project backlog aggregation
- Jira/Linear bidirectional sync
- Automatic priority scoring
