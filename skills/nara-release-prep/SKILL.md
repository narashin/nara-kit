---
name: nara-release-prep
description: >-
  One-shot release preparation: collect PRs merged into develop but not in the base branch,
  recreate the release branch, trigger the QA deploy workflow (workflow_dispatch), and append
  the release Fix Version to every referenced Jira ticket. Per-repo config with first-run
  bootstrap. USE FOR: "릴리즈 준비", "release prep", "release-prep", "fix version 추가",
  "pre-release 만들어", "QA 배포 준비", "/nara-release-prep 1.2.3".
  DO NOT USE FOR: PR 생성 (→ pr), 커밋 메시지 (→ commit), Jira 티켓 생성 (→ slack-to-jira),
  Jira 버전 생성 (team creates versions beforehand), production deploys.
---

# release-prep — One-Shot Release Preparation

Automates the release-prep chore chain: base↔develop diff → merged PR list → ticket keys →
release branch recreation → QA deploy dispatch → Jira Fix Version append. One command,
zero mid-run gates. All remote side effects are declared in the final receipt.

## Arguments

`<version>` — the Jira Fix Version name to apply (e.g. `1.2.3`).

- Config present + version given → full release flow.
- Config present + version missing → abort: ask for the version. No side effects.
- Config missing → Bootstrap mode (version optional; if given, release flow continues right after bootstrap).

## Config

Read `.claude/release-prep.local.md` at the repo root — resolve root via
`git rev-parse --show-toplevel`, never cwd. Schema + template:
[config-template.md](references/config-template.md).

Defaults when optional keys are absent: `ticket_pattern` = `[A-Z][A-Z0-9]+-\d+`,
`jira_project` inferred from extracted ticket keys, `gh_host` = github.com.
When `gh_host` is set, prefix every `gh` call with `GH_HOST=<gh_host>`.

## Bootstrap Mode (first run)

Entered only when the config file does not exist. Writes the config, asks the minimum:

1. Scan `.github/workflows/*.y*ml` for files containing a `workflow_dispatch` trigger.
   List candidates via AskUserQuestion → user picks `deploy_workflow`. Zero candidates →
   abort: this skill requires a workflow_dispatch deploy (report which workflows exist).
2. Parse the chosen workflow's `workflow_dispatch.inputs`. For each input ask a value
   (present `default`/`options` from the schema). No inputs → omit `workflow_inputs`.
3. Detect branches: propose `base_branch`/`develop_branch`/`release_branch` from
   `git branch -r` (prefer `main`/`master`, `develop`, `pre-release`). Confirm once.
4. Propose `jira_project` when recent branch names match `ticket_pattern` (e.g.
   `feature/PROJ-431-x` → `PROJ`). User may leave it empty (inference at runtime).
5. Write `.claude/release-prep.local.md` following
   [config-template.md](references/config-template.md). Report the path.
6. Version argument already given → continue to Release Flow step 1. Otherwise stop:
   config written, rerun with `/nara-release-prep <version>`.

## Release Flow (one-shot)

1. **Preflight** — all checks before ANY remote mutation:
   - Parse config; abort on missing required keys (point to the template).
   - Version argument present, else abort.
   - `gh auth status` succeeds (honor `gh_host`).
   - Read `deploy_workflow` file: every required `workflow_dispatch` input without a
     `default` must have a value in `workflow_inputs`, else abort listing the gaps.
   - If `jira_project` is set: `jira_get_project_versions` now — version name must exist
     (fail-fast; see Error Handling).
2. **Collect PRs** — `git fetch origin`, then:
   - `git rev-list origin/<base_branch>..origin/<develop_branch>` — the release commit set.
   - `gh pr list --state merged --base <develop_branch> --json number,title,headRefName,mergeCommit --limit 200`,
     keeping PRs whose `mergeCommit.oid` is in the release commit set. Matching on the merge
     commit SHA works for merge, squash, and rebase merge strategies alike.
   - Guard: zero PRs matched while the commit set is non-empty → stop and report the
     likely cause: `--limit` truncation (raise the limit and retry), direct pushes to
     `<develop_branch>` with no PRs this cycle (a legitimate stop — confirm with the
     human), or rewritten history.
   - Extract ticket keys with `ticket_pattern` from BOTH `headRefName` and `title`;
     union + dedup. PRs with no key go to the skipped list (they still ship, just untracked).
3. **Verify Jira version** (only if not done in preflight): infer project = most frequent
   key prefix; `jira_get_project_versions`; the version must exist. Missing → stop with
   `→ ESCALATE:` asking the team to create it. Zero side effects at this point.
   Single Jira project per repo is assumed: apply the version only to tickets whose
   prefix matches the verified project; foreign-prefix keys go to the skipped list.
   If NO ticket keys were extracted and `jira_project` is unset, stop before any
   branch op and ask for `jira_project` — the version cannot be verified.
4. **Recreate release branch**:
   - `git push origin --delete <release_branch>` — tolerate "remote ref does not exist".
   - `git push origin origin/<develop_branch>:refs/heads/<release_branch>` — no local
     checkout needed, no force flag needed after deletion.
5. **Trigger deploy** — `gh workflow run <deploy_workflow> --ref <release_branch>`
   plus `-f key=value` per `workflow_inputs` entry. Grab the run URL
   (`gh run list --workflow <deploy_workflow> --limit 1 --json url,status`). Do NOT wait
   for completion — deploys are long and Fix Version updates don't depend on the result.
6. **Apply Fix Version** — for each ticket key:
   - `jira_get_issue` (field: `fixVersions`). Nonexistent key → skip, record.
   - Target version already present → skip (idempotent).
   - Else `jira_update_issue` setting `fixVersions` = existing list + the target version.
     **Append-only: never drop versions already on the ticket.**
7. **Receipt** (output contract): PR count, tickets updated/skipped (with reasons),
   release branch ref, deploy run URL, declared side effects (branch delete/create,
   workflow dispatch, per-ticket Jira updates). Next action: QA 확인 + 배포 결과 모니터.

## Error Handling

| Situation | Action |
|-----------|--------|
| Config missing | Bootstrap mode (not an error) |
| Commit set non-empty, zero PRs matched | Stop, report cause candidates (limit truncation / direct pushes / rewritten history) |
| No ticket keys and `jira_project` unset | Stop before branch ops, ask for `jira_project` |
| Version absent from Jira | Stop BEFORE branch ops — `→ ESCALATE:` request version creation; side effects 0 |
| Required dispatch input unset | Abort in preflight, list missing inputs |
| Ticket key not found in Jira | Skip ticket, record in receipt |
| Deploy dispatch fails | Continue to Fix Version step; mark deploy as `pending escalation` in receipt |
| `gh auth` fails | Abort in preflight with the auth command to run |

## Constraints

- **Never create Jira versions** — the team creates them; this skill only verifies + applies.
- **fixVersions is append-only.** Overwriting the list is data loss on shared tickets.
- **No remote mutation before the Jira version is verified** — ordering is the safety model.
- **One repo per run.** Multi-repo release = run once per repo (each has its own config).
- Deploy completion is not awaited; the receipt links the run for the human to watch.

## Examples

`/nara-release-prep 1.2.3` (config exists)
- 37 commits in `main..develop`, 11 merged PRs matched by `mergeCommit.oid`, keys: PROJ-101 … PROJ-118 (9 unique)
- Version `1.2.3` found in PROJ → `pre-release` deleted + recreated at `origin/develop`
- `gh workflow run deploy-qa.yml --ref pre-release -f environment=qa` → run URL
- 8 tickets updated, 1 skipped (already had 1.2.3), 2 PRs had no ticket key → listed

`/nara-release-prep 1.2.3` (no config)
- Bootstrap: finds `deploy-qa.yml` + `ci.yml`; user picks `deploy-qa.yml`, sets
  `environment=qa`, confirms branches, accepts inferred `PROJ`
- Config written to `.claude/release-prep.local.md` → release flow continues unchanged

`/nara-release-prep 9.9.9` (version not in Jira)
- Preflight: `jira_get_project_versions` lacks `9.9.9`
- `→ ESCALATE: PROJ에 버전 9.9.9 없음 — 버전 생성 후 재실행. 원격 변경 0건.`
