# Pipeline — 4 Stages

## Stage 1. Context Collection

**Input**: 한 줄 의도, optional domain hint/코드 경로.

**Actions**:
- Intent verbatim 캡처 — 의역/요약 금지
- 코드베이스 auto-scan:
  - 관련 모듈/디렉토리 (`grep`/file pattern 검색)
  - 기존 actor 정의 (auth roles, user model, permission enum)
  - 도메인 어휘 (intent 키워드와 코드 식별자 매칭)
- 못 찾는 항목은 `[NOT FOUND]` 마크
- 사용자에게 묻지 않음 — 수집 우선

**Output**: 내부 컨텍스트 노트 (다음 단계 입력).

## Stage 2. Actor/Capability Decomposition

**Goal**: User Story 골격 3축 분해.

**3축**:
- **Who** — actor 후보: end-user / admin / 내부 API caller / scheduler / 외부 시스템 등
- **What** — capability 후보: UI 액션 (선택, 입력) / API 호출 / 백그라운드 처리 / 데이터 변환
- **Why** — benefit 한 문장. 작성 불가능하면 **User Story 거부** (의도 자체가 너무 얕음을 사용자에게 통지)

**규칙**:
- 각 축 확정 불가 → `[NEEDS_CONFIRMATION]` 마크 + 후보 2~4개 나열
- 단일 후보로 임의 확정 금지
- Why는 비즈니스/사용자 가치만 — 기술 구현 이유 금지 ("성능 향상", "코드 정리" 등 거부)

## Stage 3. Candidate Discovery (S2)

**Goal**: 의도적 과생성으로 누락 방지.

**Actions**:
- User Story 1.5~2.5x 과생성 (S3 목표 개수 기준)
- 각 Story에 Gherkin AC 1~3개 draft
- Tag 부여:
  - Category: Happy / Sad / Edge
  - 임시 AC-ID (`tmp-AC-1`, ...)
- 환각 차단: intent/코드에 근거 없는 구체값 발견 시 인라인 `[UNVERIFIED]` 마크
  - 예: "응답 200ms 이내" — intent에 없으면 `[UNVERIFIED: 임계값 출처 불명]`
  - 예: API 엔드포인트 `/api/v2/users` — 코드 scan에 없으면 `[UNVERIFIED]`

**과생성 강제 이유**: 첫 발상에서 빠진 actor/edge case는 검토 단계에서 회수 불가. 일단 풀어내고 필터링.

## Stage 4. Selection + Detailing (S3)

**Goal**: S2 후보 → 최종 산출물.

**Actions**:
1. S2 → S3 ratio 0.4~0.6으로 필터링
2. AC-ID 확정 (`AC-1`, `AC-2`, ...) — 임시 ID에서 영구 ID로 승격
3. 각 AC Gherkin 상세화 (Given/When/Then)
4. `Unknown / Needs Confirmation` 섹션 작성 — **never empty**
5. `Open Questions` 섹션 — blocking 항목만
6. frontmatter 작성 (sources, generated_by, intent, fetched_at)
7. `docs/requirements.md` write

**비울 수 없는 섹션**:
- User Stories (≥1)
- Functional Requirements (US 1:1 대응)
- Acceptance Criteria (≥1 AC, Sad/Edge 각 ≥1)
- Unknown / Needs Confirmation (≥1 — intents zero-ambiguity 아님)

## 재실행 정책

같은 intent + 새 정보 추가로 재호출 시:
- 기존 AC-ID 유지 (downstream `test-discover` 매핑 보호)
- 신규 AC만 다음 번호 부여
- 삭제된 AC는 `[DEPRECATED]` 마크 (ID 재사용 금지)
- frontmatter `confirmed_at` 갱신
