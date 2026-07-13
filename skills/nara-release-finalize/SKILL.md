---
name: nara-release-finalize
description: >-
  Finalize a release after QA passes on the pre-release branch: open (or detect) the merge PR
  into the base branch with drafted release notes, then — once that PR is merged — tag the merge
  commit and push it (which triggers production deploy) behind an explicit confirmation gate.
  One command, re-run as-is; it auto-detects the stage from PR state. Approval and merge always
  stay human-only. USE FOR: "release finalize", "release-finalize", "pre-release main 머지",
  "머지 PR 열어", "release 태그", "release note 작성", "release@v 태그",
  "/nara-release-finalize 1.5.0". DO NOT USE FOR: QA 배포 준비 (→ release-prep), PR
  approve/merge 실행 자체 (사람이 GitHub에서 수행), 일반 feature PR 생성 (→ pr), 커밋 메시지 (→ commit).
---

# release-finalize — Merge-PR + Tag + Release Note, Gated at Prod Trigger

Picks up where `release-prep` leaves off: QA already passed on the release branch. Automates
the two mechanical halves (merge-PR open, release note draft, tag + `gh release create`) and
hard-gates the one step that fires production deploy (tag push). Never touches PR
approval/merge — those happen in GitHub, by a human.

## Arguments

`<version>` — e.g. `1.5.0`. Used to build the tag (`<tag_prefix><version>`) and the PR/release
title.

## Config

Read `.claude/release-finalize.local.md` (resolve root via `git rev-parse --show-toplevel`).
Schema + template: [config-template.md](references/config-template.md).

## Bootstrap Mode (first run)

Entered only when the config file does not exist.

1. If `.claude/release-prep.local.md` exists, read `base_branch`/`release_branch`/`develop_branch`/
   `gh_host` from it and propose reusing them (confirm once) — do not ask the user to redefine
   branches already on record. Otherwise ask for `base_branch`/`release_branch` the same way
   `release-prep` bootstrap does (propose from `git branch -r`).
2. Ask `tag_prefix` (default `release@v`).
3. Detect the production trigger mode: scan `.github/workflows/*.y*ml` for a file with an
   `on.push.tags` trigger. Found → propose `production_deploy_trigger: tag_push_auto` with that
   filename (informational only, not dispatched by this skill). Not found → list
   `workflow_dispatch` candidates via AskUserQuestion; user picks one → `workflow_dispatch` mode,
   then ask its required inputs (a `${TAG}` placeholder is resolved to the pushed tag at
   dispatch time).
4. Write `.claude/release-finalize.local.md`. Report the path. Version argument already given →
   continue to Release Flow. Otherwise stop: config written, rerun with
   `/nara-release-finalize <version>`.

## Release Flow (one command, two stages by PR state)

1. **Preflight** — before any remote mutation: parse config (abort on missing keys, point to
   template); version argument present (else abort); `gh auth status` (honor `gh_host`);
   `origin/<release_branch>` exists.
2. **Detect stage** — `gh pr list --head <release_branch> --base <base_branch> --state all --json number,state,mergeCommit,url,body --limit 5`, take the most recent:
   - **No PR** → Stage A.
   - **PR open** → report URL + state, zero side effects, stop. Next: 승인/머지 대기.
   - **PR merged** → Stage B.
3. **Stage A — open merge PR**:
   - Draft the release note: if `develop_branch` is known, reuse `release-prep`'s matching
     algorithm (`git rev-list origin/<base_branch>..origin/<release_branch>`, then
     `gh pr list --state merged --base <develop_branch> --json number,title,headRefName,mergeCommit`,
     keep PRs whose `mergeCommit.oid` is in the commit set) to build a ticket/PR table. Unknown
     `develop_branch` → fall back to `git log origin/<base_branch>..origin/<release_branch> --oneline`
     as a flat commit list.
   - `gh pr create --base <base_branch> --head <release_branch> --title "Release v<version>" --body <drafted note>`.
   - Receipt, stop. Next: 승인 + 머지 대기 — 머지 완료 후 동일 커맨드 재실행.
4. **Stage B — tag + release**:
   - Tag = `<tag_prefix><version>`. `git ls-remote --tags origin <tag>` already exists → stop,
     report the existing tag + `gh release view <tag>` URL, zero side effects (idempotent rerun).
   - `git merge-base --is-ancestor <PR mergeCommit.oid> origin/<base_branch>` — guard against
     stale PR data before trusting the commit.
   - **Hard confirmation gate** (stays in normal register regardless of response style — see
     output contract §4, irreversible-action exception): state the tag name and that pushing it
     triggers production deploy (name the workflow from config); wait for explicit yes.
   - On confirm only: `git tag <tag> <mergeCommit.oid>` → `git push origin <tag>` →
     `gh release create <tag> --title "v<version>" --notes <PR body fetched in step 2>`. If
     `production_deploy_trigger: workflow_dispatch`, also `gh workflow run <production_deploy_workflow> --ref <tag>`
     with `workflow_inputs` (substituting `${TAG}` → the tag) as part of the same confirmed action.
   - Receipt: tag, release URL, dispatch run URL if applicable, declared side effects. Next:
     production 배포 상태 모니터.

## Constraints

- **Never run `gh pr merge` or `gh pr review --approve`.** Approval and merge are human-only;
  this skill only detects the resulting state.
- **Tag creation + push always requires the explicit confirmation in Stage B** — no config flag
  bypasses it, because pushing the tag is the production deploy trigger.
- **Idempotent by construction** — rerunning after the tag already exists changes nothing.
- **One repo per run**, same as `release-prep`.

## Error Handling

| Situation | Action |
|-----------|--------|
| Config missing | Bootstrap mode (not an error) |
| No merge PR yet | Stage A: create it |
| Merge PR still open | Report + stop, zero side effects |
| Tag already exists remotely | Stop, report existing release, zero side effects |
| PR `mergeCommit.oid` not an ancestor of `base_branch` | Stop — stale PR data, ask user to refresh |
| User declines the confirmation gate | Stop, zero side effects, no partial tag/push |
| `production_deploy_trigger: workflow_dispatch` dispatch fails | Tag/release already pushed — mark deploy dispatch `pending escalation` in receipt |
| `gh auth` fails | Abort in preflight with the auth command to run |

## Examples

`/nara-release-finalize 1.5.0` (no merge PR yet)
- Stage A: PR #82 opened `pre-release → main`, body = 10-PR/ticket table (reused from
  `develop_branch` match). Next: 승인 + 머지 대기.

`/nara-release-finalize 1.5.0` (PR #82 now merged)
- Stage B: tag `release@v1.5.0` not found remotely → confirm gate shown, naming
  `production-deploy.yml` (tag-push trigger) → user confirms → tag pushed, `gh release create`
  done, run URL reported.

`/nara-release-finalize 1.5.0` (rerun after Stage B already completed)
- Tag `release@v1.5.0` already exists → idempotent stop, existing release URL reported.
