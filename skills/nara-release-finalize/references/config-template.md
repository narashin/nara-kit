# release-finalize config template

Copy into the target repo as `.claude/release-finalize.local.md` (path resolved from git root),
or let the skill's bootstrap mode write it for you on first run.

No secrets live here. Committing it is recommended so the whole team shares one config.

```markdown
---
# Branch the merge PR targets (usually the same as release-prep's base_branch)
base_branch: main
# Branch already QA-verified, source of the merge PR (usually release-prep's release_branch)
release_branch: pre-release
# Optional — integration branch used to build the structured PR/ticket release note table.
# Omit to fall back to a flat commit-log note.
develop_branch: develop
# Prefix used to build the tag from the version argument, e.g. 1.5.0 -> release@v1.5.0
tag_prefix: 'release@v'
# How production deploy is triggered once the tag is pushed:
#   tag_push_auto      - a workflow already listens on `on.push.tags`; this skill only tags+pushes
#   workflow_dispatch  - this skill also dispatches a workflow after the tag push (same confirm gate)
production_deploy_trigger: tag_push_auto
# Required only when production_deploy_trigger is workflow_dispatch.
production_deploy_workflow: production-deploy.yml
# Dispatch inputs for workflow_dispatch mode. ${TAG} resolves to the pushed tag at dispatch time.
# Omit the block entirely if the workflow takes no inputs or trigger mode is tag_push_auto.
workflow_inputs:
  tag: ${TAG}
# GitHub Enterprise host, e.g. github.example.com. Omit for github.com.
gh_host:
---

Notes for humans (optional, ignored by the skill).
```

| Key | Required | Meaning |
|-----|----------|---------|
| `base_branch` | yes | Merge PR target — usually shared with `release-prep` |
| `release_branch` | yes | Merge PR source — the QA-verified branch |
| `develop_branch` | no | Enables the structured PR/ticket release note table; omit for a flat commit list |
| `tag_prefix` | no | Default `release@v`; combined with the version argument to build the tag |
| `production_deploy_trigger` | yes | `tag_push_auto` or `workflow_dispatch` |
| `production_deploy_workflow` | only if `workflow_dispatch` | Workflow filename dispatched after tag push |
| `workflow_inputs` | no | Key/value map passed as `-f key=value`; `${TAG}` resolves to the pushed tag |
| `gh_host` | no | GitHub Enterprise host for `GH_HOST` |
