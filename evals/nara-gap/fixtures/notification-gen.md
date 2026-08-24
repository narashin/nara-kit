# Requirements — notification delivery

## FR

- [ ] FR-1: A ticket transition MUST send a Slack notification to the assignee.
- [ ] FR-2: A ticket transition should also send an email notification.
- [ ] FR-3: The Slack message body must read `Ticket {id} moved to {state}`.
- [ ] FR-4: The notification API response must include `notification_id`.

## AC

- AC1: Given a ticket in `IN_REVIEW`, When an approver rejects it, Then the
  assignee receives a Slack notification.
- AC2: Given an expired token, When the notification API is called, Then it
  returns 401 with code `TOKEN_EXPIRED`.

# Workspace state (raw command output — no interpretation supplied)

```
$ git ls-files src/notify
src/notify/slack.ts
src/notify/api.ts
```

```
$ wc -l src/notify/slack.ts src/notify/api.ts
      64 src/notify/slack.ts
      48 src/notify/api.ts
     112 total
```

```
$ git grep -Fn "Ticket {id} moved to {state}" .
```

```
$ git grep -Fn "moved to" src/notify/slack.ts
src/notify/slack.ts:22:  const text = `Ticket ${id} is now ${state}`
```

```
$ git grep -Fn "notification_id" src/notify/api.ts
src/notify/api.ts:39:    notification_id: created.id,
```

```
$ git grep -Fn "TOKEN_EXPIRED" .
```

```
$ git grep -rln "email" src/notify
```

No `docs/gap.md` and no `docs/implementation-notes.md` in this workspace.
