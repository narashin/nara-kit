# Phase 3: Routing — Core + Conditional Reviewers

Not every change needs every lens. 4 core reviewers always run; conditional
reviewers run only when their trigger matches the manifest + diff content.

## Core (always run)

| Agent | Responsibility |
|---|---|
| [behavior-state](agents/behavior-state.md) | 비즈니스 로직, 상태 전이, 경계값, 순서 의존성, 이전 동작과의 차이 |
| [contracts-compatibility](agents/contracts-compatibility.md) | 타입, nullability, API·DTO·serialization 계약, 하위 호환성 |
| [resilience-data-integrity](agents/resilience-data-integrity.md) | 예외, retry, timeout, transaction, idempotency, race, 데이터 정합성 |
| [tests-regression](agents/tests-regression.md) | 변경 동작의 테스트 충분성, 잘못된 assertion, 누락된 회귀 테스트, flaky |

## Conditional (trigger-matched)

| Agent | Run when the diff touches |
|---|---|
| [security-privacy](agents/security-privacy.md) | 인증·인가, 외부 입력, 파일·네트워크·SQL, secret, 개인정보, dependency manifest |
| [performance-resources](agents/performance-resources.md) | 반복문 내 I/O, DB query, 대량 처리, hot path(startup/request/render), React render, 메모리·connection 관리 |
| [architecture-reuse](agents/architecture-reuse.md) | 새 모듈·추상화·dependency 추가, 여러 레이어 동시 변경, 공통 코드 중복 |
| [frontend-ux-a11y](agents/frontend-ux-a11y.md) | `*.tsx` `*.jsx` `*.css` `*.scss`, `components/`, `pages/`, styles |
| [database-migration](agents/database-migration.md) | schema, entity, repository, migration, query |
| [operations-config](agents/operations-config.md) | config, logging, metrics, Dockerfile/Helm/CI, feature flag, env, rollback, deployment docs |

Routing decisions go in the report header: which conditional agents ran and which
triggers fired. When in doubt on a trigger, run the agent — false-positive routing
costs tokens; false-negative routing costs coverage.

## Launch rules

- Launch all selected reviewers concurrently via the Agent tool in a single message.
- Each reviewer prompt = [reviewer-contract](reviewer-contract.md)
  + its own `agents/<name>.md` + relevant [stack-specific](stack-specific.md) section
  + project override block (if loaded) + manifest + diff + context map.
- Do NOT inject other agents' checklists or any shared cross-cutting checklist —
  orthogonality is the point. The only shared text is the reviewer contract.
- `--focus=<agent>` runs exactly that reviewer (legacy aliases in [scope](scope.md)).
