# nara-kit Output Contract

> 모든 nara-kit 스킬이 따르는 채팅 출력 규약. 응답 스타일 호환, MCP 부수효과, error/long-running receipt, 검증 가능 형식 포함.

## 원칙

**채팅 출력은 영수증(receipt)이지 산출물 자체가 아니다.**

산출물은 파일/메모리/커밋에 저장. 채팅에는 **무엇이 어디에 어떻게 기록됐는지**만 짧게 보고. 디테일은 파일 경로 따라가 직접 확인.

contract는 **alignment 메커니즘**. 형식적 실수 (혼동/누락/모호함) 감소. 내용 정확성(환각/버그)은 LSP/리뷰/hook이 담당.

---

## 1. 응답 4요소

| 요소 | 내용 |
|------|------|
| **Outcome** | 무엇을 완료했는가 (한 줄) |
| **Evidence / Risk / Ambiguity** | 사실 상태와 불확실성. recorded vs applied 구분 |
| **Artifact Paths** | 기록 위치 (파일/메모리/커밋) |
| **Next Action** | 다음 단계 추천 또는 사용자 확인 필요 항목 |

Next Action 규칙:
- **사람이 할 일은 빠짐없이.** 남은 사용자 행동(승인, 수동 확인, 직접 실행해야 하는 명령)을 전부 적는다. 하나라도 남았으면 "없음"이라고 쓰지 않는다.
- **없으면 `next: 없음`.** 할 일이 없는데 후속 작업을 만들어 채우지 않는다. 4요소는 자리를 지키는 것이지 내용을 지어내는 것이 아니다.
- **스킬이 할 일을 사용자에게 넘기지 않는다.** 스킬 권한 안에서 할 수 있는 단계를 "이 명령을 실행하세요"로 바꿔 놓지 않는다. 사람만 할 수 있는 것(커밋, 원격 게시 승인, 로그인)만 넘긴다.
- 여러 단계면 순서 있는 짧은 목록으로, 단계마다 끝이 분명한 행동 하나.

---

## 2. 분량

- 기본 **3~6라인**. 길어도 10라인 이내
- 줄 수보다 빠짐없음이 먼저다: 요청받은 항목, 중요한 위험·단서, 출처를 줄 수 때문에 버리지 않는다. 넘치면 산출물 파일로 보내고 경로를 적는다
- 표는 비교가 핵심일 때만
- 코드/문서 내용 인라인 덤프 금지 — 경로만

---

## 3. 상태 분류 (4종)

출력에 반드시 명시:

| 상태 | 의미 | 예시 |
|------|------|------|
| **recorded only** | 파일/메모리에 기록만. 코드 미반영 | "결정 사항 메모리에 저장" |
| **applied** | 실제 코드/시스템 변경 완료 | "테스트 코드 추가, 통과 확인" |
| **pending escalation** | 격상 후보 — 사용자 결정 필요 | "→ ESCALATE: CLAUDE.md 추가 반영" |
| **skipped** | 의도적으로 안 함 + 이유 | "갭 80 이상이라 갭 분석 스킵" |

계획과 실행을 섞지 않는다: 하려는 것은 `planned`, 한 것만 `applied`. 로컬 커밋은 원격 게시가 아니고, 기준 측정(baseline)은 수락 판정이 아니다.

---

## 3-bis. 주장 provenance 라벨 (4-tier)

§3 상태 라벨이 **행위 상태**(기록/적용/격상/스킵)라면, provenance 라벨은 **주장의 근거 수준**이다 — 관찰인가 추론인가 결정인가 제안인가. gap·retro·incident·code-review·ac-draft가 각자 "evidence" 의미를 재발명하지 않도록 **단일 어휘** 사용. 주장의 근거가 자명하지 않을 때 붙인다.

| 라벨 | 의미 | 규칙 |
|------|------|------|
| **Evidence** | 직접 관찰 | `파일:라인` / 커밋 / diff 인용 필수 |
| **Interpretation** | 관찰에서 추론 | 근거 관찰 + 추론임을 명시. 미검증이면 `[UNVERIFIED]` 병기 |
| **Decision** | 사용자 또는 근거로 확정 | 누가/무엇으로 확정했는지 |
| **Suggestion** | 제안 (미확정) | 사용자 결정 필요 시 `→ ESCALATE:`로 격상 |

- `[UNVERIFIED]`는 Interpretation의 하위 케이스(미검증 추론), `→ ESCALATE:`는 결정 필요한 Suggestion — **기존 prefix 재사용**, 신규 축 아님
- summary를 confirmed로 격상 금지(§12) = "Interpretation을 Evidence로 표기 금지"의 다른 말

---

## 4. 응답 스타일 호환

세션에 걸린 출력 스타일이 얼마나 짧게 쓰라고 요구하느냐에 따라 receipt 압축 수준이 다름. 아래 3단계는 **동작 기준**이고 특정 스타일·플러그인 이름에 묶이지 않는다 — 현재 걸린 스타일의 요구를 이 중 하나로 매핑해 적용한다.

| 압축 수준 | 규칙 |
|------|------|
| **full** (기본) | 라벨 + 값 풀 (`branch: feature/x`) |
| **compact** | 필드 라벨 축약 가능 (`br: feature/x | gap: 85`). 관사·필러 드롭, 핵심 값만 |
| **minimal** | 라벨 생략. 값과 prefix 기호만 (`feature/x · 85 · /nara-code-review`) |

압축은 **형식만** 줄인다. §1의 4요소는 어느 수준에서도 빠지지 않는다 — 라벨을 지워도 값은 남는다.

**모드 무관 normal 유지**:
- 코드 블록 / commit / PR 본문
- 보안 경고 / 비가역 작업 확인
- 다단계 시퀀스 순서 중요 시
- 사용자가 명확화 요청 시

---

## 5. 외부 부수효과 (MCP side effects)

MCP 호출이 외부 시스템을 변경한 경우 명시. 감사/롤백 가시화.

```
side effects:
- confluence: 1 page created (PAGE-ID: 12345)
- linear: 0 (read only)
- slack: 0
- jira: 1 comment added (TICKET-456)
```

규칙:
- **읽기만은 생략 가능**. 쓰기/생성/수정/삭제만 필수 명시
- ID/URL 포함해 추적 가능하게
- 0건이어도 사용자 기대 가능 시 명시 (예: `/nara-publish-spec` 후 confluence: 0이면 의심해야)

---

## 6. Error / Block Receipt

실패 또는 차단 시 형식:

```
❌ 실패: <한 줄 이유>
- recovered: <yes/no>
- artifact 영향: <none | partial write to docs/gap.md>
- side effects: <부분 외부 변경 있으면 명시>
- next action: <명확한 1개>
```

규칙:
- 실패 원인은 1줄 + 해결 가능한 형태로
- 롤백 가능성(`recovered`) 명시
- 부분 적용된 변경 사항 반드시 명시 (가장 위험)

---

## 7. Long-running 진행 보고

다단계 스킬 (code-review multi-agent, ac-draft multi-source, test-discover 4-stage) 중간 보고:

```
(2/5) Architecture agent 완료
- finding: 2건 (medium 1, low 1)
- elapsed: ~30s
- next: Correctness agent 시작
```

규칙:
- `(현재/전체)` prefix 고정 → 사용자 진행률 즉시 파악
- 중간 발견 요약 1~2줄
- `elapsed`·진행률은 잰 값만. 추정 시간이나 아직 안 된 진행을 적지 않는다
- 최종 receipt와 형식 분리 (최종은 4요소 풀 적용)

---

## 8. 검증 가능 형식 (Machine-parseable)

receipt가 regex/yaml로 파싱 가능하도록 키 prefix 표준화:

| Key | 값 형식 |
|-----|--------|
| `branch:` | git branch 이름 |
| `artifact:` | 파일 경로 (백틱) |
| `score:` | 0-100 정수 |
| `recorded:` | yes/no 또는 N개 |
| `applied:` | yes/no |
| `side effects:` | 카운터 리스트 |
| `next:` | 슬래시 커맨드 또는 한 줄 |
| `→ ESCALATE:` | 격상 대상 한 줄 |
| `❌ 실패:` | 실패 사유 1줄 |
| `Evidence:` / `Interpretation:` / `Decision:` / `Suggestion:` | 주장 provenance 라벨 (§3-bis) |

→ waza eval에서 contract 위반 자동 감지 가능 (provenance 라벨 오용 — Interpretation을 Evidence로 표기 등 — 포함). AI 출력 일관성 자동화 검증.

---

## 9. 격상 신호 (Escalation signals)

사용자 결정 필요한 항목은 **`→ ESCALATE:`** prefix 고정. 권유/추천과 구분.

```
→ ESCALATE: CLAUDE.md managed section 추가 필요 — 확인 요청
→ ESCALATE: 신규 패키지 zod 도입 검토 필요
```

vs 단순 추천:
```
다음 추천: /nara-code-review
```

**자리 규칙**: 답을 받아야 진행하는 ESCALATE는 receipt의 마지막 산문 블록이다. 뒤에 올 수 있는 것은 trailing status 블록과 답 형식 안내뿐이고, "참고로"·"그 밖의"·"남은 일은" 꼬리 산문은 ESCALATE **앞**으로 옮긴다. receipt에 다른 내용이 있으면 Outcome 줄에 `pending escalation`을 적어 첫 줄이 질문을 가리키게 한다. 답 없이도 진행 가능한 항목은 ESCALATE가 아니라 추천이다. (근거: 2026-10-12 로컬 transcript 68개 측정, 턴 종료 메시지의 10~14%가 질문 뒤 꼬리 산문. 분기마다 재측정)

---

## 10. Receipt 템플릿

### /nara-now
```
세션 상황 평가 완료.
- branch: `<name>` · gap: `<n>` or none · 미커밋: <n>개
- handoff: `docs/handoff.md` 존재 → "<핵심 1줄>" · 없음
- next: <skill 1-2개>
```

### /nara-ac-draft
```
요구사항 정리 완료 (recorded only).
- artifact: `docs/requirements.md`
- sources: <n> (internal-draft면 0) · AC <n> (원문 <a> / [draft] <b>) · UNVERIFIED: <n>
- side effects: jira/confluence read N건
- next: /nara-plan | [draft] AC 확정 요청
```

### /nara-gap
```
갭 분석 완료 (recorded only).
- artifact: `docs/gap.md`
- score: <n>/100
- missing: <n> · partial: <n> · agreed exceptions: <n>
- next: <80 → 구현 계속 | 80+ → /nara-code-review
```

### /nara-retro
```
회고 완료 (recorded only | applied).
- 학습 <n>: memory <a> · 추천 <b> · no change <c> · discard <d>
- memory: <파일 경로> / 도구 레코드 <id> | 없음
- → ESCALATE: <CLAUDE.md/ADR 후보 있으면> 또는 생략
- next: <남은 사람 할 일 | 없음>
```

### /nara-handoff
```
인계 기록 (applied).
- artifact: `docs/handoff.md` (baseline: <sha>)
- in progress: <n> (carry-forward <k>, 신규 <m>, 해소 제거 <r>)
- open questions: <n>
- next: 다음 세션 `/nara-now`
```

### /handoff-read (또는 /nara-now가 handoff.md 감지 시)
```
이전 세션 handoff 읽음.
- artifact: `docs/handoff.md` (baseline: `<sha>`)
- stale risk: <none | HEAD 변경 있음 — 검증 필요>
- open questions: <n>개
- next: <명확한 1개>
```

### /nara-publish-spec (외부 부수효과 큰 케이스)
```
스펙 게시 완료 (applied).
- artifact: `docs/spec-x.md`
- side effects:
  - confluence: 1 page created (PAGE-ID: 12345, parent: PARENT-678)
  - slack: 0
- next: 팀 공유 또는 /nara-rfc 작성
```

### /nara-commit
```
커밋 메시지 생성 완료 (recorded only — 사용자 확인 대기).
- message: `<TICKET-ID> <type>: <subject>`
- staged: <N> files
- 분리 제안: <yes — N개 관심사 섞임 | no>
- next: 사용자가 직접 `git commit` 실행
```

### /nara-pr
```
PR 본문 생성 완료 (recorded only — gh pr create 대기).
- base: `<branch>` · commits: <N>
- title: `<TICKET-ID> <type>: <subject>`
- side effects: <적용 시 — github: 1 PR created (#NNN)>
- next: 사용자 확인 후 gh pr create 실행
```

### /nara-code-review
```
multi-agent 리뷰 완료.
- artifact: `docs/review/<YYMMDD>-<desc>.md`
- findings: <N>건 (blocking <n>, suggestion <n>, nitpick <n>)
- auto-fix rounds: <N>/3 (converged | max-reached | no-progress)
- adversarial review: <applied | skipped — codex unavailable>
- next: 보고서 검토 후 /nara-commit 또는 수정 보완
```

### /nara-pr-respond
```
PR #<N> 리뷰 대응 완료.
- comments processed: <N>
- accepted: <n> (implemented) · rebutted: <n> · on hold: <n>
- side effects:
  - github: <n> replies posted, <n> code changes pushed
- artifact: PR thread (#<N>)
- next: hold 항목 사용자 결정 또는 reviewer 응답 대기
```

### /nara-rfc
```
RFC 문서 작성 완료 (recorded only).
- artifact: `docs/rfc/<TICKET-ID>-rfc.md`
- ticket: <TICKET-ID>
- work to do: <N>개 (검증 가능 형태)
- → ESCALATE: <외부 의존성/팀 합의 필요 항목 있으면> 또는 생략
- next: 사용자 검토 또는 /nara-publish-spec
```

### /nara-adr
```
ADR <NNNN> 기록 완료 (recorded only).
- artifact: `docs/adr/<NNNN>-<slug>.md`
- status: <proposed | accepted | superseded>
- supersedes: <ADR-NNNN 또는 없음>
- CLAUDE.md 참조 갱신: <yes | no>
- next: <팀 리뷰 | 구현 진행>
```

### /nara-skill-forge
```
Skill forge 완료 (applied).
- target: `skills/<name>/SKILL.md`
- waza check: <pass | N issues remaining>
- iter: <N>/N (converged | max-reached | no-progress)
- artifact: `skills/<name>/SKILL.md`, `evals/<name>/`
- side effects: waza eval N건 실행 (외부 LLM 호출)
- next: <skill 사용 또는 추가 튜닝>
```

### /nara-empirical-prompt-tuning
```
EPT 완료 (applied).
- target prompt: `<path>`
- iterations: <N> (converged | unclear-points remaining)
- subagent dispatch: <N>회 (병렬 N · 직렬 N)
- final metrics: success <%>, unclear <N>
- artifact: `<path>` (수정됨), 평가 기록 `<eval-log>`
- next: <실사용 검증 또는 추가 시나리오>
```

---

## 11. Do

- 결정의 **이유** 포함 (한 줄)
- Ambiguity는 해결된 척 하지 말고 그대로 노출
- 파일 경로는 백틱으로 감싸 클릭 가능하게
- 다음 단계는 1~2개만 — 선택지 나열 금지
- 외부 변경은 부수효과 섹션에 격리

## 12. Don't

- 산출물 전체 dump (요구사항 본문, gap 표 전체)
- 메타데이터 범람 (timestamp, 모델명, 토큰수 — 묻기 전엔 X)
- 내부 워크플로우 상태 노출 ("Phase 3 of 7…")
- "summary"를 "confirmed requirement"로 격상 — 추정은 [UNVERIFIED]
- reflection 기록을 영속 산출물 변경으로 혼동
- 외부 시스템 변경을 침묵으로 처리 (반드시 side effects)

---

## 13. 점진 적용

- ✅ 1차 (워크플로우 골격): `/nara-now`, `/nara-ac-draft`, `/nara-gap`, `/nara-retro`, `/nara-handoff`
- ✅ 2차 (코드 라이프사이클): `/nara-commit`, `/nara-pr`, `/nara-code-review`, `/nara-pr-respond`, `/nara-publish-spec`
- ✅ 3차 선별 (문서·메타): `/nara-rfc`, `/nara-adr`, `/nara-skill-forge`, `/nara-empirical-prompt-tuning`
- 일반 원칙 흡수 (명시 receipt 없이 CLAUDE.md 4요소 자동 적용): `/nara-explain`, `/nara-incident`, `/nara-incident-fix`, `/nara-test-discover`, `/nara-test-verify`, `/nara-test-implement`, `/nara-design-md`, `/nara-spec-revision`

각 스킬은 nara-kit CLAUDE.md를 통해 contract를 자동 상속 — SKILL.md에 개별 참조 라인 불필요. 명시 receipt 없는 스킬은 4요소(Outcome/Evidence/Paths/Next) + 상태 라벨만 따라 자유 생성.
