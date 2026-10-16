# Memory directory (already listed; no repo in this run)

Path: `~/.claude/projects/-work-web-ui/memory/` (outside any git repo)

## MEMORY.md

```
- [Commit style](feedback_commit_style.md) — 커밋 제목은 영어, 티켓 접두사
- [Deploy freeze](project_deploy_freeze.md) — 금요일 배포 금지
- [Old review skill](reference_review_skill.md) — 리뷰는 /code-review 로
```

## scripts/audit.sh output (one line per file)

```json
{"file":"feedback_commit_style.md","score":0,"signals":[],"label":"healthy"}
{"file":"project_deploy_freeze.md","score":2,"signals":["age_days","ref_validity"],"details":{"age_days":140,"validity_pct":0},"label":"suspect"}
{"file":"reference_review_skill.md","score":2,"signals":["age_days","skill_ref_broken"],"details":{"age_days":120,"skill_refs_broken":["/code-review"]},"label":"suspect"}
```

## project_deploy_freeze.md

```
---
name: deploy-freeze
metadata: { type: project, verified_at: 2026-06-01, ref_paths: [ops/deploy-calendar.md] }
---
금요일에는 배포하지 않는다. 근거: ops/deploy-calendar.md
```

## reference_review_skill.md

```
---
name: review-skill
metadata: { type: reference, verified_at: 2026-06-20, ref_paths: [] }
---
코드 리뷰는 `/code-review` 를 쓴다.
```

Installed skills now include `/nara-code-review` (no `/code-review`). `ops/deploy-calendar.md` does not exist in the repo.
