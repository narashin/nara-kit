# nara-kit

> **Note:** Personal skill collection by shinnara. Workflows and conventions reflect personal preferences — use as reference or fork to adapt.
>
> 개인 워크플로우 스킬 모음. 개인 취향이 반영되어 있으므로 참고용 또는 포크해서 커스터마이즈.

Personal Claude Code workflow toolkit — **39 skills** for structured software development and documentation workflows, orchestrated in two modes (dev / doc).

Claude Code 워크플로우 툴킷 — 구조화된 개발·문서화 워크플로우를 위한 **39개 스킬** (dev / doc 2-모드 오케스트레이션).

## Install / 설치

```
/plugin marketplace add <repo-url>     # 1. 마켓플레이스 등록 (git URL 또는 로컬 clone 경로)
/plugin install nara-kit@nara-kit      # 2. 설치 (<plugin>@<marketplace> — 양쪽 동일)
# 3. Claude Code 재시작 — hooks는 SessionStart에만 로드됨 (필수)
/plugin list                           # 4. 검증 — nara-kit: Status Enabled, 에러 0
```

캐시 확인: `ls ~/.claude/plugins/cache/nara-kit/nara-kit/<version>/skills/` → 39개 디렉토리면 OK.

**Update**: `/plugin marketplace update nara-kit` → `/plugin update nara-kit` → 재시작.
**Uninstall**: `/plugin uninstall nara-kit` (캐시까지: `rm -rf ~/.claude/plugins/cache/nara-kit/`).

## What's inside / 구성

| 위치 | 내용 |
|------|------|
| **[skills/README.md](skills/README.md)** | 39개 스킬 카탈로그 + 사용법 + 워크플로우(dev/doc mermaid) + Gates + Artifacts + Override 규약 |
| **[references/output-contract.md](references/output-contract.md)** | 모든 스킬이 따르는 공통 출력 규약 (영수증 형식, 상태 라벨, 격상 신호) |
| **hooks/** | SessionStart `memory-audit` hook (auto-memory 건강도 점검) |
| `docs/`, `evals/` | per-project 작업물·평가 (gitignore — 플러그인 배포 대상 아님) |

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

`publish-spec` 사용 시 플러그인 루트에 `confluence.local.md` 생성:

```yaml
---
confluence_base_url: https://your-confluence.example.com
default_space_key: YOUR_SPACE
default_parent_page_id: "YOUR_PAGE_ID"
default_parent_page_name: Development
---
```
