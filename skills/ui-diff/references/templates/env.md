# ui-diff env profile — <project>
# 소비 repo의 .claude/ui-diff/env.md 로 bootstrap됨. 실제 값으로 채우세요.

## local
- local_url: http://localhost:3000
- local_dev_cmd: npm run dev
- local_ready_signal: "ready on http://localhost:3000"
- notes:

## baseline
- baseline_url: https://qa.example.com
- notes: qa | staging | prod-like — 어느 환경이 비교 기준인지

## viewport
- width: 1440
- height: 900
- device_scale_factor: 2

## auth/context
- requires_login: true
- default_user_role: member
- seed_or_fixture:
- context_notes: 양쪽 런타임에 맞출 feature-flag / locale / org-selector
