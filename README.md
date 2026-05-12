# nara-kit

> **Note:** Personal skill collection by [@shinnara](https://git.linecorp.com/shinnara). Workflows and conventions reflect personal preferences — use as reference or fork to adapt.
>
> 개인 워크플로우 스킬 모음. 개인 취향이 반영되어 있으므로 참고용 또는 포크해서 커스터마이즈.

Personal Claude Code workflow toolkit — 21 skills for structured software development and documentation workflows.

Claude Code 워크플로우 툴킷 — 구조화된 소프트웨어 개발 및 문서화를 위한 21개 스킬.

## Skills / 스킬 목록

### Workflow / 워크플로우

| Skill | Description / 설명 |
|-------|---------------------|
| `mwhat` | Session state assessment + next action / 세션 상황 판단 + 다음 행동 추천 |
| `workflow-orchestrator` | Route requests to dev or doc mode / 요청을 dev/doc 모드로 라우팅 |
| `workflow-dev-mode` | Implementation workflow (prep → gap → plan → execute → verify) / 구현 워크플로우 |
| `workflow-doc-mode` | Documentation workflow (spec/RFC/design artifacts) / 문서화 워크플로우 |

### Requirements & Analysis / 요구사항 & 분석

| Skill | Description / 설명 |
|-------|---------------------|
| `prep` | Localize external SoT (Jira/Figma/Confluence) into `docs/requirements.md` + Readiness score / 외부 SoT 로컬화 + 충분성 판정 |
| `gap` | Requirements vs implementation gap analysis → `docs/gap.md` (0-100 score) / 요구사항 vs 구현 갭 분석 |
| `incident` | Structured incident analysis report (no code changes) / 장애 분석 리포트 (코드 수정 없음) |
| `incident-fix` | TDD-based fix from `docs/incident-report.md` / 장애 리포트 기반 TDD 수정 |

### Code Lifecycle / 코드 라이프사이클

| Skill | Description / 설명 |
|-------|---------------------|
| `commit` | Generate conventional commit message with ticket ID / 커밋 메시지 생성 |
| `pr` | Generate PR title and body in Korean / PR 제목 + 본문 생성 |
| `code-review` | 5-agent parallel review (Architecture/Correctness/Reliability/Security/Test) / 5-에이전트 병렬 코드 리뷰 |
| `pr-respond` | Respond to PR review comments (accept/rebut/hold) / PR 리뷰 코멘트 대응 |

### Documentation / 문서

| Skill | Description / 설명 |
|-------|---------------------|
| `rfc` | Write RFC document in Korean Markdown / RFC 문서 작성 |
| `adr` | Architecture Decision Record / 아키텍처 결정 기록 |
| `explain` | Shareable explanations for different audiences / 대상별 설명 문서 생성 |
| `publish-spec` | Publish spec to Confluence wiki / 스펙 → Confluence 게시 |
| `reflect` | Capture session learnings (decisions, conventions, warnings) / 세션 학습 캡처 |

### Testing / 테스트

| Skill | Description / 설명 |
|-------|---------------------|
| `test-discover` | Discover test scenarios for a feature or file / 테스트 시나리오 발굴 |
| `test-verify` | Review and validate test scenarios (3-persona review) / 테스트 시나리오 검증 |
| `test-implement` | Implement tests from scenario documents / 시나리오 기반 테스트 구현 |

### Meta / 메타

| Skill | Description / 설명 |
|-------|---------------------|
| `empirical-prompt-tuning` | Iteratively improve prompts via bias-free executor testing — via [@mizchi](https://github.com/mizchi/skills/blob/main/empirical-prompt-tuning/SKILL.md) / 프롬프트 경험적 튜닝 |

## Install / 설치

```bash
claude plugin marketplace add https://git.linecorp.com/shinnara/nara-kit.git
```

## Workflow / 워크플로우

nara-kit skills are orchestrated in two modes. `workflow-orchestrator` classifies requests and routes to the appropriate mode. All 21 skills work standalone — external plugins enhance automation but are **not required**.

nara-kit 스킬은 두 모드로 오케스트레이션됨. `workflow-orchestrator`가 요청을 분류하여 적절한 모드로 라우팅. 21개 스킬 모두 독립 실행 가능 — 외부 플러그인은 자동화 수준을 높여주지만 **필수는 아님**.

### Mode A — Dev (Implementation / 구현)

```mermaid
flowchart TD
    START([Session Start]) --> MWHAT["/mwhat<br>Assess state"]
    MWHAT --> PREP["/prep<br>Localize SoT + Readiness"]
    PREP --> READY{Readiness?}
    READY -->|"READY 4/4"| BRAIN["☆ superpowers:brainstorming<br>(optional)"]
    READY -->|"PARTIAL or<br>INSUFFICIENT"| OOO_INT["◇ ooo interview<br>(optional)"]
    OOO_INT --> PREP
    BRAIN --> GAP["/gap<br>Gap analysis"]
    GAP --> PLAN["☆ superpowers:writing-plans<br>(optional)"]
    PLAN --> EXEC{Scope?}
    EXEC -->|small| DIRECT["Direct impl<br>☆ superpowers:TDD"]
    EXEC -->|large| SDD["☆ superpowers:SDD"]
    EXEC -->|fallback| OOO_RUN["◇ ooo run/auto<br>(optional)"]
    DIRECT --> VERIFY["/gap --verify"]
    SDD --> VERIFY
    OOO_RUN --> VERIFY
    VERIFY --> ADR_Q{Arch decision?}
    ADR_Q -->|yes| ADR["/adr"]
    ADR_Q -->|no| REVIEW
    ADR --> REVIEW["/code-review<br>5-agent parallel"]
    REVIEW --> CODEX["☆ codex:adversarial-review<br>(optional)"]
    CODEX --> REFLECT["/reflect"]
    REFLECT --> FINISH["☆ superpowers:finish-branch<br>(optional)"]
    FINISH --> PR_RESPOND["/pr-respond"]
    PR_RESPOND -->|changes| PR_RESPOND

    style BRAIN fill:#e8f5e9
    style PLAN fill:#e8f5e9
    style DIRECT fill:#e8f5e9
    style SDD fill:#e8f5e9
    style FINISH fill:#e8f5e9
    style CODEX fill:#fff3e0
    style OOO_INT fill:#e3f2fd
    style OOO_RUN fill:#e3f2fd
```

### Mode B — Doc (Documentation / 문서화)

```mermaid
flowchart TD
    START([Session Start]) --> MWHAT["/mwhat<br>Doc mode"]
    MWHAT --> ORCH["workflow-orchestrator<br>→ doc mode"]
    ORCH --> OOO_INT["◇ ooo interview<br>(optional)"]
    OOO_INT --> OOO_PM["◇ ooo pm<br>(optional)"]
    OOO_PM --> OOO_SEED["◇ ooo seed<br>(optional)"]
    OOO_SEED --> SPEC["Spec artifact"]
    SPEC --> PUB{Publish?}
    PUB -->|yes| PUBLISH["/publish-spec<br>→ Confluence"]
    PUB -->|no| RFC_Q{RFC needed?}
    PUBLISH --> RFC_Q
    RFC_Q -->|yes| RFC["/rfc"]
    RFC_Q -->|no| ADR_Q{Arch decision?}
    RFC --> ADR_Q
    ADR_Q -->|yes| ADR["/adr"]
    ADR_Q -->|no| REFLECT["/reflect"]
    ADR --> REFLECT
    REFLECT --> END([END])

    style OOO_INT fill:#e3f2fd
    style OOO_PM fill:#e3f2fd
    style OOO_SEED fill:#e3f2fd
```

### Legend / 범례

| Symbol | Plugin | Required? / 필수? |
|--------|--------|-------------------|
| (no symbol) | **nara-kit** (this plugin) | **Required** — core skills / 핵심 스킬 |
| ☆ green | **superpowers** | Optional — enhances planning, execution, review / 계획, 실행, 리뷰 강화 |
| ◇ blue | **ouroboros** | Optional — design discovery, execution fallback / 설계 발견, 실행 대안 |
| ☆ orange | **codex** | Optional — adversarial review / 반론 리뷰 |

## External Plugin Dependencies / 외부 플러그인 의존성

All external skills are **optional enhancements**. Without them, the workflow falls back to manual equivalents (e.g., write plans yourself, run tests directly).

모든 외부 스킬은 **선택적 강화**. 없으면 수동 대안으로 동작 (예: 직접 계획 작성, 직접 테스트 실행).

### Referenced by nara-kit skills / 스킬에서 직접 참조

| External Skill | Plugin | Referenced By | Stage / 단계 |
|----------------|--------|---------------|--------------|
| `superpowers:brainstorming` | superpowers | workflow-dev-mode | Design exploration / 설계 탐색 |
| `superpowers:subagent-driven-development` | superpowers | workflow-dev-mode | Large-scale execution / 대규모 실행 |
| `superpowers:receiving-code-review` | superpowers | pr-respond | Core principle (reference only) / 원칙 참조 |
| `ooo interview` | ouroboros | prep, workflow-dev-mode, workflow-doc-mode | Clarify requirements / 요구사항 명확화 |
| `ooo pm` | ouroboros | workflow-doc-mode | Product framing / 프로덕트 프레이밍 |
| `ooo seed` | ouroboros | workflow-doc-mode | Design snapshot / 설계 스냅샷 |
| `ooo run` / `ooo auto` | ouroboros | workflow-dev-mode | Execution fallback / 실행 대안 |
| `ooo evaluate` | ouroboros | workflow-dev-mode | Completion verification / 완료 검증 |

> **Note**: `ooo pm` and `ooo seed` also appear in `workflow-dev-mode/references/dev-workflow-details.md` routing table, but are only directly invoked from `workflow-doc-mode` SKILL.md. In dev mode, design discovery falls back to doc mode when requirements are unsettled.
>
> `ooo pm`, `ooo seed`는 dev-mode reference 라우팅 테이블에도 등장하지만, SKILL.md에서 직접 호출하는 건 doc-mode뿐. dev-mode에서 설계가 불명확하면 doc-mode로 handoff.
| `codex:adversarial-review` | codex | code-review | Adversarial final review / 반론 최종 리뷰 |

### Referenced by workflow rules only / workflow.md에서만 참조

These are invoked by CLAUDE.md workflow rules, not by nara-kit skills directly.

이 스킬들은 nara-kit 스킬이 아니라 CLAUDE.md 워크플로우 규칙에서 호출됨.

| External Skill | Plugin | Stage / 단계 |
|----------------|--------|--------------|
| `superpowers:writing-plans` | superpowers | Plan creation / 계획 생성 |
| `superpowers:test-driven-development` | superpowers | TDD gate / TDD 게이트 |
| `superpowers:finishing-a-development-branch` | superpowers | Branch finish / 브랜치 마무리 |

## My Setup / 내 설정

Other plugins I use alongside nara-kit / nara-kit과 함께 사용하는 플러그인:

| Plugin | Source | Purpose / 용도 |
|--------|--------|----------------|
| `superpowers` | `anthropics/claude-plugins-official` | Skill framework (brainstorming, SDD, worktrees, etc.) |
| `caveman` | `JuliusBrussee/caveman` | Terse response style / 간결한 응답 |
| `claude-mem` | `thedotmack/claude-mem` | Persistent memory across sessions / 세션 간 기억 |
| `claude-hud` | `jarrodwatts/claude-hud` | Token/session HUD overlay |
| `ouroboros` | `Q00/ouroboros` | Autonomous evolution engine / 자율 진화 엔진 |
| `plannotator` | `backnotprop/plannotator` | Plan annotation and analysis / 계획 주석 및 분석 |
| `codex` | `anthropics/claude-code-codex` | Codex integration (adversarial review, rescue) |

## Inspired By / 영감

| Source | What / 영향 |
|--------|-------------|
| [tiger-kit](https://github.com/MTGVim/tiger-kit) by @MTGVim | Core workflow loop (`mwhat`, `prep`, `gap`, `reflect`), gap-driven development pattern / 핵심 워크플로우 루프, 갭 기반 개발 패턴 |
| [empirical-prompt-tuning](https://github.com/mizchi/skills/blob/main/empirical-prompt-tuning/SKILL.md) by @mizchi | EPT methodology (bias-free executor + two-sided evaluation) / EPT 방법론 |
| [superpowers](https://github.com/anthropics/claude-code-plugins-official) by Anthropic | Brainstorming, SDD, TDD, plan/finish patterns / 설계 탐색, 실행, 계획 패턴 |
| [ouroboros](https://github.com/Q00/ouroboros) by @Q00 | Interview → seed → evaluate flow / 인터뷰 → 시드 → 평가 흐름 |

## Configuration / 설정

For `publish-spec`: create `confluence.local.md` in plugin root:

`publish-spec` 사용 시: 플러그인 루트에 `confluence.local.md` 생성:

```yaml
---
confluence_base_url: https://your-confluence.example.com
default_space_key: YOUR_SPACE
default_parent_page_id: "YOUR_PAGE_ID"
default_parent_page_name: Development
---
```
