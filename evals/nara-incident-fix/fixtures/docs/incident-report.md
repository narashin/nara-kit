# Incident Report: 인사말 API가 빈 이름에 "Hello, !"를 돌려준다

- Ticket: PROJ-123
- Reported: 2026-10-01
- Severity: Minor

## 1. Summary
`greet` 엔드포인트가 이름이 비어 있거나 공백뿐일 때 400 대신 `"Hello, !"`를 200으로 돌려준다.

## 2. Impact
환영 배너에 이름 없는 인사가 노출된다. 데이터 손상은 없다.

## 3. Reproduction
`sample.py`의 `hello("")` → `"Hello, !"`, `hello("   ")` → `"Hello,    !"`.

## 4. Root Cause Analysis
### Hypothesis A: 입력 검증 없음 ⭐ (유력)
`hello(name)`이 `name`을 검증하지 않고 그대로 포매팅한다 (`sample.py:3`).
### Hypothesis B: 호출부가 기본값을 빈 문자열로 넘김
호출부 코드가 이 저장소에 없어 확인 못 함 [UNVERIFIED: requires caller repo].

## 5. Proposed Fix
`hello`가 `name.strip()`이 비면 `ValueError`를 던진다. 호출부는 이를 400으로 바꾼다.

## 6. Side Effects
`hello`를 부르는 다른 곳이 빈 문자열을 정상 입력으로 기대하면 예외가 난다. 이 저장소 안에는 호출부가 없다.

## 7. Similar Patterns
없음.

## 8. Test Gap
`hello`에 대한 테스트가 없다.

## 9. Prevention
입력 검증 테스트를 추가한다.

## 10. Self-Review (반대 심문 결과)
Hypothesis B는 근거가 없어 수정 범위에 넣지 않았다.
