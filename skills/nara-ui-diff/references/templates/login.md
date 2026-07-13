# ui-diff login flow — <project> (selector만, 비밀값 없음)
# 소비 repo의 .claude/ui-diff/login.md 로 bootstrap됨.

## selectors
- username: input[name="email"]
- password: input[name="password"]
- submit: button[type="submit"]
- post_login_ready: [data-testid="app-shell"]
- optional_modal_close:

## flow
1. navigate to <baseline_url or local_url>/login
2. username + password 입력 (크레덴셜은 login.local.md 또는 storageState — references/profile.md 참조)
3. submit 클릭
4. post_login_ready 대기

## blockers
- 2FA / captcha / SSO: storageState 사용 (1회 사람 로그인) — references/profile.md 크레덴셜 모델
