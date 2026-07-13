# Redaction Rules

meta-feedback의 privacy gate 전체 규약. 이 파일은 **공개 nara-kit repo에 실린다 → 조직 특수 코드네임을 절대 담지 않는다.** 조직 특수 패턴은 로컬 denylist(아래)에만 둔다.

## Generalization Taxonomy

원본 유형을 placeholder 또는 evidence class로 치환한다.

| 원본 | 치환 |
|---|---|
| repo / product / customer / org 이름 | `<project>` |
| page / menu / title / feature 이름 | `<domain-term>` 또는 `<ui-label>` |
| local path 또는 source path | `<internal-path>` |
| URL, ticket, issue, PR, branch, commit | `<reference>` |
| 사람 이름 (PM, 리뷰어, 동료 등) | `<person>` |
| skill / command 이름 (nara-kit 자체) | `<skill>` / `<command>` (식별 목적상 실제 이름 허용 — 이건 공개 툴킷의 자기 자산) |
| 사용자 원문 발화 | `source_type=session_correction` |
| 세션의 구체적 시행착오 | `source_type=repeated_friction` |
| 출력 형태에 대한 불만 | `source_type=output_shape_feedback` |

> 주의: nara-kit 자신의 자산은 노출 OK — 유출 대상은 **소비 프로젝트** 자산이다.
> - nara-kit 스킬/command 이름 (`gap`, `commit`, `prep` 등)
> - nara-kit 컨벤션 경로 (`docs/requirements.md`, `docs/gap.md`, `.claude/overrides/<skill>.md` 등)
>
> 이들은 over-redact하지 말 것 — 개선안의 유용성이 떨어진다. `<internal-path>`로 가리는 건 *소비 프로젝트* 경로에만.

## Local Denylist (not shipped)

조직 특수 패턴은 gitignore된 로컬 파일에 둔다 — 공개 스킬 본문엔 없음.

- 위치: `.claude/overrides/meta-feedback.md` (기존 `*.local.md` gitignore 규칙 + 프로젝트 override 컨벤션과 정합)
- 내용 예시 (각 줄 = 리터럴 또는 regex):
  - 사내 도메인 (예: `*-internal.example`, 회사 git 호스트)
  - 프로젝트 코드네임
  - 티켓 prefix
- 로드 규약: 출력 직전 이 파일이 있으면 읽어 pre-flight 스캔 패턴에 합친다. 없으면 generic regex만으로 스캔.

## Pre-flight Scan (mechanical, 강제)

출력 후보 **전체 텍스트**(4섹션 + 어떤 footer/주석이든)를 아래로 스캔. contract-enforcement 원칙: 선언만으로는 안 지켜진다 — 기계적 gate가 필수.

generic regex (조직 무관, 공개 OK):

| 패턴 | 의미 |
|---|---|
| `https?://\S+` , `ssh://\S+` , `git@\S+` | URL / git 원격 |
| `/Users/\S+` , `/home/\S+` , `[A-Za-z]:\\\S+` | 절대 경로 |
| `\b[A-Z]{2,}-\d+\b` | 티켓꼴 ID (JIRA류) |
| `\b[a-z0-9.-]+\.(example|com|net|io|corp|local)\b` | 도메인 흔적 (false positive 가능 → 문맥 확인) |

판정:
- 로컬 denylist 패턴 match → **무조건 block**
- generic regex match → 해당 토큰이 소비 프로젝트 자산이면 placeholder로 치환 후 재스캔. 치환 불가/모호하면 block.
- block = `cannot_generalize_safely`로 중단. **부분 출력 금지.**

## No Source Footer

"grounding:", "출처:", "분석 근거:" 류 footer를 붙이지 않는다. baseline 테스트에서 본문은 깨끗해도 이 footer에 절대경로가 새어나왔다. 개선안은 본문 4섹션으로 끝낸다.

## PII

사람 이름·이메일·핸들은 맥락상 "필요해 보여도" 무조건 `<person>`으로 제거. 인명은 일반화 가치가 없고 PII 위험만 있다.

## 중단 템플릿 (privacy gate 실패)

pre-flight에서 잔존 match를 못 지우면 이 형식으로 중단한다. 일부만 가리고 계속 출력 금지.

```md
## Meta Feedback Summary
- Target: <skill-or-command>
- Feedback class: safety
- Privacy status: cannot_generalize_safely

## Generalized Friction
- Situation: cannot report safely without exposing project-specific details
- Problem: cannot report safely without exposing project-specific details
- Impact: cannot report safely without exposing project-specific details

## Proposed Improvement
- Change: none
- Why: privacy gate failed

## Redaction Receipt
- Removed: attempted project-specific details
- Kept: none
- Unsafe details included: none
```
