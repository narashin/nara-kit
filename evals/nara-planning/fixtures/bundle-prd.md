<!-- EVAL-FAKE-DO-NOT-USE: placeholder planning bundle for nara-planning evals. Not a real plan. -->

# 파일: docs/product/refund-approval/prd.md

---
status: drafting
slug: refund-approval
created: 2026-10-14
requirements: none
---

# 환불 관리자 승인

## 커버리지

| 항목 | 구분 | 상태 | 근거·출처 | 채우는 데 필요한 것 |
|---|---|---|---|---|
| 문제와 근거 | 필수 | 가정 | 없음 | 고객 인터뷰 또는 문의 데이터 |
| 대상 사용자 | 필수 | 확정 | 승인 주체는 관리자라는 사용자 답 | |
| 가치 제안 | 필수 | 미결 | | 문제 근거 |
| 목표와 KPI | 필수 | 미결 | | KPI 계산식, 기준선 데이터, 목표치 |
| 범위 | 필수 | 미결 | | 승인 기준 금액 결정 |
| 인수 기준 연결 | 필수 | 미결 | | nara-ac-draft |
| policy.md | 조건부 | 미결 | | 역할 둘 이상, 승인 있음 |
| flows.md | 조건부 | 미결 | | |
| ia.md | 조건부 | 미결 | | |

## 문제

[가정] 자동 환불 때문에 부정 환불이 생긴다.

## 대상 사용자

외부: 환불을 요청하는 고객. 내부: 환불을 승인하는 관리자 (근거: 2026-10-14 사용자 답 "관리자가 승인") <!-- ref: decision-approver-is-admin -->.

## 결정 로그

### 승인 주체는 관리자 역할이다
<!-- id: decision-approver-is-admin -->
- 2026-10-14 · 출처: 사용자 답 ("관리자가 승인")

## 열린 질문

- 승인이 필요한 환불 기준 금액
- KPI와 목표치
