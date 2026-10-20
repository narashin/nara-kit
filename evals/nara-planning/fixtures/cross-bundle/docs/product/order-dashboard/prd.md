---
status: drafting
slug: order-dashboard
created: 2026-10-01
requirements: docs/product/order-dashboard/requirements.md
---

<!-- EVAL-FAKE-DO-NOT-USE: placeholder planning bundle for nara-planning evals. -->

# 주문 현황 대시보드

## 커버리지

| 항목 | 구분 | 상태 | 근거·출처 | 채우는 데 필요한 것 |
|---|---|---|---|---|
| 문제와 근거 | 필수 | 확정 | 운영팀 인터뷰 2건 | |
| 대상 사용자 | 필수 | 확정 | 운영 담당자 | |
| 범위 | 필수 | 확정 | 상태별 주문 수와 그 목록으로 가는 길 | |
| 인수 기준 연결 | 필수 | 확정 | requirements.md (인수 기준 2개) | |

## 결정 로그

### 상태별 주문 수를 누르면 그 상태로 좁힌 주문 검색으로 간다
<!-- id: decision-count-to-search -->
- 날짜: 2026-10-01
- 출처: 사용자 답 ("숫자 누르면 그 주문들이 바로 나와야 해")
- 줄의 숫자는 그 상태의 주문 수임. 누르면 주문 검색 화면이 상태 필터로 좁혀진 채 열리고, 결과 건수가 누른 숫자와 같아야 함
