# Scanned files (already listed; no repo in this run)

## ls docs/test-scenarios/

```
scenarios-detailed.md
```

## docs/test-scenarios/scenarios-detailed.md

Target: `src/cart/discount.ts` (`applyCoupon(cart, coupon)`)

- **S1 (Happy)**: 유효 쿠폰(10%, 최소 주문 10,000원)을 20,000원 장바구니에 적용하면 18,000원.
- **S2 (Happy)**: 같은 쿠폰을 30,000원 장바구니에 적용하면 27,000원.
- **S3 (Error)**: 만료된 쿠폰은 에러. 장바구니 불변 여부는 적혀 있지 않음.
- 최소 주문 금액 경계(정확히 10,000원), 원 단위 반올림, 음수 금액 방지는 시나리오에 없음.
