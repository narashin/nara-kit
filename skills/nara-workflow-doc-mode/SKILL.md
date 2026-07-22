---
name: nara-workflow-doc-mode
description: >-
  Run documentation-first workflow producing specs, RFCs, design docs, or planning artifacts.
  Routes by requirement clarity: clear → (nara-prep if external SoT) → nara-grill → persist → spec, vague → nara-ac-draft → spec.
  USE FOR: "doc mode", "기획 모드", "spec 작성", "RFC", "설계 문서".
  DO NOT USE FOR: direct code implementation, bug fixes, test writing.
---

# Workflow Doc Mode

Documentation-first workflow after router classifies request as `doc`.

## Clarity Gate

Before routing, assess requirement clarity:

| Signal | Clear | Vague |
|--------|-------|-------|
| User describes feature with acceptance criteria | ✓ | |
| External SoT available (Jira, Figma, PRD) | ✓ | |
| User says "뭔가 만들고 싶은데" / "아이디어 단계" | | ✓ |
| No concrete scope, audience, or constraints | | ✓ |

## Routes

**Clear path** (requirements stable), 순서 고정:
0. **(조건부 pre-step)** 외부 SoT(Jira/Figma/PRD) 존재 시에만 → `nara-prep`로 **로컬화**하여 `docs/requirements.md` 초안 확보. 외부 SoT 없으면 skip.
1. `nara-grill` — 설계 옵션 탐색·검증 (fact-first, 한 번에 하나씩)
2. **doc-mode가 직접 persist** — grill에서 확정된 결정 + 아래 AC Gate로 확정한 AC를 `docs/requirements.md`에 기록 (스텝 0 초안 있으면 그 위에 갱신, 없으면 신규 작성). ⚠️ 이 단계에 `nara-prep`를 쓰지 않는다 — prep은 *외부 SoT 로컬화* 전용이라 grill 산출 입력을 거부하고 재실행 시 stale-gate로 종료된다.
3. Produce artifact (spec/RFC/design/plan)

> frontmatter의 clear 흐름 `(prep if SoT) → grill → persist`가 스텝 0→1→2와 정확히 일치. prep은 외부 SoT 있을 때만 도는 조건부 로컬화(스텝 0), grill 이후 persist는 doc-mode 자체 책임(스텝 2, prep 아님).

**Vague path** (requirements need discovery):
1. `nara-ac-draft` — thin intent → User Stories + Gherkin AC → `docs/requirements.md`
2. Produce artifact

**Both paths converge**: `docs/requirements.md` is the persisted SoT before artifact creation (clear path: doc-mode 스텝 2가 기록, vague path: `nara-ac-draft`).

## AC Gate (필수)

**Artifact 산출 전 Acceptance Criteria 필수.** AC 빈 채로 spec/RFC/design 생성 차단.

### 형식

Given-When-Then (Gherkin) 권장. 한 AC = 한 시나리오.

```markdown
## Acceptance Criteria

- AC1
  - Given <초기 상태>
  - When  <행동>
  - Then  <기대 결과>
  - And   <추가 검증, 선택>

- AC2
  - ...
```

bullet 형식도 허용 (legacy spec, 외부 SoT 형식 그대로 보존 시):
```markdown
## Acceptance Criteria
- 사용자가 만료 토큰으로 호출 시 401 + "TOKEN_EXPIRED" 반환
- ...
```

### 작성 단계

1. nara-grill / nara-ac-draft 결과 → AC 후보 추출
2. 사용자에게 Given-When-Then 템플릿 제시
3. 사용자 검토 + 확정 (모호한 AC 발견 시 다시 nara-ac-draft)
4. 확정된 AC는 먼저 `docs/requirements.md`(SoT)에 기록(clear path 스텝 2) → artifact의 `## Acceptance Criteria` 섹션으로 복사. 두 곳 동일 내용 유지
5. **AC 0개 = artifact 생성 차단.** "AC 작성하라" 안내 후 중단

> **수렴 규율** (질문할 때): 코드베이스 먼저 확인해 검증 가능한 전제는 스스로 답하고, **미검증 전제만** 질문한다. 한 번에 하나씩. 이미 확정된 항목 재질문 금지. "생각나는 것 다 묻기"(interview mode) 금지. 같은 항목 5회+ 왕복 시 "가정하고 진행 vs 멈춤"을 제안 (무한 hard-cap 금지).

### 분류 신호

작성된 AC는 자동 P0 (nara-gap rubric §6 기준). spec 작성자가 명시적으로 P1/P2 표기 시만 격하.

### 외부 SoT에 AC 없는 경우

- Jira/Confluence에 AC 누락 시: doc-mode에서 작성 → 사용자가 외부 SoT에도 보강 권고 (외부와 desync 방지)
- 외부 SoT 자체가 부재 (vague path 신규 spec) → `nara-ac-draft`로 US + Gherkin AC 생성 후 사용자 확정
- 우회 금지: "AC 없어도 spec 만들어줘" 요청 시 reject + 이유 설명

### 금지: 도메인 hint 주입

AC Gate에서 사용자에게 제시 가능한 것:
- ✅ Given-When-Then 빈 템플릿 구조 (`Given <...>` 형태)
- ✅ "AC 작성하려면 nara-ac-draft 필요" 안내

제시 금지:
- ❌ 도메인별 AC 후보 영역 ("재시도 종료 조건", "fallback 정책", "멱등성" 등)
- ❌ "AC 영역 힌트" / "nara-ac-draft 질문축 후보"
- ❌ 예시 AC 본문 (실제 도메인 단어가 들어간 Given-When-Then)

이유: 영역 hint도 사용자의 사고를 좁힘 → 누락된 영역 발견 차단. nara-ac-draft 스킬이 발산적 질문을 책임짐. doc-mode는 게이트만 강제.

## 마무리 — 결정 / 가정 / 리스크 (D/A/R)

artifact 산출 직전, 이번 게이트에서 확정된 것을 세 줄로 닫는다 (gap.md + nara-reflect로 전달):

- **결정 (Decisions)**: 무엇을 어떻게 하기로 확정했는가
- **가정 (Assumptions)**: 확정 못 하고 가정한 것 — 각 항목 `[UNVERIFIED]` 병기
- **남은 리스크 (Remaining Risks)**: 미해결 항목 → blocking `Open Questions`로 남김 (별도 machinery 재발명 금지)

세 섹션 모두 비어도 헤더 + "없음" 출력.

## Post-artifact

- Architectural decision → `nara-adr`
- Publish to wiki → offer `nara-publish-spec` (dry-run → confirm → publish)
- Implementation requested → handoff to `nara-workflow-dev-mode`
- Session end → `nara-reflect`

## Later Sessions (Revision Loop)

`nara-publish-spec` 이후 며칠~몇 주 갭이 정상. 회의/리뷰에서 피드백 수집되면 별개 세션에서 standalone 진입:

- `nara-spec-revision <Confluence URL>` — v2, v3 ... append. 원본 보존, 변경 섹션만 추가
- 입력: 페이지 URL (필수) + 피드백 (user paste or Confluence inline comment 자동 수집)
- 반복 가능 — 라운드마다 새 버전 섹션 누적
- 워크플로 재진입 아님. 단일 skill 호출로 완결

**Load** [references/doc-workflow-details.md](references/doc-workflow-details.md) for routing table, output contract, examples, and hallucination guards.
