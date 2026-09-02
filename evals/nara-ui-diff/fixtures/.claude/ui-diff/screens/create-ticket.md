# screen: create-ticket — eval fixture

## Goal
Compare the "create ticket" form layout/style between QA and local.

## Entry
- start: <local_url>/tickets/new
- steps: nav → click `[data-testid="new-ticket"]` → wait modal

## Data-Context
- account: member
- flag: tickets_v2=on

## Selectors
- container: `[data-testid="ticket-form"]`
- compare-target: `.cta`, `.field-label`, `input[name="title"]`
- ready signal: `[data-testid="ticket-form"]`

## Known pitfalls
- modal open animation ~200ms — wait for ready signal before measuring

## Regression notes
- .cta background-color previously drifted after a token migration
