# Phases 1–2: Collect Changes & Gather Context

## Phase 1: Collect Changes

```bash
git diff HEAD~1 --stat
git diff HEAD~1
git diff HEAD~1 --name-only
git log HEAD~1..HEAD --pretty=format:"%H %s"
```

If staged changes exist, use `git diff HEAD` instead.
If no git changes found, review files the user mentioned or files edited earlier in this conversation.

**If `$ARGUMENTS` is `help` or `--help`, skip all phases and print the following usage guide in Korean, then stop:**

```
🔍 /code-review — 5-Agent Iterative Code Review & Auto-Fix

사용법:
  /code-review                    최근 1커밋 리뷰 + 자동 수정 (기본)
  /code-review 3                  최근 3커밋 리뷰
  /code-review main               main 브랜치 대비 리뷰
  /code-review help               이 도움말 출력

옵션:
  --report-only                   수정 없이 리포트만 출력
  --show-all                      신뢰도 필터 없이 전체 이슈 출력
  --threshold=N                   신뢰도 기준 변경 (기본: 80)
  --max-rounds=N                  리뷰-수정 반복 횟수 (기본: 3, 최대: 5)
  --focus=<agent>                 특정 에이전트만 실행
  --no-save                       파일 저장 없이 콘솔 출력만

에이전트 목록 (--focus에 사용):
  logic                           로직 오류 & 엣지 케이스
  type-safety                     타입 안전성 & 런타임 에러
  error-handling                  에러 핸들링 & ACID & 복원력
  architecture                    아키텍처 & 호환성 & 코드 재활용
  security-performance            보안 & 성능

출력:
  리포트는 ./docs/review/YYMMDD-<설명>.md 로 자동 저장됨
  --no-save로 저장 없이 콘솔만 출력 가능

조합 예시:
  /code-review --report-only --show-all       전체 이슈 리포트만 (수정 없음)
  /code-review 5 --threshold=60               최근 5커밋, 낮은 기준으로 폭넓게
  /code-review main --focus=error-handling    main 대비 에러 핸들링만 집중 리뷰
  /code-review --max-rounds=5                 최대 5라운드 반복으로 꼼꼼하게
  /code-review --no-save                      파일 저장 없이 빠른 리뷰
```

---

### Argument Parsing

- Empty `$ARGUMENTS`: `HEAD~1` (last 1 commit)
- Number: `HEAD~N` (last N commits)
- Branch name: `main..HEAD` etc.
- `--show-all`: show all findings regardless of confidence
- `--threshold=N`: change confidence threshold (default 80)
- `--focus=<agent>`: run only a specific agent
- `--report-only`: report only, no auto-fix
- `--max-rounds=N`: max review-fix iterations (default 3, hard cap 5)
- `--no-save`: skip saving report to file, console output only

## Phase 2: Gather Context

For each changed file:
1. Read full file content (diff alone is insufficient)
2. Check imported modules and type definitions
3. Read project CLAUDE.md and .claude/rules/ if present
4. Check related test files
5. **Search for reusable existing code** — scan utility directories, shared modules, and adjacent files with `grep -r`
6. Detect tech stack, then read the relevant section from `references/stack-specific.md`
7. **Design spec check (conditional)**: If changed files include `components/`, `pages/`, `styles/`, or `*.tsx`/`*.css`/`*.scss`, check for `DESIGN.md` at project root. If present, read its YAML frontmatter (colors, typography, rounded, spacing tokens) and the Do's/Don'ts section. Pass these to Agent 4 (architecture) as design context. Skip entirely if no FE files changed or no DESIGN.md exists.
