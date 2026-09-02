# 코드 리뷰 리포트 — 260722-sample-feature

대상: abc1234..def5678
변경 파일: 2개
게이트: evidence ≥ E2 AND 신뢰도 ≥ 80

## 요약

🔴 Critical: 1건  🟠 Major: 1건

## 🔴 CRITICAL

[RES-001] 결제 실패 시 주문 상태가 COMPLETED로 남는다
  📍 src/order/service.ts::completeOrder | ⚖️ confirmed | E2 | 신뢰도 92 | R2
  📝 preconditions: paymentClient.capture()가 예외 발생, order 상태 PROCESSING
  💥 영향: 미결제 주문이 완료 상태로 저장
  ✏️ 수정안: 결제 성공 이후 상태 변경 또는 보상 처리 추가
  🧪 검증 방법: 결제 실패 시 상태 유지 테스트

## 🟠 MAJOR

[CON-001] parseAmount가 NaN을 그대로 반환
  📍 src/order/parse.ts::parseAmount | ⚖️ confirmed | E2 | 신뢰도 85 | R1
  💥 영향: NaN 금액이 하위 계산으로 전파

---
overrides: none
fix-ledger: n/a
fix-verification: n/a
scope-integrity: match
validation: unavailable
