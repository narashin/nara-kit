# ui-diff login flow — eval fixture (selectors only, no secrets)

## selectors
- username: input[name="email"]
- password: input[name="password"]
- submit: button[type="submit"]
- post_login_ready: [data-testid="app-shell"]
- optional_modal_close:

## flow
1. navigate to <baseline_url or local_url>/login
2. username + password 입력 (creds: login.fixture.md — eval only)
3. submit 클릭
4. post_login_ready 대기

## blockers
- none (eval fixture)
