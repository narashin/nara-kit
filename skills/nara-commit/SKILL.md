---
name: nara-commit
description: >-
  Analyze staged git changes and generate a conventional commit message with ticket ID prefix.
  USE FOR: "commit", "커밋 메시지", "commit message", "/nara-commit TICKET-ID", 커밋 생성.
  DO NOT USE FOR: git push, PR creation, branch management.
---

# commit — Git 커밋 메시지 생성

## Steps

1. `git diff --cached --stat`으로 staged 변경 확인. staged 파일이 없으면 유저에게 안내 후 중단.
2. `git diff --cached`로 변경 내용 분석 — 변경 의도(feat/fix/refactor 등)와 범위 파악.
3. 아래 Format 규칙에 따라 커밋 메시지 생성.
4. 복수 관심사가 섞여 있으면 커밋 분리 제안.
5. 생성한 커밋 메시지를 출력하고 종료한다 (`recorded only`). **`git commit`은 Claude가 실행하지 않는다** — 사용자가 확인 후 직접 실행한다. (output-contract + 글로벌 규칙 "NEVER auto-commit")

## Commit Message Format

```
<TICKET-ID> <type>: <Subject>
```

- `<TICKET-ID>`: 인자로 받은 값 (e.g., `/nara-commit PROJ-111`). 없으면 `NO-ISSUE`.
- `<type>`: feat | fix | docs | style | refactor | perf | test | chore | ci | revert
- `<Subject>`: 대문자 동사 시작, 현재형, 72자 이내. 기능/목적 수준으로 기술 (파일 경로 반복 금지, e.g., "Add tax calculation helper" not "Add function to utils.py").

## Examples

- `PROJ-111 feat: Add new feature`
- `OPS-999 fix: Fix ticket re-open logic`
- `NO-ISSUE refactor: Merge duplicated logics`
- `NO-ISSUE docs: Update README for setup instructions`

## Error Handling

- staged 파일 없음 → `git add`로 스테이징 먼저 안내.
- pre-commit hook 실패 → 훅 에러 메시지 표시 후 수정 유도. `--no-verify` 사용 금지.
- 커밋 메시지 72자 초과 → 축약 후 재생성.
