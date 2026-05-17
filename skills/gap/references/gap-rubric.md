# Gap Rubric — 결함 판정 기준

LLM 자의 판단 방지용. 모든 gap 분석에서 이 룰을 기계적으로 적용.

## 1. Verbatim (exact match — 다르면 Missing 강제)

다음 항목은 의미 동등성과 무관하게 **문자 단위 정확 일치** 필요. 다르면 결함.

- `requirements.md` 안 따옴표(`"..."`, `'...'`), 백틱(`` `...` ``), 코드블록(``` ``` ```) 안 모든 텍스트
- UI 카피 (라벨, 버튼, 플레이스홀더, 에러 메시지, 토스트)
- 단위 표기 (괄호 단위 포함/누락 포함)
- API endpoint 경로, query param key
- env var name, config key, 상수 식별자
- 파일/디렉토리 경로

### 자동 강등 룰

| 상황 | 처리 |
|---|---|
| verbatim 텍스트가 코드 grep 결과 0건 | **Missing 강제** (LLM 판단 무시) |
| verbatim 텍스트와 코드 텍스트가 띄어쓰기/개행/특수문자 차이 | **Missing 강제** |
| verbatim 텍스트와 코드 텍스트가 단위/괄호 포함 차이 | **Missing 강제** |

## 2. Semantic (의미 동등 OK — Implemented 가능)

다음 항목은 표현 달라도 역할 동일하면 Implemented.

- 비즈니스 로직 흐름, 조건 분기 구조
- 함수/변수 이름 (역할 일치 시)
- 데이터 변환 순서
- 에러 처리 패턴

## 3. Evidence 강제 룰

| 상황 | 처리 |
|---|---|
| Implemented 주장에 `파일:라인` 없음 | **Partial 강등** |
| 요구사항 문장 ↔ 코드 라인 1:1 매핑 불가 | **Partial 강등** |
| Evidence 라인이 실제 요구사항 만족 입증 불가 | **Partial 강등** |

## 4. Forced Doubt Sampling

Implemented로 분류한 항목 중:

- 최소 2개 또는 전체의 20% (큰 쪽) 무조건 `Needs Confirm` 섹션에 표시
- user 확인 요청용. LLM 자가 확신 우회.
- 우선순위: verbatim 항목 > evidence 라인 짧은 항목 > 무작위

## 5. 비대상 (이 rubric 적용 안 함)

- `Agreed Exceptions` 항목
- `[UNVERIFIED]` 항목 (별도 처리)
