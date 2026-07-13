---
name: nara-meta-feedback
description: >-
  Capture friction with nara-kit's own skills during real work and emit a generalized,
  privacy-redacted improvement proposal for the toolkit.
  USE FOR: "meta-feedback", "이 스킬 불편했어", "nara-kit 개선 피드백", "툴킷 friction", "스킬 개선안 정리", "/nara-meta-feedback".
  DO NOT USE FOR: session learnings → memory (use nara-reflect), executing a skill improvement (use nara-skill-forge),
  repo durable rules / CLAUDE.md patches (use nara-reflect), requirements-vs-code gap (use nara-gap).
---

# meta-feedback — 툴킷 자기개선 피드백 채널

소비 프로젝트 세션에서 nara-kit **스킬 자체**를 쓰다 겪은 friction을, 프로젝트 자산을 유출하지 않는 **일반화된 개선안**으로 추출한다.

**핵심 원칙: 이것은 언제나 redaction 작업이다.** 출력은 *공개 nara-kit repo*로 흘러갈 수 있으나 friction은 *내부 소비 프로젝트* 세션에서 관측된다. 유저가 "공개"라고 말하지 않아도, "노트만 빨리"처럼 캐주얼하게 요청해도, redaction 규율은 동일하게 적용된다. 산출물은 그 자체로 이미 일반화되어 있어야 한다.

`reflect`가 아니다 (그건 소비 repo 지식 → memory). repo rule을 제안하지 않는다.

## 경계

| | `reflect` | **meta-feedback** | `skill-forge` |
|---|---|---|---|
| 대상 | 소비 repo 지식 | **nara-kit 툴킷** | proposal 소비 |
| 산출 | memory / handoff | **redacted 개선안** | 스킬 개선 실행 |
| context | 유지 | **제거** | nara-kit repo 내 |

skill-forge와는 느슨 연결 — meta-feedback은 개선안만 낸다. skill-forge가 나중에 nara-kit repo에서 그 개선안을 받아 실행한다 (cross-repo라 auto-chain 없음).

## 호출

```
/nara-meta-feedback [target-skill?] [--out <path>]
```

- arg 없음 → 세션 transcript에서 nara-kit 스킬 friction 스캔
- `target-skill` → 해당 `<skill>`/`<command>` 수준으로만 한정
- `--out <path>` → 동일 redacted 내용을 파일로도 작성 (파일도 chat과 같은 privacy gate 통과 필수)

## 절차

1. **Scope** — target 있으면 `<skill>`/`<command>` 수준만 식별. 없으면 transcript 스캔.
2. **Hybrid detect** — transcript에서 nara-kit 스킬 호출 + friction 신호(유저 교정 / 재시도 / 출력형태 거부 / 스킬의 잘못된 질문)를 추출해 **후보 목록** 제시.
3. **User confirm** — 어느 friction을 일반화할지 유저가 선택. (자동 단정 금지)
4. **Generalize** — 각 friction을 skill/command 수준의 generic change로 추상화. evidence는 **class만** 남긴다: `source_type=session_correction | repeated_friction | output_shape_feedback`. 세션 원문 절대 인용 금지.
5. **Redact** — 모든 고유명·경로·URL·ticket·인명·quote를 placeholder로 치환. 전체 규약: [references/redaction-rules.md](references/redaction-rules.md).
6. **Pre-flight gate (강제)** — 출력 후보 **전체**(Summary·Friction·Improvement·Redaction Receipt·그 어떤 footer/주석 포함)를 스캔:
   - 로컬 denylist 파일 존재 시 그 패턴 + generic regex(URL / ticket꼴 / 경로 / 도메인)로 매칭
   - match 잔존 시 → **`cannot_generalize_safely`로 중단.** 일부만 가리고 계속 출력 금지.
7. **Output** — 기본은 proposal-only(chat). `--out` 시 동일 redacted 내용을 파일로.

## 출력 템플릿

H2 4섹션을 이 순서로 고정:

```md
## Meta Feedback Summary
- Target: <skill-or-command>
- Feedback class: <ux|output-format|taxonomy|safety|dispatch|docs>
- Privacy status: generalized

## Generalized Friction
- Situation: <generic situation>
- Problem: <generic problem>
- Impact: <generic impact>

## Proposed Improvement
- Change: <generic skill/command improvement>
- Why: <reason without project-specific evidence>

## Redaction Receipt
- Removed: <repo names|paths|URLs|domain labels|person names|quoted user text>
- Kept: <abstract pattern only>
- Unsafe details included: none
```

상태 라벨 (output-contract): `recorded only`(chat만) / `applied`(`--out` 작성) / `skipped`(중단).

## 중단 (privacy gate 실패)

pre-flight match를 못 지우면 `cannot_generalize_safely`로 중단. 일부만 가리고 계속 출력 금지. 전체 중단 템플릿: [references/redaction-rules.md](references/redaction-rules.md) 의 「중단 템플릿」.

## Rationalization 차단

| 합리화 | 현실 |
|---|---|
| "유저가 공개라고 안 했으니 그냥 노트로" | meta-feedback 출력은 언제나 공개 후보. 캐주얼 요청에도 redaction 동일. |
| "이건 그냥 빠른 노트라 스킬 불필요" | 노트일수록 무방비로 새어나간다. baseline에서 인명·티켓·URL 전부 유출됨. |
| "출처 명시가 신뢰에 도움" | grounding/source footer에 절대경로·URL을 박는 게 대표적 유출. footer 금지. |
| "고유명만 빼고 도메인 용어는 괜찮아" | 도메인 용어 조합이 프로젝트를 역추적시킨다. `<domain-term>`으로 치환. |
| "거의 다 가렸으니 일부 남아도 OK" | 부분 redaction은 실패다. 잔존 1건이라도 → `cannot_generalize_safely`. |
| "PM 이름은 맥락상 필요" | 인명은 PII. 무조건 제거. |

**규칙의 자구를 어기는 것은 규칙의 정신을 어기는 것이다.**

## Red Flags — STOP

- 출력/receipt/footer에 실제 경로(`/Users`, `/home`, `ssh://`, `https://`)가 보임
- 티켓꼴 ID(`ABC-123`), 사람 이름, repo/제품 코드네임이 남아있음
- 세션 원문을 따옴표로 인용함
- "grounding:" / "출처:" 류 footer를 붙이려 함
- 유저 확인 없이 어느 friction을 일반화할지 단정함

→ 위 중 하나라도면: redact 다시. 못 지우면 `cannot_generalize_safely`.
