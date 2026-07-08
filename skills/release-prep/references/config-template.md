# release-prep config template

Copy into the target repo as `.claude/release-prep.local.md` (path resolved from git root), or let the skill's bootstrap mode write it for you on first run.

No secrets live here. Committing it is recommended so the whole team shares one release config; add `*.local.md` to `.gitignore` instead if you want it personal.

```markdown
---
# Branch the release lands on (diff base)
base_branch: main
# Integration branch containing merged PRs
develop_branch: develop
# Branch recreated from develop and deployed to QA
release_branch: pre-release
# Workflow file with a workflow_dispatch trigger (filename under .github/workflows/)
deploy_workflow: deploy-qa.yml
# Dispatch inputs — keys/values must match the workflow's `workflow_dispatch.inputs` schema.
# Omit the block entirely if the workflow takes no inputs.
workflow_inputs:
  environment: qa
# Jira project key. Optional — inferred from ticket keys found in PRs when omitted.
jira_project: PROJ
# Regex for ticket keys in branch names / PR titles. Default shown; override for exotic schemes.
ticket_pattern: '[A-Z][A-Z0-9]+-\d+'
# GitHub Enterprise host, e.g. github.example.com. Omit for github.com.
gh_host:
---

Notes for humans (optional, ignored by the skill).
```

| Key | Required | Meaning |
|-----|----------|---------|
| `base_branch` | yes | Release target branch — diff base |
| `develop_branch` | yes | Integration branch — diff head, source of the release branch |
| `release_branch` | yes | Branch deleted + recreated each release, deployed to QA |
| `deploy_workflow` | yes | Workflow filename with `workflow_dispatch` |
| `workflow_inputs` | no | Key/value map passed as `-f key=value` to `gh workflow run` |
| `jira_project` | no | Jira project key; inferred from ticket keys when omitted |
| `ticket_pattern` | no | Ticket key regex; defaults to `[A-Z][A-Z0-9]+-\d+` |
| `gh_host` | no | GitHub Enterprise host for `GH_HOST` |
