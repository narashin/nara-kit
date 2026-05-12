# Test Discover Examples

## Example A: S2 Candidate Discovery

Input target: REST API `POST /api/orders` (creates an order with items, applies discount, returns order ID)

```
S2-001 [Happy] [backend] [Create] 정상 주문 생성 -- 유효한 상품 + 할인 -> 주문 ID 반환
S2-002 [Sad]   [backend] [Create] 빈 상품 목록으로 주문 -> 400 에러
S2-003 [Edge]  [backend] [Create] 할인율 100% 적용 시 결제 금액 0원 처리
S2-004 [Edge]  [backend] [Create] 할인율 음수값 전송 -> 서버 검증
S2-005 [Error] [backend] [Create] 존재하지 않는 상품 ID -> 404
S2-006 [Edge]  [backend] [Create] 상품 수량 0개 주문 -> 검증 에러
S2-007 [Sad]   [backend] [Create] 인증 토큰 없이 요청 -> 401
S2-008 [Edge]  [backend] [Create] 동시 주문 2건 -> 재고 차감 정합성
```

## Example B: S2->S3 Filtering

Selected (S3):
```
S3-001 <- S2-001 [Happy] 정상 주문 생성
S3-002 <- S2-002 [Sad] 빈 상품 목록
S3-003 <- S2-003 [Edge] 할인율 100%
S3-004 <- S2-008 [Edge] 동시 주문 재고 정합성
```

Excluded:
```
S2-004 할인율 음수 -> LOWER_LAYER_BETTER (입력 검증은 단위 테스트)
S2-005 없는 상품 ID -> DUPLICATE (S2-002와 검증 영역 겹침)
S2-006 수량 0 주문 -> LOWER_LAYER_BETTER (폼 검증 단위 테스트)
S2-007 인증 없이 -> OUT_OF_SCOPE (인증은 별도 미들웨어 테스트 범위)
```

S3/S2 ratio: 4/8 = 0.50

## Example C: Scenario Detailing

```markdown
#### [API-ORD-001] 유효한 상품과 할인을 포함한 주문 생성은 주문 ID를 반환하고 재고를 차감한다

**진입경로**: POST /api/orders
**실행역할**: Create
**실행독립**: 가능
**데이터 힌트**: 주문 제목 `ORD-{YYYYMMDD-HHmm}`, 테스트 상품 ID 사전 준비 필요

0. 테스트 상품 재고 수량 확인 (GET /api/products/{id})
1. -> 확인: 재고 수량 >= 1
2. POST /api/orders 요청: 상품 1개, 수량 1, 할인코드 `TEST10`
3. -> 확인: HTTP 201 응답
4. -> 확인: 응답 body에 orderId 존재
5. -> 확인: 응답 body의 totalAmount = 상품가격 x 0.9
6. GET /api/products/{id} 재호출
7. -> 확인: 재고 수량이 1 감소
```
