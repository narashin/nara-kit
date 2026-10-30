# nara-grooming: 사용 가이드

> 사람용 문서. Claude는 런타임에 이 파일을 읽지 않음 (SKILL.md + references만 로드). 호출·용도 안내.

Audit persistent instructions — auto-memory, CLAUDE.md/AGENTS.md and rules files, installed or repo skills — for duplication, conflict, staleness, and stale overrides that explain a behavior the user just corrected. Report first; fix, archive or move only on per-tier approval, with a durable backup before touching files outside git.

## 호출

- Claude Code: `/nara-grooming`
- Codex: `$nara-grooming`
- 또는 자연어 트리거 (아래 USE FOR 키워드)

## 언제 쓰나

- **USE FOR:** "grooming", "메모리 감사", "메모리 점검", "stale memory", "규칙 정리", "CLAUDE.md 중복", "규칙끼리 충돌", "왜 옛날 규칙대로 했지", "스킬 지침 낡았나", "안 쓰는 스킬", memory-audit, after a breaking rename / skill add-remove / migration.
- **DO NOT USE FOR:** 새 메모리 쓰기 (→ nara-retro), 세션 회고·재발 방지 (→ nara-retro), 스킬 개선 실행 (→ nara-skill-forge), 영구 삭제 (수동 rm), 일반 코드 정리.

## 이웃 스킬과의 차이

nara-grooming은 이미 있는 지침을 감사한다. 새 메모리를 쓰는 것은 nara-retro, 스킬 본문을 고치는 것은 nara-skill-forge다.

## 설계 메모

예전 nara-memory-audit의 메모리 2단 감사(`scripts/audit.sh` + 서브에이전트 검증)를 그대로 두고 범위를 규칙과 스킬까지 넓혔다. MTGVim/tiger-kit `tk-grooming`(`5e633e3`, MIT)에서 stale override 증거 사슬, 위치 등급(T1 저장소 밖, T2 추적 안 됨, T3 추적됨)별 승인, 수정 전 영속 백업, vendor 설치본 보존, description 지름길 감사를 가져왔다. model-fit 감사와 tiger-kit 공통 블록은 가져오지 않았다.

안 쓰는 스킬 찾기(`scripts/usage.py`)는 tigerless-labs/autoharness(`4f2a358`, MIT)의 사용률 기반 수명 관리에서 착안했다. 그쪽은 훅으로 자기가 만든 스킬만 세고 자동으로 archive한다. 여기서는 세션 기록을 사후에 읽어 모든 스킬을 세고, 후보만 낸다. 훅으로 세면 사용자가 직접 친 슬래시 호출을 놓친다. 저장소 안에서 SKILL.md를 읽은 것은 개발이라 세지 않는다. 이 런타임 기록에 안 남는 실행(스케줄러, 다른 런타임)은 보정 단계에서 따로 확인한다.

## 더 보기

- 전체 스킬 카탈로그 + 워크플로우: [../README.md](../README.md)
- 스킬 정의(Claude 런타임용): [SKILL.md](SKILL.md)
