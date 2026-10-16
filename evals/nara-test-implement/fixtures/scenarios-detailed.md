# docs/test-scenarios/scenarios-detailed.md

Target: `src/cart/discount.ts` (`applyCoupon(cart, coupon)`), Jest project (`package.json` has `"test": "jest"`, no existing test files).

## Domain: coupon validation
- **TC-1 (Happy)**: 유효 쿠폰(10% 할인, 최소 주문 10,000원)을 20,000원 장바구니에 적용하면 총액이 18,000원이다.
- **TC-2 (Edge)**: 장바구니 금액이 최소 주문 금액과 정확히 같으면(10,000원) 쿠폰이 적용된다.
- **TC-3 (Error)**: 만료된 쿠폰은 `CouponExpiredError`를 던지고 장바구니는 바뀌지 않는다.

## Domain: amount calculation
- **TC-4 (Edge)**: 할인액은 원 단위 내림이다(12,345원의 10% → 1,234원).
- **TC-5 (Error)**: 할인 후 금액이 음수가 되는 정액 쿠폰은 0원으로 막는다.
