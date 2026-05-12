# nara-kit

> **Note:** Personal skill collection by [@shinnara](https://git.linecorp.com/shinnara). Workflows and conventions reflect personal preferences — use as reference or fork to adapt.

Personal Claude Code workflow toolkit.

## Skills

| Skill | Description |
|-------|-------------|
| `mwhat` | Session situation assessment + next action recommendation |
| `prep` | Localize external SoT (Jira/Figma/Confluence/PRD) into `docs/requirements.md` |
| `gap` | Requirements vs implementation gap analysis → `docs/gap.md` |
| `reflect` | Capture session learnings (decisions, conventions, warnings) |
| `rfc` | Write RFC document in Korean Markdown |
| `commit` | Generate conventional commit message |
| `pr` | Generate PR title and body |
| `incident` | Structured incident analysis report (analysis only, no code changes) |
| `incident-fix` | TDD-based fix implementation from `docs/incident-report.md` |
| `adr` | Architecture Decision Record |
| `code-review` | 5-agent parallel code review (Architecture/Correctness/Reliability/Security/Test) |
| `pr-respond` | PR review response workflow |
| `explain` | Generate shareable explanations for different audiences |
| `empirical-prompt-tuning` | Empirically evaluate and tune prompts/skills with test cases — via [@mizchi](https://github.com/mizchi/skills/blob/main/empirical-prompt-tuning/SKILL.md) |
| `workflow-orchestrator` | End-to-end workflow routing (doc or dev mode) |
| `workflow-dev-mode` | Development workflow (requirements → gap → plan → execute → verify) |
| `workflow-doc-mode` | Documentation workflow (spec/RFC/design artifacts) |
| `test-discover` | Generate test scenarios for a feature or file |
| `test-verify` | Review and validate test scenarios |
| `test-implement` | Implement tests from scenario documents |
| `publish-spec` | Publish spec/plan to Confluence wiki |

## Install

```bash
claude plugin marketplace add https://git.linecorp.com/shinnara/nara-kit.git
```

## Workflow

nara-kit skills are orchestrated in two modes. `workflow-orchestrator` classifies incoming requests and routes to the appropriate mode.

### Mode A — Dev (Implementation)

```mermaid
flowchart TD
    START([Session Start]) --> MWHAT["/mwhat<br>상황 판단"]
    MWHAT --> PREP["/prep<br>SoT 로컬화 + Readiness 판정"]
    PREP --> READY{Readiness?}
    READY -->|"READY (4/4)"| BRAIN["☆ superpowers:brainstorming"]
    READY -->|"PARTIAL/INSUFFICIENT"| OOO_INT["◇ ooo interview<br>요구사항 보완"]
    OOO_INT --> PREP
    BRAIN --> GAP["/gap<br>갭 분석"]
    GAP --> PLAN["☆ superpowers:writing-plans"]
    PLAN --> EXEC{실행 규모?}
    EXEC -->|소규모| DIRECT["직접 구현<br>☆ superpowers:TDD"]
    EXEC -->|대규모| SDD["☆ superpowers:subagent-driven-development"]
    EXEC -->|fallback| OOO_RUN["◇ ooo run / ooo auto"]
    DIRECT --> VERIFY["/gap --verify"]
    SDD --> VERIFY
    OOO_RUN --> VERIFY
    VERIFY --> ADR{아키텍처 결정?}
    ADR -->|yes| ADR_WRITE["/adr"]
    ADR -->|no| REVIEW
    ADR_WRITE --> REVIEW["/code-review<br>5-agent parallel"]
    REVIEW --> CODEX["☆ codex:adversarial-review"]
    CODEX --> REFLECT["/reflect"]
    REFLECT --> FINISH["☆ superpowers:finishing-a-development-branch"]
    FINISH --> PR_RESPOND["/pr-respond<br>리뷰 대응"]
    PR_RESPOND -->|변경 있으면| PR_RESPOND

    style BRAIN fill:#e8f5e9
    style PLAN fill:#e8f5e9
    style DIRECT fill:#e8f5e9
    style SDD fill:#e8f5e9
    style FINISH fill:#e8f5e9
    style CODEX fill:#fff3e0
    style OOO_RUN fill:#e3f2fd
```

### Mode B — Doc (Documentation)

```mermaid
flowchart TD
    START([Session Start]) --> MWHAT["/mwhat<br>기획문서 모드"]
    MWHAT --> ORCH["workflow-orchestrator<br>→ doc mode"]
    ORCH --> OOO_INT["◇ ooo interview<br>요구사항 명확화"]
    OOO_INT --> OOO_PM["◇ ooo pm<br>프로덕트 프레이밍"]
    OOO_PM --> OOO_SEED["◇ ooo seed<br>설계 스냅샷"]
    OOO_SEED --> SPEC["spec artifact 생성"]
    SPEC --> PUB{게시?}
    PUB -->|yes| PUBLISH["/publish-spec<br>→ Confluence"]
    PUB -->|no| RFC_Q{RFC 필요?}
    PUBLISH --> RFC_Q
    RFC_Q -->|yes| RFC["/rfc"]
    RFC_Q -->|no| ADR_Q{아키텍처 결정?}
    RFC --> ADR_Q
    ADR_Q -->|yes| ADR["/adr"]
    ADR_Q -->|no| REFLECT["/reflect"]
    ADR --> REFLECT
    REFLECT --> END([END])

    style OOO_INT fill:#e3f2fd
    style OOO_PM fill:#e3f2fd
    style OOO_SEED fill:#e3f2fd
```

### Design Discovery (workflow-dev-mode 내부)

dev mode에서 요구사항이 불명확할 때 ouroboros skills로 fallback:

```mermaid
flowchart LR
    UNCLEAR{설계 불명확?} -->|yes| INT["◇ ooo interview"]
    INT --> PM["◇ ooo pm"]
    PM --> SEED["◇ ooo seed"]
    SEED --> BACK["→ dev mode 복귀"]
    UNCLEAR -->|no| CONTINUE["→ gap → plan → execute"]

    VERIFY_DONE{구현 완료?} --> EVAL["◇ ooo evaluate"]
    EVAL --> CR["/code-review"]

    style INT fill:#e3f2fd
    style PM fill:#e3f2fd
    style SEED fill:#e3f2fd
    style EVAL fill:#e3f2fd
```

### Legend

| Symbol | Plugin | Used at |
|--------|--------|---------|
| ☆ | **superpowers** | brainstorming, writing-plans, TDD, SDD execution, finishing branch |
| ◇ | **ouroboros** | interview, pm, seed (design discovery), run/auto (execution fallback), evaluate (completion) |
| ☆ | **codex** | adversarial-review (final review) |

## External Plugin Dependencies

nara-kit skills reference external plugin skills at specific workflow stages:

| External Skill | Plugin | Used By | Stage |
|----------------|--------|---------|-------|
| `superpowers:brainstorming` | superpowers | workflow-dev-mode | Step 2 — Design exploration |
| `superpowers:writing-plans` | superpowers | workflow-dev-mode | Step 4 — Plan creation |
| `superpowers:subagent-driven-development` | superpowers | workflow-dev-mode | Step 5 — Large-scale execution |
| `superpowers:test-driven-development` | superpowers | workflow-dev-mode | Step 5 — TDD gate |
| `superpowers:finishing-a-development-branch` | superpowers | workflow-dev-mode | Step 10 — Branch finish |
| `superpowers:receiving-code-review` | superpowers | pr-respond | Core principle |
| `superpowers:using-git-worktrees` | superpowers | workflow-dev-mode | Workspace isolation |
| `ooo interview` | ouroboros | workflow-dev-mode, workflow-doc-mode | Discovery — clarify requirements |
| `ooo pm` | ouroboros | workflow-dev-mode, workflow-doc-mode | Discovery — product framing |
| `ooo seed` | ouroboros | workflow-dev-mode, workflow-doc-mode | Discovery — design snapshot |
| `ooo run` / `ooo auto` | ouroboros | workflow-dev-mode | Step 5 — Execution fallback |
| `ooo evaluate` | ouroboros | workflow-dev-mode | Step 8 — Completion verification |
| `codex:adversarial-review` | codex | workflow-dev-mode | Step 8 — Adversarial final review |

## My Setup

Other plugins I use alongside nara-kit:

| Plugin | Source | Purpose |
|--------|--------|---------|
| `superpowers` | `anthropics/claude-plugins-official` | Skill framework (brainstorming, SDD, worktrees, etc.) |
| `caveman` | `JuliusBrussee/caveman` | Terse response style |
| `claude-mem` | `thedotmack/claude-mem` | Persistent memory across sessions |
| `claude-hud` | `jarrodwatts/claude-hud` | Token/session HUD overlay |
| `ouroboros` | `Q00/ouroboros` | Autonomous evolution engine |
| `plannotator` | `backnotprop/plannotator` | Plan annotation and analysis |
| `harness` | `revfactory/harness` | Multi-agent orchestration |
| `context-mode` | `context-mode` | Context window management |

## Configuration

For `publish-spec`: create `confluence.local.md` in plugin root:

```yaml
---
confluence_base_url: https://your-confluence.example.com
default_space_key: YOUR_SPACE
default_parent_page_id: "YOUR_PAGE_ID"
default_parent_page_name: Development
---
```
