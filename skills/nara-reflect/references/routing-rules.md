# reflect — 타깃 충돌 tiebreaker + 실패 처리

본문(`SKILL.md`)에서 분리한 조건부 규칙. **충돌이 났을 때**, **실패했을 때**만 필요하다.
매 세션 발동하는 계약(🔴 CHECKPOINT preview, dual-store, 추천 lane 금지어)은 본문에 남아 있다 — 여기로 옮기지 말 것.

## 타깃 충돌 tiebreaker

한 학습이 2개 lane에 걸칠 때:

- **미래 세션/팀 동작을 지속적으로 규율하려는 rule·가이드라인** (강제 가능하든 — "gap<80이면 PR 차단" — 권고든 — "PR 본문은 한국어") → **CLAUDE.md suggest-only 우선** (repo=팀, user=개인).
  CLAUDE.md는 매 세션 context에 로드되고 repo는 git으로 공유됨 — recall-on-search인 memory보다 rule 전파에 맞다.
  그 rule이 *왜* 생겼는지가 코드·rule 텍스트만으로 복원 불가할 때만 memory에도 이유를 별도 write (2개 타깃 허용 예외).
  - **판별선**: 규범(prescriptive — "앞으로 X 해라") → CLAUDE.md. 서술(descriptive — "이 코드/시스템은 이렇게 동작한다"는 사실·주의사항) → auto-memory. 둘 다면 위 예외로 양쪽.
- 그 외 모든 충돌 (일회성 결정·발견 등) → 라우팅 표의 **위쪽 행 우선** (auto-memory > handoff > ADR > skill > hook).

## skill 추천 트리거 (고정밀 — 노이즈 방지)

**둘 다** 만족할 때만 skill 후보로 표면화. 아니면 침묵.

1. **절차형** — 재실행 가능한 multi-step 루틴 (결정→ADR, 사실→memory, **절차→skill**)
2. **반복** — 이번 세션 2회+ 수동 반복 OR 관련 memory 이미 존재(재발)

드물게·믿을 만하게 > 매번·무시됨. 무차별 추천은 안 눌린다.

## 실패 처리 (if-then)

| 트리거 조건 | 일차 대응 | 여전히 실패 시 |
|---|---|---|
| memory dir / 타 repo `CLAUDE.md` grep 불가 | `duplicate_status: unknown` 표시 | CREATE/UPDATE 결정을 사용자 확인으로 위임 (단정 금지) |
| memory MCP 도구 검색 0건 | 더 짧은 명사 키워드로 재시도 | `duplicate_status: unknown` 표시 → CREATE/UPDATE를 사용자 확인으로 위임 (0건을 부재로 단정 금지) |
| memory MCP 도구 미설치·호출 실패 | dual-store skip, 파일 층만 write | receipt에 `store: file-only (<사유>)` 명시 — 조용히 넘어가지 않음 |
| `audit.sh` 부재(부분 설치)·`jq`/`git` 없음 | health check skip | receipt에서 그 줄 생략. **실패 아님** — reflect는 audit에 의존하지 않는다 |
| 학습에 세션 근거(파일·커밋·발언) 못 댐 | 해당 후보 discard | 사유를 라우팅 표 `근거` 열에 명시 |
| 외부 스킬(`skill-development`·`hook-development`) 부재 | 수동 fallback 안내 (CLAUDE.md "When Adding a New Skill") | 추천 lane 유지 — reflect가 대신 생성하지 않음 |
| carry-forward 후에도 In Progress·Open Q 둘 다 없음 | handoff.md 삭제 | 삭제 실패(파일 lock 등) 시 stale 경고만, 강제 삭제 금지 |
| implementation-notes.md resolved entry와 중복 | 해당 entry skip | 애매하면 후보로 올리되 근거에 "중복 의심" 표기 |
