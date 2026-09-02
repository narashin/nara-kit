# ui-diff env profile — eval fixture (fake values)

## local
- local_url: http://localhost:3000
- local_dev_cmd: npm run dev
- local_ready_signal: "ready on http://localhost:3000"
- notes: eval fixture

## baseline
- baseline_url: https://qa.example.com
- notes: qa

## viewport
- width: 1440
- height: 900
- device_scale_factor: 2

## auth/context
- requires_login: true
- default_user_role: member
- seed_or_fixture:
- context_notes: locale=en
