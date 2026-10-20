---
name: nara-explain
description: >-
  Generate shareable explanations of code, features, projects, or PRs tailored to a specific audience.
  USE FOR: "explain", "설명해줘", "explain to PM", "발표 자료", "온보딩 문서", "이 PR 뭐 바꿨는지 설명해줘", "이 커밋 설명", "diff 설명".
  DO NOT USE FOR: own study notes (use nara-eli5-note), code review, documentation generation, a single repo question answered with path:line evidence (use nara-ask-repo).
---

# Explain

> 출력 형식은 [nara-kit 출력 계약](../nara-now/references/output-contract.md)을 따른다. 이 본문이 다르게 정한 곳은 본문이 우선한다. 파일이 없으면(단독 설치) 이 줄은 건너뛴다.

Generate shareable explanations for others. Unlike `nara-eli5-note` (a study note the user keeps for their own learning), this skill produces content the user delivers to a target audience.

## Step 1: Identify audience and scope

Infer from user message. If not stated, ask.

| Audience | Depth |
|----------|-------|
| Tech peer (팀원, 리뷰어) | Implementation details + design rationale |
| New member (신규, 온보딩) | Project context + file map + entry points |
| Non-tech (PM, 기획자) | Feature purpose + user impact, no code |
| External (발표, 컨퍼런스) | Problem background + approach + results |

| Scope | Strategy |
|-------|----------|
| Project | CLAUDE.md/AGENTS.md/README -> directory structure -> key files |
| Feature | Components/services/routes + data flow |
| Method | Function body + call context + I/O |
| Change (PR, branch, commit, range, working tree) | One self-contained HTML file: [change-html](references/change-html.md) |

## Step 2: Explore code

Read code before explaining — no guessing. If nothing found, report "no results" and stop.

## Step 3: Generate explanation

Use audience-matched format. Default to Tech peer if audience not specified.

- **Brief mode**: when user says "짧게", "슬랙에 올릴", or "한 문단" — max 5 bullet points.
- **Change scope**: HTML file at `docs/explain/<target>.html`, built from the template and passed through `assets/check_explain.py` before delivery. Markdown only when asked ("md로", "마크다운") or in Brief mode.
- **Other scopes**: Markdown document. Save to `docs/explain-<target>.md` when it runs past about 40 lines or the user asks for a file. `<target>` is the short SHA, `pr-<N>`, or the feature name in kebab-case.
- **Reply**: when a file was written, the reply is a receipt (path, pinned `base..head` for changes, checker result, what was not verified), not the document again.

## Rules

- Only state facts verified from code. Mark uncertain content `[UNVERIFIED]`. Facts taken from docs (CHANGELOG, ADR, README) are allowed when cited as such.
- Non-tech audience: no code snippets.
- Change scope: cite each substantive claim as `path:line` (head lines; deleted code as `base:path:line`).

**Load** [references/change-html.md](references/change-html.md) for change scope. **Load** [references/output-formats.md](references/output-formats.md) for the other audience templates (Tech Peer / New Member / Non-tech / External / Brief) and the Markdown change layout used only when Markdown is requested.
