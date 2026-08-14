# nara-kit

> **Note:** Personal skill collection by shinnara. Workflows and conventions reflect personal preferences — use as reference or fork to adapt.
>
> 개인 워크플로우 스킬 모음. 개인 취향이 반영되어 있으므로 참고용 또는 포크해서 커스터마이즈.

Personal workflow toolkit in the [Agent Skills](https://github.com/vercel-labs/skills) format — **48 skills** for structured software development and documentation work. Skills are invoked directly; `nara-now` reads the session state and names the next command. Works with Claude Code and Codex.

Agent Skills 포맷 워크플로우 툴킷 — 개발·문서화 작업을 위한 **48개 스킬**. 스킬을 직접 호출하고, 다음에 뭘 할지는 `nara-now`가 알려준다. Claude Code + Codex 지원.

## Install / 설치

```bash
npx skills add narashin/nara-kit --global --agent claude-code --agent codex --skill '*'
```

- `--global`: 모든 프로젝트에서 사용. 특정 스킬만: `--skill nara-gap --skill nara-code-review`
- 호출: `/nara-<skill>` (예: `/nara-prep PROJ-1234`), Codex는 `$nara-<skill>`, 또는 자연어 트리거
- **Update**: `npx skills update` — 단 **이미 설치된 스킬만 갱신한다.** 새로 추가된 스킬을 받으려면 위 `add` 명령을 다시 실행해야 하고, **제거된 스킬은 자동으로 지워지지 않아** 직접 삭제해야 한다
- 검증: `ls ~/.claude/skills | grep -c '^nara-'` → 47 (+ `naranizer` = 48)

### v0.21.0 업그레이드 (breaking)

워크플로 메타 스킬 4종이 제거됐다. `npx skills update`는 삭제를 반영하지 않으므로 **수동 정리가 필요하다** — 남겨두면 존재하지 않는 흐름을 가리키는 지침이 계속 로드된다.

```bash
rm -rf ~/.claude/skills/nara-workflow-*     # 심링크 설치면 실타겟(~/.agents/skills/...)도 함께
npx skills add narashin/nara-kit --global --agent claude-code --agent codex --skill '*'
```

대체: `orchestrator`/`dev-mode`/`doc-mode` → 개별 스킬 직접 호출 + `nara-now`의 다음 행동 추천 · `viz` → 대체 없음 · Implementation Notes Gate → `nara-implement`.

### 플러그인에서 이전 / Migrating from the plugin

v0.16까지는 Claude Code 플러그인으로 배포. 스킬 포맷 전환에 따라 기존 플러그인 제거 후 위 명령으로 재설치:

```
/plugin uninstall nara-kit@nara-kit
/plugin marketplace remove nara-kit
```

- 캐시 정리(선택): `rm -rf ~/.claude/plugins/cache/nara-kit/`
- 호출 이름 변경: `/nara-kit:<skill>` → `/nara-<skill>` — CronCreate 등 자동화에 등록한 프롬프트도 새 이름으로 재등록
- SessionStart hook(memory-audit)은 스킬 포맷에 없어 제거됨 — memory-audit/memory-archive 스킬 자체도 폐기

## What's inside / 구성

| 위치 | 내용 |
|------|------|
| **[skills/README.md](skills/README.md)** | 48개 스킬 카탈로그 + 권장 흐름(mermaid) + Gates + Artifacts + Override 규약 |
| **[CHANGELOG.md](CHANGELOG.md)** | 버전별 변경. 각 git tag = 여기 한 섹션 (breaking은 업그레이드 절차 포함) |
| **[references/output-contract.md](references/output-contract.md)** | 모든 스킬이 따르는 공통 출력 규약 (영수증 형식, 상태 라벨, 격상 신호) |
| `docs/`, `evals/` | per-project 작업물·평가 (gitignore — 설치 대상 아님) |

스킬 한눈에 보기 + 워크플로우 다이어그램 → **[skills/README.md](skills/README.md)**.

## My Setup / 내 설정

nara-kit과 함께 쓰는 플러그인:

| Plugin | Source | Purpose |
|--------|--------|---------|
| `caveman` | `JuliusBrussee/caveman` | Terse response style |
| `engram` | `Gentleman-Programming/engram` | Persistent memory across sessions (worktree 지원 — claude-mem 대체) |
| `claude-hud` | `jarrodwatts/claude-hud` | Token/session HUD overlay |
| `plannotator` | `backnotprop/plannotator` | Plan annotation and analysis |
| `codex` | `openai/codex-plugin-cc` | Codex integration (adversarial review, rescue) |

## Inspired By / 영감

- [empirical-prompt-tuning](https://github.com/mizchi/skills/blob/main/empirical-prompt-tuning/SKILL.md) by @mizchi
- [superpowers](https://github.com/obra/superpowers) by @obra

## Configuration / 설정

`nara-publish-spec` 사용 시 `~/.claude/confluence.local.md` 생성:

```yaml
---
confluence_base_url: https://your-confluence.example.com
default_space_key: YOUR_SPACE
default_parent_page_id: "YOUR_PAGE_ID"
default_parent_page_name: Development
---
```
