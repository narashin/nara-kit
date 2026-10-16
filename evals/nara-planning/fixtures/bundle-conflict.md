<!-- EVAL-FAKE-DO-NOT-USE: placeholder planning bundle for nara-planning evals. Each "파일:" heading stands for one file of the bundle. -->

# 파일: docs/product/refund-approval/prd.md

---
status: drafting
slug: refund-approval
created: 2026-10-14
requirements: docs/requirements.md
---

# 환불 관리자 승인

## 커버리지

| 항목 | 구분 | 상태 | 근거·출처 | 채우는 데 필요한 것 |
|---|---|---|---|---|
| 문제와 근거 | 필수 | 확정 | 9월 부정 환불 데이터 | |
| 대상 사용자 | 필수 | 확정 | 승인 주체는 관리자라는 사용자 답 | |
| 가치 제안 | 필수 | 확정 | | |
| 목표와 KPI | 필수 | 가정 | 목표치는 공유용 가정 | 목표치 결정 |
| 범위 | 필수 | 확정 | 고액만 승인, 부분 환불 제외 | |
| 인수 기준 연결 | 필수 | 확정 | docs/requirements.md (인수 기준 5개) | |
| policy.md | 조건부 | 확정 | | |
| flows.md | 조건부 | 확정 | | |
| ia.md | 조건부 | 확정 | | |

## 문제

자동 환불 때문에 부정 환불이 그대로 지급된다. 9월 부정 판정 환불은 37건이고 그중 31건이 10만 원 이상이었다 (근거: [9월 부정 환불 판정 데이터](evidence.md#9월-부정-환불-판정-데이터)).

## 대상 사용자

외부: 환불을 요청하는 고객. 내부: 고액 환불을 승인하는 관리자.

## 가치 제안

관리자는 고액 환불이 지급되기 전에 확인할 수 있다. 고객은 고액 환불이 검토 중인지 화면에서 알 수 있다.

## 목표와 KPI

| KPI | 계산식 | 기간 | 데이터 출처 | 기준선 | 목표 | 측정 시점 |
|---|---|---|---|---|---|---|
| 부정 환불 지급액 | 부정 판정 환불 지급액 합 | 월 | 정산 판정 기록 | 9월 데이터 | [가정] 절반 | 출시 4주 후 |

## 범위

- 첫 릴리스: 10만 원 이상 환불은 관리자 승인 후 지급한다. 고객은 내 환불 목록에서 "검토 중" 상태를 본다. 관리자는 승인 대기 목록에서 승인하거나 거절한다.
- 나중: 거절 사유 템플릿.
- 하지 않음: 부분 환불.

## 결정 로그

### 승인 주체는 관리자 역할이다
<!-- id: decision-approver-is-admin -->
- 2026-10-14 · 출처: 사용자 답 ("관리자가 승인")

### 10만 원 이상만 승인을 거친다
<!-- id: decision-threshold-100k -->
- 2026-10-16 · 출처: 결정 질문 라운드에서 사용자 확인 ("9월 데이터 보니 10만 원 이상이 대부분")

### 거절하면 사유를 반드시 입력한다
<!-- id: decision-reject-reason-required -->
- 2026-10-16 · 출처: 사용자 답

## 열린 질문

- 거절됐을 때 고객에게 보여 줄 문구와 알림 방식 (이메일인지 앱 알림인지 미정)
- 승인 대기가 며칠 이상 지속되면 어떻게 할지

## 관련 문서

- [정책](policy.md) · [흐름](flows.md) · [화면 구조](ia.md) · [근거](evidence.md) · [인수 기준](../../requirements.md)

# 파일: docs/product/refund-approval/evidence.md

# 근거: 환불 관리자 승인

## 항목

### 환불은 요청 즉시 지급되고 저장되지 않는다 (코드, 2026-10-15)
<!-- id: code-refund-immediate -->
- 출처: `src/refund/refundService.ts:13-17`
- 관찰: 고객 요청 즉시 결제사 환불을 호출한다. 환불 건을 저장하지 않는다. 상태는 요청됨, 환불됨, 실패 세 가지다.

### 9월 부정 환불 판정 데이터 (데이터, 2026-10-16)
<!-- id: data-fraud-refund-sep -->
- 출처: 정산팀 제공 판정 기록 (사용자 전달)
- 관찰: 부정 판정 37건, 그중 10만 원 이상 31건.

# 파일: docs/product/refund-approval/policy.md

# 정책: 환불 관리자 승인

## 권한

| 역할 | 대상 | 행위 | 결과 | 거부일 때 보이는 것 |
|---|---|---|---|---|
| 고객 | 자기 주문의 환불 | 요청 | 허용 | |
| 고객 | 자기 환불 | 상태 보기 | 허용 | |
| 관리자 | 승인 대기 환불 | 승인, 거절 | 허용 | |
| 고객 | 승인 대기 환불 | 승인, 거절 | 거부 | 버튼이 없음 |

## 고액 환불은 관리자 승인 후 지급
<!-- id: policy-high-value-approval -->
- 10만 원 이상 환불은 "승인 대기"로 저장되고 관리자가 승인해야 지급된다. 10만 원 미만은 지금처럼 바로 지급한다.

## 거절에는 사유가 필요하다
<!-- id: policy-reject-reason -->
- 관리자가 거절할 때 사유를 입력하지 않으면 거절할 수 없다.

## 상태 전이

| 현재 상태 | 사건 | 누가 | 조건 | 다음 상태 | 실패하면 |
|---|---|---|---|---|---|
| (없음) | 환불 요청 | 고객 | 10만 원 미만 | 지급 시도 | |
| (없음) | 환불 요청 | 고객 | 10만 원 이상 | 승인 대기 | |
| 승인 대기 | 승인 | 관리자 | | 지급 시도 | |
| 승인 대기 | 거절 | 관리자 | 사유 입력 | 거절됨 | 사유 없으면 거절 불가 |
| 지급 시도 | 결제사 응답 | 시스템 | 성공 | 환불됨 | 실패 |

# 파일: docs/product/refund-approval/flows.md

# 흐름: 환불 관리자 승인

## 고객이 고액 환불을 요청한다
- 행위자: 고객 · 시작: 주문 상세에서 환불 요청
1. 고객이 10만 원 이상 주문의 환불을 요청한다.
2. 환불이 "승인 대기"로 저장되고 고객의 내 환불 목록에 "검토 중"으로 보인다.
3. 관리자가 승인하면 지급을 시도하고 결과(환불됨 또는 실패)가 목록에 보인다.
4. 관리자가 거절하면 "거절됨"으로 보인다. 고객에게 보여 줄 문구와 알림은 미정이다.

## 관리자가 승인 대기 환불을 처리한다
- 행위자: 관리자 · 시작: 어드민 환불 승인 대기 목록
1. 관리자가 대기 목록에서 환불 하나를 연다.
2. 주문 정보와 환불 금액을 보고 승인하거나 거절한다.
3. 거절하면 사유를 입력해야 한다.

# 파일: docs/product/refund-approval/ia.md

# 화면 구조: 환불 관리자 승인

## 프론트 (고객)
- 주문 상세 (기존): 환불 요청 버튼
- 내 환불 목록 (기존, 상태 표시 추가): 진입 경로 마이페이지 > 환불 내역

## 어드민 (관리자)
- 환불 승인 대기 목록 (신규): 진입 경로 어드민 > 주문 관리 > 환불 승인
- 환불 승인 상세 (신규): 목록에서 행 클릭

# 파일: docs/requirements.md

---
sources: [internal-draft]
generated_by: nara-ac-draft
product: docs/product/refund-approval/
---

# Requirements: 환불 관리자 승인

## Acceptance Criteria

### AC-1 (US-1, Happy)
Given 고객이 10만 원 이상 주문의 환불을 요청했고
When 요청이 접수되면
Then 환불은 지급되지 않고 내 환불 목록에 "검토 중"으로 표시된다

### AC-2 (US-1, Happy)
Given 고객이 10만 원 미만 주문의 환불을 요청했고
When 요청이 접수되면
Then 지금처럼 바로 지급을 시도한다

### AC-3 (US-2, Happy)
Given 관리자가 승인 대기 환불을 열었고
When 승인하면
Then 지급을 시도하고 결과가 고객 목록에 반영된다

### AC-4 (US-2, Sad)
Given 관리자가 승인 대기 환불을 열었고
When 사유 없이 거절하려 하면
Then 거절되지 않고 사유 입력을 요구받는다

### AC-5 (US-2, Happy)
Given 관리자가 사유를 입력했고
When 거절하면
Then 환불은 "거절됨"이 된다

# 파일: src/refund/refundService.ts

```ts
import { Role } from '../auth/roles';

export type RefundStatus = 'REQUESTED' | 'REFUNDED' | 'FAILED';

export interface Refund {
  id: string;
  orderId: string;
  amount: number;
  status: RefundStatus;
}

// Refunds are processed immediately after the customer requests them.
export async function requestRefund(orderId: string, amount: number, role: Role): Promise<Refund> {
  if (role !== Role.CUSTOMER) throw new Error('only customers can request refunds');
  const refund: Refund = { id: crypto.randomUUID(), orderId, amount, status: 'REQUESTED' };
  refund.status = (await payGateway.refund(orderId, amount)) ? 'REFUNDED' : 'FAILED';
  return refund;
}

declare const payGateway: { refund(orderId: string, amount: number): Promise<boolean> };
```
