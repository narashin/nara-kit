# 예제

## 예제 1: "타임존 기능 제공해야함"

### Stage 1 — Context Collection
- Intent verbatim: `"타임존 기능 제공해야함"`
- Domain scan 결과:
  - `src/users/userProfile.ts` — User 모델 발견 (timezone 필드 없음)
  - `src/i18n/locale.ts` — 로케일 처리 모듈
  - `[NOT FOUND]` 기존 타임존 actor/role
- Related modules: `userProfile`, `i18n`

### Stage 2 — Actor/Capability Decomposition
- **Who** [NEEDS_CONFIRMATION]:
  - 후보 A: end-user (자신의 프로필 설정)
  - 후보 B: admin (특정 사용자 타임존 변경)
- **What**:
  - UI 선택 (드롭다운)
  - 시스템 자동 감지 (브라우저 → 디폴트)
  - 저장된 타임존으로 시간 표시 변환
- **Why**: "사용자가 로컬 시간으로 일정을 확인할 수 있도록"

### Stage 3 — Candidate Discovery (S2)
S2 임시 후보 (1.5x 과생성):

| ID | Story | Category |
|---|---|---|
| tmp-AC-1 | 프로필에서 타임존 선택 → 저장 | Happy |
| tmp-AC-2 | 타임존 미설정 사용자 첫 로그인 → 브라우저 감지 디폴트 | Happy |
| tmp-AC-3 | 잘못된 타임존 값 입력 (예: invalid IANA) → 에러 | Sad |
| tmp-AC-4 | DST 전환 시점에 시간 표시 | Edge |
| tmp-AC-5 | 타임존 변경 후 기존 일정 표시 갱신 | Happy |
| tmp-AC-6 | 오프라인 상태에서 타임존 변경 시도 | Edge |

### Stage 4 — Selection + Detailing (S3)
S2 → S3 ratio ~0.5. AC-1 ~ AC-3 확정.

### 최종 산출물 (`docs/requirements.md`)

```markdown
---
sources: [internal-draft]
generated_by: nara-ac-draft
intent: "타임존 기능 제공해야함"
fetched_at: 2026-05-21
---

# Requirements: 타임존 기능

## Source
- Intent (verbatim): "타임존 기능 제공해야함"
- Domain hints: userProfile, i18n
- Related modules: src/users/userProfile.ts, src/i18n/locale.ts

## User Stories
- **US-1**: As an end-user, I want to set my timezone in profile settings, so that I can view schedules in my local time.
- **US-2**: As an end-user, I want automatic timezone detection on first login, so that I don't need manual setup before using the app.

## Functional Requirements
- **FR-1**: As an end-user, I want to set my timezone in profile settings, so that I can view schedules in my local time.
- **FR-2**: As an end-user, I want automatic timezone detection on first login, so that I don't need manual setup before using the app.

## Acceptance Criteria

### AC-1 (US-1, Happy)
Given 사용자가 프로필 설정 페이지에 진입했고
When 타임존 드롭다운에서 값을 선택하고 저장 버튼을 누르면
Then 선택된 타임존이 사용자 프로필에 저장되고 이후 모든 시간 표시가 해당 타임존으로 변환된다

### AC-2 (US-2, Happy)
Given 타임존이 설정되지 않은 사용자가 처음 로그인하고
When 시스템이 브라우저 타임존을 감지하면
Then 감지된 타임존이 사용자 디폴트로 적용된다 [UNVERIFIED: 감지 실패 시 fallback 값 — Open Question]

### AC-3 (US-1, Sad)
Given 사용자가 프로필 설정 페이지에 진입했고
When 유효하지 않은 타임존 값으로 저장을 시도하면
Then 저장이 거부되고 사용자에게 오류 메시지가 표시된다 [UNVERIFIED: 메시지 텍스트/코드 — Open Question]

## Open Questions
- [blocking] 브라우저 타임존 감지 실패 시 fallback (UTC? 서버 디폴트?)
- [blocking] 잘못된 입력 시 에러 메시지 형식 — UX 결정 필요

## Unknown / Needs Confirmation
- [ ] Actor 범위: admin이 타사용자 타임존 변경 가능한가? (US-3 후보)
- [ ] DST 전환 처리 방식 (자동 갱신 vs 사용자 알림)
- [ ] 타임존 저장 위치: 서버 only / 클라이언트 + 서버 동기화
- [ ] 기존 저장된 시간 데이터 (UTC 보관 가정) — 표시 시 변환만 vs 저장값 변경

## Agreed Exceptions
(없음)

## Out of Scope
- 캘린더 이벤트 자체의 타임존 (이벤트별 vs 사용자별) — v1.1 이후 검토
- 자동 DST 알림 푸시 (별도 기획)
```

### Receipt 형식

```
✅ ac-draft 완료
- Outcome: docs/requirements.md 생성 (recorded only)
- Evidence: US 2개, AC 3개 (Happy 2 / Sad 1 / Edge 0), Unknown 4개, [UNVERIFIED] 2건
- Artifact: docs/requirements.md
- Next: nara-gap 또는 nara-grill
- 비고: 외부 SoT 부재, internal-draft로 작성됨. prep 우회.
```

## 예제 2: 환각 차단 케이스 (반례)

❌ **잘못된 출력**:
```
### AC-1 (US-1, Happy)
Given 사용자가 프로필에 진입했고
When 타임존을 선택하면
Then PUT /api/v1/users/me/timezone 호출이 200 OK 반환한다
```

위반: API 경로, HTTP method, status code 모두 intent에 없는 가공 — 환각.

✅ **올바른 출력**:
```
### AC-1 (US-1, Happy)
Given 사용자가 프로필에 진입했고
When 타임존을 선택하면
Then 선택된 타임존이 사용자 프로필에 저장된다
```

또는 구체값 필요하면:
```
Then 선택된 타임존이 저장된다 [UNVERIFIED: API endpoint 미확정 — Open Question]
```
