# done Flow

## Decision Tree

```dot
digraph done_flow {
  "done TASK-ID" [shape=doublecircle];
  "Is Level 2 (subtask)?" [shape=diamond];
  "Mark Done" [shape=box];
  "All siblings Done?" [shape=diamond];
  "Auto: done parent" [shape=box];
  "Report remaining siblings" [shape=box];
  "Has subtasks?" [shape=diamond];
  "All subtasks Done?" [shape=diamond];
  "Reject: list remaining" [shape=box];
  "Auto: /gap --verify" [shape=box];
  "Pass 80+?" [shape=diamond];
  "Parent Done + code-review hint" [shape=doublecircle];
  "Small gap?" [shape=diamond];
  "Auto-fix + re-verify" [shape=box];
  "Create subtask + notify" [shape=box];
  "3x exceeded?" [shape=diamond];
  "Report to user" [shape=doublecircle];

  "done TASK-ID" -> "Is Level 2 (subtask)?";
  "Is Level 2 (subtask)?" -> "Mark Done" [label="yes"];
  "Mark Done" -> "All siblings Done?";
  "All siblings Done?" -> "Auto: done parent" [label="yes"];
  "All siblings Done?" -> "Report remaining siblings" [label="no"];
  "Auto: done parent" -> "Has subtasks?";

  "Is Level 2 (subtask)?" -> "Has subtasks?" [label="no (Level 1)"];
  "Has subtasks?" -> "All subtasks Done?" [label="yes"];
  "Has subtasks?" -> "Auto: /gap --verify" [label="no subtasks"];
  "All subtasks Done?" -> "Auto: /gap --verify" [label="yes"];
  "All subtasks Done?" -> "Reject: list remaining" [label="no"];

  "Auto: /gap --verify" -> "Pass 80+?";
  "Pass 80+?" -> "Parent Done + code-review hint" [label="yes"];
  "Pass 80+?" -> "Small gap?" [label="no"];
  "Small gap?" -> "Auto-fix + re-verify" [label="yes, 1-2 files"];
  "Small gap?" -> "Create subtask + notify" [label="no, needs design"];
  "Auto-fix + re-verify" -> "3x exceeded?";
  "3x exceeded?" -> "Auto: /gap --verify" [label="no"];
  "3x exceeded?" -> "Report to user" [label="yes"];
}
```

## Verify Loop Rules

- Max 3 iterations of auto-fix → re-verify
- Small gap: 1-2 files, clear fix, no design needed → auto-fix in same session
- Large gap: new feature, architecture change, blocked dependency → create new subtask
- After 3 failures: report remaining gaps to user with specifics

## Commands Used

```bash
# Mark task done
backlog task edit TASK-ID -s "Done"

# Check siblings
backlog task list -s "To Do"
backlog task list -s "In Progress"
```

## Output Format

### Subtask Done
```
TASK-{ID} 완료.
남은 서브태스크: TASK-{X}, TASK-{Y}
다음: TASK-{X} 착수 (새 세션 추천)
```

### Parent Done (after verify pass)
```
TASK-{ID} 검증 통과 (점수: {N}/100). Done 처리 완료.
다음: code-review → 마무리
```

### Verify Failed
```
TASK-{ID} 검증 미달 (점수: {N}/100).
미충족 항목:
- {gap item 1}
- {gap item 2}
{auto-fix 시도 | 서브태스크 생성됨}
```
