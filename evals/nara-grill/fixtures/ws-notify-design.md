# Design note: push notifications over WebSocket (web-ui)

Status: draft, no code yet. Owner: dev. Repo: none checked out for this review.

## Goal

Replace the 30-second polling of `/api/notifications` with server push so a new
approval request shows up within 2 seconds.

## Proposal

- A gateway service holds one WebSocket per open browser tab.
- api-server publishes `notification.created` events to a queue; the gateway
  fans them out to the user's sockets.
- The client shows a toast and bumps the unread badge.

## Open points the author listed

1. Delivery: if a tab is disconnected for a few seconds, are missed events
   re-sent on reconnect (at-least-once), or simply lost until the next page load
   (at-most-once)?
2. Handshake auth: reuse the session cookie on the WebSocket upgrade, or issue a
   short-lived token from `/api/ws-token` and pass it in the first message?
3. Fallback: corporate proxies sometimes drop WebSocket upgrades. Keep the old
   30-second polling as a fallback, or show "실시간 알림을 쓸 수 없음" and stop?
4. Dedup: the client must not show the same toast twice. The dedup key design
   (event id vs. (type, entity id, timestamp)) depends on what point 1 decides:
   re-delivery makes duplicates normal, at-most-once makes them rare.

## Numbers

- 1,200 daily active users, at most 3 tabs each.
- About 40 notifications per user per day.
