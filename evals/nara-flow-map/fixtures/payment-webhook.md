# payment-webhook 흐름 메모 (fixture)

placeholder 저장소 `api-server`의 결제 웹훅 처리 흐름을 코드에서 옮겨 적은 메모다. 경로와 줄 번호는 이 fixture 안에서만 쓰는 가짜 값이다.

- `api-server/src/webhook/handler.ts:18` 결제사가 `POST /webhooks/payment`로 이벤트를 보낸다. 본문은 `event_id`, `order_id`, `amount`, `status`.
- `api-server/src/webhook/handler.ts:31` 서명을 검사하고, 실패하면 401을 돌려주고 끝낸다.
- `api-server/src/webhook/handler.ts:40` `event_id`가 `processed_events` 테이블에 있으면 200을 돌려주고 끝낸다(중복 전달).
- `api-server/src/ledger/write.ts:12` 통과하면 `ledger_entries` 테이블에 한 줄을 쓴다.
- `api-server/src/ledger/write.ts:27` 같은 트랜잭션 안에서 `processed_events`에 `event_id`를 기록한다.
- `api-server/src/notify/order.ts:9` 원장 기록이 끝나면 `order-events` 큐에 `order_paid`를 넣는다.
- 큐를 누가 읽는지는 이 저장소에 없다.
