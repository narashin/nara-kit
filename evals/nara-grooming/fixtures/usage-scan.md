# Skills usage scan (already run; this is the environment for this task)

Toolkit repo: `~/src/acme-skills` (tracked in git). Installed copies under the agent skill root
point back to it, except `vendor-helper`, which came from a third-party installer.

## scripts/usage.py output

```json
{"window":{"start":"2026-03-02","days":38},"transcripts":140,"user_turns":1210,
 "totals":{"used":1,"viewed":1,"probation":1,"unused":3,"unverifiable":1},
 "skills":{
  "nara-search":{"slash":9,"tool":4,"reads":2,"status":"used","created":"2025-11-04"},
  "nara-recall":{"slash":0,"tool":0,"reads":3,"status":"viewed","created":"2025-12-10"},
  "nara-onboard":{"slash":0,"tool":0,"reads":0,"status":"probation","created":"2026-03-20"},
  "nara-sketch":{"slash":0,"tool":0,"reads":0,"status":"unused","created":"2025-10-01"},
  "nara-nightly-report":{"slash":0,"tool":0,"reads":0,"status":"unused","created":"2025-09-15"},
  "nara-lint-docs":{"slash":0,"tool":0,"reads":0,"status":"unused","created":"2025-08-22"},
  "vendor-helper":{"slash":0,"tool":0,"reads":0,"status":"unverifiable","created":null,"reason":"age_unknown"}}}
```

## skills/nara-nightly-report/SKILL.md (frontmatter)

```yaml
---
name: nara-nightly-report
description: Post the nightly build digest. Runs from the team scheduler.
metadata: { nara: { scope: multica } }
---
```

## Other runtime on this host

`~/.codex/sessions/` exists.

```
$ grep -rlE '\$nara-sketch([^A-Za-z0-9_-]|$)' ~/.codex/sessions | wc -l
0
$ grep -rlE 'skills/nara-sketch/' ~/.codex/sessions | wc -l
0
$ grep -rlE '\$nara-lint-docs([^A-Za-z0-9_-]|$)' ~/.codex/sessions | wc -l
0
$ grep -rlE 'skills/nara-lint-docs/' ~/.codex/sessions | wc -l
3
```

`skills/nara-sketch/` and `skills/nara-lint-docs/` have no scheduler mention in SKILL.md or README.
