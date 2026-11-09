---
name: nara-pr
description: >-
  Analyze commits against the auto-detected base branch and generate a Pull Request title and body in Korean.
  Can embed local image files into the PR body.
  USE FOR: "pr", "PR 만들어", "pull request", "PR 제목", "/nara-pr", "PR에 스샷 넣어", "PR 본문에 이미지 첨부".
  DO NOT USE FOR: git commit, branch management, code review.
---

# pr — Smart PR Generator

> 출력 형식은 [nara-kit 출력 계약](../nara-now/references/output-contract.md)을 따른다. 이 본문이 다르게 정한 곳은 본문이 우선한다. 파일이 없으면(단독 설치) 이 줄은 건너뛴다.

## Steps

0. 인자가 기존 PR URL·본문 갱신 의도면 → [existing-PR 모드](references/existing-pr-mode.md). 기존 PR에 이미지만 넣는 요청도 여기로 간다.
1. base branch 자동 감지 (아래).
2. `git log $BASE..HEAD --oneline`으로 커밋 목록 수집. 리뷰 관심사가 둘 이상 직선 의존으로 이어지거나 사용자가 나눠 올리라고 하면 → [stacked](references/stacked.md)로 형태를 판정한다(줄 수 기준 없음, `single`이면 계속).
3. [repo 규칙](references/repo-rules.md)을 먼저 읽는다: 기본 브랜치 PR 템플릿, CONTRIBUTING·AGENTS·CLAUDE.md, 최근 머지 제목. 아래 형식보다 우선한다. 담당자·AI 트레일러·AI 커밋 범위는 확인된 정책으로 정한다. 모르면 묻고 작성자로 추측하지 않는다.
4. 커밋 분석 → 제목 생성 (repo 규칙 > Title Format). [body-guide.md](references/body-guide.md) Read → 본문 생성 (Korean). 템플릿이 있으면 템플릿 헤딩에 채운다.
5. naranizer 어투 변환 (프로필 없음·미설치면 스킵). 규칙: body-guide.md.
6. naranizer 다음 `nara-ko-prose`로 한국어 명확성을 수리한다 (규칙 없음·미설치면 스킵). 어휘·말투는 보존한다.
7. 화면 변경에 이미지가 없으면 승인 전에 [배포 환경·로컬 캡처](references/visual-capture.md), 구성·흐름·상태 변경이면 [archify 구조 그림](references/diagram.md)을 준비한다. 적용 규칙, 제목·본문·이미지, 담당자·트레일러·AI 커밋 범위를 보여주고 생성·업로드를 승인받는다. `gh pr create`에 승인된 담당자를 지정하고 본문 끝에 정확한 AI 트레일러 한 개를 둔다. 생성·[이미지 첨부](references/attach-images.md) 후 게시 검증을 실행한다.
8. 미기록 시간: `python3 ../nara-worklog/assets/worklog.py list` (없으면 스킵). 이 PR 티켓에 시간이 남았으면 한 줄로 `/nara-worklog`를 안내한다. Jira에는 쓰지 않는다.

## 게시 검증 (모든 게시 모드 공통)

신규·기존·이미지 전용·stacked 각 PR의 마지막 원격 변경 후 [nara-publish-verify](../nara-publish-verify/SKILL.md)를 호출한다. 확인된 호스트·담당자·트레일러·AI 커밋 full SHA를 전달한다. 미설치·정책/범위 미확정·미지원은 `unverifiable`; `fail`도 완료가 아니다. 불일치·게시 상태만 보고하며 자동 수정·재할당·커밋 재작성·push·Jira 쓰기는 금지한다. 원격 게시 없는 초안만 스킵한다.

## Base Branch Detection

우선순위: upstream > parent branch > origin/master > origin/main. Script: [references/base-branch-detection.md](references/base-branch-detection.md)

## Title Format (repo 규칙이 없을 때)
`<TICKET-ID> <primary-type>: <Subject>`
- Ticket ID: most frequent in commits, else `NO-ISSUE`
- Type priority: feat > fix > refactor > perf > chore > docs > test

## Body Sections

repo 템플릿이 없으면 섹션 5개: 요약 / 주요 변경 / 확인 방법 (QA 가이드) / 배포 시 주의사항 / Linked Issues. 템플릿이 있으면 템플릿 헤딩을 그대로 두고 QA 표만 그 검증 헤딩 아래에 넣는다. **확인 방법 필수** — 기존↔변경 후 대비 표가 본체. 상세: body-guide.md

## Examples

body-guide.md 하단 Example.

## Error Handling

- 커밋 없음 → base branch 감지 실패 가능성 안내, 수동 지정 요청.
- `gh` CLI 미설치·미인증 → 가이드 안내 후 중단.
- remote 미push → `git push -u origin <branch>` 먼저 안내.
- PR 이미 존재 / 대상 repo 미체크아웃 → existing-PR 모드 (Step 0).
