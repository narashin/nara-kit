# Repository PR rules come first

The built-in title format and five sections are the **fallback**. A repository that states its own PR rules wins. Read them before drafting (SKILL.md Step 3).

## 1. Find the rules (default branch, `git show origin/<default>:<path>`)

| Rule | Where to look |
|---|---|
| PR template | `.github/pull_request_template.md`, `.github/PULL_REQUEST_TEMPLATE.md`, `docs/pull_request_template.md`, `pull_request_template.md` (any case), `.github/PULL_REQUEST_TEMPLATE/*.md` |
| Title / body instructions | `CONTRIBUTING.md`, `.github/CONTRIBUTING.md`, `AGENTS.md`, `CLAUDE.md`: a section about pull requests or PR titles |
| Recent convention | `gh pr list --state merged --limit 10 --json title` |

Several files under `.github/PULL_REQUEST_TEMPLATE/` and no instruction picks one → ask which, once. A template on the feature branch only is not the repository's rule yet; use the default branch copy.

## 2. Title precedence

1. An explicit repository instruction (CONTRIBUTING, AGENTS, CLAUDE.md)
2. A title rule written in the PR template or maintainer docs
3. The recent merged-PR convention, only when most of the last 10 share one shape
4. The built-in `<TICKET-ID> <type>: <Subject>` (SKILL.md Title Format)

Keep the ticket ID and type you derived from commits; only the shape changes. Write the subject in the language the convention uses.

## 3. Body with a template

- Keep the template's headings verbatim and in order, its HTML comments, and its checklists. Fill each heading; do not delete one. A heading with nothing to say gets one line saying so.
- Checklist boxes: tick only items you verified in this branch (a test file exists in the diff, docs changed). Leave the rest unticked. Never tick a box to look complete.
- The QA table from body-guide.md goes under the template's verification heading (Test plan, How to test, 테스트, 확인 방법). If the template has none, append `## 확인 방법 (QA 가이드)` after its last heading.
- Do not append the built-in sections the template lacks (요약, 주요 변경, 배포 시 주의사항, Linked Issues). Their content goes under the closest template heading. Put `Closes <TICKET>` at the end if no heading takes it.
- Prose language stays Korean unless the repository rules say otherwise; headings stay as the template wrote them.

## 4. No template, no instruction

Built-in format: five sections from body-guide.md, built-in title. That is the default, not an error.

## 5. Show what decided it

At the confirm step, one line: `규칙: template .github/pull_request_template.md · title CONTRIBUTING.md` (or `규칙: 내장 형식 (repo 규칙 없음)`). The user sees which source shaped the PR before it is created.

Provenance: adapted from tiger-kit `tk-pr-open` (MTGVim/tiger-kit `5e35b6a`, MIT): template detection, heading/checklist preservation, title precedence. Omitted here: evidence manifest, Mermaid visuals. The stacked-PR split lives in [stacked.md](stacked.md).
