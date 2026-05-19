# Doc Mode — Workflow Details

## Required sequence

1. Assess requirement clarity (clear vs vague) — see Clarity Gate in SKILL.md
2. **Clear path**: brainstorming → prep (persist) → **AC Gate** → artifact
3. **Vague path**: ooo interview → prep (persist) → optional pm/seed → **AC Gate** → artifact
4. Both paths: `prep` persists to `docs/requirements.md` before artifact creation
5. **AC Gate (필수, SKILL.md 참조)**: Given-When-Then AC 작성 + 사용자 확정. AC 0개면 차단
6. Route to ADR or RFC step only when decision record is warranted
7. **Offer `publish-spec`** — ask user whether to publish to Confluence (dry-run → confirm → publish)
8. Stop before implementation unless user explicitly asks to enter dev workflow

## Clarity assessment

| Clear signals | Vague signals |
|---------------|---------------|
| Concrete feature description with boundaries | "뭔가 만들고 싶은데" |
| Acceptance criteria stated or derivable | No scope, audience, or constraints |
| External SoT available (Jira, Figma, PRD, Confluence) | "아이디어 단계", "탐색 중" |
| User names specific artifact type (RFC, spec) | "기획서 같은 거" (type unclear) |

When ambiguous, ask one question: "요구사항이 명확한 편인가요, 아직 탐색 단계인가요?"

## Mandatory routing table

### Clear path
| Condition | Route |
|-----------|-------|
| External SoT exists | `prep` → `superpowers:brainstorming` → `prep` (update) → artifact |
| No external SoT, requirements clear | `superpowers:brainstorming` → `prep` (persist) → artifact |
| Brainstorm reveals ambiguity | Fall back to vague path (ooo interview) |

### Vague path
| Condition | Route |
|-----------|-------|
| Scope/audience unclear | `ooo interview` → `prep` (persist) → artifact |
| Trade-off framing needed | `ooo interview` → `prep` → `ooo pm` → artifact |
| Design must be frozen | `ooo interview` → `prep` → `ooo pm` → `ooo seed` → artifact |

### Post-artifact
| Condition | Route |
|-----------|-------|
| Architectural decision made | `adr` |
| Artifact complete | Offer `publish-spec` |
| Implementation requested | `workflow-dev-mode` |

## prep as universal persist

`prep` serves as the convergence point for both paths:
- **Clear path**: brainstorming output → `prep` → `docs/requirements.md`
- **Vague path**: ooo interview output → `prep` → `docs/requirements.md`
- **External SoT**: Jira/Figma/Confluence → `prep` → `docs/requirements.md`

This ensures `docs/requirements.md` is always the source of truth for artifact creation, regardless of how requirements were gathered.

## Artifact types

- `spec`: implementation-shaping document with acceptance boundaries
- `rfc`: decision memo with alternatives and recommendation
- `design`: architecture or flow description
- `plan`: planning artifact before implementation begins

## Output contract

Before routing onward, produce:

### Workflow Intake
- Mode: `doc`
- Clarity: `clear` or `vague`
- Artifact type
- Scope
- Reasoning bullets

### Gate Status
- clarity assessment status
- source-of-truth localization status (`prep`)
- design exploration status (brainstorming or ooo interview)
- **acceptance criteria status (count, format: Gherkin/bullet, user-confirmed)**
- documentation artifact status
- confluence publish status
- implementation handoff status

### Next Action
- exact skill/command to invoke next
- why now

## Hallucination guards

- If required facts are not verified from current inputs, mark them `[UNVERIFIED: requires source confirmation]`.
- If requested artifact type is ambiguous, ask instead of choosing silently.
- If current environment does not confirm skill or command availability, say `[UNVERIFIED: skill or command availability not confirmed]`.
- If design recommendation depends on unstated constraints, surface those constraints explicitly.
- Do not claim implementation readiness unless acceptance criteria and scope boundaries are explicit.
- **Do not write AC on behalf of user without confirmation.** Propose Gherkin templates derived from brainstorm/interview, then wait for user review. Inventing AC = hallucination risk.
- **Do not propose domain-specific AC topic hints.** Even listing "AC 후보 영역" (재시도 정책, fallback, 멱등성 등) narrows user's thinking and risks missing areas. Only present the empty Gherkin structure. interview skill is responsible for divergent question discovery, not doc-mode.
- **Auto-invoke next skill without explicit user confirmation only when next gate is unambiguous** (per stop conditions). vague→interview transition is unambiguous; auto-invoke `ooo interview` without asking.

## Stop conditions

- stop and ask when artifact type is unclear
- stop and ask when audience materially changes document shape
- stop and ask when clarity is ambiguous (ask the one question)
- **stop and ask when AC count = 0 or any AC is ambiguous (re-interview if needed)**
- continue without asking only when next gate is unambiguous

## Examples

### Example 1: Clear path
User: `승인 후 날짜 수정 기능 기획문서 써줘. Jira에 티켓 있어.`
Route: `prep` (Jira SoT) → `superpowers:brainstorming` → `prep` (update requirements.md) → spec artifact → offer `publish-spec`.

### Example 2: Vague path
User: `Write design doc for replacing session storage.`
Route: `ooo interview` (scope unclear) → `prep` (persist) → design artifact → optional `adr`.

### Example 3: Vague path with PM
User: `Draft RFC for tenant-aware auth migration.`
Route: `ooo interview` → `prep` → `ooo pm` (trade-off comparison) → RFC artifact.

### Example 4: Clear path, no external SoT
User: `이 API spec 문서로 정리해줘. 요구사항은 이미 정해져 있어.`
Route: `superpowers:brainstorming` → `prep` (persist) → spec artifact.

### Example 5: Clarity fallback
User: `Help me plan feature rollout before we code.`
Route: clarity ambiguous → ask → user says "아직 탐색 중" → `ooo interview` → `prep` → planning artifact → handoff to `workflow-dev-mode`.
