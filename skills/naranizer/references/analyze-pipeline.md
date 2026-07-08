# Analyze Pipeline — 프로필 수집·분석 절차

Slack MCP 기반. 전 과정 read-only — 메시지 발송·리액션 없음.

## Phase 1 — 대상 확정

1. `get_me` → 본인 user_id 확보
2. `list_teams` → workspace team_id (Enterprise면 T-prefix ID 필요)
3. `list_my_channels` → 대상 채널 ID. 결과가 크면 파일로 저장 후 jq로 채널명 검색

## Phase 2 — 수집

1. `get_channel_history` (limit 200, 페이지네이션) → 저장 후 jq 추출:
   - 본인 top-level 메시지: `.messages[] | select(.user==<ID> and .subtype==null) | {ts, text}`
   - 참여 스레드 목록: `.messages[] | select(.reply_users | index(<ID>)) | .thread_ts // .ts`
2. 스레드 수가 많으면 (>30) 최근 N개 샘플링 후 **병렬 서브에이전트 2~3개**로 분산:
   - 각 에이전트: `get_thread_replies` (channel_id, thread_ts) → 본인 메시지만 JSONL append
   - 에이전트 응답은 건수 보고만 — 메시지 본문은 파일로만 전달 (컨텍스트 절약)
3. 병합 + ts 기준 dedup → `corpus.json`
4. **최소 표본 100건.** 미달 시 기간 확대/채널 추가 제안 후 사용자 확인

## Phase 3 — 정량 분석

스크립트(python/jq)로 산출 — LLM 추정 금지:

- 어미 분포: 합니다체/해요체/~네요/~군요/~죠 (정규식, 문장 경계 기준)
- 완곡 패턴: "것 같", "듯하" 빈도
- 이모지: `:[a-z0-9_\-+]+:` 전수 카운트 → 빈도순 사전
- 문장부호: 말줄임, 다중 부호(!!, ?!), ㅋㅋ/ㅎㅎ, ㅜㅠ
- 구조: 불릿(•), 괄호 부연, 멘션+님, 길이 분포(median/p90)

## Phase 4 — 정성 분석

corpus **전량 통독** (부분 샘플 금지 — 통독했음을 명시):

1. **고정 포맷 분리**: 스크럼 불릿, AI 생성 요약 등은 문체 코퍼스에서 제외하고 register 템플릿으로만 등록
2. **Register 분류**: 메시지들을 용도별 그룹핑 (요청/답글/기술 의견/공유/포맷)
3. **시그니처 추출**: 은유, 밈 어휘, 지시어 습관, 요청 공식 — 원문 예시와 함께
4. **"하지 않는 것" 도출**: 없는 것이 특징 — 인사말, 상투구, 이모지 남발, 격식 과잉 등. 정량 데이터와 교차 검증 (예: "감사합니다 2건/175건" → 남발 안 함)

## Phase 5 — 프로필 작성

[profile-schema.md](profile-schema.md) 스키마로 `~/.claude/naranizer/style-profile.md` 작성.

- 기존 프로필 있으면: 주요 변경점 diff 제시 → 사용자 확인 후 덮어쓰기
- receipt 출력: 표본 수, 기간, 제외 건수, 프로필 경로, `recorded only`

## 주의

- 타인 메시지는 수집·저장하지 않는다 (본인 user_id 필터 필수)
- corpus·프로필 모두 로컬 전용. repo 커밋 금지
- 수집 결과가 비정상적으로 적으면 tool result 절단 의심 — 좁은 범위로 재시도
