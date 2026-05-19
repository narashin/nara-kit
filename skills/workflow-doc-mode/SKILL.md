---
name: workflow-doc-mode
description: >-
  Run documentation-first workflow producing specs, RFCs, design docs, or planning artifacts.
  Routes by requirement clarity: clear → brainstorming → prep → spec, vague → ooo interview → prep → spec.
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

**Clear path** (requirements stable):
1. External SoT exists → `prep` first
2. `superpowers:brainstorming` — explore design options
3. `prep` — persist brainstorm output to `docs/requirements.md`
4. Produce artifact (spec/RFC/design/plan)

**Vague path** (requirements need discovery):
1. `ooo interview` — clarify scope, audience, constraints
2. `prep` — persist interview output to `docs/requirements.md`
3. `ooo pm` — product framing (if trade-off comparison needed)
4. `ooo seed` — lock design snapshot (if design must be frozen)
5. Produce artifact

**Both paths converge**: `prep` always persists to `docs/requirements.md` before artifact creation.

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

1. brainstorming / ooo interview 결과 → AC 후보 추출
2. 사용자에게 Given-When-Then 템플릿 제시
3. 사용자 검토 + 확정 (모호한 AC 발견 시 다시 interview)
4. artifact의 `## Acceptance Criteria` 섹션에 박음
5. **AC 0개 = artifact 생성 차단.** "AC 작성하라" 안내 후 중단

### 분류 신호

작성된 AC는 자동 P0 (gap rubric §6 기준). spec 작성자가 명시적으로 P1/P2 표기 시만 격하.

### 외부 SoT에 AC 없는 경우

- Jira/Confluence에 AC 누락 시: doc-mode에서 작성 → 사용자가 외부 SoT에도 보강 권고 (외부와 desync 방지)
- 우회 금지: "AC 없어도 spec 만들어줘" 요청 시 reject + 이유 설명

## Post-artifact

- Architectural decision → `adr`
- Publish to wiki → offer `publish-spec` (dry-run → confirm → publish)
- Implementation requested → handoff to `workflow-dev-mode`
- Session end → `reflect`

**Load** [references/doc-workflow-details.md](references/doc-workflow-details.md) for routing table, output contract, examples, and hallucination guards.
