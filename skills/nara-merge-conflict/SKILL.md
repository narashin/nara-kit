---
name: nara-merge-conflict
description: >-
  Resolve merge/rebase conflicts by reconstructing ours-intent vs theirs-intent per hunk, surfacing both as candidates for human decision.
  USE FOR: "머지 충돌", "merge conflict", "rebase 충돌", "충돌 해결", "resolve conflict", "conflict marker".
  DO NOT USE FOR: conflict-free PR merge (use pr), branch teardown (use superpowers:finishing-a-development-branch), general git ops.
---

# merge-conflict — 의도 기반 충돌 해결

머지/리베이스/체리픽 충돌을 hunk별로 **ours-intent vs theirs-intent를 재구성**해 후보 해결안으로 제시한다. 양쪽 다 의미있는 변경이면 사람이 결정 — AI는 후보 생성기, 판단은 사람.

## When to use

- `git merge` / `rebase` / `cherry-pick` 중 conflict marker (`<<<<<<<`) 발생
- 충돌 파일 수동 해결이 필요할 때

## Flow

1. **충돌 수집**: `git diff --name-only --diff-filter=U` → 충돌 파일. `git status`로 진행 중 작업(merge/rebase/cherry-pick) 종류 확인
2. **hunk별 intent 재구성**: 각 충돌 hunk에 대해
   - **ours-intent**: 주변 코드 + `git log`/`git blame`으로 ours 쪽이 무엇을 바꾸려 했는지 복원
   - **theirs-intent**: 같은 방식으로 theirs 쪽 의도 복원
   - 두 intent를 **후보 해결안**으로 제시 (기계적 ours/theirs 문자열 선택 아님)
3. **결정 규칙**:
   - 한쪽이 자명하게 추적 가능 (formatting-only, 명백한 rename, 한쪽만 실질 변경) → mechanical ours/theirs 적용
   - **양쪽 다 의미있는 변경** → 사람 결정 필수. 후보 제시 후 대기, 자동 선택 금지
4. **적용**: 결정된 해결안으로 hunk 편집, `<<<<<<< / ======= / >>>>>>>` 마커 완전 제거
5. **완료 검증**: typecheck / test / lint 실행 → 아래 Completion

## Destructive-op boundary (trailing status attestation)

해결 과정에서 파괴적 git op 금지. 응답 끝에 attestation 1줄 필수:

```
merge-conflict: no destructive git op (no reset --hard / clean / force-push / mass-delete / refactor scope-creep)
```

금지: `git reset --hard`, `git clean`, force-push, 대량 삭제, 충돌 범위 밖 리팩터.

## Completion (output-contract)

- typecheck/test/lint 모두 green → status `applied`
- 하나라도 실패 또는 미실행 → status `pending escalation` (green 아니면 완료 주장 금지)
- 프로젝트 check 명령을 모르면 사용자에게 확인 (추측 실행 금지)

## Rules

- ours/theirs 기계 선택은 **한쪽이 자명할 때만**. 애매하면 사람에게 넘긴다
- 충돌 해결 범위 밖 변경 금지 (scope creep — "겸사겸사 리팩터" 금지)
- PreToolUse prompt hook 아님 — NL 트리거로 직접 호출 (`/nara-merge-conflict`)
- branch finish/teardown은 별개 → `superpowers:finishing-a-development-branch`
- 충돌 원인이 잘못된 rebase 대상 등 구조 문제로 의심되면 해결 전 사용자 확인
