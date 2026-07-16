# 규칙 + Anti-Patterns

## 절대 규칙

1. **Gherkin 단일 형식 강제** — v0는 rule-list, checklist, free-form prose 혼용 금지. AC는 Given/When/Then만.
2. **Why 의무** — User Story "so that <benefit>" 절 없으면 거부. 의도 자체가 얕아 작성 불가능하면 사용자에게 통지.
3. **`[UNVERIFIED]` 마크 의무** — intent/code에 근거 없는 모든 구체값 (API path, 필드명, 임계값, 에러코드, 응답 시간 등). 환각 차단 1차 방어.
4. **`Unknown / Needs Confirmation` never empty** — intents는 zero-ambiguity 아님. 비었으면 Step 2 재실행.
5. **AC-ID 안정성** — 재실행 시 기존 ID 유지. 신규 AC만 다음 번호. 삭제 시 `[DEPRECATED]` 마크 (ID 재사용 금지).
6. **구현 디테일 금지** — observable behavior만. HTTP status code, JWT, DB column type, framework 이름 등 작성 금지.
7. **FR↔AC 1:1** — prep 규약 준수. US를 verbatim 재기술해 FR로 박음. 의역/재구성 금지.
8. **사용자 확정 루프** — 출력 후 add/remove/edit 수용. 확정 시 frontmatter `confirmed_at` 기록.

## 환각 방지 체크리스트

산출 전 자가 검증:
- [ ] 모든 구체값이 intent/코드 scan 결과에서 derive 가능?
- [ ] 임계값, 에러코드, API 경로 중 추측 항목 → `[UNVERIFIED]` 마크?
- [ ] User Story actor가 코드/도메인에 실재? 가공 actor → `[NEEDS_CONFIRMATION]`?
- [ ] AC Then 절이 검증 가능한 observable behavior?

## Anti-Patterns

| Anti-pattern | Why bad | Fix |
|---|---|---|
| AC 모두 Happy path | edge case 누락 | Sad/Edge 각 최소 1개 강제 |
| User Story 없이 AC만 출력 | Why 단절, downstream 모호 | US 없이 AC 출력 금지 |
| 구체 임계값 가공 ("100ms", "최대 50개") | 환각 | `[UNVERIFIED]` 또는 `Open Questions` |
| Unknown 섹션 비움 | 발견 미달 | Step 2 재실행 의무 |
| FR을 AC와 다르게 의역 | prep 규약 위반 | US verbatim 재기술 |
| 구현 디테일 ("HTTP 200 반환", "JWT 검증") | 층위 침범 | observable behavior로 재기술 |
| AC-ID 재실행마다 재번호 | downstream 매핑 깨짐 | 기존 ID 유지, 신규만 추가 |
| Why 작성 어려워 omit | User Story 자격 미달 | 거부 — intent 보강 요청 |
| Gherkin 한 AC에 Given/When/Then 각 3줄 초과 | 복잡도 폭발 | AC 분리 |
| Scenario Outline / Examples 표 사용 | v0 범위 초과 | 단일 시나리오로 분해 |
| 도메인 actor 가공 ("super-admin", "ghost-user" 등) | 코드 근거 없음 | `[NEEDS_CONFIRMATION]` 후보 나열 |
| "성능 향상", "코드 정리"를 Why로 작성 | 사용자 가치 X | 비즈니스/사용자 benefit으로 재작성 또는 US 거부 |

## Handoff Contract

산출 후 receipt 형식 (nara-kit output-contract 상속):
- **Outcome**: `docs/requirements.md` 생성/갱신 (recorded only)
- **Evidence**: US 수, AC 수 (Happy/Sad/Edge 분포), Unknown 수, `[UNVERIFIED]` 마크 수
- **Artifact Paths**: `docs/requirements.md`
- **Next Action**: `nara-gap` 또는 `nara-grill`

prep 우회 명시: "외부 SoT 부재, internal-draft로 requirements.md 작성됨. prep 단계 건너뜀."

## Downstream Traceability

- `gap`: 같은 `requirements.md`를 읽어 갭 분석. AC-ID로 누락 추적
- `test-discover`: `## Acceptance Criteria` 섹션 우선 수집 (이미 구현됨). AC-ID로 시나리오 1:1 매핑
- `test-implement`: test-discover 시나리오 기반. AC-ID traceability 유지

## 재실행 시나리오

1. **같은 intent 재호출 + 새 정보 없음** → 기존 결과 보존 + "변경 없음" 메시지
2. **같은 intent + 새 domain hint/코드 경로** → 추가 scan, 신규 AC만 추가 (기존 ID 유지)
3. **다른 intent** → 새 feature로 처리, 기존 requirements.md와 충돌 시 사용자 확정 요청

## 외부 의존 정책

- nara-kit standalone 동작 — 외부 plugin 의존 없음
- Optional 후속: `nara-gap`, `nara-grill`
