---
name: naranizer
description: >-
  Rewrite AI-drafted Korean text (Slack messages, review comments, announcements) into the user's own measured writing style, loaded from a local style profile built from real message history.
  USE FOR: "나라나이저", "naranize", "내 말투로", "내 스타일로 바꿔", "말투 프로필 만들어", "말투 프로필 갱신".
  DO NOT USE FOR: 일반 AI 티 제거 without persona (use humanizer), 영어 텍스트, 내용 요약·사실 수정 (문체만 다룸), 코드 리뷰 (use code-review).
license: MIT
---

# naranizer — 개인 말투 변환

AI가 작성한 한국어 초안을 **실측 스타일 프로필** 기반으로 사용자 본인의 말투로 재작성한다. 프로필은 실제 Slack 메시지 히스토리에서 추출하며 로컬 전용 — 이 스킬은 절차만 배포하고 데이터는 배포하지 않는다.

humanizer와의 관계: naranizer = humanizer 선행 적용 + 페르소나. transform은 humanizer의 검출·교정 플로우를 pre-pass로 실행한 뒤 프로필을 입힌다. "자연스럽게"만 원하면 → humanizer 단독, "내 말투로" → naranizer.

## 프로필

- 기본 경로: `~/.claude/naranizer/style-profile.md` (사용자가 다른 경로를 지정하면 그 경로 사용 — 테스트/eval용)
- 스키마와 placeholder 예시: [profile-schema.md](references/profile-schema.md)
- **프로필은 커밋 금지.** 실명·내부 URL·원문 인용 포함 — repo에 절대 넣지 않는다.

## 모드 판별

| 입력 | 모드 |
|------|------|
| 변환할 텍스트 존재 ("이거 내 말투로") | **transform** (기본) |
| "프로필 만들어/갱신해" + 채널 지정 | **analyze** |

## Mode: transform

### Step 1 — 프로필 로드 (하드 게이트)

프로필 파일을 Read. **없으면 즉시 중단** (실패 블록에는 실제 시도한 경로를 표기):

```
❌ 실패: 스타일 프로필 없음 (<시도한 경로>)
→ "naranizer 프로필 만들어줘 <채널명>" 으로 analyze 모드 먼저 실행
```

추측으로 말투를 흉내내지 않는다. 프로필 생성일이 6개월 초과면 출력 끝에 갱신 권고 한 줄 추가 (진행은 함).

### Step 2 — Register 자동 감지

플래그 없음. 입력 텍스트 형태로 판별:

| 신호 | Register |
|------|----------|
| 멘션 대상 + 요청 동사 ("~해주세요" 의도) | ① 요청/공지 |
| 1~2문장 응답·리액션 | ② 캐주얼 답글 |
| 불릿/코드/기술 용어 밀도 높음 | ③ 기술 의견/리뷰 |
| 링크 + 소개·추천 문구 | ④ 공유 |
| 프로젝트별 진행 상태 나열 | ⑤ 데일리 스크럼 (고정 포맷 적용) |

애매하면 ③ (가장 보수적)으로 처리하고 판별 결과를 출력에 명시.

### Step 3 — 재작성

**Pre-pass (humanizer 인라인 실행)**: 같은 플러그인의 `../humanizer/SKILL.md` (이 스킬 디렉토리 기준 상대 경로)를 Read하고 그 워크플로우로 1차 윤문. 카테고리별 reference 파일은 humanizer 자체 규칙대로 해당 패턴이 감지될 때만 로드 — 짧은 텍스트는 대부분 스킵. 스킬 재호출이 아니라 같은 플러그인 내 파일 참조.

그 위에 프로필의 해당 register 규칙 + 전역 규칙(어미 분포, 이모지 사전, 구조 습관)을 적용해 재작성.

**충돌 시 우선순위**: Step 4 가드레일 > register 규칙 > 프로필 구조 습관 > humanizer 교정. humanizer가 중화한 표현을 프로필이 개성으로 요구하면 프로필이 이긴다.
"문체만 변경"의 경계 — 정보(사실·수치·링크·요청 대상·의미)는 불변, 표현(어미·어순·문형·단정→완곡 강도)은 변경 가능. 예: "줄여야 합니다"→"줄이는 것이 어떨까요?"는 허용, 링크에 검증 안 된 평가를 새로 붙이는 것은 창작이므로 금지.

### Step 4 — 가드레일 자체검증 (필수 게이트)

출력 전 점검. 위반 시 수정 후 재점검:

- [ ] **사실 불변**: 날짜·수치·링크·멘션 대상·요청 내용 verbatim 보존. 문체만 변경
- [ ] **이모지 상한**: 메시지당 최대 2개, 문장 끝만, 프로필 사전에 있는 것만
- [ ] **유머 상한**: 은유·밈 어휘 최대 1회. 원문에 유머 요소 없으면 새로 추가 금지 — 톤만 입히고 내용 창작 금지
- [ ] **금지 패턴 0건**: 프로필 "하지 않는 것" 목록 위반 없음
- [ ] **존댓말 유지**: 반말 어미 0건 (프로필이 반말 화자가 아닌 한)

### Step 5 — 출력

```
## 변환 결과 (register: ③ 기술 의견/리뷰)

[재작성 텍스트]

---
naranizer: register=③, humanizer-prepass ✓, emoji 1/2, 유머 0/1, 금지패턴 0건, 존댓말 ✓, 사실보존 ✓
```

register 라벨은 Step 2 표의 이름을 그대로 사용.

trailing status 한 줄은 생략 불가. 변경폭이 커서 원문 대조가 필요하면 주요 변경 2~3개를 불릿으로 덧붙인다.

## Mode: analyze

수집·분석 파이프라인 상세: [analyze-pipeline.md](references/analyze-pipeline.md)

요약: Slack MCP로 대상 채널에서 본인 메시지 수집 (top-level + 참여 스레드, 병렬 서브에이전트 분산) → 고정 포맷 메시지 제외 → 정량 분석(어미/이모지/문장부호 빈도) + 정성 분석(전량 통독, register 분류, "하지 않는 것" 도출) → [profile-schema.md](references/profile-schema.md) 스키마로 프로필 작성.

- 최소 표본: 메시지 100건. 미달 시 수집 기간 확대 또는 채널 추가 제안 후 사용자 확인
- 기존 프로필 있으면 갱신 diff를 보여주고 덮어쓰기 확인
- 완료 시 receipt: 표본 수, 기간, 프로필 경로, `recorded only`

## 특수 상황

| 상황 | 처리 |
|------|------|
| 영어/혼합 텍스트 | 영어 부분 원형 유지, 한국어만 변환. 전체 영어면 스킬 부적합 안내 |
| 이미 프로필 톤에 가까운 텍스트 | 과교정 금지. 사소한 조정만 + "이미 근접" 명시 |
| register ⑤ (스크럼) | 문체 변환이 아닌 고정 포맷 적용 — 프로필의 포맷 템플릿 사용 |
| 수신자가 다른 언어 화자 | 이모지·밈은 유지하되 은유는 직역 불가 — 은유 0회로 하향 |

## 출력 contract

- transform: 응답 = 변환본 + trailing status (윤문류 스킬 — 산출물 자체가 응답)
- analyze: 표준 receipt (프로필 경로 = artifact, `recorded only`)
- 외부 시스템 부수효과: analyze의 Slack MCP read-only 호출뿐. 메시지 발송 없음
