# nara-kit

> **Note:** Personal skill collection by shinnara. Workflows and conventions reflect personal preferences — use as reference or fork to adapt.
>
> 개인 워크플로우 스킬 모음. 개인 취향이 반영되어 있으므로 참고용 또는 포크해서 커스터마이즈.

Personal workflow toolkit in the [Agent Skills](https://github.com/vercel-labs/skills) format — **47 skills** for structured software development and documentation workflows, orchestrated in two modes (dev / doc). Works with Claude Code and Codex.

Agent Skills 포맷 워크플로우 툴킷 — 구조화된 개발·문서화 워크플로우를 위한 **47개 스킬** (dev / doc 2-모드 오케스트레이션). Claude Code + Codex 지원.

## Install / 설치

```bash
npx skills add narashin/nara-kit --global --agent claude-code --agent codex --skill '*'
```

- `--global`: 모든 프로젝트에서 사용. 특정 스킬만: `--skill nara-gap --skill nara-code-review`
- 호출: `/nara-<skill>` (예: `/nara-prep PROJ-1234`), Codex는 `$nara-<skill>`, 또는 자연어 트리거
- **Update**: `npx skills update`
- 검증: `ls ~/.claude/skills | grep -c '^nara-'` → 46 (+ `naranizer` = 47)

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
| **[skills/README.md](skills/README.md)** | 47개 스킬 카탈로그 + 사용법 + 워크플로우(dev/doc mermaid) + Gates + Artifacts + Override 규약 |
| **[references/output-contract.md](references/output-contract.md)** | 모든 스킬이 따르는 공통 출력 규약 (영수증 형식, 상태 라벨, 격상 신호) |
| `docs/`, `evals/` | per-project 작업물·평가 (gitignore — 설치 대상 아님) |

스킬 한눈에 보기 + 워크플로우 다이어그램 → **[skills/README.md](skills/README.md)**.

## My Setup / 내 설정

nara-kit과 함께 쓰는 플러그인:

| Plugin | Source | Purpose |
|--------|--------|---------|
| `superpowers` | `obra/superpowers` | Skill framework (brainstorming, SDD, plans, worktrees) |
| `caveman` | `JuliusBrussee/caveman` | Terse response style |
| `claude-mem` | `thedotmack/claude-mem` | Persistent memory across sessions |
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
