---
name: explain
description: >-
  Generate shareable explanations of code, features, projects, or PRs tailored to a specific audience.
  USE FOR: "explain", "설명해줘", "explain to PM", "발표 자료", "온보딩 문서".
  DO NOT USE FOR: learning-focused explanations (use explain-like-senior), code review, documentation generation.
---

# Explain

Generate shareable explanations for others. Unlike `explain-like-senior` (learning-focused), this skill produces content the user delivers to a target audience.

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
| Project | CLAUDE.md/README -> directory structure -> key files |
| Feature | Components/services/routes + data flow |
| Method | Function body + call context + I/O |
| PR | Changed files + key diff + rationale |

## Step 2: Explore code

Read code before explaining — no guessing. If nothing found, report "no results" and stop.

## Step 3: Generate explanation

Use audience-matched format. Default to Tech peer if audience not specified.

- **Brief mode**: when user says "짧게", "슬랙에 올릴", or "한 문단" — max 5 bullet points.
- **Default**: Markdown document. Save to `docs/explain-{scope}.md` if long.

## Rules

- Only state facts verified from code. Mark uncertain content `[UNVERIFIED]`.
- Non-tech audience: no code snippets.

**Load** [references/output-formats.md](references/output-formats.md) for audience-specific templates (Tech Peer / New Member / Non-tech / External / Brief).
