# Finding Schema

Every reviewer outputs findings in EXACTLY this YAML shape. Free-form prose findings
are rejected at aggregation. Uniform structure enables dedup, adjudication, and
issue-level verification.

```yaml
id: BEH-001                      # <AGENT-PREFIX>-<seq> — BEH/CON/RES/TST/SEC/PRF/ARC/FUX/DBM/OPS
category: behavior-state         # agent id
severity: critical | major | minor | suggestion    # impact only — never blended with confidence
confidence: 92                   # per rubric in reviewer-contract.md
evidence_level: E2               # E0–E3, per reviewer-contract.md

location:
  path: src/order/service.ts
  symbol: completeOrder          # function/method/class — REQUIRED (lines drift, symbols don't)
  lines: 120-138                 # best-effort, informational

invariant: >-                    # what must hold true — one sentence
  결제가 실패하면 주문 상태가 COMPLETED가 되어서는 안 된다.

preconditions:                   # under which conditions the failure occurs
  - paymentClient.capture()가 예외를 발생시킨다.
  - order 상태는 PROCESSING이다.

failure_path:                    # how the code actually fails, step by step
  - 주문 상태를 먼저 COMPLETED로 변경한다.
  - 이후 paymentClient.capture()를 호출한다.
  - 예외 발생 시 상태를 복원하지 않는다.

impact: 결제되지 않은 주문이 완료 상태로 저장될 수 있다.

evidence:                        # code-level observations backing the claim
  - 상태 변경이 외부 결제 호출보다 먼저 실행된다.
  - 해당 메서드에 transaction 또는 compensation 처리가 없다.

counterevidence_checked:         # existing defenses you verified before claiming
  - OrderRepository 구현
  - 호출자 2곳
  - OrderServiceTest

suggested_fix: 결제 성공 이후 상태를 변경하거나 보상 처리를 추가한다.
fix_risk: R2                     # R0–R3 per fix-policy.md — Fixer/policy may override upward, never downward
validation:                      # how a fix would be verified
  - 결제 실패 시 주문 상태가 유지되는 테스트 추가
```

## Mandatory fields

A finding missing any of `invariant`, `preconditions`, `failure_path`,
`counterevidence_checked`, or `validation` is rejected at aggregation regardless of
confidence. These fields are what make a finding adjudicable and verifiable.

## Fingerprint (dedup & tracking key)

```
fingerprint = location.path + location.symbol + invariant
```

NOT line numbers — lines shift as fixes land. Two findings with the same fingerprint
are the same issue: merge, keep the higher evidence_level, note both reporters (but
hide reporter overlap from the Judge — see adjudication.md).
