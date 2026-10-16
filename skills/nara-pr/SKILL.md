---
name: nara-pr
description: >-
  Analyze commits against the auto-detected base branch and generate a Pull Request title and body in Korean.
  USE FOR: "pr", "PR 만들어", "pull request", "PR 제목", "/nara-pr".
  DO NOT USE FOR: git commit, branch management, code review.
---

# pr — Smart PR Generator

> 출력 형식은 [nara-kit 출력 계약](../nara-now/references/output-contract.md)을 따른다. 이 본문이 다르게 정한 곳은 본문이 우선한다. 파일이 없으면(단독 설치) 이 줄은 건너뛴다.

## Steps

0. 인자가 기존 PR URL·본문 갱신 의도면 → [existing-PR 모드](references/existing-pr-mode.md). 1~8은 신규 생성.
1. 아래 스크립트로 base branch 자동 감지.
2. `git log $BASE..HEAD --oneline`으로 커밋 목록 수집.
3. **repo의 PR 규칙을 먼저 읽는다** ([repo-rules.md](references/repo-rules.md)): 기본 브랜치의 PR 템플릿, CONTRIBUTING·AGENTS·CLAUDE.md의 PR 지침, 최근 머지된 PR 제목. 규칙이 있으면 그것이 이기고, 아래 Title Format·5섹션은 규칙이 없을 때의 기본값이다.
4. 커밋 분석 → 제목 생성 (repo 규칙 > Title Format). [body-guide.md](references/body-guide.md) Read → 본문 생성 (Korean). 템플릿이 있으면 템플릿 헤딩에 채운다.
5. naranizer post-pass 어투 변환 (프로필 없음·미설치면 스킵). 규칙: body-guide.md.
6. `nara-ko-prose` repair post-pass — 한국어 명확성 수리 (규칙 원문 없음·미설치면 스킵). naranizer **다음**에 실행하며, 어휘·말투를 건드리지 않으므로 5의 결과를 되돌리지 않는다.
7. `gh pr create` 제안, 유저 확인 후 실행. 확인 화면에 어떤 규칙이 제목·본문을 정했는지 한 줄 (`규칙: template <path> · title <source>` 또는 `규칙: 내장 형식`).
8. 미기록 작업시간 알림 — `python3 ../nara-worklog/assets/worklog.py list` 실행 (스크립트 없으면 이 스텝 스킵). 이 PR의 티켓에 미기록 시간이 있으면 **한 줄만** 알린다: `미기록 작업시간 3h 12m (2일) — /nara-worklog`. 여기서 Jira에 쓰지 않는다 — worklog 쓰기는 승인 게이트가 있는 별도 스킬 소관이다.

## Base Branch Detection

우선순위: upstream > parent branch > origin/master > origin/main. Script: [references/base-branch-detection.md](references/base-branch-detection.md)

## Title Format (repo 규칙이 없을 때)
`<TICKET-ID> <primary-type>: <Subject>`
- Ticket ID: most frequent in commits, else `NO-ISSUE`
- Type priority: feat > fix > refactor > perf > chore > docs > test

## Body Sections

repo 템플릿이 없으면 섹션 5개: 요약 / 주요 변경 / 확인 방법 (QA 가이드) / 배포 시 주의사항 / Linked Issues. 템플릿이 있으면 템플릿 헤딩을 그대로 두고 QA 표만 그 검증 헤딩 아래에 넣는다. **확인 방법 필수** — 기존↔변경 후 대비 표가 본체. 상세: body-guide.md

## Examples

예시 제목/본문: body-guide.md 하단 Example.

## Error Handling

- 커밋 없음 → base branch 감지 실패 가능성 안내, 수동 지정 요청.
- `gh` CLI 미설치·미인증 → 가이드 안내 후 중단.
- remote 미push → `git push -u origin <branch>` 먼저 안내.
- PR 이미 존재 / 대상 repo 미체크아웃 → existing-PR 모드 (Step 0).
