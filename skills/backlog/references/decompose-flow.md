# decompose Flow

## Pre-check

1. Verify TASK-ID exists and is "To Do" status
2. Verify TASK-ID has no existing subtasks (avoid double decompose)
3. If already decomposed or In Progress → report and skip

## Steps

1. Set status: `backlog task edit TASK-ID -s "In Progress"`
2. Extract task title, description, AC
3. Run `/gap --task TASK-ID` (scoped gap — reads only code relevant to this task's AC)
4. From gap result, identify implementation units (each completable in 1 session)
5. Create subtasks (CLI auto-assigns TASK-N ID; title contains parent reference for traceability):

```bash
backlog task create "F-{parentNum}-{seq}: {구현 단위 한국어 제목}" \
  -d "{description with context}" \
  --ac "{acceptance criterion 1}" \
  --ac "{acceptance criterion 2}"
```

6. Add dependency tags in AC where needed: `[BLOCKED: depends on TASK-X]`, `[BLOCKS: TASK-Y]`
7. Output created subtasks with suggested execution order

## Subtask Sizing

- 1 subtask = 1 session completable
- Pure logic (utils, helpers) first → UI components → integration → API hookup
- If a subtask needs >3 files changed, split further

## Scoped Gap (/gap --task)

Internal call to `/gap` with narrowed scope:

1. Derive search scope from task description keywords
2. Grep/Glob only within relevant directories
3. Check each AC item against found code
4. Return scoped gap result (NOT written to gap.md — transient)
5. Token budget: read max 10 files, prefer symbol-level reads over full files
6. If >10 relevant files: prioritize by AC coverage, note uncovered areas as needing further decomposition

## Output Format

```
## TASK-{ID} 분해 결과

Scoped Gap: {implemented}/{total} AC items

생성된 서브태스크:
1. TASK-{N}: {title} — {1-line description}
2. TASK-{N+1}: {title} — {1-line description}
...

실행 순서: TASK-{N} → TASK-{N+1} → ...
다음: brainstorm → plan → 구현 시작
```
